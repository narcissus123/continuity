# test_session_rebuild.py
import asyncio
from google.adk.sessions import DatabaseSessionService
from database.session_helpers import (
    build_state_from_db,
    get_or_create_adk_session_for_video
)
from database.models import UserModel, VideoModel

async def test_session_rebuild():
    """Test session rebuild functionality"""
    
    print("=== Testing Session Rebuild ===\n")
    
    # Step 1: Create test user
    print("Step 1: Creating test user...")
    # Check if user exists first
    user = UserModel.find_by_email("test@example.com")
    if not user:
        user = UserModel.create(
            email="test@example.com",
            user_name="Test User"
        )
        print(f"✅ User created: {user['user_id']}")
    else:
        print(f"✅ User already exists: {user['user_id']}")
    
    # Step 2: Create test video
    print("\nStep 2: Creating test video...")
    video = VideoModel.create(
        user_id=user['user_id'],
        title="Test Video"
    )
    print(f"Video created: {video['video_id']}")
    
    # Step 3: Test building state from DB
    print("\nStep 3: Building state from DB...")
    state = build_state_from_db(
        video_id=video['video_id'],
        user_id=user['user_id']
    )
    
    print(f"State built successfully!")
    print(f"   - video_id: {state.get('temp:video_id')}")
    print(f"   - user_email: {state.get('user:email')}")
    print(f"   - user_name: {state.get('user:name')}")
    print(f"   - script_completed: {state.get('temp:script_completed')}")
    print(f"   - total_scenes: {state.get('temp:total_scenes')}")
    
    # Step 4: Test session creation
    print("\nStep 4: Creating ADK session...")
    session_service = DatabaseSessionService(
        db_url="sqlite:///adk_sessions.db"
    )
    
    session = await get_or_create_adk_session_for_video(
        session_service=session_service,
        video_id=video['video_id'],
        user_id=user['user_id'],
        app_name="continuity"
    )
    
    print(f"Session created: {session.id}")
    print(f"   - Session state has {len(session.state)} keys")
    
    # Step 5: Test session resumption
    print("\nStep 5: Testing session resumption...")
    session2 = await get_or_create_adk_session_for_video(
        session_service=session_service,
        video_id=video['video_id'],
        user_id=user['user_id'],
        app_name="continuity"
    )
    
    if session2.id == session.id:
        print(f"Session resumed successfully! Same session ID: {session2.id}")
    else:
        print(f"ERROR: Got different session ID: {session2.id} vs {session.id}")
    
    # Step 6: Check video record was updated
    print("\nStep 6: Checking video record...")
    from database.session_helpers import get_video
    updated_video = get_video(video['video_id'])
    
    if updated_video.get('last_session_id') == session.id:
        print(f"Video record updated with session ID")
    else:
        print(f"ERROR: Video last_session_id not set correctly")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_session_rebuild())