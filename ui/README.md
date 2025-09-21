# Travel Planning Chatbot - Streamlit UI

This is the new and improved Streamlit-based user interface for the Travel Planning Chatbot. It provides a modern, interactive chat experience with better visual appeal and user experience.

## Features

✨ **Modern Chat Interface**: Clean, WhatsApp-like chat bubbles with proper message threading
🎨 **Beautiful Design**: Custom CSS styling with travel-themed colors and icons
📱 **Responsive Layout**: Works well on desktop and mobile devices
⚡ **Real-time Streaming**: Messages appear with a typewriter effect for better UX
📊 **Chat Statistics**: Track message count and conversation history
🧹 **Easy Management**: Clear chat history and session management
💡 **Sample Queries**: Pre-built example questions to get users started
🔌 **API Integration**: Seamless connection to the travel agent backend

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Start all services**:
   ```bash
   docker-compose up --build
   ```

2. **Access the Streamlit UI**:
   Open your browser and go to: http://localhost:8501

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   cd ui
   pip install streamlit httpx
   ```

2. **Start the API backend** (in another terminal):
   ```bash
   # From the project root
   docker-compose up agent-api chromadb
   ```

3. **Run Streamlit locally**:
   ```bash
   cd ui
   streamlit run streamlit_app.py
   ```

4. **Access the app**:
   Open your browser and go to: http://localhost:8501

### Option 3: Simple Local Version

For a simpler version without advanced styling:

```bash
cd ui
streamlit run simple_streamlit_app.py
```


## Configuration

The app automatically detects whether it's running in Docker or locally:

- **Docker**: Uses `http://agent-api:8080/ask`
- **Local**: Uses `http://localhost:8080/ask`

## Troubleshooting

### API Connection Issues

If you see "API Disconnected" in the sidebar:

1. Make sure the agent-api service is running
2. Check that port 8080 is accessible
3. Verify your environment variables are set

### Docker Issues

```bash
# Rebuild containers
docker-compose down
docker-compose up --build

# Check logs
docker-compose logs ui
docker-compose logs agent-api
```

### Local Development Issues

```bash
# Install dependencies
pip install streamlit httpx

# Check if API is running
curl http://localhost:8080/ask
```

## Files

- `streamlit_app.py` - Full-featured Streamlit app with advanced styling
- `simple_streamlit_app.py` - Simplified version for development
- `main.py` - Original FastAPI app (still available as fallback)
- `requirements.txt` - Updated with Streamlit dependency
- `Dockerfile` - Updated to run Streamlit instead of FastAPI

## Technical Details

- **Framework**: Streamlit 1.x
- **HTTP Client**: httpx for API communication
- **Session Management**: Streamlit session state
- **Port**: 8501 (Streamlit default)
- **Styling**: Custom CSS with travel theme
- **Responsive**: Mobile-first design

Enjoy your new and improved travel planning experience! ✈️🌍