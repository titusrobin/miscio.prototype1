from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
mongo_uri = os.getenv('MONGODB_URI')

# Print to verify the MONGO_URI
print(f"Loaded MONGO_URI: {mongo_uri}")

# Set up MongoDB client
mongo_client = MongoClient(mongo_uri)

def test_mongo_connection():
    try:
        # Ping the server
        mongo_client.admin.command('ping')
        print("MongoDB Atlas connection successful!")
    except Exception as e:
        print(f"Error connecting to MongoDB Atlas: {e}")

if __name__ == "__main__":
    test_mongo_connection()
