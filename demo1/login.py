import streamlit as st
from utils import get_or_create_thread, users_collection

def authenticate(username, password):
    return username == "admin" and password == "password"

def login_page():
    st.image("/Users/robintitus/Desktop/Miscio/prototype1/demo1/imgs/62698cdbd01e66c6b10f6447_Miscio Logos-02.png", width=150)
    
    username = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            
            st.session_state.thread_id = get_or_create_thread(username, identifier_type='username')
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")