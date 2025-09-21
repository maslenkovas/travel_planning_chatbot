
import sys
import os, time
import asyncio
import logging
from fastapi import FastAPI, Request
from pydantic import BaseModel
import chromadb
from dotenv import load_dotenv
load_dotenv()

CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.vector_search.document_processor import DocumentProcessor
from src.vector_search.vector_store import VectorStore
import traceback

from dotenv import load_dotenv
load_dotenv()

from langchain_mistralai import ChatMistralAI
from src.agent.prompts import Prompts
from src.agent.travel_agent import TravelChatbotGraph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logger = logging.getLogger("agent")

# Setup FastAPI
app = FastAPI()

# Request schema
class QueryRequest(BaseModel):
    query: str
    chat_history: list = []

# Agent setup with Mistral LLM and TravelChatbotGraph
api_key = os.environ["MISTRAL_API_KEY"]
llm = ChatMistralAI(
    model="mistral-small",
    temperature=0.5,
    max_retries=2,
    mistral_api_key=api_key,
)
prompts = Prompts()
graph = TravelChatbotGraph(llm=llm, prompts=prompts)

@app.on_event("startup")
async def load_book_to_chromadb():
    # Wait for ChromaDB to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            client = chromadb.HttpClient(host="chromadb", port=CHROMA_PORT)
            client.get_version()
            break
        except Exception:
            logger.info("Retrying to connect to chromadb")
            time.sleep(1)
    else:
        raise RuntimeError("ChromaDB not available after waiting")
    
    vector_store = VectorStore(collection_name="twain_book", chroma_host="chromadb", chroma_port=CHROMA_PORT)
    if vector_store.collection.count() == 0:
        print("Loading book into ChromaDB...")
        processor = DocumentProcessor()
        book_path = "src/data/book.txt"
        chunks = processor.load_and_process_document(book_path)
        vector_store.add_documents(chunks)
        print("Book loaded into ChromaDB.")
    else:
        print("ChromaDB already has data, skipping book load.")
    

@app.post("/ask")
async def ask_agent(request: QueryRequest):
    init_state = {
        "query": request.query,
        "intent": "",
        "context": "",
        "locations": [],
        "weather_info": "",
        "final_answer": "",
        "chat_history": request.chat_history,
    }
    logger.info(f"Received query: {request.query}")
    logger.info(f"Chat history: {request.chat_history}")
    try:
        result = await graph.graph.ainvoke(init_state)
        logger.info(f"Agent result: {result}")
        return {"response": result.get("final_answer", "")}
    except Exception as e:
        logger.error(f"Agent error: {e}\n{traceback.format_exc()}")
        return {"response": f"Error: {e}"}