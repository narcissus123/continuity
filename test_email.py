import asyncio
from database.models import VerificationTokenModel
from services.auth_service import AuthService

async def test_email_verification():
    """Test email sending and token verification"""
    
    print("=== Testing Email Verification System ===\n")
    
    # Test email sending
    print("Testing email sending...")
    test_email = input("Enter your email to test: ").strip()
    
    # Create token
    token = VerificationTokenModel.create_token(test_email)
    
    # Send email
    success = AuthService.send_magic_link(test_email, token)
    
    if success:
        print(f"Email sent to {test_email}")
        print("\nCheck your email inbox!")
    else:
        print("Failed to send email")
        return
    
    # Test token verification
    print("\n" + "="*50)
    print("Testing token verification...")
    user_token = input("Enter the token from your email: ").strip()
    
    verified_email = VerificationTokenModel.verify_token(user_token)
    
    if verified_email:
        print(f"Token verified! Email: {verified_email}")
    else:
        print(repr(user_token))
        print("Invalid or expired token")
    
    # Test token reuse (should fail)
    print("\n" + "="*50)
    print("Testing token reuse (should fail)...")
    verified_again = VerificationTokenModel.verify_token(user_token)
    
    if verified_again:
        print("ERROR: Token was reused (security issue!)")
    else:
        print("Token cannot be reused")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_email_verification())