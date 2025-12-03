from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from agents.root_agent import root_agent
from config import load_current_user, load_current_video, save_current_user
from database.connection import db_connection
from google.genai import types
import asyncio

session_service = DatabaseSessionService(db_url="sqlite+aiosqlite:///adk_sessions.db")
runner = Runner(app_name="continuity", agent=root_agent, session_service=session_service)

def load_user_details_from_db(user_id: str) -> dict:
    """Load user details from database"""
    with db_connection.get_connection() as conn:
        row = conn.execute(
            "SELECT email, user_name FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
    
    if row:
        return {
            "email": row["email"],
            "name": row["user_name"] or "there"
        }
    return {}

# Chat loop
# Save current_user_id and current_video_id to files when they change
async def main():
    print("=" * 60)
    print("CONTINUITY - AI Video Creation Assistant")
    print("=" * 60)

    # 1. Check if we have a current user
    user_id = load_current_user()

    if user_id:
        # Verify user exists in database
        user_details = load_user_details_from_db(user_id)
        if user_details and user_details.get("email"):
            print(f"Welcome back, {user_details.get('name', 'there')}!")
            initial_state = {
                "user:verified_user_id": user_id,
                "user:email": user_details.get("email", ""),
                "user:name": user_details.get("name", "there"),
            }
        else:
            # User file exists but no DB record - clean up
            print("👋 Hi there, Welcome to Continuity!")
            print("(Previous session data was corrupted, starting fresh)")
            from config import CURRENT_USER_FILE
            if CURRENT_USER_FILE.exists():
                CURRENT_USER_FILE.unlink()
            initial_state = {}
    else:
        print("👋 Hi there, Welcome to Continuity!")
        initial_state = {}
    
    # 2. Check if we were working on a video
    video_id = load_current_video()
    if video_id:
        print(f"Resuming video: {video_id}")
        initial_state["temp:selected_video_id"] = video_id
    
    # 3. Create or get session
    session_id = user_id or "temp_session"

    # Try to get existing session or create new one
    try:
        session = await session_service.get_session(
            app_name="continuity",
            user_id=session_id,
            session_id=session_id
        )
        if not session:
            raise ValueError("Session not found")
    except Exception:
        # Create new session with initial state
        session = await session_service.create_session(
            app_name="continuity",
            user_id=session_id,
            session_id=session_id,
            state=initial_state
        )

    # 4. Start chat loop
    while True:
        try:
            message = input("\nYou: ").strip()

            if not message:
                continue

            if message.lower() in ['quit', 'exit']:
                print("\n👋 Goodbye! Your progress is saved.")
                break

            user_msg = types.Content(role="user", parts=[types.Part(text=message)])

            # Run agent
            print("\n🤖 Agent: ", end="", flush=True)
            responses = []
            async for event in runner.run_async(
                user_id=session_id,
                session_id=session_id,
                new_message=user_msg,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            responses.append(part.text)
                            print(part.text, end="", flush=True)
            
            if not responses:
                print("(No response)")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Your progress is saved. Goodbye!")
            break
        except Exception as e:
            print(f"\n Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())