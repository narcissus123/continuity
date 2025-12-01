# test_complete_flow.py

import asyncio
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from agents.root_agent import root_agent

async def test_complete_flow():
    """Test complete authentication and menu flow"""
    
    print("="*60)
    print("TESTING COMPLETE FLOW: Auth → Menu")
    print("="*60)
    
    # Setup
    session_service = DatabaseSessionService(db_url="sqlite:///adk_sessions.db")
    
    runner = Runner(
        agent=root_agent,
        app_name="continuity",
        session_service=session_service
    )
    
    # Create or get session
    try:
        session = await session_service.get_session(
            app_name="continuity",
            user_id="test_user_123",
            session_id="test_session_complete"
        )
        print("Using existing session...")
    except:
        session = await session_service.create_session(
            app_name="continuity",
            user_id="test_user_123",
            session_id="test_session_complete",
            state={}  # Start with empty state
        )
        print("Created new session...")
    if not session:
        print("ERROR: Could not create session!")
        return

    print("\n" + "="*60)
    print("SCENARIO 1: New User Flow")
    print("="*60)
    
    # Start conversation
    print("\n[Starting conversation with root agent...]\n")
    
    # First message
    user_message = types.Content(
        role='user',
        parts=[types.Part(text="Hi")]
    )
    
    async for event in runner.run_async(
        user_id="test_user_123",
        session_id=session.id,
        new_message=user_message
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"Agent: {part.text}\n")
    
    print("\n" + "-"*60)
    print("What happens next:")
    print("1. Agent asks for your email")
    print("2. You provide email")
    print("3. If email exists in DB → Welcome back (existing user)")
    print("4. If email NOT in DB → Goes to greeting agent (new user)")
    print("5. After authentication → Shows menu with videos")
    print("-"*60)
    
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("\nYou can now interact with the agent.")
    print("Type 'quit' to exit.\n")
    
    # Interactive loop
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("\nExiting...")
            break
        
        if not user_input:
            continue
        
        # Send message
        user_message = types.Content(
            role='user',
            parts=[types.Part(text=user_input)]
        )
        
        async for event in runner.run_async(
            user_id="test_user_123",
            session_id=session.id,
            new_message=user_message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"\nAgent: {part.text}\n")
    
    # Show final state
    final_session = await session_service.get_session(
        app_name="continuity",
        user_id="test_user_123",
        session_id=session.id
    )
    
    print("\n" + "="*60)
    print("FINAL SESSION STATE")
    print("="*60)
    print(f"user:email: {final_session.state.get('user:email')}")
    print(f"user:name: {final_session.state.get('user:name')}")
    print(f"user:verified_user_id: {final_session.state.get('user:verified_user_id')}")
    print(f"temp:selected_video_id: {final_session.state.get('temp:selected_video_id')}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_complete_flow())