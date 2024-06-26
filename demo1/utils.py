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
    contacts = list(students_collection.find())
    return contacts

def send_message(to, body):
    try:
        message = twilio_client.messages.create(
            body=body,
            from_=twilio_whatsapp_number,
            to=f"whatsapp:{to}"
        )
    except Exception as e:
        print(f"Failed to send message to {to}: {e}")

def run_campaign():
    contacts = get_contacts()
    for contact in contacts:
        send_message(contact['phone_number'], "Hello! This is a campaign message from Miscio Admin.")
