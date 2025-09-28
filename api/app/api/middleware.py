"""
Authentication Middleware
========================

Middleware for handling authentication and authorization in FastAPI.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Optional
import logging
from datetime import datetime

from app.core.security import jwt_manager
from app.models.auth import DatabaseManager, User, Session

logger = logging.getLogger(__name__)

# Initialize database and models
db_manager = DatabaseManager()
user_model = User(db_manager)
session_model = Session(db_manager)

class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    def __init__(self, app, protected_paths: Optional[list] = None):
        self.app = app
        self.protected_paths = protected_paths or ["/analyze"]
        self.public_paths = ["/", "/health", "/auth", "/docs", "/openapi.json", "/redoc"]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        path = request.url.path
        method = request.method
        
        # Allow OPTIONS requests (CORS preflight) to pass through without authentication
        if method == "OPTIONS":
            await self.app(scope, receive, send)
            return
        
        # Check if path requires authentication
        if self._is_protected_path(path):
            try:
                # Extract token from Authorization header
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    return await self._unauthorized_response(scope, receive, send)
                
                token = auth_header.split(" ")[1]
                
                # Verify token
                payload = jwt_manager.verify_token(token)
                if not payload:
                    return await self._unauthorized_response(scope, receive, send)
                
                # Get user from database
                user_id = payload.get("user_id")
                if not user_id:
                    return await self._unauthorized_response(scope, receive, send)
                
                user = user_model.get_user_by_id(user_id)
                if not user:
                    return await self._unauthorized_response(scope, receive, send)
                
                # Add user info to request state
                request.state.user = user
                request.state.user_id = user_id
                
            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                return await self._unauthorized_response(scope, receive, send)
        
        await self.app(scope, receive, send)
    
    def _is_protected_path(self, path: str) -> bool:
        """Check if path requires authentication"""
        # Check exact matches first
        if path in self.public_paths:
            return False
        
        # Check if path starts with any protected path
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
        
        return False
    
    async def _unauthorized_response(self, scope, receive, send):
        """Send unauthorized response"""
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Authentication required",
                "error": "unauthorized"
            }
        )
        await response(scope, receive, send)

def create_auth_middleware(app, protected_paths: Optional[list] = None):
    """Create authentication middleware"""
    return AuthMiddleware(app, protected_paths)

# Utility functions for route protection
def require_auth(func):
    """Decorator to require authentication for a route"""
    async def wrapper(*args, **kwargs):
        # This would be used with dependency injection in FastAPI
        # The actual implementation is handled by the middleware
        return await func(*args, **kwargs)
    return wrapper

def require_admin(func):
    """Decorator to require admin privileges for a route"""
    async def wrapper(*args, **kwargs):
        # This would be used with dependency injection in FastAPI
        # The actual implementation is handled by the middleware
        return await func(*args, **kwargs)
    return wrapper

# Rate limiting middleware (basic implementation)
class RateLimitMiddleware:
    """Basic rate limiting middleware"""
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 3600):
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # In production, use Redis or similar
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        client_ip = request.client.host
        current_time = datetime.now()
        
        # Clean old entries
        self._cleanup_old_entries(current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "error": "rate_limit_exceeded"
                }
            )
            await response(scope, receive, send)
            return
        
        # Record request
        self._record_request(client_ip, current_time)
        
        await self.app(scope, receive, send)
    
    def _cleanup_old_entries(self, current_time: datetime):
        """Clean up old rate limit entries"""
        cutoff_time = current_time.timestamp() - self.window_seconds
        self.requests = {
            ip: times for ip, times in self.requests.items()
            if any(t > cutoff_time for t in times)
        }
    
    def _is_rate_limited(self, client_ip: str, current_time: datetime) -> bool:
        """Check if client is rate limited"""
        if client_ip not in self.requests:
            return False
        
        current_timestamp = current_time.timestamp()
        window_start = current_timestamp - self.window_seconds
        
        # Count requests in current window
        recent_requests = [
            t for t in self.requests[client_ip]
            if t > window_start
        ]
        
        return len(recent_requests) >= self.max_requests
    
    def _record_request(self, client_ip: str, current_time: datetime):
        """Record a request for rate limiting"""
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        self.requests[client_ip].append(current_time.timestamp())

def create_rate_limit_middleware(app, max_requests: int = 100, window_seconds: int = 3600):
    """Create rate limiting middleware"""
    return RateLimitMiddleware(app, max_requests, window_seconds)
