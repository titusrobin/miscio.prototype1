# Dependencies
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI()

# Create admin assistant and setup function calling
assistant = openai_client.beta.assistants.create(
    name="Admin Assistant",
    instructions="""
    You are an administrative assistant for Miscio, an educational institution. Your primary role is to assist administrators in running feedback campaigns and analyzing student feedback and communications. Please note that for any query about student feedback or responses, call query_student_chats. For running campaigns, call run_campaign.

    """,
    model="gpt-4-turbo",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "query_student_chats",
                "description": "Query student chat histories based on various criteria.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The query string to search for in student chats."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
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
                            "enum": ["generic", "urgent", "reminder", "event", "survey"]
                        },
                        "campaign_description": {
                            "type": "string",
                            "description": "A brief description of the campaign."
                        }
                    },
                    "required": ["campaign_type", "campaign_description"]
                }
            }
        }
    ]
)

# Save the assistant ID to use in other parts of the application
ADMIN_ASSISTANT_ID = assistant.id
#os.environ["OPENAI_ASSISTANT_ID"] = ADMIN_ASSISTANT_ID

print(f"Admin Assistant created with ID: {ADMIN_ASSISTANT_ID}")

# Optionally, you can save this ID to an environment variable or a config file
# for use in other parts of your application