import streamlit as st
import base64
from datetime import datetime
from utils import save_message, get_chathistory, get_openai_response, chat_logo, icon


def img_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def chat_content():
    if "thread_id" in st.session_state and st.session_state.thread_id:
        chat_history = list(get_chathistory(st.session_state.thread_id))
        if chat_history:
            st.session_state.chat_history = [
                {"role": chat["role"], "message": chat["message"]}
                for chat in chat_history
            ]
        else:
            st.session_state.chat_history = []
    else:
        st.session_state.chat_history = []

    # Display only the last 5 messages
    for chat in st.session_state.chat_history[-5:]:
        with st.chat_message(chat["role"]):
            st.write(chat["message"])


def chat_interface():
    try:
        logo_base64 = img_to_base64(chat_logo)
        icon_base64 = img_to_base64(icon)
    except Exception as e:
        st.error(f"Error loading images: {str(e)}")
        logo_base64 = ""
        icon_base64 = ""

    st.markdown(
        f"""
    <style>
    body {{
        overflow: hidden;
    }}
    .top-bar {{
        position: fixed;
        top: 45px;
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
        height: 30px;
        cursor: pointer;
    }}
    .chat-container {{
        position: fixed;
        top: 100px;
        left: 0;
        right: 0;
        height: 300px;
        overflow-y: auto;
        padding: 2%;
    }}
    .input-container {{
        position: fixed;
        bottom: 0;
        left: 0;
        height: 0;
        background-color: white;
        padding: 1vh 2%;
        z-index: 1000;
        box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
    }}
    .sticky {{
        position: -webkit-sticky; /* For Safari */
        position: sticky;
        bottom: 0;
        padding: 10px;
        z-index: 1000;
    }}
    .stButton>button {{
        width: 100%;
        height: 100%;
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

    # Header
    hour = datetime.now().hour
    greeting = (
        "Good morning"
        if 5 <= hour < 12
        else "Good afternoon" if 12 <= hour < 17 else "Good evening"
    )

    header_container = st.container()
    chat_container = st.container()
    input_container = st.container()

    with header_container:
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        # st.header(f"{greeting}, {st.session_state.username}!")
        st.markdown("</div>", unsafe_allow_html=True)

    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        chat_content()
        st.markdown("</div>", unsafe_allow_html=True)

    with input_container:  # input-container
        st.markdown('<div class="input-container sticky">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            prompt = st.text_input("Type your message...", key="user_input")
        with col2:
            if st.button("Send"):
                if prompt:
                    response = get_openai_response(prompt)
                    save_message(st.session_state.thread_id, "user", prompt)
                    save_message(st.session_state.thread_id, "assistant", response)
                    st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Scroll to bottom of chat container
    st.markdown(
        """
        <script>
            var chatContainer = document.querySelector('.chat-container');
            chatContainer.scrollTop = chatContainer.scrollHeight;
        </script>
    """,
        unsafe_allow_html=True,
    )
