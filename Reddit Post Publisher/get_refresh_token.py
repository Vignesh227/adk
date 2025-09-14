import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()  # load .env file

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDDIT_REDIRECT_URI", "http://localhost:8080")
AUTH_CODE = os.getenv("REDDIT_AUTH_CODE")  # paste the auth code you got from Reddit here

auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
print("aith : ", auth)
data = {
    "grant_type": "authorization_code",
    "code": AUTH_CODE,
    "redirect_uri": REDIRECT_URI
}

response = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data)
token_info = response.json()
print(token_info)
