# app/services/campaign_service.py
# app/services/campaign_service.py
from typing import Optional, Dict, List, TypeVar
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from fastapi import HTTPException, status
from app.models.campaign import Campaign
from app.services.openai_service import OpenAIService
from app.services.twilio_service import TwilioService

DBType = TypeVar('DBType', bound=AsyncIOMotorDatabase)

class CampaignService:
    def __init__(
        self,
        openai_service: OpenAIService,
        twilio_service: TwilioService,
        database: DBType
    ):
        self.openai_service = openai_service
        self.twilio_service = twilio_service
        self.db = database

    def _generate_assistant_instructions(self, campaign: Campaign) -> str:
        # Existing instruction generation code remains the same
        pass

    async def create_campaign(self, campaign: Campaign, admin_id: str) -> Dict:
        """
        Creates a new campaign with proper transaction handling and error management.
        """
        print("\n=== Creating Campaign in Service ===")
        
        # Start a MongoDB session for transaction management
        async with await self.db.client.start_session() as session:
            async with session.start_transaction():
                try:
                    # Deactivate existing campaigns within the transaction
                    print("Deactivating existing active campaigns...")
                    await self.db.campaigns.update_many(
                        {"status": "active"},
                        {"$set": {"status": "inactive"}},
                        session=session
                    )

                    # Create OpenAI assistant
                    print("\nCreating OpenAI assistant...")
                    try:
                        assistant_data = await self.openai_service.create_assistant(
                            campaign.description,
                            self._generate_assistant_instructions(campaign)
                        )
                    except Exception as openai_error:
                        print(f"\n❌ OpenAI Error: {str(openai_error)}")
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"OpenAI service error: {str(openai_error)}"
                        )

                    # Prepare campaign data
                    print("\nPreparing campaign data...")
                    campaign_data = {
                        "description": campaign.description,
                        "assistant_id": assistant_data["assistant_id"],
                        "thread_id": assistant_data["thread_id"],
                        "admin_id": admin_id,
                        "status": "active",
                        "created_at": datetime.utcnow()
                    }

                    # Insert campaign within transaction
                    print("\nInserting campaign into database...")
                    result = await self.db.campaigns.insert_one(
                        campaign_data,
                        session=session
                    )
                    campaign_data["id"] = str(result.inserted_id)
                    
                    # Initiate campaign messages within the same transaction
                    print("\nInitiating campaign messages...")
                    await self._initiate_campaign_messages(campaign_data, session)
                    
                    # Transaction will automatically commit if we reach this point
                    return campaign_data

                except Exception as e:
                    # Transaction will automatically abort on exception
                    print(f"\n❌ Error during campaign creation: {str(e)}")
                    
                    # Clean up OpenAI assistant if it was created
                    if 'assistant_data' in locals():
                        try:
                            await self.openai_service.delete_assistant(
                                assistant_data["assistant_id"]
                            )
                        except Exception as cleanup_error:
                            print(f"Failed to clean up OpenAI assistant: {cleanup_error}")
                    
                    # Re-raise appropriate exception
                    if isinstance(e, HTTPException):
                        raise
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to create campaign: {str(e)}"
                    )

    async def _initiate_campaign_messages(self, campaign_data: Dict, session) -> None:
        """
        Initiates campaign messages within a transaction session.
        """
        try:
            # Find active students within the transaction
            cursor = self.db.students.find(
                {"status": "active"},
                session=session
            )
            
            async for student in cursor:
                try:
                    # Generate initial message
                    initial_message = await self.openai_service.generate_initial_message(
                        student["first_name"],
                        campaign_data["description"]
                    )
                    
                    # Send message via Twilio
                    await self.twilio_service.send_message(
                        student["phone"],
                        initial_message
                    )
                    
                    # Record message in database within transaction
                    await self.db.messages.insert_one({
                        "campaign_id": campaign_data["id"],
                        "student_id": str(student["_id"]),
                        "message": initial_message,
                        "type": "initial",
                        "status": "sent",
                        "timestamp": datetime.utcnow()
                    }, session=session)
                    
                except Exception as student_error:
                    print(f"Failed to process student {student['_id']}: {str(student_error)}")
                    # Log error but continue with other students
                    continue

        except Exception as e:
            print(f"Failed to initiate campaign messages: {str(e)}")
            raise