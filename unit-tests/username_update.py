import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

# Fetch MongoDB Atlas connection string from environment variable
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise EnvironmentError("MONGO_URI environment variable is not set")

try:
    # MongoDB Atlas connection
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client.get_database("MiscioP1")
    admin_users_collection = db["admin_users"]

    def update_admin_username(document_id):
        try:
            result = admin_users_collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {"username": {"$regex": "^admin$", "$options": "i"}}}
            )
            if result.modified_count > 0:
                print(f"Username updated successfully for document {document_id}")
                return True
            elif result.matched_count > 0:
                print(f"Document found but no changes were necessary for {document_id}")
                return True
            else:
                print(f"No document found with id {document_id}")
                return False
        except Exception as e:
            print(f"An error occurred while updating the username: {e}")
            return False

    # Usage
    document_id = "66761166d51dd3ef4d1a9041"  # Replace with your actual document ID
    success = update_admin_username(document_id)

    if success:
        print("Username field updated or already set correctly.")
    else:
        print("Failed to update username field. Check the console for more details.")

except Exception as e:
    print(f"Failed to connect to MongoDB Atlas: {e}")

finally:
    if 'mongo_client' in locals():
        mongo_client.close()