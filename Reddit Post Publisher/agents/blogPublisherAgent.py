# Import the BlogPublisher Tool
from agents.tools.blogPublisherTool import blog_publisher_tool

# Others
from google.adk.agents import LlmAgent

# --- 4. Reddit Posting Agent ---
blog_publisher_agent = LlmAgent(
    name="BlogPublisherAgent",
    model="gemini-2.0-flash",
    instruction="""
    Use {refined_content} and {image_url}.

    Extract the first header from {refined_content} as the title, then image, then put the body as the first comment.

    MUST IMMEDIATELY call the `blog_publisher_tool` toolto post the blog.

    Pass the parameters 'title', 'body' and 'image_url' for the `blog_publisher_tool` correctly.
    """,
    tools=[blog_publisher_tool],
    output_key="reddit_post_url"
)