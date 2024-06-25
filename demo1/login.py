# Dependencies
import streamlit as st
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from utils import create_new_thread, mongo_client, db, users_collection  

# Setup
load_dotenv()

# Demo auth wall 
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
            
            user = users_collection.find_one({"username": username}) # Check if user exists
            
            if not user:
                thread_id = create_new_thread()  # Create a new thread and get its ID - utils
                users_collection.insert_one({"username": username, "thread_id": thread_id})
                st.session_state.thread_id = thread_id
            else:
                st.session_state.thread_id = user.get("thread_id") 
        else:
            st.error("Invalid credentials. Please try again.")
