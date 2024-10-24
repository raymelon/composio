import os
import datetime
from agent.helper import DiffFormatter


from composio_langgraph import Action, App, ComposioToolSet, WorkspaceType
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_aws import BedrockChat
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
import dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import typing as t
import operator
from agent.tools import pr_get_diff, pr_get_metadata
from agent.prompts import SYSTEM_LANGGRAPH as SYSTEM
from agent.prompts import REPO_ANALYZER_PROMPT

dotenv.load_dotenv()

def add_thought_to_request(request: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    request["thought"] = {
        "type": "string",
        "description": "Provide the thought of the agent in a small paragraph in concise way. This is a required field.",
        "required": True,
    }
    return request


def pop_thought_from_request(request: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    request.pop("thought", None)
    return request

def _github_pulls_create_review_comment_post_proc(response: dict) -> dict:
    if response["successfull"]:
        return {"message": "commented sucessfully"}
    return {"error": response["error"]}

def _github_list_commits_post_proc(response: dict) -> dict:
    if not response['successfull']:
        return {'error': response['error']}
    commits = []
    for commit in response.get("data", {}).get("details", []):
        commits.append(
            {
                "sha": commit["sha"],
                "author": commit["commit"]["author"]["name"],
                "message": commit["commit"]["message"],
                "date": commit["commit"]["author"]["date"],
            }
        )
    return {'commits': commits}


def _github_diff_post_proc(response: dict) -> dict:
    if not response['successfull']:
        return {'error': response['error']}
    return {'diff': DiffFormatter(response['data']['details']).parse_and_format()}

def _github_get_a_pull_request_post_proc(response: dict):
    if not response['successfull']:
        return {'error': response['error']}
    pr_content = response.get("data", {}).get("details", [])
    contents = pr_content.split("\n\n---")
    pr_content = ""
    for i, content in enumerate(contents):
        if "diff --git" in content:
            index = content.index("diff --git")
            content_filtered = content[:index] 
            if i != len(contents) - 1:
                content_filtered += "\n".join(content.splitlines()[-4:])
        else:
            content_filtered = content
        pr_content += content_filtered
    return {"details": pr_content, "message": "PR content fetched successfully, proceed with getting the diff of PR or individual commits"}
    



toolset = ComposioToolSet(
    processors={
        "pre": {
            App.GITHUB: pop_thought_from_request,
        },
        "schema": {
            App.GITHUB: add_thought_to_request,
        },
        "post": {
            Action.GITHUB_CREATE_AN_ISSUE_COMMENT: _github_pulls_create_review_comment_post_proc,
            Action.GITHUB_CREATE_A_REVIEW_COMMENT_FOR_A_PULL_REQUEST: _github_pulls_create_review_comment_post_proc,
            Action.GITHUB_LIST_COMMITS_ON_A_PULL_REQUEST: _github_list_commits_post_proc,
            Action.GITHUB_GET_A_COMMIT: _github_diff_post_proc,
            Action.GITHUB_GET_A_PULL_REQUEST: _github_get_a_pull_request_post_proc,
            # Action.GITHUB_LIST_REVIEW_COMMENTS_ON_A_PULL_REQUEST: _github_list_review_comments_on_a_pull_request_post_proc,
        }
    }
)

tools = [
    *toolset.get_tools(
        actions=[
            Action.GITHUB_GET_A_PULL_REQUEST,
            Action.GITHUB_LIST_COMMITS_ON_A_PULL_REQUEST,
            Action.GITHUB_GET_A_COMMIT,
            Action.GITHUB_CREATE_A_REVIEW_COMMENT_FOR_A_PULL_REQUEST,
            Action.GITHUB_CREATE_AN_ISSUE_COMMENT,
            # Action.GITHUB_LIST_REVIEW_COMMENTS_ON_A_PULL_REQUEST,
            pr_get_diff,
            pr_get_metadata,
        ]
    )
]



# client = ChatOpenAI(
#     model="gpt-4-turbo",
#     temperature=0,
#     max_completion_tokens=4096,
#     api_key=os.environ["OPENAI_API_KEY"],
# )

client = BedrockChat(
    credentials_profile_name="default",
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
    region_name="us-east-1",
    model_kwargs={"temperature": 0, "max_tokens": 8192},
)



tool_node = ToolNode(tools)

class AgentState(t.TypedDict):
    messages: t.Annotated[t.Sequence[BaseMessage], operator.add]
    sender: str

pr_review_agent_name = "PR-Review-Agent"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def invoke_with_retry(agent, state):
    return agent.invoke(state)

def create_agent_node(agent, name):
    def agent_node(state):
        # if isinstance(state["messages"][-1], AIMessage):
        #     state["messages"].append(HumanMessage(content="Placeholder message"))

        try:
            result = invoke_with_retry(agent, state)
        except Exception as e:
            print(f"Failed to invoke agent after 3 attempts: {str(e)}")
            result = AIMessage(
                content="I apologize, but I encountered an error and couldn't complete the task. Please try again or rephrase your request.",
                name=name,
            )
        if not isinstance(result, ToolMessage):
            if isinstance(result, dict):
                result_dict = result
            else:
                result_dict = result.dict()
            result = AIMessage(
                **{
                    k: v
                    for k, v in result_dict.items()
                    if k not in ["type", "name"]
                },
                name=name,
            )
        return {"messages": [result], "sender": name}
    return agent_node
        
def create_agent(system_prompt, tools):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    llm = client
    if tools:
        # return prompt | llm.bind_tools(tools)
        return prompt | llm.bind_tools(tools)
    else:
        return prompt | llm

pr_agent = create_agent(SYSTEM, tools)
pr_agent_node = create_agent_node(pr_agent, pr_review_agent_name)

workflow = StateGraph(AgentState)

workflow.add_node(pr_review_agent_name, pr_agent_node)
workflow.add_node("tool_node", tool_node)
workflow.add_edge(START, pr_review_agent_name)

def router(state) -> t.Literal["tool_node", "continue", "__end__"]:
    messages = state["messages"]
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            last_ai_message = message
            break
    else:
        last_ai_message = messages[-1]
    
    if last_ai_message.tool_calls:
        return "tool_node"
    if "REVIEW COMPLETED" in last_ai_message.content:
        return "__end__"
    return "continue"

workflow.add_conditional_edges(
    "tool_node",
    lambda x: x["sender"],
    {pr_review_agent_name: pr_review_agent_name},
)
workflow.add_conditional_edges(
    pr_review_agent_name,
    router,
    {
        "continue": pr_review_agent_name,
        "tool_node": "tool_node",
        "__end__": END,
    },
)

graph = workflow.compile()

########################################################
import os
from io import BytesIO

from IPython.display import Image, display
from PIL import Image

png_data = graph.get_graph().draw_mermaid_png(
    draw_method=MermaidDrawMethod.API,
)

image = Image.open(BytesIO(png_data))

output_path = "workflow_graph.png"
image.save(output_path)

