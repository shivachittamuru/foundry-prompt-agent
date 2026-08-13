import os

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()


project_client = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=AzureCliCredential(),
)

openai_client = project_client.get_openai_client()

AGENT_NAME = os.environ["FOUNDRY_AGENT_NAME"]
AGENT_VERSION = os.environ["FOUNDRY_AGENT_VERSION"]


def ask_agent(query: str) -> str:
    response = openai_client.responses.create(
        input=[
            {
                "role": "user",
                "content": query,
            }
        ],
        extra_body={
            "agent_reference": {
                "name": AGENT_NAME,
                "version": AGENT_VERSION,
                "type": "agent_reference",
            }
        },
    )

    return response.output_text


if __name__ == "__main__":
    answer = ask_agent("Tell me what you can help with.")
    print(answer)

## run this using following uv command:
# uv run src/foundry_prompt_agent/agent.py 