# Dependencies 
import streamlit as st
from login import login_page
from chat import chat_interface

# Main App Logic - Check if user is logged in and route page accordingly 
if "logged_in" not in st.session_state: # Note stored in cookies, browser but on server. 
    st.session_state.logged_in = False

if st.session_state.logged_in:
    chat_interface()
else:
    login_page()


###
# Not secure by default. Use HTTPS. 