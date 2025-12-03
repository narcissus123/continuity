from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import ToolContext
from typing import Dict, Any
import re
from database.models import UserModel, VerificationTokenModel
from services.auth_service import AuthService
from config import save_current_user

# ===== HELPER FUNCTIONS =====

def validate_email_format(email: str) -> bool:
    """Check if email format is valid"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ===== TOOL FUNCTIONS =====

def save_user_name_tool(tool_context: ToolContext, name: str) -> Dict[str, Any]:
    """Save user's name temporarily"""
    print(f"\n[TOOL] save_user_name_tool called with: {name}")
    tool_context.state["temp:pending_user_name"] = name.strip()
    result = {"success": True, "message": "Name saved"}
    print(f"[TOOL] save_user_name_tool result: {result}")
    return result


def request_verification_tool(tool_context: ToolContext, email: str) -> Dict[str, Any]:
    """Send verification email to user."""
    print(f"\n[TOOL] request_verification_tool called with: {email}")
    
    try:
        if not validate_email_format(email):
            result = {
                "success": False,
                "error": "invalid_format",
                "message": "Invalid email format."
            }
            print(f"[TOOL] request_verification_tool result: {result}")
            return result
        
        existing_user = UserModel.find_by_email(email)
        token = VerificationTokenModel.create_token(email)
        success = AuthService.send_magic_link(email, token)
        
        if success:
            # Store email in state for later
            tool_context.state["temp:pending_email"] = email
            
            if existing_user:
                result = {
                    "success": True,
                    "message": "Verification code sent.",
                    "action": "verify"
                }
            else:
                result = {
                    "success": True,
                    "message": "Verification code sent.",
                    "action": "await_token"
                }
        else:
            result = {
                "success": False,
                "error": "send_failed",
                "message": "Failed to send email."
            }
        
        print(f"[TOOL] request_verification_tool result: {result}")
        return result
        
    except Exception as e:
        print(f"[TOOL] request_verification_tool ERROR: {e}")
        return {
            "success": False,
            "error": "exception",
            "message": f"Error: {str(e)}"
        }


def verify_token_tool(tool_context: ToolContext, token: str) -> Dict[str, Any]:
    """Verify token and create/load user account."""
    print(f"\n[TOOL] verify_token_tool called with: {token[:8]}...")
    
    try:
        email = VerificationTokenModel.verify_token(token.strip())
        
        if not email:
            result = {
                "success": False,
                "error": "invalid_token",
                "message": "Invalid or expired token."
            }
            print(f"[TOOL] verify_token_tool result: {result}")
            return result
        
        user_name = tool_context.state.get("temp:pending_user_name")
        existing_user = UserModel.find_by_email(email)
        
        if not existing_user:
            user = UserModel.create(email, user_name=user_name)
        else:
            user = existing_user
        
        tool_context.state["user:email"] = email
        tool_context.state["user:verified_user_id"] = user["user_id"]
        tool_context.state["user:name"] = user.get("user_name") or "there"
        tool_context.state.pop("temp:pending_user_name", None)
        tool_context.state.pop("temp:pending_email", None)
        
        save_current_user(user["user_id"])
        
        result = {
            "success": True,
            "user_name": user.get("user_name"),
            "message": "Verified!",
            "user_id": user["user_id"],
            "email": email
        }
        print(f"[TOOL] verify_token_tool result: {result}")
        return result
        
    except Exception as e:
        print(f"[TOOL] verify_token_tool ERROR: {e}")
        return {
            "success": False,
            "error": "exception",
            "message": f"Error: {str(e)}"
        }


# ===== SUB-AGENTS FOR SEQUENTIAL WORKFLOW =====

name_agent = LlmAgent(
    name="name_agent",
    model="gemini-2.0-flash",
    instruction="""
    Ask for user's name and save it.
    
    1. Ask: "Hi! To get started, what's your name?"
    2. When user responds, call save_user_name_tool with their name
    3. Say: "Nice to meet you!"
    4. Your output_key will store the name for the email_agent agent
    
    That's it. Do not ask for anything else.
    """,
    tools=[save_user_name_tool],
    output_key="temp:name_collected"
)

email_agent = LlmAgent(
    name="email_agent",
    model="gemini-2.0-flash",
    instruction="""
    Ask for user's email and send verification code.
    
    Previous step: {temp:name_collected?}
    
    1. Ask: "Nice to meet you, {temp:pending_user_name?}! To save your videos and keep your progress, may I have your email? For example: user@example.com"
    2. When user responds, CALL request_verification_tool with their email
    3. Read the tool response:
       - If success=true: Say "I've sent a code to your email. Please check your inbox and enter the code here."
       - If error: Tell them the error and ask again
    4. STOP and WAIT for user's next message. Do not delegate the control to next agent untill you get the code.
    
    You MUST call the tool. Do not just talk about sending email.
    """,
    tools=[request_verification_tool],
    output_key="temp:email_sent"
)

token_agent = LlmAgent(
    name="token_agent",
    model="gemini-2.0-flash",
    instruction="""
    You main and only job is to verify the token the user provides.
    
    Previous step: {temp:email_sent?}
    
    1. User will provide a verification code
    2. CALL verify_token_tool with that code
    3. Read the tool response:
       - If success=true: Say "Email verified! Welcome to Continuity!"
       - If error="invalid_token": Say "That code doesn't match. Please try again."
    
    You MUST call verify_token_tool. Do not just talk about verifying.
    """,
    tools=[verify_token_tool],
    output_key="temp:verification_complete"
)

# ===== SEQUENTIAL GREETING AGENT =====

greeting_agent = SequentialAgent(
    name="greeting_agent",
    sub_agents=[name_agent, email_agent, token_agent],
    description="Handles user authentication in sequence"
)

