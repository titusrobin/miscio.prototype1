import streamlit as st # Dependencies 

# Demo boolean credentials auth system for demo purposes
def authenticate(username, password):
    return username == "admin" and password == "password"

def login_page():
    st.image("/Users/robintitus/Desktop/Miscio/prototype1/demo1/imgs/62698cdbd01e66c6b10f6447_Miscio Logos-02.png", width=150)  
    #st.title("Miscio Assistant")
    
    username = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Invalid credentials. Please try again.")