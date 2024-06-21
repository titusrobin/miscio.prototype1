# Dependencies, functions
import streamlit as st
import openai
from datetime import datetime
from utils import assistant, save_message, get_chathistory
from utils import openai_client as client

def get_response(message):
    # Create a thread if it doesn't exist for the user
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # Add user message to the thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, role="user", content=message
    )

    # Create a run and poll for its completion
    run = client.beta.threads.runs.create_and_poll(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant.id,
        instructions=f"Please address the user as Miscio Admin. They are the admin to whom you are the assistant at Miscio. The user asked: {message}",
    )

    # If the run completes, list the messages added to the thread by the assistant
    if run.status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Extract the latest assistant message
        for message in messages.data:
            if message.role == "assistant":
                content = message.content[0].text.value
                return content

    return "I'm sorry, I couldn't process your request at this time."


def chat_interface():
    # ... (greeting and chat history code)

    # Input box
    st.session_state.user_input = st.text_input("Type your message...", value=st.session_state.user_input if "user_input" in st.session_state else "")

    if st.button("Send"):
        if st.session_state.user_input:  # Only process if there's input
            response = get_response(st.session_state.user_input)
            st.session_state.chat_history.append({"sender": "Admin", "message": st.session_state.user_input})
            st.session_state.chat_history.append({"sender": "AI Agent", "message": response})
            st.session_state.user_input = ""  # Clear the input field
            st.experimental_rerun()  # Rerun the app to display the updated chat

    # ... (clear chat history button code)


### Greeting + Chat History + Input Box
def chat_interface():
    hour = datetime.now().hour

    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
    elif 17 <= hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Good evening"

    st.header(f"{greeting}, {st.session_state.username}!")

    # Creating a list to save chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for chat in st.session_state.chat_history:
        st.write(f"**{chat['sender']}:** {chat['message']}")

    # Input box
    st.session_state.user_input = st.text_input("Type your message...", value=st.session_state.user_input if "user_input" in st.session_state else "")

    if st.button("Send"):
        if st.session_state.user_input:  # Only process if there's input
            response = get_response(st.session_state.user_input)
            st.session_state.chat_history.append({"sender": "Admin", "message": st.session_state.user_input})
            st.session_state.chat_history.append({"sender": "AI Agent", "message": response})
            st.session_state.user_input = ""  # Clear the input field
            st.experimental_rerun()  # Rerun the app to display the updated chat


    # Clear chat history button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.experimental_rerun()


### Rewrite the script for the SVM and tagging systems we have setup
# def chat_interface():
