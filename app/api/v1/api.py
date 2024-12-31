#app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import campaign, webhook

router = APIRouter()
router.include_router(campaign.router, prefix="/campaigns", tags=["campaigns"])
router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])