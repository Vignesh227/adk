# from google.adk.agents import LlmAgent
# from google.adk.tools import FunctionTool
# from dotenv import load_dotenv
# import requests
# import os
# import praw

# # --- Load environment variables ---
# load_dotenv()

# # --- 1. Greeting and Query Collection Agent ---
# # greeter_agent = LlmAgent(
# #     name="GreeterAgent",
# #     model="gemini-2.0-flash",
# #     instruction="""
# # You are a friendly blog assistant. 
# # As soon as the chat starts, greet the user and say:

# # "Hi there! Tell me on what topic I should generate a blog."

# # Wait for the user's response before taking further action.
# # """,
# #     tools=[],  # call BlogGeneratorAgent next
# #     output_key="user_query"
# # )


# # --- 2. Blog Generation Agent ---
# blog_content_agent = LlmAgent(
#     name="BlogGeneratorAgent",
#     model="gemini-2.0-flash",
#     instruction="""
# Given {user_query}, generate a suitable blog post: include a catchy title and a detailed body.
# Once done, call MarkdownRefinerAgent.
# """,
#     tools=[],  # Will add MarkdownRefinerAgent as a tool later
#     output_key="blog_content"
# )

# # --- 3. Content Refinement Agent ---
# refinement_agent = LlmAgent(
#     name="MarkdownRefinerAgent",
#     model="gemini-2.0-flash",
#     instruction="""
# Read {blog_content} and rewrite it in markdown styled for Reddit blogs 
# (headers, bold/italic, code blocks as needed). 
# Once done, call ImageSearchAgent.
# """,
#     tools=[],  # Will add ImageSearchAgent as a tool later
#     output_key="refined_content"
# )

# # --- 4. Image Search Agent ---
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# GOOGLE_CX = os.getenv("GOOGLE_CX")  # Programmable Search Engine ID

# def google_search(query: str, num: int = 3):
#     url = "https://www.googleapis.com/customsearch/v1"
#     params = {
#         "key": GOOGLE_API_KEY,
#         "cx": GOOGLE_CX,
#         "q": query,
#         "searchType": "image",
#         "num": num,
#     }
#     r = requests.get(url, params=params, timeout=10)
#     r.raise_for_status()
#     data = r.json()
#     return [item["link"] for item in data.get("items", [])]

# google_search_tool = FunctionTool(google_search)

# image_search_agent = LlmAgent(
#     name="ImageSearchAgent",
#     model="gemini-2.0-flash",
#     instruction="""
# Given the blog topic in {user_query}, search for 2-3 relevant, copyright-free
# images using the google_search function as tool. 
# Always call google_search — do not fabricate links.
# Return the image links in markdown format (e.g., ![alt](url)).
# Once done, call RedditPosterAgent.
# """,
#     tools=[google_search_tool],  # tool for fetching images
#     output_key="image_markdown"
# )

# # --- 5. Reddit Posting Agent ---
# def publish_to_reddit(title: str, body: str, image_markdown: str = "") -> dict:
#     reddit = praw.Reddit(
#         client_id=os.environ["REDDIT_CLIENT_ID"],
#         client_secret=os.environ["REDDIT_CLIENT_SECRET"],
#         refresh_token=os.environ["REDDIT_REFRESH_TOKEN"],
#         user_agent=os.environ["REDDIT_USER_AGENT"]
#     )
#     subreddit = f"u_{os.environ['REDDIT_USERNAME']}"
#     sub = reddit.subreddit(subreddit)
#     post_body = body
#     if image_markdown:
#         post_body += "\n\n" + image_markdown
#     submission = sub.submit(title=title, selftext=post_body)
#     return {"post_url": f"https://reddit.com{submission.permalink}"}

# reddit_publish_tool = FunctionTool(publish_to_reddit)

# reddit_post_agent = LlmAgent(
#     name="RedditPosterAgent",
#     model="gemini-2.0-flash",
#     instruction="""
# Take {refined_content} and {image_markdown}. Parse the first header from {refined_content} as the title, 
# remaining as body. Call the publish_to_reddit tool to publish to Reddit and return the post URL.
# """,
#     tools=[reddit_publish_tool],
#     output_key="reddit_post_url"
# )

# from google.adk.tools.agent_tool import AgentTool

# # Wrap an LlmAgent as a callable FunctionTool with AgentTool
# # greeter_agent_tool = AgentTool(agent=greeter_agent)
# blog_content_tool = AgentTool(agent=blog_content_agent)
# refinement_tool = AgentTool(agent=refinement_agent)
# image_search_tool_agent = AgentTool(agent=image_search_agent)
# reddit_post_tool = AgentTool(agent=reddit_post_agent)

# # greeter_agent.tools = [blog_content_tool]
# blog_content_agent.tools = [refinement_tool]
# refinement_agent.tools = [image_search_tool_agent]
# image_search_agent.tools.append(reddit_post_tool)



# # --- 7. Root agent: only calls GreeterAgent ---
# root_agent = LlmAgent(
#     name="RootRedditBlogAgent",
#     model="gemini-2.0-flash",
#     instruction="""
#     This is a Reddit Post Content Generator and automatic publisher application. 

#     - If the user asks to write a blog, then:

#         - Immediately call the blog_content_tool with user query.
    
#     - If the user asks something apart from the context, then:

#         - Politely let the user know that the user request is out of scope.
#         - Then again ask, if the user wishes to create/generate any blogs.
#     """,
#     tools=[blog_content_tool],
#     output_key="user_query"
# )

        
#         # - Get the user query, and reply, 'your query has been received, and sent for content generation'.
#         # - Then call the `blog_content_tool` to generate blog content.

# # ---- USAGE ----
# # from google.adk.engine import run_agent_sync
# # result = run_agent_sync(root_agent)
# # print(result["final_result"])




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

def google_search(query: str, num: int = 3):
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

    return links

google_search_tool = FunctionTool(google_search)

image_search_agent = LlmAgent(
    name="ImageSearchAgent",
    model="gemini-2.0-flash",
    instruction="""
    Always call google_search with the exact {user_query}.
    Do not alter or shorten the query. Example: google_search({user_query}, num=3).
    search for 2 or 3 copyright-free images related to {user_query}.
    Return them in markdown format (![alt](url)).
    """,
    tools=[google_search_tool],
    output_key="image_markdown"
)

# --- 4. Reddit Posting Agent ---
def publish_to_reddit(title: str, body: str, image_markdown: str = "") -> dict:
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        refresh_token=os.environ["REDDIT_REFRESH_TOKEN"],
        user_agent=os.environ["REDDIT_USER_AGENT"]
    )
    subreddit = f"u_{os.environ['REDDIT_USERNAME']}"
    sub = reddit.subreddit(subreddit)
    post_body = body
    if image_markdown:
        post_body += "\n\n" + image_markdown
    submission = sub.submit(title=title, selftext=post_body)
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
    You are a blog publishing assistant in Reddit. 

    - If the user gives a topic and asks to write a blog, then reply:
    "Your query has been received, starting blog generation..."
    Then call the BlogPipeline tool. Then save the user input as `user_query`.

    - If the user asks something unrelated, politely decline
    and ask if they want to generate a blog instead.

    """,
    tools=[pipeline_tool],
    output_key="user_query"
)

# ---- USAGE ----
# from google.adk.engine import run_agent_sync
# result = run_agent_sync(root_agent)
# print(result["final_result"])
