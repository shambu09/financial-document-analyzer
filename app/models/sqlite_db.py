import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.models.database import (
    DatabaseInterface, UserRepository, SessionRepository, 
    DocumentRepository, AnalysisReportRepository
)

logger = logging.getLogger(__name__)


class SQLiteDatabase(DatabaseInterface):
    """SQLite database implementation"""
    
    def __init__(self, db_path: str = "auth.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        is_admin BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                
                # Create sessions table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_token TEXT UNIQUE NOT NULL,
                        refresh_token TEXT UNIQUE NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                    """
                )
                
                # Create refresh_tokens table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS refresh_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        token_hash TEXT UNIQUE NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        is_revoked BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                    """
                )
                
                # Create documents table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        original_name TEXT NOT NULL,
                        stored_name TEXT NOT NULL,
                        path TEXT NOT NULL,
                        size_bytes INTEGER NOT NULL,
                        checksum TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, stored_name),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                    """
                )
                
                # Create analysis_reports table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS analysis_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        document_id INTEGER,
                        analysis_type TEXT NOT NULL,
                        query TEXT NOT NULL,
                        file_name TEXT NOT NULL,
                        report_path TEXT NOT NULL,
                        status TEXT DEFAULT 'completed',
                        summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (document_id) REFERENCES documents (id)
                    )
                    """
                )
                
                conn.commit()
                logger.info("SQLite database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {str(e)}")
            raise
    
    def close_connection(self) -> None:
        """SQLite doesn't need explicit connection closing"""
        pass


class SQLiteUserRepository(UserRepository):
    """SQLite implementation of UserRepository"""
    
    def __init__(self, db: SQLiteDatabase):
        self.db = db
    
    def create_user(self, username: str, email: str, password_hash: str, is_admin: bool = False) -> int:
        """Create a new user and return user ID"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (username, email, password_hash, is_admin)
                    VALUES (?, ?, ?, ?)
                    """,
                    (username, email, password_hash, is_admin)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, password_hash, is_active, is_admin, created_at, updated_at FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "password_hash": row[3],
                        "is_active": bool(row[4]),
                        "is_admin": bool(row[5]),
                        "created_at": row[6],
                        "updated_at": row[7]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, password_hash, is_active, is_admin, created_at, updated_at FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "password_hash": row[3],
                        "is_active": bool(row[4]),
                        "is_admin": bool(row[5]),
                        "created_at": row[6],
                        "updated_at": row[7]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, password_hash, is_active, is_admin, created_at, updated_at FROM users WHERE email = ?",
                    (email,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "password_hash": row[3],
                        "is_active": bool(row[4]),
                        "is_admin": bool(row[5]),
                        "created_at": row[6],
                        "updated_at": row[7]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        try:
            if not kwargs:
                return True
            
            set_clauses = []
            values = []
            for key, value in kwargs.items():
                if key in ['username', 'email', 'password_hash', 'is_active', 'is_admin']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return True
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?",
                    values
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise
    
    def list_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List users with pagination"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, password_hash, is_active, is_admin, created_at, updated_at FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
                rows = cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "username": row[1],
                        "email": row[2],
                        "password_hash": row[3],
                        "is_active": bool(row[4]),
                        "is_admin": bool(row[5]),
                        "created_at": row[6],
                        "updated_at": row[7]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            raise


class SQLiteSessionRepository(SessionRepository):
    """SQLite implementation of SessionRepository"""
    
    def __init__(self, db: SQLiteDatabase):
        self.db = db
    
    def create_session(self, user_id: int, session_token: str, refresh_token: str, expires_at: datetime) -> int:
        """Create a new session and return session ID"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO sessions (user_id, session_token, refresh_token, expires_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, session_token, refresh_token, expires_at)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    def get_session_by_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session by session token"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, user_id, session_token, refresh_token, expires_at, is_active, created_at FROM sessions WHERE session_token = ? AND is_active = 1",
                    (session_token,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "user_id": row[1],
                        "session_token": row[2],
                        "refresh_token": row[3],
                        "expires_at": row[4],
                        "is_active": bool(row[5]),
                        "created_at": row[6]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting session by token: {str(e)}")
            raise
    
    def get_session_by_refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Get session by refresh token"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, user_id, session_token, refresh_token, expires_at, is_active, created_at FROM sessions WHERE refresh_token = ? AND is_active = 1",
                    (refresh_token,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "user_id": row[1],
                        "session_token": row[2],
                        "refresh_token": row[3],
                        "expires_at": row[4],
                        "is_active": bool(row[5]),
                        "created_at": row[6]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting session by refresh token: {str(e)}")
            raise
    
    def update_session(self, session_id: int, **kwargs) -> bool:
        """Update session information"""
        try:
            if not kwargs:
                return True
            
            set_clauses = []
            values = []
            for key, value in kwargs.items():
                if key in ['session_token', 'refresh_token', 'expires_at', 'is_active']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return True
            
            values.append(session_id)
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE sessions SET {', '.join(set_clauses)} WHERE id = ?",
                    values
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            raise
    
    def revoke_session(self, session_id: int) -> bool:
        """Revoke a session"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sessions SET is_active = 0 WHERE id = ?",
                    (session_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error revoking session: {str(e)}")
            raise
    
    def revoke_user_sessions(self, user_id: int) -> bool:
        """Revoke all sessions for a user"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sessions SET is_active = 0 WHERE user_id = ?",
                    (user_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error revoking user sessions: {str(e)}")
            raise
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sessions SET is_active = 0 WHERE expires_at <= ?",
                    (datetime.now(),)
                )
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
            raise


class SQLiteDocumentRepository(DocumentRepository):
    """SQLite implementation of DocumentRepository"""
    
    def __init__(self, db: SQLiteDatabase):
        self.db = db
    
    def create_document(self, user_id: int, original_name: str, stored_name: str, 
                       path: str, size_bytes: int, checksum: Optional[str] = None) -> int:
        """Create a new document record and return document ID"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO documents (user_id, original_name, stored_name, path, size_bytes, checksum)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, original_name, stored_name, path, size_bytes, checksum)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    def get_document(self, document_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID for a specific user"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, user_id, original_name, stored_name, path, size_bytes, checksum, created_at, updated_at FROM documents WHERE id = ? AND user_id = ?",
                    (document_id, user_id)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "user_id": row[1],
                        "original_name": row[2],
                        "stored_name": row[3],
                        "path": row[4],
                        "size_bytes": row[5],
                        "checksum": row[6],
                        "created_at": row[7],
                        "updated_at": row[8]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise
    
    def get_user_documents(self, user_id: int, search_query: Optional[str] = None,
                          limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get documents for a user with optional search"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                if search_query:
                    cursor.execute(
                        "SELECT id, user_id, original_name, stored_name, path, size_bytes, checksum, created_at, updated_at FROM documents WHERE user_id = ? AND original_name LIKE ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (user_id, f"%{search_query}%", limit, offset)
                    )
                else:
                    cursor.execute(
                        "SELECT id, user_id, original_name, stored_name, path, size_bytes, checksum, created_at, updated_at FROM documents WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                        (user_id, limit, offset)
                    )
                
                rows = cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "user_id": row[1],
                        "original_name": row[2],
                        "stored_name": row[3],
                        "path": row[4],
                        "size_bytes": row[5],
                        "checksum": row[6],
                        "created_at": row[7],
                        "updated_at": row[8]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            raise
    
    def delete_document(self, document_id: int, user_id: int) -> bool:
        """Delete document for a user"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM documents WHERE id = ? AND user_id = ?",
                    (document_id, user_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def get_documents_count(self, user_id: int) -> int:
        """Get total count of documents for a user"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM documents WHERE user_id = ?",
                    (user_id,)
                )
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting documents count: {str(e)}")
            raise


class SQLiteAnalysisReportRepository(AnalysisReportRepository):
    """SQLite implementation of AnalysisReportRepository"""
    
    def __init__(self, db: SQLiteDatabase):
        self.db = db
    
    def create_report(self, user_id: int, analysis_type: str, query: str, file_name: str,
                     report_path: str, document_id: Optional[int] = None,
                     summary: Optional[str] = None, status: str = "completed") -> int:
        """Create a new analysis report and return report ID"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO analysis_reports 
                    (user_id, document_id, analysis_type, query, file_name, report_path, status, summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, document_id, analysis_type, query, file_name, report_path, status, summary)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating analysis report: {str(e)}")
            raise
    
    def get_report(self, report_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get analysis report by ID for a user"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, user_id, document_id, analysis_type, query, file_name, 
                           report_path, status, summary, created_at, updated_at
                    FROM analysis_reports 
                    WHERE id = ? AND user_id = ?
                    """,
                    (report_id, user_id)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "user_id": row[1],
                        "document_id": row[2],
                        "analysis_type": row[3],
                        "query": row[4],
                        "file_name": row[5],
                        "report_path": row[6],
                        "status": row[7],
                        "summary": row[8],
                        "created_at": row[9],
                        "updated_at": row[10]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting analysis report: {str(e)}")
            raise
    
    def get_user_reports(self, user_id: int, analysis_type: Optional[str] = None,
                        search_query: Optional[str] = None, limit: int = 50,
                        offset: int = 0) -> List[Dict[str, Any]]:
        """Get analysis reports for a user with filtering"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with optional filters
                where_conditions = ["user_id = ?"]
                params = [user_id]
                
                if analysis_type:
                    where_conditions.append("analysis_type = ?")
                    params.append(analysis_type)
                
                if search_query:
                    where_conditions.append("(file_name LIKE ? OR query LIKE ? OR summary LIKE ?)")
                    search_term = f"%{search_query}%"
                    params.extend([search_term, search_term, search_term])
                
                where_clause = " AND ".join(where_conditions)
                
                cursor.execute(
                    f"""
                    SELECT id, user_id, document_id, analysis_type, query, file_name, 
                           report_path, status, summary, created_at, updated_at
                    FROM analysis_reports 
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    params + [limit, offset]
                )
                
                rows = cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "user_id": row[1],
                        "document_id": row[2],
                        "analysis_type": row[3],
                        "query": row[4],
                        "file_name": row[5],
                        "report_path": row[6],
                        "status": row[7],
                        "summary": row[8],
                        "created_at": row[9],
                        "updated_at": row[10]
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"Error getting user analysis reports: {str(e)}")
            raise
    
    def update_report(self, report_id: int, user_id: int, **kwargs) -> bool:
        """Update analysis report"""
        try:
            if not kwargs:
                return True
            
            set_clauses = []
            values = []
            for key, value in kwargs.items():
                if key in ['summary', 'status']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return True
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.extend([report_id, user_id])
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE analysis_reports SET {', '.join(set_clauses)} WHERE id = ? AND user_id = ?",
                    values
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating analysis report: {str(e)}")
            raise
    
    def delete_report(self, report_id: int, user_id: int) -> bool:
        """Delete analysis report"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM analysis_reports WHERE id = ? AND user_id = ?",
                    (report_id, user_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting analysis report: {str(e)}")
            raise
    
    def get_reports_count(self, user_id: int, analysis_type: Optional[str] = None) -> int:
        """Get total count of reports for a user"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                if analysis_type:
                    cursor.execute(
                        "SELECT COUNT(*) FROM analysis_reports WHERE user_id = ? AND analysis_type = ?",
                        (user_id, analysis_type)
                    )
                else:
                    cursor.execute(
                        "SELECT COUNT(*) FROM analysis_reports WHERE user_id = ?",
                        (user_id,)
                    )
                
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting analysis reports count: {str(e)}")
            raise
