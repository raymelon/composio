import os
from dotenv import load_dotenv
from composio_llamaindex import ComposioToolSet, App
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.llms import ChatMessage

load_dotenv()

# Retrieve the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OpenAI API key not found. Please set OPENAI_API_KEY in your environment or .env file."
    )

# Initialize Composio ToolSet and OpenAI model
composio_toolset = ComposioToolSet(entity_id="sam-openai")
tools = composio_toolset.get_tools(apps=[App.GOOGLESHEETS, App.FIRECRAWL])

# Use the appropriate OpenAI model
llm = OpenAI(model="gpt-4o", api_key=api_key)

# Set up prefix messages for the agent
prefix_messages = [
    ChatMessage(
        role="system",
        content=(
            "You are an AI assistant tasked with extracting quantitative metrics from company websites for data visualization. "
            "You will access a Google Sheet containing company names and their websites. "
            "For each company, use the FIRECRAWL tool to scrape their website and gather the following metrics:\n"
            "- **Number of Employees**\n"
            "- **Year Founded**\n"
            "- **Number of Offices or Locations**\n"
            "- **Number of Services or Products Offered**\n"
            "- **Annual Revenue (if available)**\n"
            "- **Industry Sector**\n"
            "Provide the extracted data in a structured format, such as a JSON object or a table. "
            "If any data is unavailable, indicate it as 'Not Available'."
        ),
    )
]

# Initialize the agent worker
agent = FunctionCallingAgentWorker(
    tools=tools,
    llm=llm,
    prefix_messages=prefix_messages,
    max_function_calls=50,
    allow_parallel_tool_calls=False,
    verbose=True,
).as_agent()

# User input to initiate the process
user_input = (
    "Please read the Google Sheet with ID '1Fmkb3bYotVBvBbDBu_nMYy2qY28qf-rWu58F38K6Hns', "
    "which contains a list of companies and their websites. "
    "For each company, extract the specified quantitative metrics for data visualization."
)

# Run the agent
response = agent.chat(user_input)

# Output the results
print("Extraction completed. Results:")
print(response.response)
