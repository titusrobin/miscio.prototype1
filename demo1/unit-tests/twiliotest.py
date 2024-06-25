from pymongo import MongoClient
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# MongoDB setup
mongo_uri = os.getenv('MONGO_URI')
mongo_client = MongoClient(mongo_uri)
db = mongo_client.get_database("MiscioP1")
contacts_collection = db['students']  # Ensure this matches your collection name

# Twilio setup
twilio_client = TwilioClient(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
twilio_whatsapp_number = "whatsapp:+14155238886"  # Twilio sandbox WhatsApp number

def get_contacts():
    return list(contacts_collection.find())

def send_message(to, body):
    message = twilio_client.messages.create(
        body=body,
        from_=twilio_whatsapp_number,
        to=f"whatsapp:{to}"
    )
    print(f"Sent message to {to}: {message.sid}")

def run_campaign():
    contacts = get_contacts()
    for contact in contacts:
        send_message(contact['phone_number'], "Hello! This is a campaign message from Miscio Admin.")

if __name__ == "__main__":
    run_campaign()
