from flask import Flask, request
from student_chat import webhook
import os
import logging
import sys

app = Flask(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.before_request
def log_request_info():
    logger.debug('Headers: %s', request.headers)
    logger.debug('Body: %s', request.get_data())

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    logger.debug("Received webhook request")
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Request data: {request.get_data(as_text=True)}")
    return webhook()

@app.route("/test", methods=["GET"])
def test():
    logger.info("Test route accessed")
    return "Flask app is running!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    logger.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port)