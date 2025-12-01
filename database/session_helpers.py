"""
ADK session rebuild helpers
Reconstructs ADK session state from persistent DB
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from google.adk.sessions import DatabaseSessionService
    from google.adk.runners import Runner
    from google.adk import types
except Exception:
    DatabaseSessionService = Any
    Runner = Any
    types = Any

from .models import UserModel
from .connection import db_connection


# === Sync DB helpers ===

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    return UserModel.find_by_id(user_id)


def get_video(video_id: str) -> Optional[Dict[str, Any]]:
    """Get video by ID"""
    with db_connection.get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM videos WHERE video_id = ?", 
            (video_id,)
        ).fetchone()
        return dict(row) if row else None


def update_video_last_session(video_id: str, session_id: str) -> None:
    """Update video's last_session_id"""
    with db_connection.get_connection() as conn:
        conn.execute(
            "UPDATE videos SET last_session_id = ? WHERE video_id = ?",
            (session_id, video_id)
        )


def get_scenes_for_video(video_id: str) -> list:
    """Get all scenes for a video"""
    with db_connection.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT scene_number, visual_description 
            FROM scenes 
            WHERE video_id = ? 
            ORDER BY scene_number
            """,
            (video_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_approved_images_for_video(video_id: str) -> list:
    """Get approved images with scene numbers"""
    with db_connection.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.scene_number, i.image_path 
            FROM images i 
            JOIN scenes s ON i.scene_id = s.scene_id 
            WHERE s.video_id = ? 
            AND i.status = 'approved'
            ORDER BY s.scene_number
            """,
            (video_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def save_checkpoint(video_id: str, checkpoint: dict) -> None:
    """Save checkpoint to DB"""
    with db_connection.get_connection() as conn:
        # Create table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                video_id TEXT PRIMARY KEY,
                next_scene INTEGER,
                current_batch INTEGER,
                character_reference_path TEXT,
                session_cost REAL,
                last_updated_at TEXT
            )
        """)
        
        # Upsert checkpoint
        conn.execute(
            """
            INSERT INTO checkpoints (
                video_id, next_scene, current_batch, 
                character_reference_path, session_cost, last_updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(video_id) DO UPDATE SET
                next_scene = excluded.next_scene,
                current_batch = excluded.current_batch,
                character_reference_path = excluded.character_reference_path,
                session_cost = excluded.session_cost,
                last_updated_at = excluded.last_updated_at
            """,
            (
                video_id,
                checkpoint.get("next_scene"),
                checkpoint.get("current_batch"),
                checkpoint.get("character_reference_path"),
                checkpoint.get("session_cost"),
                checkpoint.get("last_updated_at"),
            ),
        )


# === Main session rebuild functions ===

def build_state_from_db(video_id: str, user_id: str) -> Dict[str, Any]:
    """Rebuild minimal ADK session state from DB"""
    
    video = get_video(video_id)
    user = get_user(user_id)
    scenes = get_scenes_for_video(video_id)
    approved_images = get_approved_images_for_video(video_id)
    
    # Determine next scene to generate
    approved_scene_nums = {img['scene_number'] for img in approved_images}
    total_scenes = len(scenes)
    next_scene = 1
    
    for s in scenes:
        if s['scene_number'] not in approved_scene_nums:
            next_scene = s['scene_number']
            break
    else:
        # All scenes approved
        next_scene = total_scenes + 1
    
    state = {
        # Workflow identity
        "temp:workflow_id": f"wf_{uuid.uuid4().hex[:8]}",
        "temp:video_id": video_id,
        "temp:current_phase": video.get("status", "in_progress"),
        
        # Progress
        "temp:next_scene_to_generate": next_scene,
        "temp:total_scenes": total_scenes,
        "temp:images_in_progress": [],
        "temp:current_batch_number": 0,
        
        # Completion flags
        "temp:script_completed": bool(video.get("script")),
        "temp:scenes_completed": total_scenes > 0,
        
        # References
        "temp:character_reference_path": video.get("character_reference_path"),
        
        # Cost tracking
        "temp:session_cost": 0.0,
        "user:total_lifetime_cost": user.get("current_month_cost", 0.0) if user else 0.0,
        
        # User identity
        "user:email": user.get("email") if user else None,
        "user:verified_user_id": user.get("user_id") if user else None,
        "user:name": user.get("user_name") if user else None,
        
        # Metadata
        "temp:last_updated_at": datetime.utcnow().isoformat() + "Z",
    }
    
    # Small scene summary (first 120 chars of each prompt)
    state["temp:scenes_summary"] = [
        {
            "scene_number": s["scene_number"], 
            "short_prompt": (s["visual_description"] or "")[:120]
        }
        for s in scenes
    ]
    
    return state


async def get_or_create_adk_session_for_video(
    session_service: DatabaseSessionService,
    video_id: str,
    user_id: str,
    app_name: str = "continuity"
):
    """
    Resume ADK session for video or create new one with DB state.
    
    Returns: ADK Session object
    """
    
    # Get video from DB
    video = get_video(video_id)
    if not video:
        raise ValueError(f"Video not found: {video_id}")
    
    last_session_id = video.get("last_session_id")
    
    # Try to resume existing session
    if last_session_id:
        try:
            session = await session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=last_session_id
            )
            print(f"Resumed session: {last_session_id}")
            return session
        except Exception as e:
            print(f"Could not resume session {last_session_id}: {e}")
            print("Building new session from DB...")
    
    # Build state from DB
    initial_state = build_state_from_db(video_id, user_id)
    
    # Create new session
    new_session_id = f"video_{video_id}__{uuid.uuid4().hex[:8]}"
    
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=new_session_id,
        state=initial_state
    )
    
    # Save session_id to DB
    update_video_last_session(video_id, new_session_id)
    
    print(f"Created new session: {new_session_id}")
    return session


def persist_state_checkpoint(video_id: str, state: Dict[str, Any]) -> None:
    """
    Save checkpoint to DB after important events.
    Call this when user approves batch, selects character, etc.
    """
    checkpoint = {
        "video_id": video_id,
        "next_scene": state.get("temp:next_scene_to_generate"),
        "current_batch": state.get("temp:current_batch_number"),
        "character_reference_path": state.get("temp:character_reference_path"),
        "session_cost": state.get("temp:session_cost"),
        "last_updated_at": datetime.utcnow().isoformat() + "Z",
    }
    save_checkpoint(video_id, checkpoint)
    print(f"Checkpoint saved for video {video_id}")


# Export public functions
__all__ = [
    "build_state_from_db",
    "get_or_create_adk_session_for_video",
    "persist_state_checkpoint",
]