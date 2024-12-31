#app/schemas/campaign.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CampaignBase(BaseModel):
    description: str

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(CampaignBase):
    status: Optional[str]

class CampaignResponse(CampaignBase):
    id: str
    assistant_id: str
    status: str
    created_at: datetime
    admin_id: str

    class Config:
        from_attributes = True