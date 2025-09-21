from dotenv import load_dotenv
load_dotenv()

import os, json, requests, httpx


class WeatherAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1/current.json"

    def get_current_weather(self, location: str) -> dict:
        params = {
            "q": location,
            "key": self.api_key,
            "aqi": "no"
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Could not retrieve weather data for {location}. Status code: {response.status_code}"}
    
    async def aget_current_weather(self, location: str) -> dict:
    
        params = {
            "q": location,
            "key": self.api_key,
            "aqi": "no"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Could not retrieve weather data for {location}. Status code: {response.status_code}"}
    
    def parse_results(self, data: dict) -> str:
        if "error" in data:
            return None
        
        location = data.get("location", {})
        current = data.get("current", {})
        
        location_name = location.get("name", "Unknown location")
        region = location.get("region", "")
        country = location.get("country", "")
        temp_c = current.get("temp_c", "N/A")
        condition = current.get("condition", {}).get("text", "N/A")
        condition_icon = current.get("condition", {}).get("icon", None)
        humidity = current.get("humidity", "N/A")
        wind_kph = current.get("wind_kph", "N/A")
        feelslike_c = current.get("feelslike_c", "N/A")
        
        return (f"Current weather in {location_name}, {region}, {country}:\n"
                f"Temperature: {temp_c}°C\n"
                f"Feels like: {feelslike_c}°C\n"
                f"Condition: {condition}\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind_kph} kph")

