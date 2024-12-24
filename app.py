import streamlit as st
import os
from utils import assistant_avatar

# Streamlit configuration
st.set_page_config(
    page_title="Miscio Assistant", page_icon=assistant_avatar, layout="wide"
)

# Logic
from login import login_page
from chat import chat_interface

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def main():
    if st.session_state.logged_in:
        chat_interface()
    else:
        login_page()


if __name__ == "__main__":  # When app.py is initiated as main script
    main()
