from google.adk.tools import ToolContext
from typing import Dict, Any, List
from config import save_current_video

def list_user_videos_tool(tool_context: ToolContext) -> Dict[str, Any]:
    """
    List all videos for user.
    
    Returns:
        dict with list of user's videos
    """
    from database.connection import db_connection
    
    user_id = tool_context.state.get("user:verified_user_id")
    
    if not user_id:
        return {
            "success": False,
            "error": "User does not exist"
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
    
    # UPDATE FILE!
    save_current_video(video_id)

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
    
    # UPDATE FILE!
    save_current_video(video_id)

    return {
        "success": True,
        "video_id": video_id,
        "title": title,
        "message": f"Created new video: {title}"
    }