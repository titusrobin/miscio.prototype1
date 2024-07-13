# Dependencies 
import streamlit as st
from login import login_page
from chat import chat_interface

# Routing: Login page v Chat interface
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def run_streamlit():
    if st.session_state.logged_in:
        chat_interface()
    else:
        login_page()

# Terminal Execution on command
if __name__ == "__main__":
    run_streamlit()