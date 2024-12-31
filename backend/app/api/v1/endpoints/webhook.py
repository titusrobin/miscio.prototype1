#backend/app/api/v1/endpoints/webhook.py
from fastapi import APIRouter, HTTPException, Depends # route end points, dependency injection
from app.services.openai_service import OpenAIService
from app.services.twilio_service import TwilioService
from app.db.mongodb import db

router = APIRouter() #instance of APIRouter for endpoints 

@router.post("/webhook") #Defines a POST endpoint at the path
async def handle_webhook(
    request: dict,
    openai_service: OpenAIService = Depends(),
    twilio_service: TwilioService = Depends()
):
    try:
        # Extract message details
        incoming_msg = request.get("Body", "").lower()
        sender = request.get("From")
        
        # Find student
        student = await db.db.students.find_one({
            "phone": sender.replace("whatsapp:", "")
        })
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get active campaign
        campaign = await db.db.campaigns.find_one({"status": "active"})
        if not campaign:
            raise HTTPException(status_code=404, detail="No active campaign")
        
        # Process message
        response = await openai_service.process_message(
            thread_id=student["thread_id"],
            message=incoming_msg,
            assistant_id=campaign["assistant_id"]
        )
        
        # Send response
        await twilio_service.send_message(sender, response)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))