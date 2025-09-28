from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union
from datetime import datetime


class DatabaseInterface(ABC):
    """Abstract base class for database operations"""
    
    @abstractmethod
    def init_database(self) -> None:
        """Initialize the database with required tables"""
        pass
    
    @abstractmethod
    def close_connection(self) -> None:
        """Close database connection"""
        pass


class UserRepository(ABC):
    """Abstract repository for user operations"""
    
    @abstractmethod
    def create_user(self, username: str, email: str, password_hash: str, is_admin: bool = False) -> str:
        """Create a new user and return user ID"""
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        pass
    
    @abstractmethod
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user information"""
        pass
    
    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        pass
    
    @abstractmethod
    def list_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List users with pagination"""
        pass


class SessionRepository(ABC):
    """Abstract repository for session operations"""
    
    @abstractmethod
    def create_session(self, user_id: str, session_token: str, refresh_token: str, expires_at: datetime) -> str:
        """Create a new session and return session ID"""
        pass
    
    @abstractmethod
    def get_session_by_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session by session token"""
        pass
    
    @abstractmethod
    def get_session_by_refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Get session by refresh token"""
        pass
    
    @abstractmethod
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session information"""
        pass
    
    @abstractmethod
    def revoke_session(self, session_id: str) -> bool:
        """Revoke a session"""
        pass
    
    @abstractmethod
    def revoke_user_sessions(self, user_id: str) -> bool:
        """Revoke all sessions for a user"""
        pass
    
    @abstractmethod
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions"""
        pass


class DocumentRepository(ABC):
    """Abstract repository for document operations"""
    
    @abstractmethod
    def create_document(self, user_id: str, original_name: str, stored_name: str, 
                       path: str, size_bytes: int, checksum: Optional[str] = None) -> str:
        """Create a new document record and return document ID"""
        pass
    
    @abstractmethod
    def get_document(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID for a specific user"""
        pass
    
    @abstractmethod
    def get_user_documents(self, user_id: str, search_query: Optional[str] = None,
                          limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get documents for a user with optional search"""
        pass
    
    @abstractmethod
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document for a user"""
        pass
    
    @abstractmethod
    def get_documents_count(self, user_id: str) -> int:
        """Get total count of documents for a user"""
        pass


class AnalysisReportRepository(ABC):
    """Abstract repository for analysis report operations"""
    
    @abstractmethod
    def create_report(self, user_id: str, analysis_type: str, query: str, file_name: str,
                     report_path: str, document_id: Optional[str] = None,
                     summary: Optional[str] = None, status: str = "completed") -> str:
        """Create a new analysis report and return report ID"""
        pass
    
    @abstractmethod
    def get_report(self, report_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis report by ID for a user"""
        pass
    
    @abstractmethod
    def get_user_reports(self, user_id: str, analysis_type: Optional[str] = None,
                        search_query: Optional[str] = None, limit: int = 50,
                        offset: int = 0) -> List[Dict[str, Any]]:
        """Get analysis reports for a user with filtering"""
        pass
    
    @abstractmethod
    def update_report(self, report_id: str, user_id: str, **kwargs) -> bool:
        """Update analysis report"""
        pass
    
    @abstractmethod
    def delete_report(self, report_id: str, user_id: str) -> bool:
        """Delete analysis report"""
        pass
    
    @abstractmethod
    def get_reports_count(self, user_id: str, analysis_type: Optional[str] = None) -> int:
        """Get total count of reports for a user"""
        pass
