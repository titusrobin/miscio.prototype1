#app/services/openai_service.py
from app.core.config import settings
from typing import Dict, Any
from .base_service import BaseAPIService
import json

class OpenAIService(BaseAPIService):
    """
    Service for interacting with OpenAI's API with proper v2 support.
    """
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "OpenAI-Beta": "assistants=v2",
            "Content-Type": "application/json"
        }
        print("\n=== Initializing OpenAI Service ===")
        print("Headers configured:", json.dumps(self.headers, indent=2))

    async def create_assistant(self, description: str, instructions: str) -> Dict[str, str]:
        """
        Creates an OpenAI assistant using v2 API with proper header handling.
        """
        print("\n=== Creating Assistant ===")
        try:
            # Prepare assistant data
            assistant_data = {
                "name": f"Student Feedback Assistant - {description}",
                "instructions": instructions,
                "model": settings.OPENAI_ASSISTANT_MODEL,
                "tools": [{"type": "code_interpreter"}, {"type": "file_search"}],
                "metadata": {
                    "type": "feedback_assistant",
                    "version": "v2",
                    "description": description
                }
            }
            print("Request data:", json.dumps(assistant_data, indent=2))

            # Create assistant
            response = await self.make_request(
                method="POST",
                url=f"{self.base_url}/assistants",
                headers=self.headers,
                data=assistant_data
            )
            print("Assistant created:", json.dumps(response, indent=2))

            # Create thread
            thread_response = await self.make_request(
                method="POST",
                url=f"{self.base_url}/threads",
                headers=self.headers
            )
            print("Thread created:", json.dumps(thread_response, indent=2))

            return {
                "assistant_id": response["id"],
                "thread_id": thread_response["id"]
            }
        except Exception as e:
            print(f"Error creating assistant: {str(e)}")
            raise

    async def process_message(
        self, 
        thread_id: str,
        message: str,
        assistant_id: str
    ) -> str:
        """
        Processes a message using the v2 Assistants API.
        """
        try:
            # Create message
            message_data = {
                "role": "user",
                "content": message
            }
            await self.make_request(
                method="POST",
                url=f"{self.base_url}/threads/{thread_id}/messages",
                headers=self.headers,
                data=message_data
            )

            # Create run
            run_data = {
                "assistant_id": assistant_id
            }
            run_response = await self.make_request(
                method="POST",
                url=f"{self.base_url}/threads/{thread_id}/runs",
                headers=self.headers,
                data=run_data
            )

            # Monitor run status
            while True:
                status_response = await self.make_request(
                    method="GET",
                    url=f"{self.base_url}/threads/{thread_id}/runs/{run_response['id']}",
                    headers=self.headers
                )

                if status_response["status"] == "completed":
                    messages_response = await self.make_request(
                        method="GET",
                        url=f"{self.base_url}/threads/{thread_id}/messages",
                        headers=self.headers,
                        params={"limit": 1, "order": "desc"}
                    )
                    return messages_response["data"][0]["content"][0]["text"]["value"]

                elif status_response["status"] in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Run failed with status: {status_response['status']}")

                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            raise

    async def __aenter__(self):
        """Support for async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensure proper cleanup of resources."""
        await self.close()