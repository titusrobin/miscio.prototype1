import streamlit as st
from utils import create_new_thread, users_collection, authenticate_user, misio_logo

def login_page(): 
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.image(misio_logo, width=100, use_column_width=True)
        st.markdown("<h1 style='text-align: center;'>Welcome back</h1>", unsafe_allow_html=True)
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", key="login_button"):
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

        st.markdown("*Don't have an account? [Sign Up](#)*")

# CSS and JavaScript for dynamic button and input field styling
st.markdown("""
    <style>
    .stButton>button {
        color: white;
        background-color: #1A73E8;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #14438E;
        color: white;
    }
    .stButton>button:active {
        background-color: #0f1535;
        color: white;
    }
    .stTextInput>div>div>input {
        padding: 10px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #14438E !important;
        box-shadow: 0 0 0 1px #14438E !important;
    }
    div[data-baseweb="input"] > div:focus-within {
        border-color: #14438E !important;
        box-shadow: 0 0 0 1px #14438E !important;
    }
    </style>
    
    <script>
    const buttons = window.parent.document.querySelectorAll('.stButton > button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#14438E';
            this.style.color = 'white';
        });
        button.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '#1A73E8';
            this.style.color = 'white';
        });
        button.addEventListener('mousedown', function() {
            this.style.backgroundColor = '#0f1535';
            this.style.color = 'white';
        });
        button.addEventListener('mouseup', function() {
            this.style.backgroundColor = '#1A73E8';
            this.style.color = 'white';
        });
    });
    </script>
    """, unsafe_allow_html=True)