from google.adk.agents import LlmAgent, SequentialAgent
# from google.adk.tools import google_search
from dotenv import load_dotenv  
import requests
import os

# Load env variables
load_dotenv()


# --- 1. Greeting and Query Collection Agent ---
greeter_agent = LlmAgent(
    name="GreeterAgent",
    model="gemini-2.0-flash",
    instruction="Greet the user and ask for their blog topic or query.",
    output_key="user_query"
)

# --- 2. Blog Generation Agent ---
blog_content_agent = LlmAgent(
    name="BlogGeneratorAgent",
    model="gemini-2.0-flash",
    instruction="Given {user_query}, generate a suitable blog post: include a catchy title and a detailed body.",
    output_key="blog_content"
)

# --- 3. Content Refinement Agent ---
refinement_agent = LlmAgent(
    name="MarkdownRefinerAgent",
    model="gemini-2.0-flash",
    instruction="Read {blog_content} and rewrite it in markdown styled for Reddit blogs (headers, bold/italic, code blocks as needed).",
    output_key="refined_content"
)


# --- 4. Image Search Agent ---

from google.adk.tools import FunctionTool

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")  # Programmable Search Engine ID

def google_search(query: str, num: int = 3):
    """
    Google Image Search via Custom Search API.
    Returns direct image links (scoped to your CX, e.g. Unsplash/Pexels/Pixabay).
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "searchType": "image",   # 👈 ensures we get images, not web pages
        "num": num,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    # Just return the image URLs
    return [item["link"] for item in data.get("items", [])]

# Wrap your Python function as a tool
google_search_tool = FunctionTool(google_search)

image_search_agent = LlmAgent(
    name="ImageSearchAgent",
    model="gemini-2.0-flash",
    instruction="""
    Given the blog topic in {user_query}, search for 2-3 relevant, copyright-free
    images using the google_search function as tool. 
    ALWAYS call google_search — do not fabricate links.
    Only return the image links in markdown format (e.g., ![alt](url)).
    """,
    tools=[google_search_tool],
    output_key="image_markdown",
)


# --- 5. Reddit Posting Agent  ---
import praw

def publish_to_reddit(title: str, body: str, image_markdown: str = "") -> dict:
    """
    Publishes a post to the user's profile subreddit (u_username).
    No flair required, safe for testing and automation.
    """

    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        refresh_token=os.environ["REDDIT_REFRESH_TOKEN"],
        user_agent=os.environ["REDDIT_USER_AGENT"]
    )

    # Profile subreddit (no flair needed)
    subreddit = f"u_{os.environ['REDDIT_USERNAME']}"
    sub = reddit.subreddit(subreddit)

    # Build post body
    post_body = body
    if image_markdown:
        post_body += "\n\n" + image_markdown

    # Submit directly (no flair issues here)
    submission = sub.submit(
        title=title,
        selftext=post_body
    )

    return {"post_url": f"https://reddit.com{submission.permalink}"}


# --- ADK integration ---
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

reddit_publish_tool = FunctionTool(publish_to_reddit)

reddit_post_agent = LlmAgent(
    name="RedditPosterAgent",
    model="gemini-2.0-flash",
    instruction=(
        "Take {refined_content} and {image_markdown}. Parse the first header from {refined_content} as the title, "
        "remaining as body. Call the publish_to_reddit tool to publish to the subreddit "
        "(subreddit name from env or user input), and return the resulting post_url."
    ),
    tools=[reddit_publish_tool],
    output_key="reddit_post_url"
)


# --- 6. Compose the Sequential Multi-Agent Pipeline ---
root_agent = SequentialAgent(
    name="Reddit_Post_Publisher",
    sub_agents=[
        greeter_agent,
        blog_content_agent,
        refinement_agent,
        image_search_agent,
        reddit_post_agent
    ]
)

# ---- USAGE: ----
# (In your actual runner script or notebook)
# from google.adk.engine import run_agent_sync
# result = run_agent_sync(blog_pipeline)
# print(result)
