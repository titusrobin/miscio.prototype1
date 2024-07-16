import streamlit as st
import os

# Streamlit configuration
st.set_page_config(page_title="Miscio Assistant", page_icon="🧊", layout="wide")

# Custom CSS for white background
st.markdown("""
    <style>
    .reportview-container {
        background: white;
    }
    .main {
        background-color: white;
    }
    body {
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

# Your existing code starts here
from login import login_page
from chat import chat_interface

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def main():
    if st.session_state.logged_in:
        chat_interface()
    else:
        login_page()

if __name__ == "__main__":
    main()