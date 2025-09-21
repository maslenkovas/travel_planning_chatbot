import streamlit as st
import httpx
import time
from typing import List, Dict

# Simple version for local development without complex styling

# Page configuration
st.set_page_config(
    page_title="Travel Planning Assistant",
    page_icon="✈️",
    layout="centered"
)

# Title
st.title("✈️ Travel Planning Assistant")
st.caption("Your AI-powered companion for planning amazing trips!")

# Configuration
API_URL = "http://localhost:8080/ask"

def call_travel_agent(query: str, chat_history: List[Dict]) -> str:
    """Call the travel agent API"""
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(API_URL, json={
                "query": query, 
                "chat_history": chat_history
            })
            if response.status_code == 200:
                return response.json().get("response", "No response received")
            else:
                return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Connection Error: Unable to reach the travel planning service. Please ensure the API is running at {API_URL}. ({str(e)})"

# Sidebar
with st.sidebar:
    st.header("🛠️ Settings")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    # Display chat stats
    if "messages" in st.session_state:
        user_messages = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
        st.metric("Messages Sent", user_messages)
    
    st.header("💡 Try These Examples")
    sample_queries = [
        "Plan a 5-day trip to Italy",
        "What's the weather like in Paris?",
        "Recommend budget hotels in Tokyo",
        "Best time to visit Santorini"
    ]
    
    for query in sample_queries:
        if st.button(query, key=f"sample_{hash(query)}"):
            st.session_state.pending_query = query

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm your travel planning assistant. I can help you plan trips, check weather, find accommodations, and answer travel-related questions. What would you like to know?"
    })

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle sample query from sidebar
if "pending_query" in st.session_state:
    prompt = st.session_state.pending_query
    del st.session_state.pending_query
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        # Prepare history for API
        recent_messages = st.session_state.messages[-9:-1]
        api_history = []
        
        i = 0
        while i < len(recent_messages) - 1:
            if recent_messages[i]["role"] == "user" and recent_messages[i + 1]["role"] == "assistant":
                api_history.append({
                    "user": recent_messages[i]["content"],
                    "agent": recent_messages[i + 1]["content"]
                })
                i += 2
            else:
                i += 1
        
        with st.spinner("Thinking..."):
            response = call_travel_agent(prompt, api_history[-4:])
        
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask me anything about travel planning..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        # Prepare history for API
        recent_messages = st.session_state.messages[-9:-1]
        api_history = []
        
        i = 0
        while i < len(recent_messages) - 1:
            if recent_messages[i]["role"] == "user" and recent_messages[i + 1]["role"] == "assistant":
                api_history.append({
                    "user": recent_messages[i]["content"],
                    "agent": recent_messages[i + 1]["content"]
                })
                i += 2
            else:
                i += 1
        
        with st.spinner("Thinking..."):
            response = call_travel_agent(prompt, api_history[-4:])
        
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})