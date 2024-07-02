from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI()

# Create the assistant
assistant = openai_client.beta.assistants.create(
    name="Admin Assistant",
    instructions="You are an administrative assistant for an educational institution. Answer admin queries to the best of your ability.",
    model="gpt-4-turbo",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "run_campaign",
                "description": "Run a campaign to send messages to students.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_type": {
                            "type": "string",
                            "description": "The type of campaign to run.",
                            "enum": ["generic"]
                        }
                    },
                    "required": ["campaign_type"]
                }
            }
        }
    ]
)

# Print the assistant ID
print("Assistant ID:", assistant.id)
