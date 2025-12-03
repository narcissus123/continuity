from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from tools.auth_tools import check_and_restore_user_tool
from agents.greeting_agent import greeting_agent
from agents.menu_agent import menu_agent
from database.session_helpers import persist_state_checkpoint

video_workflow_agent = LlmAgent(
  name="video_workflow_agent",
  Instruction:
    """
    Coordinate video creation workflow (supervisor pattern).
    
    Selected video: {temp:selected_video_id}
    
    === INITIALIZATION ===
    On entry:
    1. Get video_id from state: temp:selected_video_id
    2. Get user_id from state: user:verified_user_id
    3. Call get_or_create_adk_session_for_video(video_id, user_id)
       → This returns session with rebuilt state
       → State now has:
          - temp:script_completed (bool)
          - temp:scenes_completed (bool)
          - temp:next_scene_to_generate (int)
          - temp:total_scenes (int)
          - etc.
    
    === WORKFLOW LOGIC ===
    Check state and route:
    
    IF script_completed == False:
      → "Let's create your script first."
      → Use script_agent_tool
      → After completion: persist_state_checkpoint
    
    ELIF scenes_completed == False:
      → "Breaking script into scenes..."
      → Use scene_agent_tool
      → After completion: persist_state_checkpoint
    
    ELIF next_scene_to_generate <= total_scenes:
      → "Generating images (batch {current_batch})..."
      → Use image_batch_agent_tool
      → After completion: persist_state_checkpoint
    
    ELSE:
      → "Video complete! All {total_scenes} scenes done."
      → Escalate to root_agent
    
    === INTERRUPTION ===
    If user says "menu", "stop", "pause":
      → persist_state_checkpoint (save progress)
      → "Saved! You can resume anytime."
      → Escalate to root_agent
    """,
  Tools=[
    - get_video_session_tool (wraps get_or_create_adk_session_for_video)
    - save_checkpoint_tool (wraps persist_state_checkpoint)
    # - AgentTool(script_agent)
    # - AgentTool(scene_agent)
    # - AgentTool(image_batch_agent)
  ]
)
