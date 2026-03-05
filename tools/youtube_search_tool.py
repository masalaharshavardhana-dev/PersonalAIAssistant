from googleapiclient.discovery import build
import os
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

@tool
def search_youtube_videos(query, max_results=5):
    """Tool for searching videos on YouTube"""
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=max_results,
        order="title"
    )
    response = request.execute()

    videos = []

    for item in response["items"]:
        video_data = {
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "video_url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "published_at": item["snippet"]["publishedAt"]
        }
        videos.append(video_data)

    return videos