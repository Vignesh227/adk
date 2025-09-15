# Import the Sub Agents
from agents.blogGeneratorAgent import blog_generator_agent
from agents.blogRefinerAgent import blog_refiner_agent
from agents.imageGoogleSearchAgent import image_google_search_agent
from agents.blogPublisherAgent import blog_publisher_agent

# Others
from google.adk.agents import SequentialAgent


# --- 5. Wrap them into a Sequential Pipeline ---
sequential_pipeline_agent = SequentialAgent(
    name="BlogPipeline",
    sub_agents=[
        blog_generator_agent,
        blog_refiner_agent,
        image_google_search_agent,
        blog_publisher_agent
    ]
)

# sequential_pipeline_tool = AgentTool(agent=sequential_pipeline_agent)