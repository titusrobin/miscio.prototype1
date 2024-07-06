# Dependencies 
import streamlit as st
import os
import base64
from datetime import datetime
from utils import save_message, get_chathistory, users_collection, run_campaign, get_openai_response, chat_logo, icon

# Load environment variables
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

def img_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def chat_content():
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

def chat_interface():
    # Debug: Print image paths
    print(f"Logo path: {chat_logo}")
    print(f"Icon path: {icon}")

    try:
        logo_base64 = img_to_base64(chat_logo)
        icon_base64 = img_to_base64(icon)
    except Exception as e:
        st.error(f"Error loading images: {str(e)}")
        logo_base64 = ""
        icon_base64 = ""

    st.markdown(f"""
    <style>
    .top-bar {{
        position: fixed;
        top: 43px;
        left: 0;
        right: 0;
        width: 100%;
        height: 40px;
        background-color: #ffffff;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    .logo {{
        height: 35px;
        margin-left: 20px;
    }}
    .upload-icon {{
        height: 35px;
        cursor: pointer;
        margin-right: 20px;
    }}
    .content {{
        padding-top: 10px;  # Reduced to bring content closer to top bar
    }}
    .stHeader {{
        margin-top: -100px;  # Negative margin to move header up
    }}
    </style>
    
    <div class="top-bar">
        <img src="data:image/png;base64,{logo_base64}" class="logo" alt="Logo">
        <img src="data:image/png;base64,{icon_base64}" class="upload-icon" alt="Upload" onclick="document.getElementById('file-upload').click();">
        <input type="file" id="file-upload" style="display: none;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content">', unsafe_allow_html=True)
    chat_content()
    st.markdown('</div>', unsafe_allow_html=True)