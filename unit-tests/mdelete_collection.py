from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client.get_database("MiscioP1")
db["admin_chats"].delete_many({})
print("All documents in admin_chats have been deleted.")