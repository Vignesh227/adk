
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
import os, requests, praw
from dotenv import load_dotenv

load_dotenv()

# --- 1. Blog Generation Agent ---
blog_content_agent = LlmAgent(
    name="BlogGeneratorAgent",
    model="gemini-2.0-flash",
    instruction="""
    Given {user_query}, generate a suitable blog post with a catchy title and a detailed body.
    (Note: Dont ask or generate any unwanted texts apart from the blog content).
    """,
    output_key="blog_content"   
)

# --- 2. Content Refinement Agent ---
refinement_agent = LlmAgent(
    name="MarkdownRefinerAgent",
    model="gemini-2.0-flash",
    instruction="""
    Take {blog_content} and rewrite it in Markdown styled for Reddit blogs
    (headers, bold/italic, code blocks as needed).
    """,
    output_key="refined_content"
)

# --- 3. Image Search Agent ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

def google_search(query: str, num: int = 1):
    print("\n[Google Search Tool Called] Query:", query)
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "searchType": "image",
        "num": num,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    links = [item["link"] for item in data.get("items", [])]
    print("[Google Search Results]:", links)

    return links[0] if links else None

google_search_tool = FunctionTool(google_search)

image_search_agent = LlmAgent(
    name="ImageSearchAgent",
    model="gemini-2.0-flash",
    instruction="""
    Always call google_search with the exact {user_query}.
    Do not alter or shorten the query. Example: google_search({user_query}, num=3).
    Search for a single copyright-free images related to {user_query}.
    Return the image URL alone.
    """,
    tools=[google_search_tool],
    output_key="image_markdown"
)

# --- 4. Reddit Posting Agent ---
def publish_to_reddit(title: str, body: str, image_urls: str) -> dict:
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        refresh_token=os.environ["REDDIT_REFRESH_TOKEN"],
        user_agent=os.environ["REDDIT_USER_AGENT"]
    )
    subreddit = f"u_{os.environ['REDDIT_USERNAME']}"
    sub = reddit.subreddit(subreddit)

    if not image_urls:
        # fallback: text-only post
        submission = sub.submit(title=title, selftext=body)
        return {"post_url": f"https://reddit.com{submission.permalink}"}

    # download first image
    # img_url = image_urls[0]
    img_url = image_urls
    img_data = requests.get(img_url, timeout=10).content
    img_path = "temp_image.jpg"
    with open(img_path, "wb") as f:
        f.write(img_data)

    # submit as image post
    submission = sub.submit_image(title=title, image_path=img_path)

    # optionally add body as a comment
    if body:
        submission.reply(body)

    os.remove(img_path)  # cleanup

    return {"post_url": f"https://reddit.com{submission.permalink}"}

reddit_publish_tool = FunctionTool(publish_to_reddit)

reddit_post_agent = LlmAgent(
    name="RedditPosterAgent",
    model="gemini-2.0-flash",
    instruction="""
    Use {refined_content} and {image_markdown}.
    Extract the first header from {refined_content} as the title, rest as body.
    Then call publish_to_reddit.
    """,
    tools=[reddit_publish_tool],
    output_key="reddit_post_url"
)

# --- 5. Wrap them into a Sequential Pipeline ---
pipeline = SequentialAgent(
    name="BlogPipeline",
    sub_agents=[
        blog_content_agent,
        refinement_agent,
        image_search_agent,
        reddit_post_agent
    ]
)

pipeline_tool = AgentTool(agent=pipeline)

# --- 6. Root Agent with conditional logic ---
root_agent = LlmAgent(
    name="RootRedditBlogAgent",
    model="gemini-2.0-flash",
    instruction="""
    You are a automatic blog generating & publishing assistant in Reddit. 

    1. If the user asks to write a blog on a topic, then: 
        - IMMEDIATELY call the `pipeline` sub agent, and save the User question as `user_query`.
        - Then reply "Your query has been received, starting blog generation..."
        - Then save the user question as `user_query`.
    

    2. If the user asks something unrelated to blog/content generation, politely decline
    and ask if they want to generate a blog instead.

    """,
    # tools=[pipeline_tool],
    sub_agents=[pipeline],
    output_key="user_query"
)

# - IMMEDIATELY call the BlogPipeline `pipeline_tool` tool. 
# ---- USAGE ----
# from google.adk.engine import run_agent_sync
# result = run_agent_sync(root_agent)
# print(result["final_result"])
