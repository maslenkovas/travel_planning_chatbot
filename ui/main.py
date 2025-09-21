from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import httpx

app = FastAPI()

API_URL = "http://agent-api:8080/ask"

@app.get("/", response_class=HTMLResponse)
def form_get():
    return """
    <html>
        <head><title>Travel Planning Chatbot</title></head>
        <body>
            <h2>Travel Planning Chatbot</h2>
            <form method="post">
                <input type="text" name="query" style="width:300px" placeholder="Enter your query" required>
                <button type="submit">Submit</button>
            </form>
            <div id="response">{response}</div>
        </body>
    </html>
    """.format(response="")

@app.post("/", response_class=HTMLResponse)
def form_post(query: str = Form(...)):
    response_text = ""
    try:
        with httpx.Client() as client:
            r = client.post(API_URL, json={"query": query})
            if r.status_code == 200:
                response_text = r.json().get("response", "No response")
            else:
                response_text = f"Error: {r.text}"
    except Exception as e:
        response_text = f"Exception: {e}"
    return """
    <html>
        <head><title>Agent UI</title></head>
        <body>
            <h2>Ask the Agent</h2>
            <form method="post">
                <input type="text" name="query" style="width:300px" value="{query}" required>
                <button type="submit">Ask</button>
            </form>
            <div id="response"><b>Response:</b> {response}</div>
        </body>
    </html>
    """.format(query=query, response=response_text)
