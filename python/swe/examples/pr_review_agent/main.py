from composio.utils.logging import WithLogger
from pydantic import BaseModel, Field

from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import FunctionCallingAgentWorker, AgentRunner
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI

from composio import Action

from composio_llamaindex import ComposioToolSet, Action
from agent.tools import get_diff
from agent.prompts import SYSTEM


def _github_pulls_create_review_comment_post_proc(response: dict) -> dict:
    if response["successfull"]:
        return {"message": "commented sucessfully"}
    return {"error": response["error"]}


def _github_list_review_comments_on_a_pull_request_post_proc(response: dict) -> dict:
    if not response["successfull"]:
        return {"error": response["error"]}

    comments = []
    for comment in response.get("data", {}).get("details", []):
        comments.append(
            {
                "author": comment["user"]["login"],
                "body": comment["body"],
                "file": comment["path"],
                "content": comment["diff_hunk"],
                "commitId": comment["commit_id"],
            }
        )
    return {"comments": comments}


class AgentConfig(BaseModel):

    model: str = Field(
        default="gpt-4-turbo",
        description="LLM Model to use.",
    )


def get_tools(toolset: ComposioToolSet) -> list:
    return list(
        toolset.get_tools(
            actions=[
                Action.GITHUB_LIST_PULL_REQUESTS,
                Action.GITHUB_GET_A_PULL_REQUEST,
                Action.GITHUB_GET_A_COMMIT,
                Action.GITHUB_PULLS_CREATE_REVIEW_COMMENT,
                Action.GITHUB_CREATE_AN_ISSUE_COMMENT,
                Action.GITHUB_LIST_REVIEW_COMMENTS_ON_A_PULL_REQUEST,
                get_diff,
            ]
        )
    )


def get_prefix_messages() -> list:
    return [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=SYSTEM,
        )
    ]


def get_agent(model: str, toolset: ComposioToolSet) -> AgentRunner:
    return FunctionCallingAgentWorker(
        llm=OpenAI(model=model),
        tools=get_tools(toolset=toolset),
        prefix_messages=get_prefix_messages(),
        max_function_calls=10,
        allow_parallel_tool_calls=False,
        verbose=True,
    ).as_agent()


def main():
    config = AgentConfig()
    toolset = ComposioToolSet(
        processors={
            "post": {
                Action.GITHUB_CREATE_AN_ISSUE_COMMENT: _github_pulls_create_review_comment_post_proc,
                Action.GITHUB_PULLS_CREATE_REVIEW_COMMENT: _github_pulls_create_review_comment_post_proc,
                Action.GITHUB_LIST_REVIEW_COMMENTS_ON_A_PULL_REQUEST: _github_list_review_comments_on_a_pull_request_post_proc,
            }
        }
    )
    agent = get_agent(model=config.model, toolset=toolset)
    pr = "https://github.com/ComposioHQ/composio/pull/643"  # input("Enter PR link :")
    agent.chat(message=(f"Review following PR {pr} and create comments on the same PR"))


if __name__ == "__main__":
    main()
