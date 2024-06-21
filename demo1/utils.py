# Dependencies 
from openai import OpenAI
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# OpenAI setup
load_dotenv()
OpenAI.api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI()

# MongoDB setup
mongo_client = MongoClient(os.getenv('MONGO_URI'))
db = mongo_client.get_database("MiscioP1")
chat_collection = db['chats']

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

### Create OpenAI Assistant !!!!!!!! THIS IS CREATING ASSISTANTS EVERYTIME  
def get_or_create_assistant():
    # Ideally, store and retrieve the assistant ID from a database or cache.
    assistant = openai_client.beta.assistants.create(
        name="Admin Assistant",
        ### Instructions can take up to 250K chars as input 
        instructions="You are an adminstrative assistant for an educational institution. Answer admin queries to the best of your ability.",
        model="gpt-4o"
    )
    return assistant

# Call the function and store the assistant globally
assistant = get_or_create_assistant()
