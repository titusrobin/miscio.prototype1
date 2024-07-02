# Dependencies
import os, streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from twilio.rest import Client as TwilioClient
from openai import OpenAI

# Environment setup
load_dotenv()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI()

# Front end: Images
misio_logo = '/Users/robintitus/Desktop/Miscio/prototype1/demo1/imgs/62698cdbd01e66c6b10f6447_Miscio Logos-02.png'

# MongoDB setup
mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client.get_database("MiscioP1")
chat_collection = db['chats']
users_collection = db['users']
students_collection = db['students']
campaigns_collection = db['campaigns']

# Twilio setup
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

def create_student_assistant(campaign_description):
    assistant = openai_client.beta.assistants.create(
        name="Student Assistant",
        instructions=f"You are a student assistant for the '{campaign_description}' campaign. Answer student queries to the best of your ability.",
        model="gpt-4-turbo"
    )
    return assistant.id

def run_campaign(campaign_description):
    assistant_id = create_student_assistant(campaign_description)
    contacts = get_contacts()
    for contact in contacts:
        send_message(contact['phone_number'], f"Hello {contact['first_name']}! This is a campaign message from Miscio Student Assistant.")
    campaigns_collection.insert_one({"campaign_description": campaign_description, "assistant_id": assistant_id})
    return assistant_id

def authenticate_user(username, password):
    return username == "admin" and password == "password"

def get_openai_response(message):
    if "thread_id" not in st.session_state or not st.session_state.thread_id:
        thread = openai_client.beta.threads.create()
        st.session_state.thread_id = thread.id
        users_collection.update_one(
            {"username": st.session_state.username},
            {"$set": {"thread_id": st.session_state.thread_id}}
        )

    active_run = None
    runs = openai_client.beta.threads.runs.list(thread_id=st.session_state.thread_id)
    for run in runs.data:
        if run.status in ["pending", "requires_action"]:
            active_run = run
            break

    if not active_run:
        openai_client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=message
        )
        save_message(st.session_state.thread_id, "user", message)
        run = openai_client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=os.getenv('OPENAI_ASSISTANT_ID'),
            instructions=f"Please address the user as Miscio Admin. They are the admin to whom you are the assistant at Miscio. The user asked: {message}"
        )
        run = openai_client.beta.threads.runs.poll(thread_id=st.session_state.thread_id, run_id=run.id)
    else:
        run = active_run

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
        run = openai_client.beta.threads.runs.poll(thread_id=st.session_state.thread_id, run_id=run.id)

    if run.status == "completed":
        messages = openai_client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in messages.data:
            if msg.role == "assistant":
                content = msg.content[0].text.value
                save_message(st.session_state.thread_id, "assistant", content)
                return content

    return "I'm sorry, I couldn't process your request at this time."
