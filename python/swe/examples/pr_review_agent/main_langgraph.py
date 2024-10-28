from distutils.core import extension_keywords
from agent_lang import get_graph
from composio import ComposioToolSet, Action
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from agent.tools import get_pr_metadata



pr = "https://github.com/ComposioHQ/composio/pull/766"
repo_path = "/Users/shrey/trial_repos/composio"

graph, toolset = get_graph(repo_path)

toolset.execute_action(
    action=Action.FILETOOL_CHANGE_WORKING_DIRECTORY,
    params={"path": repo_path}
)

response = toolset.execute_action(
    action=get_pr_metadata,
    params={
        "owner": "ComposioHQ",
        "repo": "composio",
        "pull_number": "766",
        "thought": "Get the metadata for the PR"
    }
)
base_commit = response["data"]["metadata"]["base"]["sha"]

toolset.execute_action(
    action=Action.FILETOOL_GIT_CLONE,
    params={
        "repo_name": "composiohq/composio",
        "just_reset": True,
        "commit_id": base_commit
    }
)


run_result = graph.invoke(
    {"messages": [HumanMessage(content=f"Review PR {pr} and create comments on the same PR")]},
    {"recursion_limit": 50},
)

print(run_result)
