from pathlib import Path

# User data directory
USER_DATA_DIR = Path.home() / ".continuity"
USER_DATA_DIR.mkdir(exist_ok=True)

# Files that track current context
CURRENT_USER_FILE = USER_DATA_DIR / "current_user_id"
CURRENT_VIDEO_FILE = USER_DATA_DIR / "current_video_id"

def save_current_user(user_id: str):
    """Save current logged-in user"""
    CURRENT_USER_FILE.write_text(user_id)

def load_current_user():
    """Load current logged-in user (or None)"""
    if CURRENT_USER_FILE.exists():
        return CURRENT_USER_FILE.read_text().strip()
    return None

def save_current_video(video_id: str):
    """Save currently selected video"""
    CURRENT_VIDEO_FILE.write_text(video_id)

def load_current_video():
    """Load currently selected video (or None)"""
    if CURRENT_VIDEO_FILE.exists():
        return CURRENT_VIDEO_FILE.read_text().strip()
    return None

def clear_current_video():
    """Clear current video (back to menu)"""
    if CURRENT_VIDEO_FILE.exists():
        CURRENT_VIDEO_FILE.unlink()