"""
Migration helper to transition from old auth.py to new modular structure
This file provides backward compatibility and migration utilities
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.factory import get_model_manager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Backward compatibility wrapper for old DatabaseManager"""
    
    def __init__(self, db_path: str = "auth.db"):
        self.db_path = db_path
        self.model_manager = get_model_manager()
        self.db = self.model_manager.get_database()
    
    def init_database(self):
        """Initialize database - now handled by model manager"""
        # Database is already initialized by model manager
        pass


class User:
    """Backward compatibility wrapper for old User class"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.model_manager = get_model_manager()
        self.user_model = self.model_manager.get_user_model()
    
    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> int:
        """Create a new user"""
        return self.user_model.create_user(username, email, password, is_admin)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user"""
        return self.user_model.authenticate_user(username, password)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.user_model.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        return self.user_model.get_user_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return self.user_model.get_user_by_email(email)
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user"""
        return self.user_model.update_user(user_id, **kwargs)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        return self.user_model.delete_user(user_id)
    
    def list_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List users"""
        return self.user_model.list_users(limit, offset)


class Session:
    """Backward compatibility wrapper for old Session class"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.model_manager = get_model_manager()
        self.session_model = self.model_manager.get_session_model()
    
    def create_session(self, user_id: int, expires_hours: int = 24) -> Dict[str, str]:
        """Create session"""
        return self.session_model.create_session(user_id, expires_hours)
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session"""
        return self.session_model.validate_session(session_token)
    
    def refresh_session(self, refresh_token: str, expires_hours: int = 24) -> Optional[Dict[str, str]]:
        """Refresh session"""
        return self.session_model.refresh_session(refresh_token, expires_hours)
    
    def revoke_session(self, session_token: str) -> bool:
        """Revoke session"""
        return self.session_model.revoke_session(session_token)
    
    def revoke_user_sessions(self, user_id: int) -> bool:
        """Revoke user sessions"""
        return self.session_model.revoke_user_sessions(user_id)
    
    def cleanup_expired_sessions(self) -> int:
        """Cleanup expired sessions"""
        return self.session_model.cleanup_expired_sessions()


class AnalysisReport:
    """Backward compatibility wrapper for old AnalysisReport class"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.model_manager = get_model_manager()
        self.analysis_report_model = self.model_manager.get_analysis_report_model()
    
    def create_report(
        self,
        user_id: int,
        analysis_type: str,
        query: str,
        file_name: str,
        report_path: str,
        document_id: Optional[int] = None,
        summary: Optional[str] = None,
        status: str = "completed"
    ) -> int:
        """Create analysis report"""
        return self.analysis_report_model.report_repo.create_report(
            user_id, analysis_type, query, file_name, report_path,
            document_id, summary, status
        )
    
    def get_report(self, report_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get analysis report"""
        return self.analysis_report_model.get_report(report_id, user_id)
    
    def get_user_reports(
        self, 
        user_id: int, 
        analysis_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user reports"""
        return self.analysis_report_model.get_user_reports(
            user_id, analysis_type, search_query, limit, offset
        )
    
    def delete_report(self, report_id: int, user_id: int) -> bool:
        """Delete analysis report"""
        return self.analysis_report_model.delete_report(report_id, user_id)
    
    def update_report_summary(self, report_id: int, user_id: int, summary: str) -> bool:
        """Update report summary"""
        return self.analysis_report_model.update_report(report_id, user_id, summary=summary)
    
    def get_reports_count(self, user_id: int, analysis_type: Optional[str] = None) -> int:
        """Get reports count"""
        return self.analysis_report_model.get_reports_count(user_id, analysis_type)
