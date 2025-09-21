import streamlit as st
import httpx
import time
from typing import List, Dict


# Page configuration
st.set_page_config(
    page_title="WanderWords",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        color: #6B7280;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        color: #1F2937 !important;
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] p {
        color: #1F2937 !important;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    
    .user-message [data-testid="stMarkdownContainer"] p {
        color: #1565C0 !important;
    }
    
    .assistant-message {
        background-color: #F1F8E9;
        border-left: 4px solid #4CAF50;
    }
    
    .assistant-message [data-testid="stMarkdownContainer"] p {
        color: #2E7D32 !important;
    }
    
    /* Additional chat message styling */
    .stChatMessage [data-testid="stMarkdownContainer"] {
        color: #1F2937 !important;
    }
    
    .stChatMessage [data-testid="stMarkdownContainer"] * {
        color: inherit !important;
    }
    
    .sidebar .element-container {
        margin-bottom: 1rem;
    }
    
    .status-box {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .status-connected {
        background-color: #D4EDDA;
        color: #155724;
        border: 1px solid #C3E6CB;
    }
    
    .status-error {
        background-color: #F8D7DA;
        color: #721C24;
        border: 1px solid #F5C6CB;
    }
    
    /* Streamlit chat message overrides */
    .stChatMessage {
        color: #1F2937 !important;
    }
    
    .stChatMessage p {
        color: #1F2937 !important;
        margin-bottom: 0.5rem;
    }
    
    .stChatMessage div[data-testid="chatAvatarIcon-user"] ~ div {
        background-color: #E3F2FD !important;
        border-left: 4px solid #2196F3 !important;
    }
    
    .stChatMessage div[data-testid="chatAvatarIcon-assistant"] ~ div {
        background-color: #F1F8E9 !important;
        border-left: 4px solid #4CAF50 !important;
    }
    
    /* Ensure all text in chat messages is visible */
    .stChatMessage * {
        color: #1F2937 !important;
    }
    
    /* Override any default Streamlit text colors */
    [data-testid="stChatMessageContent"] {
        color: #1F2937 !important;
    }
    
    [data-testid="stChatMessageContent"] p {
        color: #1F2937 !important;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_URL = "http://agent-api:8080/ask"
LOCAL_API_URL = "http://localhost:8080/ask"  # Fallback for local testing

def check_api_connection():
    """Check if the API is accessible"""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(API_URL.replace("/ask", "/health"))
            return True
    except:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(LOCAL_API_URL.replace("/ask", "/health"))
                return True
        except:
            return False

def call_travel_agent(query: str, chat_history: List[Dict]) -> str:
    """Call the travel agent API"""
    try:
        # Try the main API URL first
        with httpx.Client(timeout=30.0) as client:
            response = client.post(API_URL, json={
                "query": query, 
                "chat_history": chat_history
            })
            if response.status_code == 200:
                return response.json().get("response", "No response received")
            else:
                return f"API Error: {response.status_code} - {response.text}"
    except httpx.ConnectError:
        # Fallback to local URL
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(LOCAL_API_URL, json={
                    "query": query, 
                    "chat_history": chat_history
                })
                if response.status_code == 200:
                    return response.json().get("response", "No response received")
                else:
                    return f"API Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Connection Error: Unable to reach the travel planning service. Please ensure the API is running. ({str(e)})"
    except Exception as e:
        return f"Error: {str(e)}"

def stream_response(text: str):
    """Stream response text word by word for better UX"""
    words = text.split()
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(0.02)

# Sidebar
with st.sidebar:
    st.markdown("### 🛠️ Settings")
    
    # API Status
    st.markdown("### 📡 Connection Status")
    if check_api_connection():
        st.markdown('<div class="status-box status-connected">🟢 API Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box status-error">🔴 API Disconnected</div>', unsafe_allow_html=True)
        st.warning("The travel planning API is not accessible. Please check if the service is running.")
    
    # Chat History Management
    st.markdown("### 💬 Chat Management")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Display chat stats
    if "messages" in st.session_state:
        user_messages = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
        st.metric("Messages Sent", user_messages)
    
    # Sample queries
    st.markdown("### 💡 Try These Examples")
    
    sample_queries = [
        "What's the weather like in Paris?",
        "What did Mark Twain think about the Sphynx?",
        "I want to visit the places Twain went to in Italy - what's the weather like there now?",
    ]
    
    for query in sample_queries:
        if st.button(f"📝 {query}", key=f"sample_{hash(query)}", use_container_width=True):
            st.session_state.sample_query = query

# Main content
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Display logo if it exists
    try:
        st.image("/app/images/logo.jpg", width=200)
    except:
        # If logo not found, show emoji instead
        st.markdown('<div style="text-align: center; font-size: 4rem;">✈️</div>', unsafe_allow_html=True)

st.markdown('<h1 class="main-header">WanderWords - Travel Planning Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">It provides travel-related answers and weather information based on Mark Twain\'s travels..</p>', unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm your travel planning assistant. I can help you with current weather information or answer questions about locations, experiences, and insights from 'The Innocents Abroad'. What would you like to know?"
    })

# Handle sample query from sidebar
if "sample_query" in st.session_state:
    st.session_state.pending_query = st.session_state.sample_query
    del st.session_state.sample_query

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle pending query from sidebar
if "pending_query" in st.session_state:
    prompt = st.session_state.pending_query
    del st.session_state.pending_query
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        # Prepare chat history for API (last 8 messages to maintain context)
        recent_history = [
            {"user": msg["content"] if msg["role"] == "user" else "", 
             "agent": msg["content"] if msg["role"] == "assistant" else ""}
            for msg in st.session_state.messages[-8:]
            if msg["role"] in ["user", "assistant"]
        ]
        
        # Filter out empty entries and restructure
        api_history = []
        for i in range(0, len(recent_history), 2):
            if i < len(recent_history) - 1:  # Make sure we have both user and assistant
                user_msg = st.session_state.messages[-(len(recent_history)-i)]
                if user_msg["role"] == "user":
                    next_msg_idx = -(len(recent_history)-i-1)
                    if next_msg_idx < 0 and abs(next_msg_idx) <= len(st.session_state.messages):
                        assistant_msg = st.session_state.messages[next_msg_idx]
                        if assistant_msg["role"] == "assistant":
                            api_history.append({
                                "user": user_msg["content"],
                                "agent": assistant_msg["content"]
                            })
        
        # Show loading indicator
        with st.spinner("🤔 Thinking..."):
            response = call_travel_agent(prompt, api_history[-4:])  # Last 4 exchanges
        
        # Stream the response
        response_placeholder = st.empty()
        full_response = ""
        
        for chunk in stream_response(response):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
            
        response_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask me anything about travel planning..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        # Prepare chat history for API (last 8 messages to maintain context)
        recent_messages = st.session_state.messages[-9:-1]  # Exclude the current user message
        api_history = []
        
        # Pair up user and assistant messages
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
        
        # Show loading indicator
        with st.spinner("🤔 Thinking..."):
            response = call_travel_agent(prompt, api_history[-4:])  # Last 4 exchanges
        
        # Stream the response
        response_placeholder = st.empty()
        full_response = ""
        
        for chunk in stream_response(response):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
            
        response_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6B7280; font-size: 0.9rem;'>
        🌟 Powered by AI • Built with Streamlit • Travel smarter, not harder
    </div>
    """, 
    unsafe_allow_html=True
)