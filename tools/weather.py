import json
import requests
import os
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()

@tool
def get_weather(location: str):
    """Get the current weather for a given location"""
    api_key = os.getenv('WEATHER_API_KEY')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={api_key}"

    response = requests.get(url)
    data = response.json()
    if data.get("cod") == 200:
        
        return json.dumps({
            "location": location, 
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        })
    else:
        return json.dumps({"error": "Oops! Something went wrong."})  
