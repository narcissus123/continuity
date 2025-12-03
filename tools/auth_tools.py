from google.adk.tools import ToolContext
from typing import Dict, Any
import re
from config import save_current_user

def validate_email_format(email: str) -> bool:
    """Check if email format is valid"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def check_and_restore_user_tool(tool_context: ToolContext, email: str) -> Dict[str, Any]:
    """
    Check if user exists in DB and restore their identity to state.
    
    Used when state is empty but user might exist in DB.

    Args:
        email: User's email address
        
    Returns:
        dict with status (existing_user, new_user, or invalid_email)
    """
    from database.models import UserModel
    
    # Validate email format
    if not validate_email_format(email):
        return {
            "status": "invalid_email",
            "message": "Invalid email format. Please provide a valid email address."
        }
    
    # Check if user exists in DB
    user = UserModel.find_by_email(email)
    
    if user:
        # EXISTING USER - restore to state
        tool_context.state["user:email"] = user["email"]
        tool_context.state["user:verified_user_id"] = user["user_id"]
        tool_context.state["user:name"] = user.get("user_name") or "there"
        
        return {
            "status": "existing_user",
            "user_name": user.get("user_name") or "there",
            "message": f"Welcome back, {user.get('user_name') or 'there'}!"
        }
    else:
        # NEW USER - needs full registration
        return {
            "status": "new_user",
            "email": email,
            "message": "This email is not registered yet. Let's create your account."
        }