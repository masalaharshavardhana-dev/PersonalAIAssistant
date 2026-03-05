import requests
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
load_dotenv()


@tool
def irctc_tool(fromStationCode: str, toStationCode: str, dateOfJourney: str):
    """Get train deatils between two stations"""
    url = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"

    querystring = {
        "fromStationCode": fromStationCode,
        "toStationCode": toStationCode,
        "dateOfJourney": dateOfJourney
    }

    headers = {
        "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
        "x-rapidapi-host": "irctc1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()