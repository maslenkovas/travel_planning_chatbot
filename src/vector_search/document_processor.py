from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " "]
        )
    
    def load_and_process_document(self, file_path):
        """Load document and split into semantic chunks"""
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Clean text and split into chapters/sections
        chunks = self.text_splitter.split_text(text)
        
        # Add metadata (chapter, page numbers if available)
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                'text': chunk,
                'chunk_id': i,
                'metadata': self._extract_metadata(chunk)
            })
        
        return processed_chunks
    
    def _extract_metadata(self, chunk):
        """Extract location names, chapter info, etc."""
        # Implementation for extracting locations, chapters, etc.
        pass