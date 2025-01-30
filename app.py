import streamlit as st
import json
import requests
from typing import Optional

# Constants from your API code
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "34d17c26-a986-4b87-a228-81e15a1ecc86"
FLOW_ID = "c684fe71-125c-417b-8e6f-7d0de56d6c32"
APPLICATION_TOKEN = st.secrets["APPLICATION_TOKEN"]

# Your existing TWEAKS dictionary
TWEAKS = {
    "ChatInput-tVn2G": {},
    "ParseData-ubf9h": {},
    "Prompt-pBJ0b": {},
    "OpenAIModel-VU7gI": {},
    "ChatOutput-YYy3t": {},
    "AstraDB-R8Juu": {},
    "OpenAIEmbeddings-486bm": {}
}

# Custom styling to match Sarvodaya Finance website
st.set_page_config(
    page_title="Sarvodaya Finance Assistant",
    page_icon="💰",
    layout="centered"
)

# Custom CSS to match Sarvodaya Finance colors
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .stMarkdown {
        color: #333333;
    }
    .stButton button {
        background-color: #1e4999;
        color: white;
    }
    .stButton button:hover {
        background-color: #163a7a;
    }
    h1 {
        color: #1e4999;
        text-align: center;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #f0f2f6;
    }
    .assistant-message {
        background-color: #e8f0ff;
        border-left: 5px solid #1e4999;
    }
    div.stImage {
        text-align: center;
        margin-bottom: 2rem;
    }
    .sample-prompt {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .sample-prompt:hover {
        background-color: #e9ecef;
        border-color: #1e4999;
    }
    .sample-prompts-container {
        margin: 2rem 0;
        display: grid;
        gap: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def run_flow(message: str,
    endpoint: str = FLOW_ID,
    output_type: str = "chat",
    input_type: str = "chat",
    tweaks: Optional[dict] = TWEAKS) -> dict:
    
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }
    
    if tweaks:
        payload["tweaks"] = tweaks
        
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def process_message(prompt):
    """Helper function to process messages and get responses"""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get bot response
    with st.spinner("Processing your request..."):
        response = run_flow(prompt)
        try:
            # Navigate through the nested structure to get the message
            if isinstance(response, dict):
                # Extract message from the nested structure
                message = (response.get('outputs', [])[0]
                          .get('outputs', [])[0]
                          .get('results', {})
                          .get('message', {})
                          .get('data', {})
                          .get('text', 'No response received'))
                
                st.session_state.messages.append({"role": "assistant", "content": message})
            else:
                st.error("I apologize, but I couldn't process your request at the moment.")
                st.write("Technical details:", response)
        except Exception as e:
            st.error("I apologize, but something went wrong. Please try again.")
            st.write("Technical details:", str(e))

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header with Sarvodaya styling and logo
st.image("logo.png", width=300)
st.title("Sarvodaya Development Finance Investor Assistant")
st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;'>
        Welcome to Sarvodaya Development Finance's AI-Powered Investor Assistant. I'm here to help you with information about our financial and business performance 
    </div>
""", unsafe_allow_html=True)

# Sample prompts section
st.markdown("""
    <div style='margin-bottom: 1rem;'>
        <h3 style='color: #1e4999;'>Try asking about:</h3>
    </div>
""", unsafe_allow_html=True)

# Sample prompts with improved styling
sample_prompts = [
    "Give me an overview of loan growth in FY2024",
    "Provide me an analysis of the asset quality",
    "How is the overall profitability of the company"
]

# Create columns for sample prompts
col1, col2, col3 = st.columns(3)
for col, prompt in zip([col1, col2, col3], sample_prompts):
    if col.button(prompt, key=f"sample_{prompt}", help=f"Click to ask about {prompt}"):
        process_message(prompt)

# Display chat history with custom styling
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"""
            <div class='chat-message {message["role"]}-message'>
                {message["content"]}
            </div>
        """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    process_message(prompt)

# Footer with Sarvodaya styling
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666666; font-size: 0.8rem;'>
        © 2025 Sarvodaya Development Finance PLC. All rights reserved.<br>
        Licensed by the Monetary Board of the Central Bank of Sri Lanka under the Finance Business Act No. 42 of 2011.
    </div>
""", unsafe_allow_html=True)

# Clear chat button in sidebar with Sarvodaya styling
if st.sidebar.button("Clear Conversation", key="clear"):
    st.session_state.messages = []
    st.rerun()
