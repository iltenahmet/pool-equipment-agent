from openai import OpenAI
from dotenv import load_dotenv
from os import getenv

load_dotenv()
llm_client = OpenAI()

prompt = {
    "role": "system",
    "content": "You are an helpful assistant to help with pool stuff",
}

def query_agent(user_message: str) -> str:
    messages = [
        prompt,
        {"role": "user", "content": user_message},
    ]

    completion = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    return completion.choices[0].message.content