# Dependencies 
from openai import OpenAI
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from twilio.rest import Client as TwilioClient

# Environment
load_dotenv()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI()

# MongoDB setup
mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client.get_database("MiscioP1")
chat_collection = db['chats']
users_collection = db['users']
students_collection = db['students']

# Twilio setup
twilio_client = TwilioClient(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
twilio_whatsapp_number = "whatsapp:+14155238886"  # Twilio sandbox WhatsApp number

##### MongoDB #####
def get_chathistory(thread_id):
    return chat_collection.find({"thread_id": thread_id})

def save_message(thread_id, role, message):
    chat_collection.insert_one({
        "thread_id": thread_id,
        "role": role,
        "message": message
    })

def get_contacts():
    print("Fetching contacts...")
    contacts = list(students_collection.find())
    print(f"Contacts fetched: {contacts}")
    return contacts   

##### Twilio #####
def send_message(to, body):
    print(f"Sending message to {to}...")
    try:
        message = twilio_client.messages.create(
            body=body,
            from_=twilio_whatsapp_number,
            to=f"whatsapp:{to}"
        )
        print(f"Sent message to {to}: {message.sid}")
        print(f"Twilio response: {message.status}")
    except Exception as e:
        print(f"Failed to send message to {to}: {e}")

##### OpenAI #####
def create_new_thread():
    thread = openai_client.beta.threads.create()
    return thread.id

def get_or_create_assistant():
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
                        "properties": { # Only extracting information from prompt to return as object. 
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
    return assistant

assistant = get_or_create_assistant() # Store the assistant globally

def run_campaign():
    contacts = get_contacts()
    for contact in contacts:
        send_message(contact['phone_number'], "Hello! This is a campaign message from Miscio Admin.")