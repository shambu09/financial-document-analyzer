# Financial Document Analyzer - System Design

## Table of Contents
1. [Quick Start](#quick-start)
2. [Project Overview](#project-overview)
3. [System Architecture](#system-architecture)
4. [Backend API Features](#backend-api-features)
5. [Database Design](#database-design)
6. [AI-Powered Analysis Engine](#ai-powered-analysis-engine)
7. [Security & Authentication](#security--authentication)
8. [Key Architectural Decisions](#key-architectural-decisions)
9. [Technology Stack](#technology-stack)
10. [Deployment & Scalability](#deployment--scalability)
11. [API Documentation](#api-documentation)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key

### 1. Environment Setup
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# Required: OPENAI_API_KEY, MONGODB_CONNECTION_STRING
```

### 2. Start Services
```bash
# Start all services (API, Database, Redis, Celery)
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Access the API
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Task Monitor**: http://localhost:5555
- **Database UI**: http://localhost:8081

### 4. Test the API
```bash
# Register a user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### 5. Upload and Analyze Documents
```bash
# Upload a document for analysis
curl -X POST "http://localhost:8000/analysis/comprehensive" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@your_document.pdf" \
  -F "query=Analyze this financial document"
```

## Project Overview

The Financial Document Analyzer is a production-grade, enterprise-level system that processes financial documents using AI-powered analysis agents. The system provides comprehensive financial insights, investment recommendations, risk assessments, and document verification through a robust REST API.

### Core Value Proposition
- **AI-Powered Analysis**: Leverages CrewAI framework with specialized financial agents
- **Multi-Format Support**: Handles PDF, TXT, and other financial document formats
- **Real-time Processing**: Asynchronous background processing with status tracking
- **Enterprise Security**: JWT-based authentication with role-based access control
- **Scalable Architecture**: Modular design supporting multiple database backends

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   Web Frontend  │    │   Mobile Apps   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     FastAPI Gateway      │
                    │   (Authentication &      │
                    │    Rate Limiting)        │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    API Router Layer      │
                    │  (Documents, Analysis,   │
                    │   Reports, Auth)         │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Business Logic Layer   │
                    │  (Models, Services,      │
                    │   Background Tasks)      │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    AI Analysis Engine    │
                    │  (CrewAI Agents, Tools,  │
                    │   LLM Integration)       │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Data Layer            │
                    │  (Database, File Storage,│
                    │   Report Generation)     │
                    └───────────────────────────┘
```

### Component Architecture

```
app/
├── api/                    # API Layer
│   ├── routers/           # FastAPI route handlers
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── documents.py  # Document management
│   │   ├── analysis.py   # Analysis endpoints
│   │   └── reports.py    # Report management
│   └── middleware.py      # CORS, rate limiting, auth
├── domain/                # Business Logic
│   ├── agents.py         # CrewAI financial agents
│   └── task.py           # Analysis task definitions
├── models/                # Data Layer
│   ├── database.py       # Abstract interfaces
│   ├── sqlite_db.py      # SQLite implementation
│   ├── mongodb_db.py     # MongoDB implementation
│   ├── schemas.py        # Pydantic models
│   └── factory.py        # Database factory pattern
├── services/              # Service Layer
│   ├── tools.py          # CrewAI tools
│   └── background_tasks.py # Async processing
└── config.py             # Configuration management
```

## Backend API Features

### Core API Capabilities

#### 1. **Document Management System**
- **Multi-Format Upload**: Support for PDF, TXT, and other financial document formats
- **File Storage**: Secure file storage in `data/` directory with user isolation
- **Document Metadata**: Comprehensive metadata tracking (size, type, upload date, user)
- **Document Search**: Full-text search across document names and metadata
- **Document History**: Complete audit trail of document operations
- **File Validation**: Format validation and security checks

#### 2. **AI-Powered Financial Analysis**
- **Comprehensive Analysis**: Complete financial document analysis with metrics extraction
- **Investment Analysis**: Investment recommendations with risk-return profiles
- **Risk Assessment**: Multi-dimensional risk analysis with scoring
- **Document Verification**: Validation of financial document authenticity
- **Confidence Scoring**: AI confidence levels for all analysis results
- **Market Context**: Integration with external market data and benchmarks

#### 3. **Asynchronous Processing**
- **Background Tasks**: Non-blocking analysis processing using FastAPI BackgroundTasks
- **Status Tracking**: Real-time status updates (pending → in_progress → completed/failed)
- **Progress Monitoring**: Detailed progress tracking for long-running operations
- **Error Handling**: Comprehensive error handling and recovery mechanisms
- **Resource Management**: Thread pool management for CPU-intensive operations

#### 4. **Report Management System**
- **Report Generation**: Automated Markdown report generation
- **Report Storage**: Organized storage in `outputs/` directory
- **Report Retrieval**: Multiple retrieval methods (download, content API, metadata)
- **Report History**: Complete analysis history per user
- **Report Search**: Search across report content and metadata
- **Report Deletion**: Secure report deletion with cleanup

#### 5. **User Authentication & Authorization**
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Admin and user roles with different permissions
- **Session Management**: Comprehensive session tracking and management
- **Password Security**: Bcrypt hashing with salt
- **Token Refresh**: Automatic token refresh mechanism
- **Multi-User Support**: Complete user management system

#### 6. **API Management & Monitoring**
- **Rate Limiting**: Configurable rate limiting per user/IP
- **CORS Support**: Cross-origin resource sharing configuration
- **Request Validation**: Comprehensive input validation using Pydantic
- **Error Handling**: Detailed error responses with proper HTTP status codes
- **Logging**: Comprehensive logging throughout the application
- **Health Checks**: System health monitoring endpoints

### API Endpoints Overview

#### Authentication Endpoints
```
POST /auth/register          # User registration
POST /auth/login            # User login
POST /auth/refresh          # Token refresh
POST /auth/logout           # User logout
GET  /auth/me              # Current user info
PUT  /auth/me              # Update user info
POST /auth/change-password  # Change password
GET  /auth/users           # List users (admin)
DELETE /auth/users/{id}    # Delete user (admin)
```

#### Document Management Endpoints
```
GET    /documents/         # List user documents
POST   /documents/upload   # Upload document
GET    /documents/{id}     # Get document details
DELETE /documents/{id}     # Delete document
GET    /documents/{id}/download # Download document
```

#### Analysis Endpoints
```
POST /analysis/comprehensive  # Comprehensive analysis
POST /analysis/investment     # Investment analysis
POST /analysis/risk          # Risk assessment
POST /analysis/verify        # Document verification
GET  /analysis/types         # Available analysis types
```

#### Report Management Endpoints
```
GET    /reports/                    # List user reports
GET    /reports/{id}               # Get report details
GET    /reports/{id}/download      # Download report
GET    /reports/{id}/content       # Get report content
DELETE /reports/{id}               # Delete report
```

#### Task Management & Progress APIs
```
GET  /tasks/{task_id}/status       # Get task status and progress
POST /tasks/{task_id}/cancel       # Cancel running task
GET  /tasks/active                 # List active tasks
GET  /tasks/stats                  # Get task statistics
GET  /tasks/queues                 # Get queue information
```

#### Task-Report Mapping APIs
```
GET  /task-mappings/by-task/{task_id}     # Get mapping by task ID
GET  /task-mappings/by-report/{report_id} # Get mapping by report ID
GET  /task-mappings/                      # List user mappings
DELETE /task-mappings/by-task/{task_id}   # Delete mapping by task ID
DELETE /task-mappings/by-report/{report_id} # Delete mapping by report ID
POST /task-mappings/cleanup               # Cleanup old mappings (admin)
```

### Background Task Processing

The system uses **Celery** for asynchronous task processing with Redis as the message broker:

#### Task Status Values
- **PENDING**: Task queued, waiting to be processed
- **STARTED**: Task execution started
- **SUCCESS**: Task completed successfully
- **FAILURE**: Task failed with error
- **RETRY**: Task being retried after failure
- **REVOKED**: Task cancelled/revoked

#### Report Status Values
- **pending**: Report waiting for analysis
- **in_progress**: Analysis currently running
- **completed**: Analysis finished successfully
- **failed**: Analysis failed with error

#### Real-time Progress Tracking
- **Polling**: Automatic status updates every 5 seconds
- **Progress**: Percentage completion (0-100)
- **Messages**: Current operation description
- **Error Handling**: Detailed error information
- **Auto-stop**: Stops polling when task completes

## Database Design

### Multi-Database Architecture

The system supports multiple database backends through a factory pattern:

#### Supported Databases
- **SQLite**: Lightweight, file-based database for development and small deployments
- **MongoDB**: Document-based database for scalable, production deployments

#### Database Schema

##### Users Table
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##### Sessions Table
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    token_hash TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

##### Documents Table
```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    original_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

##### Analysis Reports Table
```sql
CREATE TABLE analysis_reports (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    document_id TEXT,
    analysis_type TEXT NOT NULL,
    query TEXT NOT NULL,
    file_name TEXT NOT NULL,
    report_path TEXT NOT NULL,
    summary TEXT,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (document_id) REFERENCES documents (id)
);
```

### Repository Pattern

The system uses the Repository pattern for data access:

- **UserRepository**: User CRUD operations
- **SessionRepository**: Session management
- **DocumentRepository**: Document management
- **AnalysisReportRepository**: Report management

## AI-Powered Analysis Engine

### CrewAI Framework Integration

The system leverages CrewAI for AI agent orchestration:

#### Financial Analysis Agents

##### 1. **Senior Financial Analyst**
- **Role**: Comprehensive financial document analysis
- **Tools**: Document reader, metrics extractor, web search
- **Capabilities**: 
  - Financial metrics extraction and calculation
  - Trend analysis and performance indicators
  - Market context and industry comparisons
  - Actionable recommendations

##### 2. **Investment Advisor & Product Specialist**
- **Role**: Investment recommendations and strategies
- **Tools**: Document reader, investment analyzer, web search
- **Capabilities**:
  - Investment opportunity analysis
  - Risk-return profile assessment
  - Portfolio recommendations
  - Market research integration

##### 3. **Financial Risk Assessment Expert**
- **Role**: Multi-dimensional risk analysis
- **Tools**: Document reader, risk assessor, metrics extractor
- **Capabilities**:
  - Quantitative risk scoring
  - Scenario analysis
  - Risk mitigation strategies
  - Early warning indicators

##### 4. **Financial Document Verifier**
- **Role**: Document authenticity validation
- **Tools**: Document reader, metrics extractor
- **Capabilities**:
  - Document structure analysis
  - Financial terminology validation
  - Compliance checking
  - Authenticity scoring

### Analysis Tools

#### 1. **Document Processing Tools**
- **PDF Reader**: PyPDFLoader for PDF document processing
- **Text Extraction**: Advanced text cleaning and formatting
- **Multi-Format Support**: Handles various document formats

#### 2. **Financial Analysis Tools**
- **Metrics Extractor**: Automated financial metrics extraction
- **Investment Analyzer**: Investment opportunity analysis
- **Risk Assessor**: Comprehensive risk evaluation
- **Web Search**: Free DuckDuckGo search integration

#### 3. **Report Generation**
- **Markdown Formatting**: Professional report formatting
- **Template System**: Consistent report structure
- **Metadata Integration**: Rich metadata in reports

### LLM Configuration

- **Model**: GPT-4o-mini (cost-optimized)
- **Temperature**: 0.3 (consistent analysis)
- **Max Tokens**: 1500 (controlled costs)
- **Rate Limiting**: 3 requests per minute per agent
- **Iteration Limits**: 2 iterations max per analysis

## Security & Authentication

### Authentication System

#### JWT Token Management
- **Access Tokens**: 30-minute expiration
- **Refresh Tokens**: 7-day expiration
- **Token Signing**: HMAC-SHA256 with secret key
- **Token Validation**: Comprehensive validation middleware

#### Password Security
- **Hashing**: Bcrypt with salt
- **Password Requirements**: Minimum 8 characters
- **Salt Storage**: Secure salt storage with hashes

#### Session Management
- **Session Tracking**: Database-backed session storage
- **Session Cleanup**: Automatic expired session cleanup
- **Multi-Device Support**: Multiple concurrent sessions per user
- **Session Revocation**: Admin ability to revoke user sessions

### Authorization & Access Control

#### Role-Based Access Control
- **User Role**: Standard user permissions
- **Admin Role**: Full system access
- **Permission Matrix**: Granular permission system

#### API Security
- **Rate Limiting**: 100 requests per hour per IP
- **CORS Protection**: Configurable allowed origins
- **Input Validation**: Comprehensive Pydantic validation
- **File Upload Security**: File type and size validation

### Data Protection

#### File Security
- **User Isolation**: Files stored per user
- **Path Validation**: Secure file path handling
- **Access Control**: User-specific file access
- **Cleanup**: Automatic temporary file cleanup

#### Database Security
- **SQL Injection Prevention**: Parameterized queries
- **Data Encryption**: Sensitive data encryption
- **Connection Security**: Secure database connections

## Key Architectural Decisions

### 1. **Modular Database Architecture**
**Decision**: Factory pattern with multiple database support
**Rationale**: 
- Easy switching between SQLite (development) and MongoDB (production)
- Clean separation of database-specific logic
- Future extensibility for additional databases

### 2. **Distributed Task Processing with Celery**
**Decision**: Celery with Redis message broker for background task processing
**Rationale**:
- **Scalability**: Horizontal scaling across multiple workers
- **Reliability**: Task persistence and retry mechanisms
- **Monitoring**: Real-time task status and progress tracking
- **Fault Tolerance**: Automatic retry with exponential backoff
- **Resource Management**: Efficient CPU and memory utilization
- **Production Ready**: Battle-tested distributed task queue

### 3. **CrewAI Agent Framework**
**Decision**: Specialized financial agents with specific roles
**Rationale**:
- Domain expertise in financial analysis
- Modular agent design for different analysis types
- Cost optimization through targeted agent usage
- Extensible framework for additional analysis types

### 4. **Repository Pattern**
**Decision**: Abstract repository interfaces with concrete implementations
**Rationale**:
- Clean separation of data access logic
- Easy testing with mock repositories
- Database-agnostic business logic
- Maintainable and extensible codebase

### 5. **Pydantic Schema Validation**
**Decision**: Comprehensive Pydantic models for all API interactions
**Rationale**:
- Automatic request/response validation
- Type safety throughout the application
- Auto-generated API documentation
- Clear data contracts between layers

### 6. **Multi-Format File Support**
**Decision**: Dynamic file extension handling
**Rationale**:
- Support for various financial document formats
- Flexible file processing pipeline
- User-friendly file upload experience
- Future extensibility for new formats

## Celery Task Processing Architecture

### Message Queue Design

The system implements a robust distributed task processing architecture using **Celery** with **Redis** as the message broker:

#### **Core Components**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI API   │───▶│  Redis Broker   │───▶│ Celery Workers  │
│                 │    │                 │    │                 │
│ - Task Creation │    │ - Message Queue │    │ - Task Execution│
│ - Status Query  │    │ - Task Storage  │    │ - Progress Update│
│ - Result Return │    │ - Result Cache  │    │ - Error Handling│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │   Flower UI     │
         │                       │              │                 │
         │                       │              │ - Task Monitor  │
         │                       │              │ - Worker Stats  │
         │                       │              │ - Queue Status  │
         │                       │              └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ Task-Report     │    │   Database      │
│ Mapping Table   │    │                 │
│                 │    │ - Task Results  │
│ - Task ID       │    │ - Report Data   │
│ - Report ID     │    │ - Status Info   │
│ - User ID       │    │ - Progress Log  │
└─────────────────┘    └─────────────────┘
```

#### **Task Processing Flow**

1. **Task Submission**
   - API receives analysis request
   - Creates analysis report with `PENDING` status
   - Enqueues Celery task with task metadata
   - Creates task-report mapping entry
   - Returns task ID and status URLs to client

2. **Task Execution**
   - Celery worker picks up task from Redis queue
   - Updates report status to `IN_PROGRESS`
   - Executes CrewAI analysis with progress callbacks
   - Handles errors with automatic retry logic
   - Updates report with results or failure status

3. **Status Monitoring**
   - Client polls task status endpoint
   - Real-time progress updates (0-100%)
   - Automatic polling stops on completion
   - Error details and retry information

#### **Queue Configuration**

```python
# Task routing by analysis type
task_routes = {
    'app.celery_tasks.process_comprehensive_analysis_task': {'queue': 'analysis'},
    'app.celery_tasks.process_investment_analysis_task': {'queue': 'analysis'},
    'app.celery_tasks.process_risk_analysis_task': {'queue': 'analysis'},
    'app.celery_tasks.process_verification_analysis_task': {'queue': 'analysis'},
}
```

#### **Worker Configuration**

- **Concurrency**: Configurable worker processes
- **Memory Management**: Automatic garbage collection
- **Error Handling**: Exponential backoff retry (3 attempts)
- **Time Limits**: 10-minute hard limit, 9-minute soft limit
- **Resource Monitoring**: CPU and memory usage tracking

#### **Monitoring & Observability**

- **Flower Dashboard**: Real-time task monitoring
- **Task Statistics**: Worker performance metrics
- **Queue Health**: Redis queue length monitoring
- **Error Tracking**: Detailed error logs and stack traces
- **Progress Tracking**: Granular progress updates

#### **Scalability Features**

- **Horizontal Scaling**: Add more workers as needed
- **Load Balancing**: Automatic task distribution
- **Fault Tolerance**: Worker failure recovery
- **Resource Isolation**: Separate queues for different task types
- **Auto-scaling**: Dynamic worker scaling based on queue length

#### **Data Persistence**

- **Task State**: Stored in Redis for fast access
- **Results**: Cached in Redis with TTL
- **Mappings**: Stored in database for persistence
- **Progress**: Real-time updates via Redis
- **Logs**: Comprehensive logging for debugging

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11+**: Latest Python features and performance
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for production deployment

### AI & Machine Learning
- **CrewAI 0.130.0**: Multi-agent AI framework
- **CrewAI Tools 0.47.1**: Specialized tools for agents
- **OpenAI GPT-4o-mini**: Cost-optimized LLM
- **PyPDFLoader**: PDF document processing

### Database & Storage
- **SQLite**: Development and small-scale deployment
- **MongoDB**: Production and scalable deployment
- **Motor**: Async MongoDB driver
- **File System**: Local file storage with organized structure

### Task Processing & Message Queues
- **Celery**: Distributed task queue for background processing
- **Redis**: Message broker and result backend
- **Flower**: Real-time task monitoring dashboard
- **Task Routing**: Queue-based task distribution
- **Progress Tracking**: Real-time status and progress updates

### Security & Authentication
- **JWT**: JSON Web Token authentication
- **Bcrypt**: Password hashing
- **Python-multipart**: File upload handling
- **Email-validator**: Email validation

### Development & Deployment
- **Docker**: Containerization support
- **Docker Compose**: Multi-service orchestration
- **Environment Variables**: Configuration management
- **Logging**: Comprehensive application logging

## Deployment & Scalability

### Development Environment
```bash
# Using Docker (Recommended)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment
```bash
# Start all services
docker-compose up -d

# Scale workers if needed
docker-compose up -d --scale celery-worker=3

# View service status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f celery-worker
```

### Service Management
```bash
# Restart specific service
docker-compose restart api

# View logs for specific service
docker-compose logs -f celery-worker

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## API Documentation

### Interactive Documentation
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Schema**: Auto-generated from code

### API Standards
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Responses**: Consistent JSON response format
- **Error Handling**: Standardized error response format
- **Versioning**: API versioning strategy

### Response Format
```json
{
  "status": "success|error",
  "data": {},
  "message": "Human-readable message",
  "timestamp": "2025-09-28T23:43:11Z"
}
```

### Error Format
```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-09-28T23:43:11Z"
}
```

---

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service status
docker-compose ps

# View error logs
docker-compose logs api
docker-compose logs celery-worker
```

#### Database Connection Issues
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Restart database
docker-compose restart mongodb
```

#### Task Processing Issues
```bash
# Check Celery worker logs
docker-compose logs celery-worker

# Check Redis connection
docker-compose logs redis

# Restart workers
docker-compose restart celery-worker
```

#### Memory Issues
```bash
# Scale down workers
docker-compose up -d --scale celery-worker=1

# Check resource usage
docker stats
```

### Environment Variables
Ensure all required environment variables are set in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key
- `MONGODB_CONNECTION_STRING`: MongoDB connection string
- `REDIS_URL`: Redis connection URL
- `JWT_SECRET_KEY`: JWT signing key

## Conclusion

The Financial Document Analyzer is a production-ready system that combines modern web technologies with advanced AI capabilities. Key features include:

- **AI-Powered Analysis**: CrewAI agents for financial document processing
- **Distributed Processing**: Celery with Redis for scalable task processing
- **Real-time Monitoring**: Flower dashboard for task monitoring
- **Multi-Database Support**: SQLite for development, MongoDB for production
- **Comprehensive Security**: JWT authentication with role-based access control
- **Developer-Friendly**: Interactive API documentation and clear setup instructions

This system is designed for both development and production environments, with Docker Compose providing easy deployment and management.
