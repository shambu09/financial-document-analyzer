"""
JWT Utilities for Authentication
===============================

This module contains JWT token generation, validation, and management utilities.
"""

import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class JWTManager:
    """Manages JWT token operations"""
    
    def __init__(self):
        # Get secret key from environment or generate one
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
            logger.warning("JWT_SECRET_KEY not found in environment. Using generated key.")
        
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access"
            })
            
            # Ensure secret key is properly encoded
            if isinstance(self.secret_key, str):
                secret_key = self.secret_key.encode('utf-8')
            else:
                secret_key = self.secret_key
                
            encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=self.algorithm)
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise
    
    def create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT refresh token"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
            
            to_encode.update({
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "refresh"
            })
            
            # Ensure secret key is properly encoded
            if isinstance(self.secret_key, str):
                secret_key = self.secret_key.encode('utf-8')
            else:
                secret_key = self.secret_key
                
            encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=self.algorithm)
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Error creating refresh token: {str(e)}")
            raise
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            # Ensure secret key is properly encoded
            if isinstance(self.secret_key, str):
                secret_key = self.secret_key.encode('utf-8')
            else:
                secret_key = self.secret_key
                
            payload = jwt.decode(token, secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                logger.warning(f"Invalid token type. Expected: {token_type}, Got: {payload.get('type')}")
                return None
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                logger.warning("Token has expired")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None
    
    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token payload without verification (for debugging)"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            return payload
        except Exception as e:
            logger.error(f"Error getting token payload: {str(e)}")
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired without raising exception"""
        try:
            payload = self.get_token_payload(token)
            if not payload:
                return True
            
            exp = payload.get("exp")
            if not exp:
                return True
            
            return datetime.utcnow() > datetime.fromtimestamp(exp)
        except Exception:
            return True
    
    def extract_user_id(self, token: str) -> Optional[int]:
        """Extract user ID from token"""
        try:
            payload = self.verify_token(token)
            if payload:
                return payload.get("user_id")
            return None
        except Exception as e:
            logger.error(f"Error extracting user ID: {str(e)}")
            return None
    
    def create_token_pair(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create both access and refresh tokens"""
        try:
            access_token = self.create_access_token(user_data)
            refresh_token = self.create_refresh_token({"user_id": user_data.get("user_id")})
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
        except Exception as e:
            logger.error(f"Error creating token pair: {str(e)}")
            raise

# Global JWT manager instance
jwt_manager = JWTManager()
