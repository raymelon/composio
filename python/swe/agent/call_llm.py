from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
import os
import time
from botocore.exceptions import ClientError

max_retries = 5
base_delay = 1  # in seconds

MODEL = "claude"

def retry_with_exponential_backoff(func, *args, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            if attempt == max_retries - 1:
                raise
            delay = (2 ** attempt) * base_delay
            time.sleep(delay)

system_prompt = "You are a helpful assistant."
human_prompt = "Write a story about a cat."

# client = ChatOpenAI(
#     model="o1-preview",
#     temperature=1,
#     max_completion_tokens=4096, 
#     api_key=openai_api_key,
# )

inference_profile_id = "arn:aws:bedrock:us-west-2:008971668139:inference-profile/us.meta.llama3-2-90b-instruct-v1:0"
model_id = "us.meta.llama3-2-90b-instruct-v1:0"
model_id = "meta.llama3-2-90b-instruct-v1:0"
# client = ChatBedrock(
#     credentials_profile_name="default",
#     model_id=inference_profile_id,
#     # model_provider="meta",
#     # modelId=inference_profile_id,
#     # region_name="us-east-1",
#     model_kwargs={"temperature": 0},
#     provider="meta",
# )

client = ChatBedrock(
    credentials_profile_name="default",
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name="us-west-2",
    model_kwargs={"temperature": 0, "max_tokens": 8192},
)


response = retry_with_exponential_backoff(
    client.invoke,
    [
        ("system", system_prompt),
        ("human", human_prompt)
    ]
)

print(response.content)


# from openai import OpenAI
# import os

# system_prompt = "You are a helpful assistant."
# human_prompt = "What is the capital of France?"


# client = OpenAI(
#   api_key=openai_api_key
# )

# completion = client.chat.completions.create(
#   model="o1-mini",
#   messages=[
#     {"role": "user", "content": human_prompt}
#   ]
# )

# print(completion.choices[0].message.content)


