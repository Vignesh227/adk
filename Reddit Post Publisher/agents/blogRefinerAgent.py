from google.adk.agents import LlmAgent


# --- 2. Content Refinement Agent ---
blog_refiner_agent = LlmAgent(
    name="MarkdownBlogRefinerAgent",
    model="gemini-2.0-flash",
    instruction="""
    Take {blog_content} and rewrite it in Markdown styled for Reddit blogs
    (headers, bold/italic, code blocks as needed).
    """,
    output_key="refined_content"
)