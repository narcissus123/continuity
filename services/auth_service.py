import smtplib
import uuid
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class AuthService:
    """Handle email verification via magic links"""
    
    @staticmethod
    def send_magic_link(email: str, token: str) -> bool:
        """
        Send magic link email to user.
        
        Args:
            email: User's email address
            token: Verification token (UUID)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            gmail_address = os.getenv("GMAIL_ADDRESS")
            gmail_password = os.getenv("GMAIL_APP_PASSWORD")
            
            
            if not gmail_address or not gmail_password:
                print(gmail_address)
                print(gmail_password)
                raise ValueError("Gmail credentials not found in .env file")
            
            # email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Continuity - Verify Your Email'
            msg['From'] = gmail_address
            msg['To'] = email
            
            # email body (plain text and HTML versions)
            text_body = f"""Welcome to Continuity!

            Click the link below to verify your email and start creating videos:

            Verification Token: {token}

            This link expires in 1 hour.

            ---
            Continuity - AI Video Generation
            """
                        
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2>Welcome to Continuity!</h2>
                <p>Click the button below to verify your email and start creating videos:</p>
                
                <div style="margin: 30px 0;">
                <p><strong>Your verification token:</strong></p>
                <p style="background-color: #f4f4f4; padding: 10px; font-family: monospace; font-size: 16px;">{token}</p>

                </div>
                
                <p style="color: #666; font-size: 14px;">This token expires in 1 hour.</p>
                
                <hr style="margin-top: 30px; border: none; border-top: 1px solid #ddd;">
                <p style="color: #999; font-size: 12px;">Continuity - AI Video Generation</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email via Gmail SMTP
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Secure connection
                server.login(gmail_address, gmail_password)
                server.send_message(msg)
            
            print(f"Magic link sent to {email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False