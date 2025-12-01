from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext
from typing import Dict, Any
import re
from database.models import UserModel, VerificationTokenModel
from services.auth_service import AuthService

def save_user_name_tool(tool_context: ToolContext, name: str) -> Dict[str, Any]:
    """Save user's name temporarily"""
    tool_context.state["temp:pending_user_name"] = name.strip()
    return {"success": True}

def validate_email_format(email: str) -> bool:
    """Check if email format is valid"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def request_verification_tool(tool_context: ToolContext, email: str) -> Dict[str, Any]:
    """
    Send verification email to user.
    
    Args:
        email: User's email address
        
    Returns:
        dict with status and message
    """
    # Validate email format
    if not validate_email_format(email):
        return {
            "success": False,
            "error": "invalid_format",
            "message": "Invalid email format. Please provide a valid email address."
        }
    
    # Check if user already exists
    existing_user = UserModel.find_by_email(email)
    if existing_user:
        return {
            "success": False,
            "message": "This email is already registered. Please verify your token to continue.",
            "action": "verify"
        }
    
    # Create verification token
    token = VerificationTokenModel.create_token(email)
    
    # Send email
    success = AuthService.send_magic_link(email, token)
    
    if success:
        return {
            "success": True,
            "message": f"Verification email sent to {email}. Please check your inbox and provide the token.",
            "action": "await_token"
        }
    else:
        return {
            "success": False,
            "error": "send_failed",
            "message": "Failed to send email. Please try again or use a different email address."
        }


def verify_token_tool(tool_context: ToolContext, token: str) -> Dict[str, Any]:
    """
    Verify token and create user account.
    
    Args:
        token: Verification token from email
        
    Returns:
        dict with status and user info
    """
    # Verify token
    email = VerificationTokenModel.verify_token(token.strip())
    
    if not email:
        return {
            "success": False,
            "error": "invalid_token",
            "message": "Invalid or expired token. Please request a new verification email."
        }
    
    # Check if user already exists
    user_name = tool_context.state.get("temp:pending_user_name")
    existing_user = UserModel.find_by_email(email)
    
    if not user:
        # Create new user
        user = UserModel.create(email, user_name=user_name)
    
    # Save to ADK state
    tool_context.state["user:email"] = email
    tool_context.state["user:verified_user_id"] = user["user_id"]
    tool_context.state["user:name"] = user.get("user_name") or "there"
    tool_context.state.pop("temp:pending_user_name", None)

    return {
        "success": True,
        "user_name": user.get("user_name"),
        "message": f"Email verified! Welcome to Continuity, {email}",
        "user_id": user["user_id"],
        "email": email
    }


# Define the greeting agent
greeting_agent = LlmAgent(
    name="greeting_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
    You handle user authentication for Continuity.
    
    Your job:
    Step 1: Ask "What's your name?"
    → Use save_user_name_tool

    Step 2: Ask "What's your email?"
    → Use request_verification_tool
    → If error="invalid_format": Ask for email again
    → If error="send_failed": Ask them to check internet and try again

    Step 3: Say "Check your email for a verification token."
    → Wait for user to provide token
    → Use verify_token_tool
    → If error="invalid_token": Let them try again OR request new email (Step 2)

    Step 4: When success=True
    → Say "Welcome to Continuity, {user_name}!"
    → STOP - your job is done
    
    Be friendly and concise. Guide them through the process step by step.
    
    Example flow:
    - "To get started, please provide your email address."
    - User provides email
    - "Great! I've sent a verification token to your email. Please check your inbox and paste the token here."
    - User provides token
    - "Email verified! Welcome to Continuity. You can now start creating videos."
    """,
    tools=[
        save_user_name_tool,
        request_verification_tool,
        verify_token_tool
    ]
)