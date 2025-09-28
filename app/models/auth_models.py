import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

import bcrypt
from app.models.database import UserRepository, SessionRepository

logger = logging.getLogger(__name__)

# Password hashing functions using direct bcrypt
def _hash_password(password: str) -> str:
    """Hash password using direct bcrypt with proper byte handling"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_LENGTH:
        password_bytes = password_bytes[:BCRYPT_MAX_PASSWORD_LENGTH]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def _verify_password(password: str, hashed: str) -> bool:
    """Verify password using direct bcrypt with proper byte handling"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_LENGTH:
        password_bytes = password_bytes[:BCRYPT_MAX_PASSWORD_LENGTH]
    return bcrypt.checkpw(password_bytes, hashed.encode('utf-8'))

# Bcrypt has a 72-byte limit for passwords
BCRYPT_MAX_PASSWORD_LENGTH = 72




class User:
    """User model for authentication and user management"""
    
    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository):
        self.user_repo = user_repo
        self.session_repo = session_repo
    
    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> int:
        """Create a new user with hashed password"""
        try:
            # Check if username or email already exists
            if self.user_repo.get_user_by_username(username):
                raise ValueError("Username already exists")
            
            if self.user_repo.get_user_by_email(email):
                raise ValueError("Email already exists")
            
            # Hash password (bcrypt has a 72-byte limit)
            password_hash = _hash_password(password)
            
            # Create user
            user_id = self.user_repo.create_user(username, email, password_hash, is_admin)
            logger.info(f"User created successfully: {username}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username and password"""
        try:
            user_data = self.user_repo.get_user_by_username(username)
            if not user_data:
                return None
            
            if not user_data.get('is_active', True):
                return None
            
            if not _verify_password(password, user_data['password_hash']):
                return None
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            return self.user_repo.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            return self.user_repo.get_user_by_username(username)
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            return self.user_repo.get_user_by_email(email)
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        try:
            # Hash password if provided (bcrypt has a 72-byte limit)
            if 'password' in kwargs:
                password = kwargs.pop('password')
                kwargs['password_hash'] = _hash_password(password)
            
            return self.user_repo.update_user(user_id, **kwargs)
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user and revoke all sessions"""
        try:
            # Revoke all user sessions first
            self.session_repo.revoke_user_sessions(user_id)
            
            # Delete user
            return self.user_repo.delete_user(user_id)
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise
    
    def list_users(self, limit: int = 50, offset: int = 0) -> list:
        """List users with pagination"""
        try:
            return self.user_repo.list_users(limit, offset)
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            raise


class Session:
    """Session model for managing user sessions"""
    
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo
    
    def create_session(self, user_id: int, expires_hours: int = 24) -> Dict[str, str]:
        """Create a new session for a user"""
        try:
            # Generate tokens
            session_token = secrets.token_urlsafe(32)
            refresh_token = secrets.token_urlsafe(32)
            
            # Calculate expiration
            expires_at = datetime.now() + timedelta(hours=expires_hours)
            
            # Create session in database
            session_id = self.session_repo.create_session(
                user_id, session_token, refresh_token, expires_at
            )
            
            return {
                "session_token": session_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at.isoformat(),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return session data"""
        try:
            session_data = self.session_repo.get_session_by_token(session_token)
            if not session_data:
                return None
            
            # Check if session is expired
            if datetime.now() > datetime.fromisoformat(session_data['expires_at']):
                # Mark session as inactive
                self.session_repo.update_session(session_data['id'], is_active=False)
                return None
            
            return session_data
            
        except Exception as e:
            logger.error(f"Error validating session: {str(e)}")
            raise
    
    def refresh_session(self, refresh_token: str, expires_hours: int = 24) -> Optional[Dict[str, str]]:
        """Refresh session using refresh token"""
        try:
            session_data = self.session_repo.get_session_by_refresh_token(refresh_token)
            if not session_data:
                return None
            
            # Check if session is expired
            if datetime.now() > datetime.fromisoformat(session_data['expires_at']):
                # Mark session as inactive
                self.session_repo.update_session(session_data['id'], is_active=False)
                return None
            
            # Generate new tokens
            new_session_token = secrets.token_urlsafe(32)
            new_refresh_token = secrets.token_urlsafe(32)
            new_expires_at = datetime.now() + timedelta(hours=expires_hours)
            
            # Update session
            success = self.session_repo.update_session(
                session_data['id'],
                session_token=new_session_token,
                refresh_token=new_refresh_token,
                expires_at=new_expires_at
            )
            
            if not success:
                return None
            
            return {
                "session_token": new_session_token,
                "refresh_token": new_refresh_token,
                "expires_at": new_expires_at.isoformat(),
                "session_id": session_data['id']
            }
            
        except Exception as e:
            logger.error(f"Error refreshing session: {str(e)}")
            raise
    
    def revoke_session(self, session_token: str) -> bool:
        """Revoke a session by session token"""
        try:
            session_data = self.session_repo.get_session_by_token(session_token)
            if not session_data:
                return False
            
            return self.session_repo.revoke_session(session_data['id'])
        except Exception as e:
            logger.error(f"Error revoking session: {str(e)}")
            raise
    
    def revoke_user_sessions(self, user_id: int) -> bool:
        """Revoke all sessions for a user"""
        try:
            return self.session_repo.revoke_user_sessions(user_id)
        except Exception as e:
            logger.error(f"Error revoking user sessions: {str(e)}")
            raise
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            return self.session_repo.cleanup_expired_sessions()
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
            raise
