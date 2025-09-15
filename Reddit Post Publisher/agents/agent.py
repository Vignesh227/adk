# Import the Sequential Agent
from agents.sequentialPipeline import sequential_pipeline_agent

# Import the Tools
from agents.tools.imageGoogleSearchTool import image_google_search_tool
from agents.tools.blogPublisherTool import blog_publisher_tool

# Import the Agents
from agents.blogGeneratorAgent import blog_generator_agent
from agents.blogRefinerAgent import blog_refiner_agent
from agents.imageGoogleSearchAgent import image_google_search_agent
from agents.blogPublisherAgent import blog_publisher_agent

# Others
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

load_dotenv()


# --- Root Agent ---
root_agent = LlmAgent(
    name="RootRedditBlogAgent",
    model="gemini-2.0-flash",
    instruction="""
    You are a automatic blog generating & publishing assistant in Reddit. Make decision based on the bewlo conditions:

    1. If the user asks to write a blog, then: 
        - MUST IMMEDIATELY call the `sequential_pipeline_agent` sub agent with the user's input.    

    2. If the user asks something unrelated to blog/content generation, politely decline
    and ask if they want to generate a blog instead.

    """,
    # tools=[sequential_pipeline_tool],
    sub_agents=[sequential_pipeline_agent],
    output_key="user_query"
)
