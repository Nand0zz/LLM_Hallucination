import streamlit as st
import json
import uuid
import time
import base64
import requests
import game_logic # Import the new game logic script

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="LLM Arena",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# Custom CSS for Styling
# ---------------------------
st.markdown("""
    <style>
        /* === Global Background === */
        .stApp {
            background: linear-gradient(135deg, #1e1e2f, #3c1e64) !important;
            font-family: 'Segoe UI', sans-serif;
            color: #ffffff !important;
        }

        header, [data-testid="stDecoration"] {
            display: none !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: #121224 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        /* Sidebar radios */
        .stRadio div[role="radiogroup"] label {
            color: #f0f0f0 !important;
            padding: 6px 10px;
            border-radius: 6px;
        }
        .stRadio div[role="radiogroup"] label:hover {
            background: #7b1fa2 !important;
            color: #fff !important;
        }

        /* Expander (Power-Up Hint) */
        div[data-testid="stExpander"] {
            background: rgba(60, 20, 90, 0.95) !important;
            border-radius: 12px !important;
            border: 1px solid #9c27b0 !important;
            box-shadow: 0px 0px 12px rgba(156, 39, 176, 0.6) !important;
        }
        div[data-testid="stExpander"] * {
            color: #ffffff !important;
        }
        div[data-testid="stExpander"] strong, 
        div[data-testid="stExpander"] b {
            color: #ff80ff !important;
        }
        div.streamlit-expanderHeader {
            font-weight: bold !important;
            color: #ffeb3b !important;
        }

        /* === FORM FIXES (Team Details) === */
        label, .stTextInput label, .stTextArea label, .stSelectbox label {
            color: #ffffff !important;   /* force white labels */
            font-weight: 600 !important;
        }
        .stTextInput input, .stTextArea textarea {
            background: #2e2e4a !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            border: 1px solid #7b1fa2 !important;
        }
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {
            color: #cccccc !important; /* lighter placeholder */
        }

        /* === SUCCESS / ERROR MESSAGES === */
        [data-testid="stNotification"] {
            color: #ffffff !important;      /* white text */
            font-weight: bold !important;
        }
        [data-testid="stNotification"] p {
            color: #ffffff !important;      /* white text in paragraph */
        }

        /* Headers */
        h1, h2, h3, h4, h5 {
            color: #ffffff !important;
        }

        /* Buttons */
        div.stButton > button {
            background: linear-gradient(90deg, #7b1fa2, #9c27b0) !important;
            color: white !important;
            border-radius: 12px !important;
            font-weight: bold !important;
            padding: 10px 20px !important;
        }
        div.stButton > button:hover {
            background: linear-gradient(90deg, #9c27b0, #e91e63) !important;
        }
        
                /* === Chat Messages === */
        .stChatMessage {
            color: #ffffff !important;        /* make all chat text white */
        }
        .stChatMessage div, .stChatMessage p, .stChatMessage span {
            color: #ffffff !important;        /* ensure nested elements are also white */
        }
        .stChatMessage[data-testid="stChatMessageAssistant"] {
            background: rgba(60, 20, 90, 0.6) !important;  /* subtle purple bg for assistant */
            border-radius: 12px !important;
            padding: 10px !important;
        }
        .stChatMessage[data-testid="stChatMessageUser"] {
            background: rgba(123, 31, 162, 0.6) !important; /* darker purple for user */
            border-radius: 12px !important;
            padding: 10px !important;
        }

    </style>
""", unsafe_allow_html=True)

# ---------------------------
# User ID
# ---------------------------
def get_current_user_id():
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())
    return st.session_state["user_id"]


# ---------------------------
# Home Dashboard
# ---------------------------
def display_home_dashboard():
    st.title("🏟️ Welcome to the **LLM Arena** 🤖")
    st.markdown("### Enter the championship and show off your **Prompt Engineering Power!**")

    with st.form("user_details_form"):
        st.subheader("👥 Team Details")
        st.text_input("Team Name", key="team_name")
        st.text_input("Participant 1", key="p1_name")
        st.text_input("Participant 2", key="p2_name")
        st.text_input("Participant 3", key="p3_name")
        st.text_input("Email", key="email")
        st.text_input("College", key="college")

        submitted = st.form_submit_button("🚀 Enter Arena")
        if submitted:
            st.session_state["form_submitted"] = True
            st.success("✅ Team Registered! Use the sidebar to begin the challenges.")


# ---------------------------
# Levels
# ---------------------------
def display_level(level):
    level_info = game_logic.get_level_info(level)
    st.header(level_info.get("title", f"Level {level}"))
    st.markdown(level_info.get("description2", ""))

    with st.expander("💡 Power-Up Hint"):
        st.info(level_info.get("description", ""))

    if f"messages_{level}" not in st.session_state:
        st.session_state[f"messages_{level}"] = []

    for message in st.session_state[f"messages_{level}"]:
        role = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(message["content"])

    prompt = st.chat_input("Type your prompt here...")
    if prompt:
        st.session_state[f"messages_{level}"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("⚡ Arena Bot is thinking..."):
                llm_response = game_logic.generate_response(prompt, level)
                if llm_response:
                    st.markdown(llm_response)
                    st.session_state[f"messages_{level}"].append({"role": "assistant", "content": llm_response})

    st.markdown("---")
    st.button(f"🏆 Submit Final Answer for Level {level}", key=f"submit_{level}")


# ---------------------------
# Main
# ---------------------------
def main():
    st.sidebar.markdown("## 🏟️ LLM Arena")
    st.sidebar.markdown("Level Up Your Prompts, Unlock the Future")
    st.sidebar.markdown("---")

    if st.session_state.get("form_submitted"):
        st.sidebar.subheader("👥 Your Team")
        st.sidebar.markdown(f"**Team:** {st.session_state.get('team_name','-')}")
        st.sidebar.markdown(f"**Member 1:** {st.session_state.get('p1_name','-')}")
        if st.session_state.get("p2_name"): st.sidebar.markdown(f"**Member 2:** {st.session_state['p2_name']}")
        if st.session_state.get("p3_name"): st.sidebar.markdown(f"**Member 3:** {st.session_state['p3_name']}")
        st.sidebar.markdown("---")

    tabs = ["Home", "Level 1", "Level 2", "Level 3"]
    selected_tab = st.sidebar.radio("🎮 Navigate Arena", tabs)

    if selected_tab == "Home":
        display_home_dashboard()
    elif selected_tab == "Level 1":
        display_level(1)
    elif selected_tab == "Level 2":
        display_level(2)
    elif selected_tab == "Level 3":
        display_level(3)


if __name__ == "__main__":
    main()
