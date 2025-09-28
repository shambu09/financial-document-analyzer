import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv(".env")

class DatabaseConfig:
    """Database configuration management"""
    
    @staticmethod
    def get_database_config() -> Dict[str, Any]:
        """Get database configuration from environment variables"""
        db_type = os.getenv("DATABASE_TYPE", "sqlite").lower()
        
        if db_type == "sqlite":
            return {
                "db_type": "sqlite",
                "db_path": os.getenv("SQLITE_DB_PATH", "auth.db")
            }
        elif db_type == "mongodb":
            return {
                "db_type": "mongodb",
                "connection_string": os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017"),
                "database_name": os.getenv("MONGODB_DATABASE_NAME", "financial_analyzer")
            }
        else:
            raise ValueError(f"Unsupported database type: {db_type}. Supported types: sqlite, mongodb")
    
    @staticmethod
    def get_jwt_config() -> Dict[str, Any]:
        """Get JWT configuration from environment variables"""
        return {
            "secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production"),
            "algorithm": os.getenv("JWT_ALGORITHM", "HS256"),
            "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            "refresh_token_expire_days": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        }
    
    @staticmethod
    def get_app_config() -> Dict[str, Any]:
        """Get application configuration from environment variables"""
        return {
            "app_name": os.getenv("APP_NAME", "Financial Document Analyzer API"),
            "app_version": os.getenv("APP_VERSION", "2.0.0"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
            "rate_limit_requests": int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            "rate_limit_window": int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))
        }
