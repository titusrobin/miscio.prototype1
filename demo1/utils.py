import os
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from twilio.rest import Client as TwilioClient
from openai import OpenAI

load_dotenv()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI()

misio_logo = '/Users/robintitus/Desktop/Miscio/prototype1/demo1/imgs/m3logo.jpg'
chat_logo = '/Users/robintitus/Desktop/Miscio/prototype1/demo1/imgs/misciologo.jpg'
icon = '/Users/robintitus/Desktop/Miscio/prototype1/demo1/imgs/a.jpg'
assistant_avatar='/Users/robintitus/Desktop/Miscio/prototype1/demo1/imgs/miscio_agent.jpg'
user_avatar = '/Users/robintitus/Desktop/Miscio/prototype1/demo1/imgs/user_icon.jpg'

mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client.get_database("MiscioP1")
chat_collection = db['chats']
users_collection = db['users']
students_collection = db['students']
campaigns_collection = db['campaigns']

twilio_client = TwilioClient(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
twilio_whatsapp_number = "whatsapp:+14155238886"

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
        twilio_client.messages.create(
            body=body,
            from_=twilio_whatsapp_number,
            to=f"whatsapp:{to}"
        )
    except Exception as e:
        print(f"Failed to send message to {to}: {e}")

def send_student_message(to, body):
    try:
        twilio_client.messages.create(
            body=body,
            from_=twilio_whatsapp_number,
            to=to
        )
        print(f"Successfully sent message to {to}")
    except Exception as e:
        print(f"Failed to send message to {to}: {str(e)}")

def create_student_assistant(campaign_description):
    assistant = openai_client.beta.assistants.create(
        name=f"Student Assistant - {campaign_description}",
        instructions=f"You are a student assistant for the '{campaign_description}' campaign. Answer student queries related to this campaign to the best of your ability. Keep your responses concise and friendly.",
        model="gpt-4-turbo"
    )
    return assistant.id

def run_campaign(campaign_description):
    assistant_id = create_student_assistant(campaign_description)
    contacts = get_contacts()
    threads = []
    for contact in contacts:
        thread = openai_client.beta.threads.create()
        threads.append({"student_id": contact['_id'], "thread_id": thread.id})
        send_initial_message(contact, campaign_description, thread.id, assistant_id)
    campaign_id = campaigns_collection.insert_one({
        "campaign_description": campaign_description,
        "student_assistant_id": assistant_id,
        "status": "active",
        "threads": threads
    }).inserted_id
    return campaign_id

def send_initial_message(contact, campaign_description, thread_id, assistant_id):
    message = f"Hello {contact['first_name']}! This is a message from Miscio regarding the '{campaign_description}' campaign. You can now interact with our Student Assistant for any questions about this campaign."
    send_message(contact['phone_number'], message)
    students_collection.update_one(
        {"_id": contact['_id']},
        {"$push": {
            "active_campaigns": {
                "campaign_description": campaign_description,
                "thread_id": thread_id,
                "student_assistant_id": assistant_id
            }
        }}
    )

def authenticate_user(username, password):
    return username == "admin" and password == "admin123//"

def get_openai_response(message):
    if "thread_id" not in st.session_state or not st.session_state.thread_id:
        thread = openai_client.beta.threads.create()
        st.session_state.thread_id = thread.id
        users_collection.update_one(
            {"username": st.session_state.username},
            {"$set": {"thread_id": st.session_state.thread_id}}
        )

    openai_client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, role="user", content=message
    )
    save_message(st.session_state.thread_id, "user", message)
    run = openai_client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=os.getenv('OPENAI_ASSISTANT_ID'),
        instructions=f"Please address the user as Miscio Admin. They are the admin to whom you are the assistant at Miscio. The user asked: {message}"
    ) 
    run = openai_client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)
    
    while run.status != "completed":
        run = openai_client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run.id)
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool in tool_calls:
                if tool.function.name == "run_campaign":
                    campaign_description = message
                    assistant_id = run_campaign(campaign_description)
                    tool_outputs.append({"tool_call_id": tool.id, "output": f"Campaign run successfully with assistant ID: {assistant_id}"})
            openai_client.beta.threads.runs.submit_tool_outputs(
                thread_id=st.session_state.thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

    messages = openai_client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    for msg in messages.data:
        if msg.role == "assistant":
            content = msg.content[0].text.value
            save_message(st.session_state.thread_id, "assistant", content)
            return content

    return "I'm sorry, I couldn't process your request at this time."



