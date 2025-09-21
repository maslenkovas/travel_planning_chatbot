from langchain_core.documents import Document
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
import os, asyncio
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

# Import custom modules
from src.tools.schemas import WeatherToolInput, RagToolInput
from src.tools.wether_api import WeatherAPIClient
from src.vector_search.vector_store import VectorStore
from src.utils.text_processing import format_retrieved_chunks

# Load environment variables for ChromaDB configuration
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

# load other config variables
from src.config import n_rag_results

class WeatherTool(BaseTool):
    name: str = "weather_tool"
    description: str = """Useful for when you need to get current weather information for a specific location.
    The input should be a list of locations (list[str]). The output will be a string with the weather information.
    Th output consists of the current weather conditions, temperature, feels like temperature, humidity, and wind speed for each location.
    Example locations: "Paris", "New York", "Tokyo", "London", "Berlin"
    """

    def _run(self, locations: list[str]) -> str:
        # Accept either a list or a dict with 'locations'
        if not locations:
            return []
        
        weather_client = WeatherAPIClient(api_key=WEATHERAPI_KEY)
        results_list = []
        for loc in locations:
            results = weather_client.get_current_weather(location=loc)  
            parsed_result = weather_client.parse_results(results)
            if parsed_result:
                results_list.append(parsed_result)
        
        return results_list

    async def _arun(self, locations) -> str:
        # Accept either a list or a dict with 'locations'
        if not locations:
            return []
        weather_client = WeatherAPIClient(api_key=os.getenv("WEATHERAPI_KEY"))
        # get weather all locations concurrently
        tasks = [weather_client.aget_current_weather(loc) for loc in locations]
        results = await asyncio.gather(*tasks)
        results_list = []
        for result in results:
            parsed_result = weather_client.parse_results(result)
            if parsed_result:
                results_list.append(parsed_result)
            
        return results_list
        


class RagTool(BaseTool):
    name: str="rag_tool"
    description: str="""Useful for when you need to answer questions about Mark Twain's book "The Innocents Abroad".
    The input should be a question (str). The output will be a string with the text chunks retrieved usinf cosine similarity from the book.
    """
    args_schema: Optional[ArgsSchema] = RagToolInput

    def _run(self, query: str) -> str:
        vector_store = VectorStore(collection_name=CHROMA_COLLECTION_NAME, chroma_host=CHROMA_HOST, chroma_port=CHROMA_PORT)
        retrieved_chunks = vector_store.search(query, n_results=n_rag_results)
        formatted_context = format_retrieved_chunks(retrieved_chunks)
        return formatted_context
    
    async def _arun(self, query: str) -> str:
        raise NotImplementedError("RAG tool does not support async")