#backend/app/api/v1/endpoints/campaign.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.services.campaign_service import CampaignService
from app.core.security import get_current_admin_user
from app.models.campaign import Campaign
from app.services.openai_service import OpenAIService
from app.services.twilio_service import TwilioService

router = APIRouter() #define a set of routes to be included in main app 


@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    current_admin=Depends(get_current_admin_user)
):
    try:
        openai_service = OpenAIService()
        twilio_service = TwilioService()
        campaign_service = CampaignService(openai_service, twilio_service, db.db)
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
    campaign_service: CampaignService = Depends(),
    current_admin=Depends(get_current_admin_user),
):
    """
    Retrieves the currently active campaign.
    Only one campaign can be active at a time.
    """
    campaign = await campaign_service.get_active_campaign()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No active campaign found"
        )
    return campaign


@router.get("/{campaign_id}/stats") #TODO clarify 
async def get_campaign_stats(
    campaign_id: str,
    campaign_service: CampaignService = Depends(),
    current_admin=Depends(get_current_admin_user),
):
    """
    Retrieves detailed statistics for a specific campaign, including:
    - Total number of students reached
    - Response rate
    - Average sentiment
    - Common themes in feedback
    """
    try:
        return await campaign_service.get_campaign_stats(campaign_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve campaign stats: {str(e)}",
        )
