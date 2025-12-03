from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from typing import Dict, Any, List
from tools.video_tools import list_user_videos_tool, select_video_tool, create_new_video_tool

menu_agent = LlmAgent(
    name="menu_agent",
    model="gemini-2.0-flash",
    instruction="""
    You show the user's videos and ask what they want next.
    
    User info:
    - User: {user:verified_user_id?}
    
    === YOUR JOB ===
    
    STEP 1: Get Videos
    → Use list_user_videos_tool
    
    STEP 2: Format Display

    → Display results clearly:
        - If no videos: "You don't have any videos yet. Let's create one!"
        - If has videos: Show list with status
    
    Step 3: Ask what user wants to do
    → Options:
        a) "Continue working on [video title]"
        b) "Create a new video"
        c) "View limits"
        d) "About Continuity"
    
    Step 4: Handle user choice
    → Get user choice 
    → if user selects continue working on [video title], use select_video_tool tool to update state with user choice
    → if user selects create a new video, use create_new_video_tool tool to create new video on db
    → Escalate back to root_agent with choice
   
        → STOP - video_creation_agent will take over

    === FORMAT ===
    Keep messages short and friendly.
    Format video list clearly:
    
    Example:
    "Your videos:
    1. Dragon Adventure (in progress)
    2. Robot Story (completed)
    
    What would you like to do?
     • Continue a video
     • Create new video"
     • View limits
     • About Continuity"
    """,
    tools=[
        list_user_videos_tool,
        select_video_tool,
        create_new_video_tool
    ]
)