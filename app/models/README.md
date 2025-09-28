# Database Models Architecture

This directory contains a refactored, modular database architecture that supports multiple database types and provides clear separation of concerns.

## Architecture Overview

### Core Components

1. **`database.py`** - Abstract base classes and interfaces
2. **`sqlite_db.py`** - SQLite-specific implementations
3. **`auth_models.py`** - Authentication and user management logic
4. **`document_models.py`** - Document and analysis report management
5. **`schemas.py`** - Pydantic models for API validation
6. **`factory.py`** - Factory pattern for creating database instances
7. **`migration.py`** - Backward compatibility layer

### Design Principles

- **Separation of Concerns**: Database logic, business logic, and data validation are separated
- **Interface Segregation**: Clear interfaces for different repository types
- **Dependency Inversion**: High-level modules don't depend on low-level database details
- **Factory Pattern**: Easy switching between different database types
- **Backward Compatibility**: Old code continues to work during migration

## File Structure

```
app/models/
├── database.py          # Abstract interfaces
├── sqlite_db.py         # SQLite implementations
├── auth_models.py       # Authentication logic
├── document_models.py   # Document/analysis logic
├── schemas.py           # Pydantic schemas
├── factory.py           # Factory pattern
├── migration.py         # Backward compatibility
├── auth.py             # DEPRECATED - backward compatibility
└── README.md           # This file
```

## Usage Examples

### New Modular Approach

```python
from app.models.factory import get_user_model, get_document_model

# Get model instances
user_model = get_user_model()
document_model = get_document_model()

# Use the models
user_id = user_model.create_user("john", "john@example.com", "password")
documents = document_model.get_user_documents(user_id)
```

### Backward Compatibility

```python
from app.models.auth import DatabaseManager, User, Session

# Old code still works
db = DatabaseManager()
user = User(db)
session = Session(db)
```

## Database Support

### Current Support
- **SQLite**: Full support with `SQLiteDatabase`

### Future Support (Easy to Add)
- **PostgreSQL**: Create `PostgreSQLDatabase` class
- **MySQL**: Create `MySQLDatabase` class
- **MongoDB**: Create `MongoDatabase` class

### Adding New Database Type

1. Create new database class implementing `DatabaseInterface`
2. Create repository classes implementing respective interfaces
3. Update `DatabaseFactory` to support new type
4. Add configuration options

Example:
```python
class PostgreSQLDatabase(DatabaseInterface):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.init_database()
    
    def init_database(self):
        # PostgreSQL-specific initialization
        pass
```

## Repository Pattern

Each repository handles a specific domain:

- **`UserRepository`**: User CRUD operations
- **`SessionRepository`**: Session management
- **`DocumentRepository`**: Document management
- **`AnalysisReportRepository`**: Analysis report management

## Model Classes

Model classes contain business logic and use repositories for data access:

- **`User`**: User authentication and management
- **`Session`**: Session management and validation
- **`Document`**: File upload and management
- **`AnalysisReport`**: Analysis report creation and management

## Pydantic Schemas

All API request/response models are defined in `schemas.py`:

- **User schemas**: `UserCreate`, `UserResponse`, `UserUpdate`
- **Auth schemas**: `LoginRequest`, `LoginResponse`, `RefreshTokenRequest`
- **Document schemas**: `DocumentResponse`, `DocumentListResponse`
- **Analysis schemas**: `AnalysisReportResponse`, `AnalysisReportListResponse`

## Migration Guide

### From Old Structure

1. **Immediate**: No changes needed - backward compatibility maintained
2. **Gradual**: Update imports to use new factory functions
3. **Complete**: Remove old `auth.py` file and update all imports

### Update Imports

```python
# Old
from app.models.auth import DatabaseManager, User, Session

# New
from app.models.factory import get_user_model, get_session_model
```

## Configuration

Database type can be configured via environment variables:

```python
# In your application startup
import os
from app.models.factory import ModelManager

db_type = os.getenv("DATABASE_TYPE", "sqlite")
db_kwargs = {"db_path": os.getenv("DATABASE_PATH", "auth.db")}

model_manager = ModelManager(db_type, **db_kwargs)
```

## Benefits

1. **Maintainability**: Clear separation makes code easier to maintain
2. **Testability**: Each component can be tested independently
3. **Scalability**: Easy to add new database types or features
4. **Flexibility**: Can switch database types without changing business logic
5. **Type Safety**: Full type hints and Pydantic validation
6. **Backward Compatibility**: Existing code continues to work

## Future Enhancements

- Add connection pooling
- Implement database migrations
- Add caching layer
- Support for read replicas
- Add database health checks
- Implement transaction management
