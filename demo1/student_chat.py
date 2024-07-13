# Dependencies 
from flask import Flask, request
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

# Create a Flask app
app = Flask(__name__)

@app.route("/") #temp homepage 
def home():
    """Home endpoint returning a simple message."""
    return "Home"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").lower()
    sender = request.values.get("From")

    student = students_collection.find_one(
        {"phone": sender.replace("whatsapp:", "")}
    )
    if not student: # Student must exist in database 
        return "Student not found", 400

    student_chat = student_chats_collection.find_one({"student_id": student["_id"]})
    
    if not student_chat: # Create a new chat history for this student
        thread = openai_client.beta.threads.create()
        student_chat = {
            "student_id": student["_id"],
            "thread_id": thread.id,
            "messages": []
        }
        student_chats_collection.insert_one(student_chat)

    active_campaign = campaigns_collection.find_one({"status": "active"})
    if not active_campaign:
        return "No active campaign found", 402

    thread_id = student_chat["thread_id"]
    campaign_id = active_campaign["_id"]
    assistant_id = active_campaign["student_assistant_id"]

    print(f"Creating message in thread {thread_id}")
    openai_client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=incoming_msg
    )

    save_student_message(student["_id"], "user", incoming_msg)

    print(f"Creating run with assistant {assistant_id}")
    run = openai_client.beta.threads.runs.create(
        thread_id=thread_id, assistant_id=assistant_id
    )

    print(f"Retrieving run {run.id}")
    run = openai_client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    while run.status != "completed":
        print(f"Run {run.id} not completed, retrieving again")
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run.id
        )

    print(f"Listing messages in thread {thread_id}")
    messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
    assistant_message = next(
        msg.content[0].text.value for msg in messages.data if msg.role == "assistant"
    )

    save_student_message(student["_id"], "assistant", assistant_message)

    print(f"Sending message: {assistant_message}")
    send_student_message(sender, assistant_message)

    return str(MessagingResponse())

if __name__ == "__main__":
    app.run(debug=True, port=5003)