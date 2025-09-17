
import praw
import requests
import os

from google.adk.tools import FunctionTool


def blog_publisher_function(title: str, body: str, image_urls: str) -> dict:
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        refresh_token=os.environ["REDDIT_REFRESH_TOKEN"],
        user_agent=os.environ["REDDIT_USER_AGENT"]
    )

    # Post on my own subreddit
    subreddit = f"u_{os.environ['REDDIT_USERNAME']}"
    sub = reddit.subreddit(subreddit)

    if not image_urls:
        # IF no image is found, then post, text-only post
        submission = sub.submit(title=title, selftext=body)
        return {"post_url": f"https://reddit.com{submission.permalink}"}

    
    img_url = image_urls
    response = requests.get(img_url, stream=True, timeout=10)
    response.raise_for_status()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_dir, "temp_image.jpg")

    with open(img_path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    # submit as image post
    submission = sub.submit_image(title=title, image_path=img_path)

    # If body exits, then add body as a comment
    if body:
        submission.reply(body)

    # delete the image
    os.remove(img_path)

    return {"post_url": f"https://reddit.com{submission.permalink}"}


blog_publisher_tool = FunctionTool(blog_publisher_function)
