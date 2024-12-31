#backend/app/services/openai_service.py
from openai import AsyncOpenAI
from app.core.config import settings
from typing import Optional
import asyncio

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    #creates student/campaign assistant? what about admin assistant - TODO
    async def create_assistant(self, description: str, instructions: str) -> str:
        """Creates an OpenAI assistant for a campaign."""
        try:
            assistant = await self.client.beta.assistants.create(
                name=f"Student Assistant - {description}",
                instructions=instructions, 
                model="gpt-4-turbo"
            )
            return assistant.id
        except Exception as e:
            # Log the error
            raise Exception(f"Failed to create OpenAI assistant: {str(e)}")

    async def process_message(self, thread_id: str, message: str, assistant_id: str):
        """Processes a message using the OpenAI assistant."""
        try:
            # Create message
            await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            
            # Create run
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            
            # Wait for completion
            while True:
                run_status = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                await asyncio.sleep(1)
            
            # Get response
            messages = await self.client.beta.threads.messages.list(
                thread_id=thread_id
            )
            return next(
                msg.content[0].text.value 
                for msg in messages.data 
                if msg.role == "assistant"
            )
        except Exception as e:
            # Log the error
            raise Exception(f"Failed to process message: {str(e)}")

