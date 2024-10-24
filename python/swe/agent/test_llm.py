from langchain_openai import ChatOpenAI
import os
import time
from botocore.exceptions import ClientError

max_retries = 5
base_delay = 1  # in seconds

client = ChatOpenAI(
    model="o1-mini",
    temperature=1,
    # max_completion_tokens=4096, 
    api_key=openai_api_key,
)

def retry_with_exponential_backoff(func, *args, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except ClientError as e:
            if attempt == max_retries - 1:
                raise
            delay = (2 ** attempt) * base_delay
            time.sleep(delay)

prompt = open("prompt.txt", "r").read()


response = retry_with_exponential_backoff(
    client.invoke,
    [
        ("human", prompt)
    ]
)
print(response.content)