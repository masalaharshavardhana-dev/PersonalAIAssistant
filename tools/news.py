from langchain_core.tools import tool
import requests
import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
load_dotenv()

api_key = os.getenv('NEWS_API_KEY')

@tool
def get_latest_news(topic: str):
    """Get the latest news articles for a given topic"""
    newsapi = NewsApiClient(api_key=api_key)

    try:
        all_articles = newsapi.get_everything(
            q=topic,
            sources='bbc-news,the-verge',
            domains='bbc.co.uk,techcrunch.com',
            language='en',
            sort_by='relevancy',
            page=1
        )

        if all_articles["status"] == "ok":
            return all_articles["articles"][:3]
        else:
            return "Error fetching news"

    except Exception as e:
        return "Something went wrong: " + str(e)