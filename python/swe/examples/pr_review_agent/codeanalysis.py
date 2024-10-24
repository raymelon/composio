from composio import ComposioToolSet, Action, App

dir_to_index = "/Users/shrey/trial_repos/composio"

composio_toolset = ComposioToolSet(
    metadata = {
        App.CODE_ANALYSIS_TOOL: {
            "dir_to_index_path": dir_to_index
        }
    }
)

response = composio_toolset.execute_action(
    action=Action.CODE_ANALYSIS_TOOL_GET_CLASS_INFO,
    params={"class_name": "GitUserInfo"},
)

print(response['data']['result'])

