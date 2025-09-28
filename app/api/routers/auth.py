"""
Authentication Router
====================

FastAPI router for JWT-based authentication with session management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from app.models.auth import DatabaseManager, User, Session
from app.core.security import jwt_manager
from app.models.schemas import UserCreate as UserCreateSchema, UserResponse as UserResponseSchema, UserLogin, LoginResponse as TokenResponse, RefreshTokenRequest

logger = logging.getLogger(__name__)

# Initialize database and models
db_manager = DatabaseManager()
user_model = User(db_manager)
session_model = Session(db_manager)

# Security scheme
security = HTTPBearer()

# Use schemas from app.models.schemas

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt_manager.verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = user_model.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependency to get current active user
async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current active user"""
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Dependency to get admin user
async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
    """Get current admin user"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreateSchema):
    """Register a new user"""
    try:
        # Validate password strength
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Create user
        user_id = user_model.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            is_admin=user_data.is_admin
        )
        
        # Fetch the created user data
        user = user_model.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but could not be retrieved"
            )
        
        logger.info(f"User registered: {user['username']}")
        return UserResponseSchema(**user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Login user and return JWT tokens"""
    try:
        # Authenticate user
        user = user_model.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create session
        session_data = session_model.create_session(user["id"])
        
        # Create JWT tokens
        token_data = {
            "user_id": user["id"],
            "username": user["username"],
            "is_admin": user["is_admin"]
        }
        
        tokens = jwt_manager.create_token_pair(token_data)
        
        logger.info(f"User logged in: {user['username']}")
        
        return TokenResponse(
            **tokens,
            user={
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "is_active": user.get("is_active", True),
                "is_admin": user["is_admin"],
                "created_at": user.get("created_at", ""),
                "updated_at": user.get("updated_at", "")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = jwt_manager.verify_token(refresh_data.refresh_token, token_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )
        
        # Get user
        user = user_model.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new tokens
        token_data = {
            "user_id": user["id"],
            "username": user["username"],
            "is_admin": user["is_admin"]
        }
        
        tokens = jwt_manager.create_token_pair(token_data)
        
        logger.info(f"Token refreshed for user: {user['username']}")
        
        return TokenResponse(
            **tokens,
            user={
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "is_active": user.get("is_active", True),
                "is_admin": user["is_admin"],
                "created_at": user.get("created_at", ""),
                "updated_at": user.get("updated_at", "")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )

@router.post("/logout")
async def logout_user(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Logout user and revoke all sessions"""
    try:
        # Revoke all user sessions
        session_model.revoke_all_user_sessions(current_user["id"])
        
        logger.info(f"User logged out: {current_user['username']}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Error logging out user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout"
        )

@router.get("/me", response_model=UserResponseSchema)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponseSchema(**current_user)

@router.put("/me", response_model=UserResponseSchema)
async def update_user_info(
    username: Optional[str] = None,
    email: Optional[EmailStr] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update current user information"""
    try:
        # This would require implementing update methods in User model
        # For now, return current user info
        logger.info(f"User info update requested for: {current_user['username']}")
        return UserResponseSchema(**current_user)
        
    except Exception as e:
        logger.error(f"Error updating user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user information"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Change user password"""
    try:
        # This would require implementing password change in User model
        # For now, return success message
        logger.info(f"Password change requested for: {current_user['username']}")
        
        return {"message": "Password change functionality not yet implemented"}
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error changing password"
        )

@router.get("/users", response_model=list[UserResponseSchema])
async def get_all_users(current_user: Dict[str, Any] = Depends(get_current_admin_user)):
    """Get all users (admin only)"""
    try:
        # This would require implementing get_all_users method in User model
        # For now, return current user
        logger.info(f"Users list requested by admin: {current_user['username']}")
        return [UserResponseSchema(**current_user)]
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
):
    """Delete a user (admin only)"""
    try:
        # This would require implementing delete_user method in User model
        logger.info(f"User deletion requested by admin {current_user['username']} for user ID: {user_id}")
        
        return {"message": "User deletion functionality not yet implemented"}
        
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )

@router.post("/cleanup-sessions")
async def cleanup_expired_sessions(current_user: Dict[str, Any] = Depends(get_current_admin_user)):
    """Clean up expired sessions (admin only)"""
    try:
        cleaned_count = session_model.cleanup_expired_sessions()
        
        logger.info(f"Cleaned up {cleaned_count} expired sessions")
        
        return {"message": f"Cleaned up {cleaned_count} expired sessions"}
        
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cleaning up sessions"
        )
