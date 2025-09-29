from typing import Dict, Any
import logging

from app.models.database import DatabaseInterface, UserRepository, SessionRepository, DocumentRepository, AnalysisReportRepository, TaskReportMappingRepository
from app.models.sqlite_db import (
    SQLiteDatabase, SQLiteUserRepository, SQLiteSessionRepository, 
    SQLiteDocumentRepository, SQLiteAnalysisReportRepository, SQLiteTaskReportMappingRepository
)
from app.models.mongodb_sync_db import (
    MongoDBDatabase, MongoDBUserRepository, MongoDBSessionRepository,
    MongoDBDocumentRepository, MongoDBAnalysisReportRepository, MongoDBTaskReportMappingRepository
)
from app.models.auth_models import User, Session
from app.models.document_models import Document, AnalysisReport
from app.models.task_report_mapping_models import TaskReportMapping

logger = logging.getLogger(__name__)


class DatabaseFactory:
    """Factory class for creating database instances and repositories"""
    
    @staticmethod
    def create_database(db_type: str = "sqlite", **kwargs) -> DatabaseInterface:
        """Create a database instance based on type"""
        if db_type.lower() == "sqlite":
            db_path = kwargs.get("db_path", "auth.db")
            return SQLiteDatabase(db_path)
        elif db_type.lower() == "mongodb":
            connection_string = kwargs.get("connection_string", "mongodb://localhost:27017")
            database_name = kwargs.get("database_name", "financial_analyzer")
            return MongoDBDatabase(connection_string, database_name)
        else:
            raise ValueError(f"Unsupported database type: {db_type}. Supported types: sqlite, mongodb")
    
    @staticmethod
    def create_repositories(db: DatabaseInterface) -> Dict[str, Any]:
        """Create all repository instances for a database"""
        if isinstance(db, SQLiteDatabase):
            return {
                "user_repo": SQLiteUserRepository(db),
                "session_repo": SQLiteSessionRepository(db),
                "document_repo": SQLiteDocumentRepository(db),
                "analysis_report_repo": SQLiteAnalysisReportRepository(db),
                "task_report_mapping_repo": SQLiteTaskReportMappingRepository(db)
            }
        elif isinstance(db, MongoDBDatabase):
            return {
                "user_repo": MongoDBUserRepository(db),
                "session_repo": MongoDBSessionRepository(db),
                "document_repo": MongoDBDocumentRepository(db),
                "analysis_report_repo": MongoDBAnalysisReportRepository(db),
                "task_report_mapping_repo": MongoDBTaskReportMappingRepository(db)
            }
        else:
            raise ValueError(f"Unsupported database type: {type(db)}")
    
    @staticmethod
    def create_models(repositories: Dict[str, Any]) -> Dict[str, Any]:
        """Create all model instances using repositories"""
        return {
            "user": User(repositories["user_repo"], repositories["session_repo"]),
            "session": Session(repositories["session_repo"]),
            "document": Document(repositories["document_repo"]),
            "analysis_report": AnalysisReport(repositories["analysis_report_repo"]),
            "task_report_mapping": TaskReportMapping(repositories["task_report_mapping_repo"])
        }


class ModelManager:
    """Central manager for all models and database operations"""
    
    def __init__(self, db_type: str = "sqlite", **db_kwargs):
        self.db_type = db_type
        self.db = DatabaseFactory.create_database(db_type, **db_kwargs)
        self.repositories = DatabaseFactory.create_repositories(self.db)
        self.models = DatabaseFactory.create_models(self.repositories)
        
        logger.info(f"ModelManager initialized with {db_type} database")
    
    def get_user_model(self) -> User:
        """Get user model instance"""
        return self.models["user"]
    
    def get_session_model(self) -> Session:
        """Get session model instance"""
        return self.models["session"]
    
    def get_document_model(self) -> Document:
        """Get document model instance"""
        return self.models["document"]
    
    def get_analysis_report_model(self) -> AnalysisReport:
        """Get analysis report model instance"""
        return self.models["analysis_report"]
    
    def get_task_report_mapping_model(self) -> TaskReportMapping:
        """Get task-report mapping model instance"""
        return self.models["task_report_mapping"]
    
    def get_database(self) -> DatabaseInterface:
        """Get database instance"""
        return self.db
    
    def close(self):
        """Close database connections"""
        self.db.close_connection()
        logger.info("Database connections closed")


# Global model manager instance
# This can be configured via environment variables or config files
def get_model_manager() -> ModelManager:
    """Get the global model manager instance"""
    # In a real application, you might want to use dependency injection
    # or a singleton pattern here
    if not hasattr(get_model_manager, '_instance'):
        from app.config import DatabaseConfig
        db_config = DatabaseConfig.get_database_config()
        
        # Try to create the configured database, fall back to SQLite if it fails
        try:
            get_model_manager._instance = ModelManager(**db_config)
            logger.info(f"ModelManager initialized with {db_config['db_type']} database")
        except Exception as e:
            logger.warning(f"Failed to initialize {db_config['db_type']} database: {e}")
            logger.info("Falling back to SQLite database")
            # Fall back to SQLite
            fallback_config = {
                "db_type": "sqlite",
                "db_path": "auth.db"
            }
            get_model_manager._instance = ModelManager(**fallback_config)
            logger.info("ModelManager initialized with SQLite database (fallback)")
    
    return get_model_manager._instance


# Convenience functions for getting specific models
def get_user_model() -> User:
    """Get user model instance"""
    return get_model_manager().get_user_model()


def get_session_model() -> Session:
    """Get session model instance"""
    return get_model_manager().get_session_model()


def get_document_model() -> Document:
    """Get document model instance"""
    return get_model_manager().get_document_model()


def get_analysis_report_model() -> AnalysisReport:
    """Get analysis report model instance"""
    return get_model_manager().get_analysis_report_model()


def get_task_report_mapping_model() -> TaskReportMapping:
    """Get task-report mapping model instance"""
    return get_model_manager().get_task_report_mapping_model()
