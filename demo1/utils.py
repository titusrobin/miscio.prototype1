from pymongo import MongoClient
import os
from dotenv import load_dotenv
from openai import OpenAI
from twilio.rest import Client as TwilioClient

load_dotenv()

# MongoDB setup
mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client.get_database("MiscioP1")
chat_collection = db['chats']
users_collection = db['users']
students_collection = db['students']
campaigns_collection = db['campaigns']

# OpenAI setup
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Twilio setup
twilio_client = TwilioClient(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
twilio_whatsapp_number = "whatsapp:+14155238886"  # Twilio sandbox WhatsApp number

def create_new_thread():
    thread = openai_client.beta.threads.create()
    return thread.id

def get_chathistory(thread_id):
    return chat_collection.find({"thread_id": thread_id})

def save_message(thread_id, role, message):
    chat_collection.insert_one({
        "thread_id": thread_id,
        "role": role,
        "message": message
    })

def get_contacts():
    return list(students_collection.find())

def send_message(to, body):
    try:
        message = twilio_client.messages.create(
            body=body,
            from_=twilio_whatsapp_number,
            to=f"whatsapp:{to}"
        )
        print(f"Message sent to {to}: {message.sid}")
    except Exception as e:
        print(f"Failed to send message to {to}: {e}")

def create_campaign_assistant(campaign_description):
    assistant = openai_client.beta.assistants.create(
        name=f"Campaign Assistant - {campaign_description[:30]}",
        instructions=f"You are an AI assistant for the campaign: {campaign_description}. Engage with students and provide information related to this campaign.",
        model="gpt-4-turbo"
    )
    return assistant.id

def run_campaign(campaign_description):
    assistant_id = create_campaign_assistant(campaign_description)
    contacts = get_contacts()
    for contact in contacts:
        send_message(contact['phone_number'], f"Hello {contact['first_name']}! This is a message from our new campaign: {campaign_description[:100]}... Reply to interact with our AI assistant.")
    
    campaign_id = campaigns_collection.insert_one({
        "campaign_description": campaign_description, 
        "assistant_id": assistant_id
    }).inserted_id
    return str(campaign_id)

def get_or_create_thread(identifier, identifier_type='username'):
    if identifier_type == 'username':
        collection = users_collection
        query = {"username": identifier}
    elif identifier_type == 'phone_number':
        collection = students_collection
        query = {"phone_number": identifier}
    else:
        raise ValueError("Invalid identifier_type. Must be 'username' or 'phone_number'.")

    user = collection.find_one(query)
    
    if not user or "thread_id" not in user:
        thread = openai_client.beta.threads.create()
        thread_id = thread.id
        collection.update_one(
            query,
            {"$set": {"thread_id": thread_id}},
            upsert=True
        )
    else:
        thread_id = user["thread_id"]
    
    return thread_id
    
