import os
from flask import Flask, request
from twilio.rest import Client
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Set up Twilio configuration
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(account_sid, auth_token)
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

# Initialize Flask app
app = Flask(__name__)

@app.route("/")
def home():
    """Home endpoint returning a simple message."""
    return "Home"

@app.route("/twilio/receiveMessage", methods=["POST"])
def receive_message():
    """Receives messages via POST from Twilio, processes with OpenAI, and sends response."""
    message = request.form["Body"]
    sender_id = request.form["From"]
    result = text_completion(message)
    if result["status"] == 1:
        send_message(sender_id, result["response"])
    return "OK", 200

def text_completion(prompt: str) -> dict:
    """Calls OpenAI API for chat completions."""
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return {"status": 1, "response": response.choices[0].message.content.strip()}

def send_message(to: str, message: str):
    """Sends a response message to a WhatsApp user via Twilio."""
    twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER, body=message, to=to
    )

if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")
