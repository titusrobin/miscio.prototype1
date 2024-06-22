import streamlit as st
import openai
from datetime import datetime
from utils import assistant, save_message, get_chathistory, users_collection  # Ensure this import
from utils import openai_client as client

def get_response(message):
    if "thread_id" not in st.session_state or not st.session_state.thread_id:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        # Update the user's document with the new thread_id
        users_collection.update_one(
            {"username": st.session_state.username},
            {"$set": {"thread_id": st.session_state.thread_id}}
        )

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, role="user", content=message
    )

    save_message(st.session_state.thread_id, "user", message)

    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant.id,
        instructions=f"Please address the user as Miscio Admin. They are the admin to whom you are the assistant at Miscio. The user asked: {message}",
    )

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
        for msg in messages.data:
            if msg.role == "assistant":
                content = msg.content[0].text.value
                save_message(st.session_state.thread_id, "assistant", content)
                return content

    return "I'm sorry, I couldn't process your request at this time."

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
        response = get_response(user_input)
        st.session_state.chat_history.append({"role": "Admin", "message": user_input})
        st.session_state.chat_history.append({"role": "AI Agent", "message": response})
        st.experimental_rerun()

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()
