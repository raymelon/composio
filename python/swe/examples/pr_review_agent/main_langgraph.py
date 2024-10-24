from agent_lang import graph
from composio import ComposioToolSet
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

REPO_DIR = "/Users/shrey/trial_repos/composio"



pr = "https://github.com/ComposioHQ/composio/pull/709"
run_result = graph.invoke(
    {"messages": [HumanMessage(content=f"Review PR {pr} and create comments on the same PR")]},
    {"recursion_limit": 50},
)

print(run_result)
