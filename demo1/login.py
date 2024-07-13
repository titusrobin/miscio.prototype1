# Dependencies
import streamlit as st
from utils import create_new_thread, admin_users_collection, authenticate_user, misio_logo


def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])  # Fit window to center

    with col2:
        st.image(misio_logo, width=100, use_column_width=True)
        st.markdown(
            "<h1 style='text-align: center;'>Welcome back</h1>", unsafe_allow_html=True
        )

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", key="login_button"):
            if authenticate_user(username, password):  # Authwall for demo
                st.session_state.logged_in = True
                st.session_state.username = username

                user = admin_users_collection.find_one({"username": username})

                if not user:
                    thread_id = create_new_thread()
                    admin_users_collection.insert_one(
                        {"username": username, "thread_id": thread_id}
                    )  # Create a new thread per user
                    st.session_state.thread_id = thread_id
                else:
                    st.session_state.thread_id = user.get("thread_id")
                    if not st.session_state.thread_id:
                        # This handles the case where a user exists but doesn't have a thread_id
                        thread_id = create_new_thread()
                        admin_users_collection.update_one(
                            {"username": username}, {"$set": {"thread_id": thread_id}}
                        )
                        st.session_state.thread_id = thread_id

                st.experimental_rerun()  # State history update and Loading
            else:
                st.error("Invalid credentials. Please try again.")

        st.markdown("*Don't have an account? [Sign Up](#)*")

    # CSS for styling
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )
