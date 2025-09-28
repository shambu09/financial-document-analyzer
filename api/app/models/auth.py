"""
DEPRECATED: This file is maintained for backward compatibility.
Please use the new modular structure in:
- app.models.database (interfaces)
- app.models.sqlite_db (SQLite implementation)
- app.models.auth_models (authentication logic)
- app.models.document_models (document and analysis logic)
- app.models.factory (factory pattern)
- app.models.schemas (Pydantic schemas)

This file will be removed in a future version.
"""

import logging
from app.models.migration import DatabaseManager, User, Session, AnalysisReport

logger = logging.getLogger(__name__)

# Re-export for backward compatibility
__all__ = ['DatabaseManager', 'User', 'Session', 'AnalysisReport']