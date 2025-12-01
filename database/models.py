from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timedelta
import hashlib
from .connection import db_connection

class UserModel:
    """User data access layer"""
    
    @staticmethod
    def create(email: str, user_id: Optional[str] = None, user_name: Optional[str] = None) -> Dict[str, Any]:
        if user_id is None:
            user_id = hashlib.sha256(email.encode()).hexdigest()[:12]
        
        with db_connection.get_connection() as conn:
            conn.execute(
                "INSERT INTO users (user_id, email, user_name) VALUES (?, ?, ?)",
                (user_id, email, user_name)
            )
        
        return {"user_id": user_id, "email": email, "user_name": user_name}

    @staticmethod
    def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        with db_connection.get_connection() as conn:
            result = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()
        
        return dict(result) if result else None
    
    @staticmethod
    def find_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by ID"""
        with db_connection.get_connection() as conn:
            result = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            ).fetchone()
        
        return dict(result) if result else None


class VideoModel:
    """Video data access layer"""
    
    @staticmethod
    def create(user_id: str, title: str, video_id: Optional[str] = None) -> Dict[str, Any]:
        """Create new video"""
        if video_id is None:
            video_id = str(uuid.uuid4())
        
        with db_connection.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO videos (video_id, user_id, title, status)
                VALUES (?, ?, ?, 'in_progress')
                """,
                (video_id, user_id, title)
            )
        
        return {
            "video_id": video_id,
            "user_id": user_id,
            "title": title,
            "status": "in_progress"
        }


class VerificationTokenModel:
    """Manage email verification tokens"""
    
    @staticmethod
    def create_token(email: str) -> str:
        """
        Create a new verification token for an email.
        Token expires in 1 hour.
        
        Args:
            email: User's email address
            
        Returns:
            token: UUID token string
        """
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)
        with db_connection.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO verification_tokens (token, email, expires_at)
                VALUES (?, ?, ?)
                """,
                (token, email, expires_at.isoformat())
            )
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        Verify a token and return the associated email if valid.
        Marks token as used after successful verification.
        
        Args:
            token: UUID token string
            
        Returns:
            email if token is valid, None otherwise
        """
        with db_connection.get_connection() as conn:
            # Check if token exists, not used, and not expired
            result = conn.execute(
                """
                SELECT email FROM verification_tokens
                WHERE token = ?
                AND used = 0
                AND datetime(expires_at) > datetime('now')
                """,
                (token,)
            ).fetchone()
            
            if result:
                email = result["email"]
                
                # Mark token as used
                conn.execute(
                    "UPDATE verification_tokens SET used = 1 WHERE token = ?",
                    (token,)
                )
                
                return email
            
            return None
    
    @staticmethod
    def cleanup_expired_tokens() -> int:
        """
        Delete expired tokens from database.
        Run periodically to keep table clean.
        
        Returns:
            Number of tokens deleted
        """
        with db_connection.get_connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM verification_tokens
                WHERE datetime(expires_at) < datetime('now')
                OR used = 1
                """
            )
            return cursor.rowcount