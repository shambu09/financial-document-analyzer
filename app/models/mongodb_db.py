import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError, OperationFailure

from app.models.database import (
    DatabaseInterface, UserRepository, SessionRepository, 
    DocumentRepository, AnalysisReportRepository
)

logger = logging.getLogger(__name__)


class MongoDBDatabase(DatabaseInterface):
    """MongoDB database implementation"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017", database_name: str = "financial_analyzer"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize MongoDB database with required collections and indexes"""
        try:
            # Create async client
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            
            # Run async initialization in a new event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If there's already a running loop, we can't use run_until_complete
                    # Just log that initialization will happen later
                    logger.info(f"MongoDB database '{self.database_name}' connected (async init pending)")
                else:
                    # No running loop, we can use run_until_complete
                    loop.run_until_complete(self._init_collections())
                    logger.info(f"MongoDB database '{self.database_name}' initialized successfully")
            except RuntimeError:
                # No event loop exists, create one
                asyncio.run(self._init_collections())
                logger.info(f"MongoDB database '{self.database_name}' initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MongoDB database: {str(e)}")
            raise
    
    async def _init_collections(self):
        """Initialize collections and indexes"""
        try:
            # Create collections
            collections = ['users', 'sessions', 'refresh_tokens', 'documents', 'analysis_reports']
            
            for collection_name in collections:
                if collection_name not in await self.db.list_collection_names():
                    await self.db.create_collection(collection_name)
            
            # Create indexes for better performance
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Error creating collections and indexes: {str(e)}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            await self.db.users.create_index("username", unique=True)
            await self.db.users.create_index("email", unique=True)
            await self.db.users.create_index("is_active")
            await self.db.users.create_index("created_at")
            
            # Sessions collection indexes
            await self.db.sessions.create_index("session_token", unique=True)
            await self.db.sessions.create_index("refresh_token", unique=True)
            await self.db.sessions.create_index("user_id")
            await self.db.sessions.create_index("expires_at")
            await self.db.sessions.create_index("is_active")
            
            # Refresh tokens collection indexes
            await self.db.refresh_tokens.create_index("token_hash", unique=True)
            await self.db.refresh_tokens.create_index("user_id")
            await self.db.refresh_tokens.create_index("expires_at")
            await self.db.refresh_tokens.create_index("is_revoked")
            
            # Documents collection indexes
            await self.db.documents.create_index([("user_id", 1), ("stored_name", 1)], unique=True)
            await self.db.documents.create_index("user_id")
            await self.db.documents.create_index("original_name")
            await self.db.documents.create_index("created_at")
            
            # Analysis reports collection indexes
            await self.db.analysis_reports.create_index("user_id")
            await self.db.analysis_reports.create_index("analysis_type")
            await self.db.analysis_reports.create_index("created_at")
            await self.db.analysis_reports.create_index([("user_id", 1), ("analysis_type", 1)])
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            raise
    
    def close_connection(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


class MongoDBUserRepository(UserRepository):
    """MongoDB implementation of UserRepository"""
    
    def __init__(self, db: MongoDBDatabase):
        self.db = db
    
    def create_user(self, username: str, email: str, password_hash: str, is_admin: bool = False) -> int:
        """Create a new user and return user ID"""
        try:
            # Run async operation in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._create_user_async(username, email, password_hash, is_admin))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def _create_user_async(self, username: str, email: str, password_hash: str, is_admin: bool = False) -> int:
        """Async implementation of create_user"""
        user_doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "is_active": True,
            "is_admin": is_admin,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.db.db.users.insert_one(user_doc)
        return result.inserted_id
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_user_by_id_async(user_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise
    
    async def _get_user_by_id_async(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Async implementation of get_user_by_id"""
        user_doc = await self.db.db.users.find_one({"_id": ObjectId(str(user_id))})
        if user_doc:
            return self._convert_user_doc(user_doc)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            # Try to get the current event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in an async context, we need to use a different approach
                # Use asyncio.create_task to run in the current loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._get_user_by_username_async(username))
                    return future.result()
            except RuntimeError:
                # No event loop running, create a new one
                return asyncio.run(self._get_user_by_username_async(username))
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            raise
    
    async def _get_user_by_username_async(self, username: str) -> Optional[Dict[str, Any]]:
        """Async implementation of get_user_by_username"""
        user_doc = await self.db.db.users.find_one({"username": username})
        if user_doc:
            return self._convert_user_doc(user_doc)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_user_by_email_async(email))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    async def _get_user_by_email_async(self, email: str) -> Optional[Dict[str, Any]]:
        """Async implementation of get_user_by_email"""
        user_doc = await self.db.db.users.find_one({"email": email})
        if user_doc:
            return self._convert_user_doc(user_doc)
        return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user information"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._update_user_async(user_id, **kwargs))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    async def _update_user_async(self, user_id: int, **kwargs) -> bool:
        """Async implementation of update_user"""
        if not kwargs:
            return True
        
        # Add updated_at timestamp
        kwargs['updated_at'] = datetime.utcnow()
        
        result = await self.db.db.users.update_one(
            {"_id": ObjectId(str(user_id))},
            {"$set": kwargs}
        )
        return result.modified_count > 0
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._delete_user_async(user_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise
    
    async def _delete_user_async(self, user_id: int) -> bool:
        """Async implementation of delete_user"""
        result = await self.db.db.users.delete_one({"_id": ObjectId(str(user_id))})
        return result.deleted_count > 0
    
    def list_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List users with pagination"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._list_users_async(limit, offset))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            raise
    
    async def _list_users_async(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Async implementation of list_users"""
        cursor = self.db.db.users.find().sort("created_at", -1).skip(offset).limit(limit)
        users = []
        async for user_doc in cursor:
            users.append(self._convert_user_doc(user_doc))
        return users
    
    def _convert_user_doc(self, user_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to standard format"""
        return {
            "id": str(user_doc["_id"]),
            "username": user_doc["username"],
            "email": user_doc["email"],
            "password_hash": user_doc["password_hash"],
            "is_active": user_doc.get("is_active", True),
            "is_admin": user_doc.get("is_admin", False),
            "created_at": user_doc["created_at"],
            "updated_at": user_doc["updated_at"]
        }


class MongoDBSessionRepository(SessionRepository):
    """MongoDB implementation of SessionRepository"""
    
    def __init__(self, db: MongoDBDatabase):
        self.db = db
    
    def create_session(self, user_id: int, session_token: str, refresh_token: str, expires_at: datetime) -> int:
        """Create a new session and return session ID"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._create_session_async(user_id, session_token, refresh_token, expires_at))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    async def _create_session_async(self, user_id: int, session_token: str, refresh_token: str, expires_at: datetime) -> int:
        """Async implementation of create_session"""
        session_doc = {
            "user_id": str(user_id),
            "session_token": session_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.db.sessions.insert_one(session_doc)
        return result.inserted_id
    
    def get_session_by_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session by session token"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_session_by_token_async(session_token))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting session by token: {str(e)}")
            raise
    
    async def _get_session_by_token_async(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Async implementation of get_session_by_token"""
        session_doc = await self.db.db.sessions.find_one({
            "session_token": session_token,
            "is_active": True
        })
        if session_doc:
            return self._convert_session_doc(session_doc)
        return None
    
    def get_session_by_refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Get session by refresh token"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_session_by_refresh_token_async(refresh_token))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting session by refresh token: {str(e)}")
            raise
    
    async def _get_session_by_refresh_token_async(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Async implementation of get_session_by_refresh_token"""
        session_doc = await self.db.db.sessions.find_one({
            "refresh_token": refresh_token,
            "is_active": True
        })
        if session_doc:
            return self._convert_session_doc(session_doc)
        return None
    
    def update_session(self, session_id: int, **kwargs) -> bool:
        """Update session information"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._update_session_async(session_id, **kwargs))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            raise
    
    async def _update_session_async(self, session_id: int, **kwargs) -> bool:
        """Async implementation of update_session"""
        if not kwargs:
            return True
        
        result = await self.db.db.sessions.update_one(
            {"_id": ObjectId(str(session_id))},
            {"$set": kwargs}
        )
        return result.modified_count > 0
    
    def revoke_session(self, session_id: int) -> bool:
        """Revoke a session"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._revoke_session_async(session_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error revoking session: {str(e)}")
            raise
    
    async def _revoke_session_async(self, session_id: int) -> bool:
        """Async implementation of revoke_session"""
        result = await self.db.db.sessions.update_one(
            {"_id": ObjectId(str(session_id))},
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0
    
    def revoke_user_sessions(self, user_id: int) -> bool:
        """Revoke all sessions for a user"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._revoke_user_sessions_async(user_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error revoking user sessions: {str(e)}")
            raise
    
    async def _revoke_user_sessions_async(self, user_id: int) -> bool:
        """Async implementation of revoke_user_sessions"""
        result = await self.db.db.sessions.update_many(
            {"user_id": str(user_id)},
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._cleanup_expired_sessions_async())
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
            raise
    
    async def _cleanup_expired_sessions_async(self) -> int:
        """Async implementation of cleanup_expired_sessions"""
        result = await self.db.db.sessions.update_many(
            {"expires_at": {"$lt": datetime.utcnow()}},
            {"$set": {"is_active": False}}
        )
        return result.modified_count
    
    def _convert_session_doc(self, session_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to standard format"""
        return {
            "id": str(session_doc["_id"]),
            "user_id": session_doc["user_id"],
            "session_token": session_doc["session_token"],
            "refresh_token": session_doc["refresh_token"],
            "expires_at": session_doc["expires_at"],
            "is_active": session_doc["is_active"],
            "created_at": session_doc["created_at"]
        }


class MongoDBDocumentRepository(DocumentRepository):
    """MongoDB implementation of DocumentRepository"""
    
    def __init__(self, db: MongoDBDatabase):
        self.db = db
    
    def create_document(self, user_id: int, original_name: str, stored_name: str, 
                       path: str, size_bytes: int, checksum: Optional[str] = None) -> int:
        """Create a new document record and return document ID"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._create_document_async(user_id, original_name, stored_name, path, size_bytes, checksum))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    async def _create_document_async(self, user_id: int, original_name: str, stored_name: str, 
                                   path: str, size_bytes: int, checksum: Optional[str] = None) -> int:
        """Async implementation of create_document"""
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
        
        result = await self.db.db.documents.insert_one(document_doc)
        return result.inserted_id
    
    def get_document(self, document_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID for a specific user"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_document_async(document_id, user_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise
    
    async def _get_document_async(self, document_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Async implementation of get_document"""
        document_doc = await self.db.db.documents.find_one({
            "_id": ObjectId(str(document_id)),
            "user_id": str(user_id)
        })
        if document_doc:
            return self._convert_document_doc(document_doc)
        return None
    
    def get_user_documents(self, user_id: int, search_query: Optional[str] = None,
                          limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get documents for a user with optional search"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_user_documents_async(user_id, search_query, limit, offset))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting user documents: {str(e)}")
            raise
    
    async def _get_user_documents_async(self, user_id: int, search_query: Optional[str] = None,
                                      limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Async implementation of get_user_documents"""
        query = {"user_id": str(user_id)}
        
        if search_query:
            query["original_name"] = {"$regex": search_query, "$options": "i"}
        
        cursor = self.db.db.documents.find(query).sort("created_at", -1).skip(offset).limit(limit)
        documents = []
        async for document_doc in cursor:
            documents.append(self._convert_document_doc(document_doc))
        return documents
    
    def delete_document(self, document_id: int, user_id: int) -> bool:
        """Delete document for a user"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._delete_document_async(document_id, user_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    async def _delete_document_async(self, document_id: int, user_id: int) -> bool:
        """Async implementation of delete_document"""
        result = await self.db.db.documents.delete_one({
            "_id": ObjectId(str(document_id)),
            "user_id": str(user_id)
        })
        return result.deleted_count > 0
    
    def get_documents_count(self, user_id: int) -> int:
        """Get total count of documents for a user"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_documents_count_async(user_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting documents count: {str(e)}")
            raise
    
    async def _get_documents_count_async(self, user_id: int) -> int:
        """Async implementation of get_documents_count"""
        count = await self.db.db.documents.count_documents({"user_id": str(user_id)})
        return count
    
    def _convert_document_doc(self, document_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to standard format"""
        return {
            "id": str(document_doc["_id"]),
            "user_id": document_doc["user_id"],
            "original_name": document_doc["original_name"],
            "stored_name": document_doc["stored_name"],
            "path": document_doc["path"],
            "size_bytes": document_doc["size_bytes"],
            "checksum": document_doc.get("checksum"),
            "created_at": document_doc["created_at"],
            "updated_at": document_doc["updated_at"]
        }


class MongoDBAnalysisReportRepository(AnalysisReportRepository):
    """MongoDB implementation of AnalysisReportRepository"""
    
    def __init__(self, db: MongoDBDatabase):
        self.db = db
    
    def create_report(self, user_id: int, analysis_type: str, query: str, file_name: str,
                     report_path: str, document_id: Optional[int] = None,
                     summary: Optional[str] = None, status: str = "completed") -> int:
        """Create a new analysis report and return report ID"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._create_report_async(user_id, analysis_type, query, file_name, report_path, document_id, summary, status))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error creating analysis report: {str(e)}")
            raise
    
    async def _create_report_async(self, user_id: int, analysis_type: str, query: str, file_name: str,
                                 report_path: str, document_id: Optional[int] = None,
                                 summary: Optional[str] = None, status: str = "completed") -> int:
        """Async implementation of create_report"""
        report_doc = {
            "user_id": str(user_id),
            "document_id": str(document_id) if document_id else None,
            "analysis_type": analysis_type,
            "query": query,
            "file_name": file_name,
            "report_path": report_path,
            "status": status,
            "summary": summary,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.db.db.analysis_reports.insert_one(report_doc)
        return result.inserted_id
    
    def get_report(self, report_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get analysis report by ID for a user"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_report_async(report_id, user_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting analysis report: {str(e)}")
            raise
    
    async def _get_report_async(self, report_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Async implementation of get_report"""
        report_doc = await self.db.db.analysis_reports.find_one({
            "_id": ObjectId(str(report_id)),
            "user_id": str(user_id)
        })
        if report_doc:
            return self._convert_report_doc(report_doc)
        return None
    
    def get_user_reports(self, user_id: int, analysis_type: Optional[str] = None,
                        search_query: Optional[str] = None, limit: int = 50,
                        offset: int = 0) -> List[Dict[str, Any]]:
        """Get analysis reports for a user with filtering"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_user_reports_async(user_id, analysis_type, search_query, limit, offset))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting user analysis reports: {str(e)}")
            raise
    
    async def _get_user_reports_async(self, user_id: int, analysis_type: Optional[str] = None,
                                    search_query: Optional[str] = None, limit: int = 50,
                                    offset: int = 0) -> List[Dict[str, Any]]:
        """Async implementation of get_user_reports"""
        query = {"user_id": str(user_id)}
        
        if analysis_type:
            query["analysis_type"] = analysis_type
        
        if search_query:
            query["$or"] = [
                {"file_name": {"$regex": search_query, "$options": "i"}},
                {"query": {"$regex": search_query, "$options": "i"}},
                {"summary": {"$regex": search_query, "$options": "i"}}
            ]
        
        cursor = self.db.db.analysis_reports.find(query).sort("created_at", -1).skip(offset).limit(limit)
        reports = []
        async for report_doc in cursor:
            reports.append(self._convert_report_doc(report_doc))
        return reports
    
    def update_report(self, report_id: int, user_id: int, **kwargs) -> bool:
        """Update analysis report"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._update_report_async(report_id, user_id, **kwargs))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error updating analysis report: {str(e)}")
            raise
    
    async def _update_report_async(self, report_id: int, user_id: int, **kwargs) -> bool:
        """Async implementation of update_report"""
        if not kwargs:
            return True
        
        # Add updated_at timestamp
        kwargs['updated_at'] = datetime.utcnow()
        
        result = await self.db.db.analysis_reports.update_one(
            {"_id": ObjectId(str(report_id)), "user_id": str(user_id)},
            {"$set": kwargs}
        )
        return result.modified_count > 0
    
    def delete_report(self, report_id: int, user_id: int) -> bool:
        """Delete analysis report"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._delete_report_async(report_id, user_id))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error deleting analysis report: {str(e)}")
            raise
    
    async def _delete_report_async(self, report_id: int, user_id: int) -> bool:
        """Async implementation of delete_report"""
        result = await self.db.db.analysis_reports.delete_one({
            "_id": ObjectId(str(report_id)),
            "user_id": str(user_id)
        })
        return result.deleted_count > 0
    
    def get_reports_count(self, user_id: int, analysis_type: Optional[str] = None) -> int:
        """Get total count of reports for a user"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self._get_reports_count_async(user_id, analysis_type))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error getting analysis reports count: {str(e)}")
            raise
    
    async def _get_reports_count_async(self, user_id: int, analysis_type: Optional[str] = None) -> int:
        """Async implementation of get_reports_count"""
        query = {"user_id": str(user_id)}
        if analysis_type:
            query["analysis_type"] = analysis_type
        
        count = await self.db.db.analysis_reports.count_documents(query)
        return count
    
    def _convert_report_doc(self, report_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to standard format"""
        return {
            "id": str(report_doc["_id"]),
            "user_id": report_doc["user_id"],
            "document_id": report_doc.get("document_id"),
            "analysis_type": report_doc["analysis_type"],
            "query": report_doc["query"],
            "file_name": report_doc["file_name"],
            "report_path": report_doc["report_path"],
            "status": report_doc["status"],
            "summary": report_doc.get("summary"),
            "created_at": report_doc["created_at"],
            "updated_at": report_doc["updated_at"]
        }
