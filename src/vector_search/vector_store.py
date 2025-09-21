import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load environment variables for ChromaDB configuration
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "twain_book")
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

# Load configuration variables
from src.config import embedding_model_name

class VectorStore:
    def __init__(self, collection_name=None, chroma_host=None, chroma_port=None, use_docker=True):
        # Get configuration from environment variables or use defaults
        self.collection_name = collection_name
        self.chroma_host = chroma_host 
        self.chroma_port = chroma_port
        
        if use_docker:
            # Use HTTP client to connect to Dockerized ChromaDB
            self.client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port
            )
        else:
            # Fallback to persistent client for local development
            chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            self.client = chromadb.PersistentClient(path=chroma_db_path)
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = SentenceTransformer(embedding_model_name)
    
    def add_documents(self, chunks: List[Dict[str, Any]]):
        """Add book chunks to vector store"""
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.encode(texts).tolist()
        
        ids = [f"chunk_{chunk['chunk_id']}" for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for relevant passages"""
        query_embedding = self.embedder.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        return self._format_results(results)
    
    def _format_results(self, results):
        """Format ChromaDB results"""
        formatted = []
        for i in range(len(results['documents'][0])):
            formatted.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        return formatted