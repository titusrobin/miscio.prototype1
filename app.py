import streamlit as st, os
from flask import Flask, request
from login import login_page
from chat import chat_interface
from student_chat import webhook
import threading

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def flask_webhook():
    return webhook()

def run_flask():
    port = int(os.environ.get("PORT", 5004))
    app.run(host="0.0.0.0", port=port)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def run_streamlit():
    if st.session_state.logged_in:
        chat_interface()
    else:
        login_page()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    run_streamlit()