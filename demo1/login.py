# Dependencies
import streamlit as st
from utils import create_new_thread, users_collection, authenticate_user, misio_logo

# Authenticate, session_state, username, thread_id
def login_page():
    st.image(misio_logo, width=150)
    
    username = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            
            user = users_collection.find_one({"username": username})
            
            if not user:
                thread_id = create_new_thread()
                users_collection.insert_one({"username": username, "thread_id": thread_id})
                st.session_state.thread_id = thread_id
            else:
                st.session_state.thread_id = user.get("thread_id")
        else:
            st.error("Invalid credentials. Please try again.")
