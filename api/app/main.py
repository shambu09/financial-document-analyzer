from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import create_auth_middleware, create_rate_limit_middleware
from app.api.routers.auth import router as auth_router
from app.api.routers.documents import router as documents_router
from app.api.routers.analysis import router as analysis_router
from app.api.routers.reports import router as reports_router
from app.api.routers.tasks import router as tasks_router
from app.api.routers.task_mappings import router as task_mappings_router
from app.config import DatabaseConfig


def create_app() -> FastAPI:
    # Get configuration
    db_config = DatabaseConfig.get_database_config()
    app_config = DatabaseConfig.get_app_config()
    
    app = FastAPI(
        title=app_config["app_name"],
        description="FastAPI application with JWT auth, document management, and CrewAI agents",
        version=app_config["app_version"],
        debug=app_config["debug"]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config["cors_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers must be added before wrapping with custom middleware
    app.include_router(auth_router)
    app.include_router(documents_router)
    app.include_router(analysis_router)
    app.include_router(reports_router)
    app.include_router(tasks_router)
    app.include_router(task_mappings_router)

    # Basic endpoints
    @app.get("/")
    async def root():
        # Get actual database type being used
        from app.models.factory import get_model_manager
        actual_db_type = get_model_manager().db_type
        return {
            "message": f"{app_config['app_name']} is running", 
            "version": app_config["app_version"],
            "database": actual_db_type
        }

    @app.get("/health")
    async def health():
        # Get actual database type being used
        from app.models.factory import get_model_manager
        actual_db_type = get_model_manager().db_type
        return {
            "status": "healthy",
            "version": app_config["app_version"],
            "database": actual_db_type,
            "available_analysis_types": ["comprehensive", "investment", "risk", "verification"],
        }

    # Middlewares (wrap AFTER routers are added)
    app = create_rate_limit_middleware(
        app, 
        max_requests=app_config["rate_limit_requests"], 
        window_seconds=app_config["rate_limit_window"]
    )
    app = create_auth_middleware(app, protected_paths=["/analysis", "/documents", "/reports"])  # protect analysis, documents, and reports

    return app


app = create_app()


