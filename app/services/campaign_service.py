#app/services/campaign_service.py
from typing import Optional, Dict, List
from datetime import datetime
from app.db.mongodb import db
from app.models.campaign import Campaign
from app.services.openai_service import OpenAIService
from app.services.twilio_service import TwilioService
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorDatabase

class CampaignService:
    def __init__(
        self,
        openai_service: OpenAIService,
        twilio_service: TwilioService,
        database: AsyncIOMotorDatabase
    ):
        self.openai_service = openai_service
        self.twilio_service = twilio_service
        self.db = database

    async def create_campaign(self, campaign: Campaign, admin_id: str) -> Dict:
        """
        Creates a new campaign and sets up all necessary components.
        This method handles the complete campaign creation workflow.
        """
        # First, deactivate any currently active campaigns
        await self.db.campaigns.update_many(
            {"status": "active"},
            {"$set": {"status": "inactive"}}
        )

        # Create an AI assistant for this campaign
        assistant_id = await self.openai_service.create_assistant(
            campaign.description,
            self._generate_assistant_instructions(campaign)
        )

        # Prepare campaign data
        campaign_data = {
            "description": campaign.description,
            "assistant_id": assistant_id,
            "admin_id": admin_id,
            "status": "active",
            "created_at": datetime.utcnow(),
            "settings": campaign.settings,
            "target_completion_date": campaign.target_completion_date
        }

        # Insert the campaign into database
        result = await self.db.campaigns.insert_one(campaign_data)
        campaign_data["id"] = str(result.inserted_id)

        # Start the campaign by sending initial messages
        await self._initiate_campaign_messages(campaign_data)

        return campaign_data

    async def get_active_campaign(self) -> Optional[Dict]:
        """
        Retrieves the currently active campaign with its statistics.
        """
        campaign = await self.db.campaigns.find_one({"status": "active"})
        if campaign:
            campaign["id"] = str(campaign["_id"])
            campaign["stats"] = await self.get_campaign_stats(campaign["id"])
        return campaign

    async def get_campaign_stats(self, campaign_id: str) -> Dict:
        """
        Generates comprehensive statistics for a campaign.
        """
        # Get all messages for this campaign
        messages = self.db.messages.find({
            "campaign_id": campaign_id
        })

        # Initialize statistics
        stats = {
            "total_students": 0,
            "responded_students": 0,
            "total_messages": 0,
            "average_response_time": 0,
            "sentiment_analysis": {},
            "common_themes": [],
            "completion_rate": 0
        }

        # Process messages to generate statistics
        async for message in messages:
            # Update message counts
            stats["total_messages"] += 1

            # Track unique students
            if message["student_id"] not in stats["student_ids"]:
                stats["total_students"] += 1

        # Calculate completion rate
        total_students = await self.db.students.count_documents({})
        stats["completion_rate"] = (stats["responded_students"] / total_students) * 100

        return stats

    def _generate_assistant_instructions(self, campaign: Campaign) -> str:
        """
        Generates customized instructions for the OpenAI assistant based on campaign type.
        """
        base_instructions = """
        You are an AI assistant helping to gather student feedback. Your role is to:
        1. Maintain a friendly and professional tone
        2. Ask relevant follow-up questions
        3. Show empathy and understanding
        4. Keep responses concise and clear
        5. Flag any urgent concerns for administrator attention
        """
        
        # Add campaign-specific instructions
        campaign_instructions = f"""
        Campaign Focus: {campaign.description}
        Key Areas to Explore:
        - Student satisfaction
        - Areas for improvement
        - Specific feedback on {campaign.focus_areas}
        """

        return base_instructions + campaign_instructions

    async def _initiate_campaign_messages(self, campaign_data: Dict):
        """
        Initiates the campaign by sending initial messages to all relevant students.
        """
        # Get all active students
        students = self.db.students.find({"status": "active"})
        
        async for student in students:
            try:
                # Generate personalized initial message
                initial_message = await self.openai_service.generate_initial_message(
                    student["first_name"],
                    campaign_data["description"]
                )

                # Send message via Twilio
                await self.twilio_service.send_message(
                    student["phone"],
                    initial_message
                )

                # Record message in database
                await self.db.messages.insert_one({
                    "campaign_id": campaign_data["id"],
                    "student_id": str(student["_id"]),
                    "message": initial_message,
                    "type": "initial",
                    "status": "sent",
                    "timestamp": datetime.utcnow()
                })

            except Exception as e:
                # Log the error but continue with other students
                print(f"Failed to send initial message to student {student['_id']}: {str(e)}")
                continue