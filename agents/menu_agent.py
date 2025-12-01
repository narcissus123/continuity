# agents/menu_agent.py

from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from typing import Dict, Any, List


def list_user_videos_tool(tool_context: ToolContext) -> Dict[str, Any]:
    """
    List all videos for the authenticated user.
    
    Returns:
        dict with list of user's videos
    """
    from database.connection import db_connection
    
    user_id = tool_context.state.get("user:verified_user_id")
    
    if not user_id:
        return {
            "success": False,
            "error": "User not authenticated"
        }
    
    # Get user's videos from DB
    with db_connection.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT video_id, title, status, created_at,
                   (SELECT COUNT(*) FROM scenes WHERE scenes.video_id = videos.video_id) as scene_count
            FROM videos
            WHERE user_id = ?
            ORDER BY updated_at DESC
            LIMIT 10
            """,
            (user_id,)
        ).fetchall()
    
    videos = [dict(row) for row in rows]
    
    if not videos:
        return {
            "success": True,
            "videos": [],
            "message": "You don't have any videos yet."
        }
    
    return {
        "success": True,
        "videos": videos,
        "count": len(videos)
    }


def select_video_tool(tool_context: ToolContext, video_id: str) -> Dict[str, Any]:
    """
    Select a video to work on.
    Sets temp:selected_video_id in state.
    
    Args:
        video_id: The video to work on
        
    Returns:
        dict with video info
    """
    from database.connection import db_connection
    
    user_id = tool_context.state.get("user:verified_user_id")
    
    # Verify video belongs to user
    with db_connection.get_connection() as conn:
        video = conn.execute(
            "SELECT * FROM videos WHERE video_id = ? AND user_id = ?",
            (video_id, user_id)
        ).fetchone()
    
    if not video:
        return {
            "success": False,
            "error": "Video not found or doesn't belong to you"
        }
    
    # Set selected video in state
    tool_context.state["temp:selected_video_id"] = video_id
    
    return {
        "success": True,
        "video_id": video_id,
        "title": video["title"],
        "status": video["status"],
        "message": f"Selected video: {video['title']}"
    }


def create_new_video_tool(tool_context: ToolContext, title: str) -> Dict[str, Any]:
    """
    Create a new video for the user.
    
    Args:
        title: Video title
        
    Returns:
        dict with new video info
    """
    import uuid
    from database.connection import db_connection
    
    user_id = tool_context.state.get("user:verified_user_id")
    
    if not user_id:
        return {
            "success": False,
            "error": "User not authenticated"
        }
    
    # Create video in DB
    video_id = str(uuid.uuid4())
    
    with db_connection.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO videos (video_id, user_id, title, status)
            VALUES (?, ?, ?, 'in_progress')
            """,
            (video_id, user_id, title)
        )
    
    # Set as selected video
    tool_context.state["temp:selected_video_id"] = video_id
    
    return {
        "success": True,
        "video_id": video_id,
        "title": title,
        "message": f"Created new video: {title}"
    }


menu_agent = LlmAgent(
    name="menu_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You help users navigate their videos.
    
    User info:
    - Name: {user:name?}
    - Email: {user:email?}
    
    === YOUR JOB ===
    
    Step 1: Show video list
    → Use list_user_videos_tool
    → Display results clearly:
        - If no videos: "You don't have any videos yet. Let's create one!"
        - If has videos: Show list with status and scene count
    
    Step 2: Ask what user wants to do
    → Options:
        a) "Continue working on [video title]"
        b) "Create a new video"
    
    Step 3: Handle user choice
    
    If user wants to continue existing video:
        → Use select_video_tool with video_id
        → Say: "Loading [video title]..."
        → STOP - video_creation_agent will take over
    
    If user wants to create new video:
        → Ask: "What's your video title?"
        → Use create_new_video_tool with title
        → Say: "Created! Let's start building your video."
        → STOP - video_creation_agent will take over
    
    === FORMAT ===
    Keep messages short and friendly.
    Format video list clearly:
    
    Example:
    "Your videos:
    1. Dragon Adventure (in progress, 5 scenes)
    2. Robot Story (completed, 20 scenes)
    
    Which would you like to work on, or create a new one?"
    """,
    tools=[
        list_user_videos_tool,
        select_video_tool,
        create_new_video_tool
    ]
)