from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client.get_database("MiscioP1")
students_collection = db["students"]
campaigns_collection = db["campaigns"]
student_chats_collection = db["student_chats"]
admin_chats_collection = db["admin_chats"]
admin_users_collection = db["admin_users"]

def clear_chat_history():
    # Clear messages from admin_chats_collection
    admin_chats_collection.update_many(
        {},
        {"$set": {"messages": []}}
    )
    
    # Remove thread_id from admin_users_collection
    admin_users_collection.update_many(
        {},
        {"$unset": {"thread_id": ""}}
    )
    
    # Optionally, if you want to completely remove the admin_chats documents:
    # admin_chats_collection.delete_many({})
    
    print("Chat history cleared and thread IDs removed.")