# Dependencies 
from flask import request
from twilio.twiml.messaging_response import MessagingResponse
from utils import (
    openai_client,
    campaigns_collection,
    students_collection,
    student_chats_collection,
    send_student_message,
    save_student_message
)
from bson import ObjectId
import logging
import sys
import os

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def webhook():
    logger.debug("Webhook function called")
    try:
        incoming_msg = request.values.get("Body", "").lower()
        sender = request.values.get("From")
        logger.debug(f"Received message: '{incoming_msg}' from {sender}")

        student = students_collection.find_one(
            {"phone": sender.replace("whatsapp:", "")}
        )
        if not student:
            logger.error(f"Student not found for phone: {sender}")
            return "Student not found", 400

        logger.debug(f"Student found: {student['_id']}")

        student_chat = student_chats_collection.find_one({"student_id": student["_id"]})
        
        if not student_chat:
            logger.debug("Creating new chat history for student")
            thread = openai_client.beta.threads.create()
            student_chat = {
                "student_id": student["_id"],
                "thread_id": thread.id,
                "messages": []
            }
            student_chats_collection.insert_one(student_chat)

        active_campaign = campaigns_collection.find_one({"status": "active"})
        if not active_campaign:
            logger.error("No active campaign found")
            return "No active campaign found", 402

        thread_id = student_chat["thread_id"]
        campaign_id = active_campaign["_id"]
        assistant_id = active_campaign["student_assistant_id"]

        logger.debug(f"Creating message in thread {thread_id}")
        openai_client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=incoming_msg
        )

        save_student_message(student["_id"], "user", incoming_msg)

        logger.debug(f"Creating run with assistant {assistant_id}")
        run = openai_client.beta.threads.runs.create(
            thread_id=thread_id, assistant_id=assistant_id
        )

        logger.debug(f"Retrieving run {run.id}")
        run = openai_client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        while run.status != "completed":
            logger.debug(f"Run {run.id} not completed, retrieving again")
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )

        logger.debug(f"Listing messages in thread {thread_id}")
        messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
        assistant_message = next(
            msg.content[0].text.value for msg in messages.data if msg.role == "assistant"
        )

        save_student_message(student["_id"], "assistant", assistant_message)

        logger.debug(f"Sending message: {assistant_message}")
        send_student_message(sender, assistant_message)

        logger.debug("Webhook processing completed successfully")
        return str(MessagingResponse())

    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}", exc_info=True)
        return "Internal server error", 500

if __name__ == "__main__":
    # This block is useful for local testing
    from flask import Flask
    app = Flask(__name__)

    @app.route("/webhook", methods=["POST"])
    def handle_webhook():
        return webhook()

    @app.route("/test", methods=["GET"])
    def test():
        logger.info("Test route accessed")
        return "Flask app is running!", 200

    port = int(os.environ.get("PORT", 5002))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port)