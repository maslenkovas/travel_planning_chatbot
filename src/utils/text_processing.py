def format_retrieved_chunks(results: list[dict]) -> str:
    """Formats the retrieved chunks into a single string for being passed into the prompt for llm as context."""
    retrieved_chunks_str = ""
    for i, result in enumerate(results):
        added_string = f"Passage {i+1}:\n{result.get('text', '')}\n\n"
        retrieved_chunks_str += added_string
    return retrieved_chunks_str