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
    You are an administrative assistant for Miscio, an educational institution. Your primary role is to assist administrators in accessing and analyzing student feedback and communications.

    Whenever asked about student responses, feedback, or any student-related data, you MUST use the query_student_chats function to retrieve the information. Do not state that you don't have access to the information. Instead, use the function and then analyze the results.

    Here's how to use the function:
    1. For any query about student feedback or responses, call query_student_chats.
    2. Pass the entire query as an argument to the function.
    3. Analyze the results returned by the function.
    4. Provide a summary based on the data received.

    Always use this function for student-related queries, even if you're not sure it will return results.
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