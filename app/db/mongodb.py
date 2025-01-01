#app/db/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient as m
from app.core.config import settings

class MongoDB: #To manage the connection to the MongoDB database
    client: m = None
    db = None

    async def connect_to_database(self): #db config 
        self.client = m(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DB_NAME]
        
    async def close_database_connection(self):
        if self.client:
            self.client.close()

db = MongoDB()