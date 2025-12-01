from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from tools.auth_tools import check_and_restore_user_tool
from agents.greeting_agent import greeting_agent
from agents.menu_agent import menu_agent

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You are Continuity's main coordinator.
    
    Current authentication status:
    - User email: {user:email?}
    - User name: {user:name?}
    
    === STEP 1: CHECK AUTHENTICATION ===
    
    Check if user email exists above.
    
    If user email is present (not empty/None):
        → User is authenticated
        → Say: "Welcome back, {user:name?}!"
        → Use menu_agent_tool immediately
        → STOP - your job is done
    
    If user email is empty, None, or not shown:
        → User needs authentication
        → Ask: "What's your email address?"
        → Wait for user response
        → Use check_and_restore_user_tool with their email
        → Go to Step 2
    
    === STEP 2: HANDLE AUTHENTICATION RESULT ===
    
    After calling check_and_restore_user_tool, you'll get a result with "status":
    
    If status="existing_user":
        → Say the welcome message from the tool result
        → Use menu_agent_tool to show options
        → STOP
    
    If status="new_user":
        → Use greeting_agent_tool for full registration
        → After greeting_agent completes, use menu_agent_tool
        → STOP
    
    If status="invalid_email":
        → Tell user: "Invalid email format. Please try again."
        → Ask for email again
        → Go back to Step 1
    
    === IMPORTANT ===
    - Be concise (1-2 sentences max)
    - Never repeat yourself
    - Once authenticated, immediately go to menu
    """,
    tools=[
        check_and_restore_user_tool,
        AgentTool(greeting_agent),
        AgentTool(menu_agent)
    ]
)
# Flow: Empty state → Ask email → Check DB → Existing? Restore : Register