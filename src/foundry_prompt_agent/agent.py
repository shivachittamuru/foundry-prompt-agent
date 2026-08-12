from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient
import os
from dotenv import load_dotenv
load_dotenv()

# Use the Azure CLI identity explicitly; DefaultAzureCredential can pick a cached
# corp account that lacks Foundry roles on this subscription.
project_client = AIProjectClient(
    endpoint=os.environ['FOUNDRY_PROJECT_ENDPOINT'],
    credential=AzureCliCredential(),
)

my_agent = os.environ['FOUNDRY_AGENT_NAME']
my_version = os.environ['FOUNDRY_AGENT_VERSION']

openai_client = project_client.get_openai_client()

# Reference the agent to get a response
response = openai_client.responses.create(
    input=[{"role": "user", "content": "Tell me what you can help with."}],
    extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
)

print(f"Response output: {response.output_text}")

## run this using following uv command:
# uv run src/foundry_prompt_agent/agent.py 