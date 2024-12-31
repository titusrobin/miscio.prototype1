from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.services.campaign_service import CampaignService
from app.core.security import get_current_admin_user
from app.models.campaign import Campaign
from app.services.openai_service import OpenAIService
from app.services.twilio_service import TwilioService
from app.db.mongodb import db

# Define APIRouter for campaign-related endpoints
router = APIRouter()

def get_campaign_service() -> CampaignService:
    """
    Creates and returns a configured CampaignService instance.
    This dependency injection function ensures proper initialization
    of required services.
    """
    openai_service = OpenAIService()
    twilio_service = TwilioService()
    return CampaignService(openai_service, twilio_service, db.db)

@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    campaign_service: CampaignService = Depends(get_campaign_service),
    current_admin=Depends(get_current_admin_user)
):
    """
    Creates a new campaign with the provided configuration.
    Only authenticated admin users can create campaigns.
    """
    try:
        return await campaign_service.create_campaign(
            campaign=campaign, 
            admin_id=current_admin.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/active", response_model=CampaignResponse)
async def get_active_campaign(
    campaign_service: CampaignService = Depends(get_campaign_service),
    current_admin=Depends(get_current_admin_user)
):
    """
    Retrieves the currently active campaign.
    Only one campaign can be active at a time.
    Requires admin authentication.
    """
    try:
        campaign = await campaign_service.get_active_campaign()
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active campaign found"
            )
        return campaign
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: str,
    campaign_service: CampaignService = Depends(get_campaign_service),
    current_admin=Depends(get_current_admin_user)
):
    """
    Retrieves detailed statistics for a specific campaign, including:
    - Total number of students reached
    - Response rate
    - Average sentiment
    - Common themes in feedback
    
    Requires admin authentication and valid campaign ID.
    """
    try:
        return await campaign_service.get_campaign_stats(campaign_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaign stats: {str(e)}"
        )