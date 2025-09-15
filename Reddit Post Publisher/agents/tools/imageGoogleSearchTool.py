import os
import requests
from google.adk.tools import FunctionTool

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")



def image_google_search_function(query: str, num: int = 1):

    print("\n[Google Search Tool Called] Query:", query)

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "searchType": "image",
        "fileType": "jpg,png",
        "imgType": "photo",
        "num": num,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    links = [item["link"] for item in data.get("items", [])]

    print("[Google Search Results]:", links)

    return links[0] if links else None

image_google_search_tool = FunctionTool(image_google_search_function)
