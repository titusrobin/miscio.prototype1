from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils import students_collection, get_or_create_thread
from openai_utils import get_openai_response
from pyngrok import ngrok
import os

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").lower()
    sender = request.values.get("From", "")

    student = students_collection.find_one(
        {"phone_number": sender.replace("whatsapp:", "")}
    )
    if not student:
        resp = MessagingResponse()
        resp.message("Sorry, we couldn't identify you in our system.")
        return str(resp)

    campaign_id = student.get("current_campaign")

    if not campaign_id:
        resp = MessagingResponse()
        resp.message("Sorry, you're not currently enrolled in any active campaigns.")
        return str(resp)

    thread_id = get_or_create_thread(
        sender.replace("whatsapp:", ""), identifier_type="phone_number"
    )
    response = get_openai_response(incoming_msg, thread_id)

    resp = MessagingResponse()
    resp.message(response)
    return str(resp)


def start_webhook_server():
    # Start ngrok
    ngrok_tunnel = ngrok.connect(5000)
    print(f'Ngrok tunnel "{ngrok_tunnel.public_url}" -> "http://127.0.0.1:5000"')

    # Update your Twilio webhook URL here
    # You'll need to implement this function
    update_twilio_webhook_url(ngrok_tunnel.public_url + "/webhook")

    # Run the Flask app
    app.run(port=5000)


def update_twilio_webhook_url(url):
    # Implement the logic to update your Twilio webhook URL
    # This might involve using the Twilio API or manually updating it in the Twilio console
    print(f"Update your Twilio webhook URL to: {url}")
    # For now, we'll just print the URL. In a production environment, you'd want to automate this.
