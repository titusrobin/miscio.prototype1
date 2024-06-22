from openai import OpenAI
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')

# OpenAI setup
openai_client = OpenAI()

# MongoDB setup
mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client.get_database("MiscioP1")
chat_collection = db['chats']
users_collection = db['users']

# Save thread - insert MongoDB
def save_message(thread_id, role, message):
    chat_collection.insert_one({
        "thread_id": thread_id,
        "role": role,
        "message": message
    })

# Get thread - retrieve from MongoDB
def get_chathistory(thread_id):
    return chat_collection.find({"thread_id": thread_id})

# Create a new thread and return its ID
def create_new_thread():
    thread = openai_client.beta.threads.create()
    return thread.id

# Create OpenAI Assistant
def get_or_create_assistant():
    assistant = openai_client.beta.assistants.create(
        name="Admin Assistant",
        instructions="You are an administrative assistant for an educational institution. Answer admin queries to the best of your ability.",
        model="gpt-4o"
    )
    return assistant

# Call the function and store the assistant globally
assistant = get_or_create_assistant()
