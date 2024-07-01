import streamlit as st
from login import login_page
from chat import chat_interface
from twilio_webhook import start_webhook_server
import threading

# Start the webhook server in a separate thread
webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
webhook_thread.start()

# Main App Logic - Check if user is logged in and route page accordingly 
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    chat_interface()
else:
    login_page()