# Dependencies
import streamlit as st
import base64
from utils import (
    save_admin_message,
    get_admin_chathistory,
    get_openai_response,
    chat_logo,
    icon,
    user_avatar,
    assistant_avatar,
)

# Loading images
def img_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def chat_interface():
    try:
        logo_base64 = img_to_base64(chat_logo)
        icon_base64 = img_to_base64(icon)
    except Exception as e:
        st.error(f"Error loading images: {str(e)}")
        logo_base64 = ""
        icon_base64 = ""

    # Custom CSS for header bar and chat container
    st.markdown(
        f"""
        <style>
        #root > div:nth-child(1) > div > div > div > div > section > div {{
            padding-top: 0rem;
        }}
        .top-bar {{
            position: fixed;
            top: 50px;
            left: 0;
            right: 0;
            height: 50px;
            background-color: #ffffff;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 5px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .logo {{
            height: 40px;
        }}
        .upload-icon {{
            height: 40px;
            cursor: pointer;
        }}
        .chat-container {{
            margin-top: 100px;
            padding-bottom: 100px;
        }}
        </style>

        <div class="top-bar">
            <img src="data:image/png;base64,{logo_base64}" class="logo" alt="Logo">
            <img src="data:image/png;base64,{icon_base64}" class="upload-icon" alt="Upload" onclick="document.getElementById('file-upload').click();">
            <input type="file" id="file-upload" style="display: none;">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Load chat history only if it's not already loaded
        if "thread_id" in st.session_state and st.session_state.thread_id:
            chat_history = get_admin_chathistory(st.session_state.thread_id)
            if chat_history:
                st.session_state.messages = chat_history

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            with st.chat_message(
                message["role"],
                avatar=user_avatar if message["role"] == "user" else assistant_avatar,
            ):
                st.markdown(message["message"])
        st.markdown("</div>", unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "message": prompt})
        
        # Display user message
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(prompt)
        
        # Display "Thinking..." message
        thinking_message = st.empty()
        with thinking_message.container():
            with st.chat_message("assistant", avatar=assistant_avatar):
                st.markdown("Typing...")
        
        # Get assistant response
        response = get_openai_response(prompt)
        
        # Remove "Thinking..." message and display actual response
        thinking_message.empty()
        with st.chat_message("assistant", avatar=assistant_avatar):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "message": response})
        
        # Save messages to database
        if "thread_id" in st.session_state:
            save_admin_message(st.session_state.thread_id, "user", prompt)
            save_admin_message(st.session_state.thread_id, "assistant", response)

        # Rerun to update the chat display
        st.experimental_rerun()

if __name__ == "__main__":
    chat_interface()