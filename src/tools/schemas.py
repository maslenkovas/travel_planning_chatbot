from pydantic import BaseModel, Field

class WeatherToolInput(BaseModel):
    locations: list[str] = Field(..., description="List of locations to get weather information for.")

class RagToolInput(BaseModel):
    query: str = Field(..., description="User query to search in the book passages.")