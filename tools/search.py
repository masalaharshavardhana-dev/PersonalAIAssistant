from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
load_dotenv()
@tool
def tavily_search(query: str):
    """Search for information on the web using Tavily if you dont have the information"""
    api_key = os.getenv("TAVILY_API_KEY")
    tavily_search = TavilySearch(max_results=5, tavily_api_key = api_key)
    return tavily_search.invoke({"query": query})