"""
Synchronous MongoDB Database Implementation
==========================================

This module provides a synchronous MongoDB implementation using pymongo
to avoid async/await issues in the FastAPI application.
"""

import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from bson import ObjectId

import pymongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure

from app.models.database import (
    DatabaseInterface, UserRepository, SessionRepository, 
    DocumentRepository, AnalysisReportRepository
)

logger = logging.getLogger(__name__)


class MongoDBDatabase(DatabaseInterface):
    """Synchronous MongoDB database implementation"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017", database_name: str = "financial_analyzer"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.db: Optional[pymongo.database.Database] = None
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize MongoDB database with required collections and indexes"""
        try:
            # Create synchronous client
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            
            # Create collections and indexes
            self._create_collections()
            self._create_indexes()
            
            logger.info(f"MongoDB database '{self.database_name}' initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MongoDB database: {str(e)}")
            raise
    
    def _create_collections(self):
        """Create required collections"""
        collections = ['users', 'sessions', 'refresh_tokens', 'documents', 'analysis_reports']
        for collection_name in collections:
            if collection_name not in self.db.list_collection_names():
                self.db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
    
    def _create_indexes(self):
        """Create indexes for better performance"""
        try:
            # Users collection indexes
            self.db.users.create_index("username", unique=True)
            self.db.users.create_index("email", unique=True)
            
            # Sessions collection indexes
            self.db.sessions.create_index("user_id")
            self.db.sessions.create_index("session_token", unique=True)
            self.db.sessions.create_index("expires_at")
            
            # Refresh tokens collection indexes
            self.db.refresh_tokens.create_index("user_id")
            self.db.refresh_tokens.create_index("token", unique=True)
            self.db.refresh_tokens.create_index("expires_at")
            
            # Documents collection indexes
            self.db.documents.create_index("user_id")
            self.db.documents.create_index("original_name")
            self.db.documents.create_index("stored_name", unique=True)
            
            # Analysis reports collection indexes
            self.db.analysis_reports.create_index("user_id")
            self.db.analysis_reports.create_index("document_id")
            self.db.analysis_reports.create_index("analysis_type")
            self.db.analysis_reports.create_index("created_at")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


class MongoDBUserRepository(UserRepository):
    """Synchronous MongoDB user repository implementation"""
    
    def __init__(self, db: MongoDBDatabase):
        self.db = db
    
    def create_user(self, username: str, email: str, password_hash: str, is_admin: bool = False) -> int:
        """Create a new user"""
        try:
            user_doc = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "is_active": True,
                "is_admin": is_admin,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = self.db.db.users.insert_one(user_doc)
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            if "username" in str(e):
                raise ValueError("Username already exists")
            elif "email" in str(e):
                raise ValueError("Email already exists")
            else:
                raise ValueError("User already exists")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user_doc = self.db.db.users.find_one({"_id": ObjectId(str(user_id))})
            if user_doc:
                return self._convert_user_doc(user_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            user_doc = self.db.db.users.find_one({"username": username})
            if user_doc:
                return self._convert_user_doc(user_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user_doc = self.db.db.users.find_one({"email": email})
            if user_doc:
                return self._convert_user_doc(user_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user information"""
        try:
            # Convert user_id to ObjectId
            user_object_id = ObjectId(str(user_id))
            
            # Add updated_at timestamp
            kwargs['updated_at'] = datetime.utcnow()
            
            result = self.db.db.users.update_one(
                {"_id": user_object_id},
                {"$set": kwargs}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        try:
            user_object_id = ObjectId(str(user_id))
            result = self.db.db.users.delete_one({"_id": user_object_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise
    
    def list_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List users with pagination"""
        try:
            users = self.db.db.users.find().skip(offset).limit(limit).sort("created_at", -1)
            return [self._convert_user_doc(user) for user in users]
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            raise
    
    def _convert_user_doc(self, user_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to user dict"""
        return {
            "id": str(user_doc["_id"]),
            "username": user_doc["username"],
            "email": user_doc["email"],
            "password_hash": user_doc["password_hash"],
            "is_active": user_doc.get("is_active", True),
            "is_admin": user_doc.get("is_admin", False),
            "created_at": user_doc["created_at"].isoformat() if isinstance(user_doc["created_at"], datetime) else str(user_doc["created_at"]),
            "updated_at": user_doc["updated_at"].isoformat() if isinstance(user_doc["updated_at"], datetime) else str(user_doc["updated_at"])
        }


class MongoDBSessionRepository(SessionRepository):
    """Synchronous MongoDB session repository implementation"""
    
    def __init__(self, db: MongoDBDatabase):
        self.db = db
    
    def create_session(self, user_id: str, session_token: str, refresh_token: str, expires_at: datetime) -> str:
        """Create a new session and return session ID"""
        try:
            session_doc = {
                "user_id": str(user_id),
                "session_token": session_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "created_at": datetime.utcnow()
            }
            result = self.db.db.sessions.insert_one(session_doc)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    def get_session_by_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session by session token"""
        try:
            session_doc = self.db.db.sessions.find_one({"session_token": session_token})
            if session_doc:
                return self._convert_session_doc(session_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting session by token: {str(e)}")
            raise
    
    def get_session_by_refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Get session by refresh token"""
        try:
            session_doc = self.db.db.sessions.find_one({"refresh_token": refresh_token})
            if session_doc:
                return self._convert_session_doc(session_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting session by refresh token: {str(e)}")
            raise
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session information"""
        try:
            session_object_id = ObjectId(str(session_id))
            result = self.db.db.sessions.update_one(
                {"_id": session_object_id},
                {"$set": kwargs}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            raise
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke a session"""
        try:
            session_object_id = ObjectId(str(session_id))
            result = self.db.db.sessions.delete_one({"_id": session_object_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error revoking session: {str(e)}")
            raise
    
    def revoke_user_sessions(self, user_id: str) -> bool:
        """Revoke all sessions for a user"""
        try:
            result = self.db.db.sessions.delete_many({"user_id": str(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error revoking user sessions: {str(e)}")
            raise
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions"""
        try:
            result = self.db.db.sessions.delete_many({"expires_at": {"$lt": datetime.utcnow()}})
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
            raise
    
    def _convert_session_doc(self, session_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to session dict"""
        return {
            "id": str(session_doc["_id"]),
            "user_id": session_doc["user_id"],
            "session_token": session_doc["session_token"],
            "expires_at": session_doc["expires_at"].isoformat() if isinstance(session_doc["expires_at"], datetime) else str(session_doc["expires_at"]),
            "created_at": session_doc["created_at"].isoformat() if isinstance(session_doc["created_at"], datetime) else str(session_doc["created_at"])
        }


class MongoDBDocumentRepository(DocumentRepository):
    """Synchronous MongoDB document repository implementation"""
    
    def __init__(self, db: MongoDBDatabase):
        self.db = db
    
    def create_document(self, user_id: int, original_name: str, stored_name: str, 
                       path: str, size_bytes: int, checksum: Optional[str] = None) -> int:
        """Create a new document record"""
        try:
            document_doc = {
                "user_id": str(user_id),
                "original_name": original_name,
                "stored_name": stored_name,
                "path": path,
                "size_bytes": size_bytes,
                "checksum": checksum,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = self.db.db.documents.insert_one(document_doc)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    def get_document(self, document_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID for a specific user"""
        try:
            document_doc = self.db.db.documents.find_one({
                "_id": ObjectId(str(document_id)),
                "user_id": str(user_id)
            })
            if document_doc:
                return self._convert_document_doc(document_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise
    
    def get_user_documents(self, user_id: str, search_query: Optional[str] = None,
                          limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get documents for a user with optional search"""
        try:
            query = {"user_id": str(user_id)}
            if search_query:
                query["original_name"] = {"$regex": search_query, "$options": "i"}
            
            documents = self.db.db.documents.find(query).skip(offset).limit(limit).sort("created_at", -1)
            return [self._convert_document_doc(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            raise
    
    def delete_document(self, document_id: int, user_id: int) -> bool:
        """Delete document for a user"""
        try:
            result = self.db.db.documents.delete_one({
                "_id": ObjectId(str(document_id)),
                "user_id": str(user_id)
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def get_documents_count(self, user_id: int) -> int:
        """Get total count of documents for a user"""
        try:
            count = self.db.db.documents.count_documents({"user_id": str(user_id)})
            return count
        except Exception as e:
            logger.error(f"Error getting documents count: {str(e)}")
            raise
    
    def _convert_document_doc(self, document_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to document dict"""
        return {
            "id": str(document_doc["_id"]),
            "user_id": document_doc["user_id"],
            "original_name": document_doc["original_name"],
            "stored_name": document_doc["stored_name"],
            "path": document_doc["path"],
            "size_bytes": document_doc["size_bytes"],
            "checksum": document_doc["checksum"],
            "created_at": document_doc["created_at"].isoformat() if isinstance(document_doc["created_at"], datetime) else str(document_doc["created_at"]),
            "updated_at": document_doc["updated_at"].isoformat() if isinstance(document_doc["updated_at"], datetime) else str(document_doc["updated_at"])
        }


class MongoDBAnalysisReportRepository(AnalysisReportRepository):
    """Synchronous MongoDB analysis report repository implementation"""
    
    def __init__(self, db: MongoDBDatabase):
        self.db = db
    
    def create_report(self, user_id: int, analysis_type: str, query: str, file_name: str,
                     report_path: str, document_id: Optional[int] = None,
                     summary: Optional[str] = None, status: str = "completed") -> int:
        """Create a new analysis report"""
        try:
            report_doc = {
                "user_id": str(user_id),
                "analysis_type": analysis_type,
                "query": query,
                "file_name": file_name,
                "report_path": report_path,
                "document_id": str(document_id) if document_id else None,
                "summary": summary,
                "status": status,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = self.db.db.analysis_reports.insert_one(report_doc)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating analysis report: {str(e)}")
            raise
    
    def get_report(self, report_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis report by ID for a user"""
        try:
            report_doc = self.db.db.analysis_reports.find_one({
                "_id": ObjectId(str(report_id)),
                "user_id": str(user_id)
            })
            if report_doc:
                return self._convert_report_doc(report_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting report: {str(e)}")
            raise
    
    def get_user_reports(self, user_id: str, analysis_type: Optional[str] = None,
                        search_query: Optional[str] = None, limit: int = 50,
                        offset: int = 0) -> List[Dict[str, Any]]:
        """Get analysis reports for a user with filtering"""
        try:
            query = {"user_id": str(user_id)}
            if analysis_type:
                query["analysis_type"] = analysis_type
            if search_query:
                query["$or"] = [
                    {"query": {"$regex": search_query, "$options": "i"}},
                    {"file_name": {"$regex": search_query, "$options": "i"}},
                    {"summary": {"$regex": search_query, "$options": "i"}}
                ]
            
            reports = self.db.db.analysis_reports.find(query).skip(offset).limit(limit).sort("created_at", -1)
            return [self._convert_report_doc(report) for report in reports]
        except Exception as e:
            logger.error(f"Error getting user reports: {str(e)}")
            raise
    
    def update_report(self, report_id: str, user_id: str, **kwargs) -> bool:
        """Update analysis report"""
        try:
            result = self.db.db.analysis_reports.update_one(
                {"_id": ObjectId(str(report_id)), "user_id": str(user_id)},
                {"$set": kwargs}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating report: {str(e)}")
            raise
    
    def delete_report(self, report_id: str, user_id: str) -> bool:
        """Delete analysis report"""
        try:
            result = self.db.db.analysis_reports.delete_one({
                "_id": ObjectId(str(report_id)),
                "user_id": str(user_id)
            })
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting report: {str(e)}")
            raise
    
    def get_reports_count(self, user_id: str, analysis_type: Optional[str] = None) -> int:
        """Get total count of reports for a user"""
        try:
            query = {"user_id": str(user_id)}
            if analysis_type:
                query["analysis_type"] = analysis_type
            count = self.db.db.analysis_reports.count_documents(query)
            return count
        except Exception as e:
            logger.error(f"Error getting reports count: {str(e)}")
            raise
    
    def _convert_report_doc(self, report_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to report dict"""
        return {
            "id": str(report_doc["_id"]),
            "user_id": report_doc["user_id"],
            "analysis_type": report_doc["analysis_type"],
            "query": report_doc.get("query", ""),
            "file_name": report_doc.get("file_name", ""),
            "report_path": report_doc.get("report_path", ""),
            "document_id": report_doc.get("document_id"),
            "summary": report_doc.get("summary", ""),
            "status": report_doc.get("status", "completed"),
            "created_at": report_doc["created_at"].isoformat() if isinstance(report_doc["created_at"], datetime) else str(report_doc["created_at"]),
            "updated_at": report_doc["updated_at"].isoformat() if isinstance(report_doc["updated_at"], datetime) else str(report_doc["updated_at"])
        }
