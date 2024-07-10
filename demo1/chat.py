import streamlit as st
import base64
from utils import save_message, get_chathistory, get_openai_response, chat_logo, icon

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
            margin-top: 100px;  /* Adjusted to account for the fixed top bar */
            padding-bottom: 100px;  /* Add some padding at the bottom */
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

    # Load chat history
    if "thread_id" in st.session_state and st.session_state.thread_id:
        chat_history = list(get_chathistory(st.session_state.thread_id))
        if chat_history:
            st.session_state.messages = [
                {"role": chat["role"], "content": chat["message"]}
                for chat in chat_history
            ]

    # Display chat messages
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages[-5:]:  # Display only the last 5 messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display assistant response
        with st.chat_message("assistant"):
            response = get_openai_response(prompt)
            st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Save messages to database
        save_message(st.session_state.thread_id, "user", prompt)
        save_message(st.session_state.thread_id, "assistant", response)

if __name__ == "__main__":
    chat_interface()