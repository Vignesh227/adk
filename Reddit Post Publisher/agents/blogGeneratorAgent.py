from google.adk.agents import LlmAgent


# --- 1. Blog Generation Agent ---
blog_generator_agent = LlmAgent(
    name="BlogGeneratorAgent",
    model="gemini-2.0-flash",
    # instruction="""
    # Given {user_query}, generate a suitable blog post with a catchy title and a detailed body.
    # (Note: Dont ask or generate any unwanted texts apart from the blog content).
    # """,
    instruction="""
    You are a blog writer. Based on the user's current message (the prompt they just sent), generate a blog post with:
    - A catchy title on the first line prefixed "Title: "
    - Then a blank line and a detailed body.

    (Note: Dont ask or generate any unwanted texts apart from the blog content).
    """,
    output_key="blog_content"   
)