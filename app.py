import streamlit as st
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