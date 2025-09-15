# Import the GoogleSearch Tool
from agents.tools.imageGoogleSearchTool import image_google_search_tool

# Others
from google.adk.agents import LlmAgent


# --- 3. Image Search Agent ---
image_google_search_agent = LlmAgent(
    name="ImageGoogleSearchAgent",
    model="gemini-2.0-flash",
    instruction="""
    Always call `image_google_search_tool` with the exact user's input to fetch relevant images as per the user query.
    Do not alter or shorten the query. Example: image_google_search_function(user's input, num=1).
    Search for a single copyright-free images related to user's input.
    Return the fetched image URL alone.
    """,
    tools=[image_google_search_tool],
    output_key="image_url"
)