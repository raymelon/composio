import babyagi
from dotenv import load_dotenv
from composio_babyagi.toolset import ComposioToolSet, Action

load_dotenv()

# Initialize the toolset
toolset = ComposioToolSet()

# Get and automatically register tools with babyagi
tools = toolset.get_tools(
    actions=[],
)

# Create and run the babyagi app
app = babyagi.create_app('/dashboard')

# Example of executing an action
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
