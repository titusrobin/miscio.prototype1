#app/core/config.py
from pydantic_settings import BaseSettings # auto support loading from .env 
from typing import List # type hints and type checks 

class Settings(BaseSettings):
    # API configuration
    API_V1_STR: str = "/api/v1" #base url for api 
    PROJECT_NAME: str = "Miscio Assistant"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI Assistant for School Administrators"
    
    # Security #TODO - need?, add 
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_ASSISTANT_ID: str  # Add this
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "MiscioP1"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()

# Access the settings

# Print the settings
print(f"API_V1_STR: {settings.API_V1_STR}")
print(f"PROJECT_NAME: {settings.PROJECT_NAME}")
print(f"VERSION: {settings.VERSION}")
print(f"DESCRIPTION: {settings.DESCRIPTION}")
#print(f"SECRET_KEY: {settings.SECRET_KEY}")
#print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
print(f"MONGODB_URL: {settings.MONGODB_URL}")
print(f"MONGODB_DB_NAME: {settings.MONGODB_DB_NAME}")
print(f"REDIS_URL: {settings.REDIS_URL}")
print(f"OPENAI_API_KEY: {settings.OPENAI_API_KEY}")
print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID}")
print(f"TWILIO_AUTH_TOKEN: {settings.TWILIO_AUTH_TOKEN}")
print(f"TWILIO_WHATSAPP_NUMBER: {settings.TWILIO_WHATSAPP_NUMBER}")
print(f"ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")