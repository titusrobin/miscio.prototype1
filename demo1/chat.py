# Dependencies 
import streamlit as st, os
from datetime import datetime
from utils import save_message, get_chathistory, users_collection, run_campaign, get_openai_response

# Load environment variables
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")


# Greeting, chat history, input and get_response, and chat history display
def chat_interface():
    hour = datetime.now().hour
    greeting = "Good morning" if 5 <= hour < 12 else "Good afternoon" if 12 <= hour < 17 else "Good evening"

    st.header(f"{greeting}, {st.session_state.username}!")

    if "thread_id" in st.session_state and st.session_state.thread_id:
        chat_history = list(get_chathistory(st.session_state.thread_id))
        if chat_history:
            st.session_state.chat_history = [{"role": chat["role"], "message": chat["message"]} for chat in chat_history]
        else:
            st.session_state.chat_history = []
    else:
        st.session_state.chat_history = []

    for chat in st.session_state.chat_history:
        st.write(f"**{chat['role']}:** {chat['message']}")

    user_input = st.text_input("Type your message...")

    if st.button("Send") and user_input:
        response = get_openai_response(user_input)
        st.session_state.chat_history.append({"role": "Admin", "message": user_input})
        st.session_state.chat_history.append({"role": "AI Agent", "message": response})
        st.rerun()

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
