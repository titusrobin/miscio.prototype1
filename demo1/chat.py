import streamlit as st
from datetime import datetime
from utils import save_message, get_chathistory
from openai_utils import get_openai_response

def chat_interface():
    hour = datetime.now().hour
    greeting = "Good morning" if 5 <= hour < 12 else "Good afternoon" if 12 <= hour < 17 else "Good evening"

    st.header(f"{greeting}, {st.session_state.username}!")

    if "thread_id" not in st.session_state or not st.session_state.thread_id:
        thread = openai_client.beta.threads.create()
        st.session_state.thread_id = thread.id
        users_collection.update_one(
            {"username": st.session_state.username},
            {"$set": {"thread_id": st.session_state.thread_id}}
        )

    chat_history = list(get_chathistory(st.session_state.thread_id))
    st.session_state.chat_history = [{"role": chat["role"], "message": chat["message"]} for chat in chat_history]

    for chat in st.session_state.chat_history:
        st.write(f"**{chat['role']}:** {chat['message']}")

    user_input = st.text_input("Type your message...")

    if st.button("Send") and user_input:
        try:
            response = get_openai_response(user_input, st.session_state.thread_id)
            st.session_state.chat_history.append({"role": "Admin", "message": user_input})
            st.session_state.chat_history.append({"role": "AI Agent", "message": response})
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        st.rerun()

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()