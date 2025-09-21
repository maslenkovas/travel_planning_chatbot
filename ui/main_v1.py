
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import httpx
from typing import List


app = FastAPI()

API_URL = "http://agent-api:8080/ask"

# Store chat history in memory (per session, not per user)
chat_history: List[dict] = []

@app.get("/", response_class=HTMLResponse)
def form_get():
    chat_html = "".join([
        f'<div><b>User:</b> {msg["user"]}<br><b>Agent:</b> {msg["agent"]}</div>'
        for msg in chat_history
    ])
    return f"""
    <html>
        <head><title>Travel Planning Chatbot</title></head>
        <body>
            <h2>Travel Planning Chatbot</h2>
            <form method="post">
                <input type="text" name="query" style="width:300px" placeholder="Enter your query" required>
                <button type="submit">Submit</button>
            </form>
            <div id="chat_history">{chat_html}</div>
            <div id="response"></div>
        </body>
    </html>
    """

@app.post("/", response_class=HTMLResponse)
def form_post(query: str = Form(...)):
    global chat_history
    response_text = ""
    # Prepare history for API: last 4 exchanges
    history_for_api = [
        {"user": msg["user"], "agent": msg["agent"]}
        for msg in chat_history[-4:]
    ]
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.post(API_URL, json={"query": query, "chat_history": history_for_api})
            if r.status_code == 200:
                response_text = r.json().get("response", "No response")
            else:
                response_text = f"Error: {r.text}"
    except Exception as e:
        response_text = f"Exception: {e}"
    # Update chat history (cap to last 4)
    chat_history.append({"user": query, "agent": response_text})
    chat_history = chat_history[-4:]
    chat_html = "".join([
        f'<div><b>User:</b> {msg["user"]}<br><b>Agent:</b> {msg["agent"]}</div>'
        # get history for the previous 4 messages except the last assistant response
        for msg in chat_history[-5:-1]
    ])
    return f"""
    <html>
        <head><title>Agent UI</title></head>
        <body>
            <h2>Ask the Agent</h2>
            <form method="post">
                <input type="text" name="query" style="width:300px" value="{query}" required>
                <button type="submit">Ask</button>
            </form>
            <div id="chat_history">{chat_html}</div>
            <div id="response"><b>Response:</b> {response_text}</div>
        </body>
    </html>
    """