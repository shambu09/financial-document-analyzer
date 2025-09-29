# Financial Document Analyzer

An AI-powered financial document analysis system with real-time task processing and modern web interface.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for client development)

### Start the Application
```bash
# Clone the repository
git clone <repository-url>
cd financial-document-analyzer

# Start all services
cd api
docker-compose up -d

# Start frontend
cd client
npm install
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Task Monitor**: http://localhost:5555
- **Database UI**: http://localhost:8081

## 🏗️ Architecture

### Backend (FastAPI + Celery)
- **API Server**: FastAPI with JWT authentication
- **Task Processing**: Celery with Redis message broker
- **AI Analysis**: CrewAI agents for financial document analysis
- **Database**: MongoDB (production) / SQLite (development)
- **Monitoring**: Flower dashboard for task monitoring

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query for API state
- **UI Components**: Custom component library
- **Real-time Updates**: Task status polling

## 📁 Project Structure

```
├── api/                   # Backend API server
│   ├── app/               # FastAPI application
│   ├── docker-compose.yml # Docker orchestration
│   └── README.md          # Detailed API documentation
└── client/                # Frontend React application
    ├── src/               # React source code
    └── README.md          # Frontend documentation
```

## 🔧 Development

### Backend Development
```bash
cd api
docker-compose up -d          # Start all services
docker-compose logs -f        # View service logs
docker-compose down           # Stop all services
```

### Frontend Development
```bash
cd client
npm install       # Install dependencies
npm run dev       # Start development server
npm run build     # Build for production
```

## 📊 Features

- **Document Upload**: Support for PDF, TXT, and other formats
- **AI Analysis**: Comprehensive, investment, risk, and verification analysis
- **Real-time Progress**: Live task status and progress tracking
- **User Management**: Registration, authentication, and profile management
- **Report Generation**: Downloadable analysis reports
- **Task Monitoring**: Real-time task queue monitoring

## 🛠️ Technology Stack

**Backend**: FastAPI, Celery, Redis, MongoDB, CrewAI, OpenAI
**Frontend**: React, TypeScript, Tailwind CSS, React Query
**DevOps**: Docker, Docker Compose

## 📚 Documentation

- [API Documentation](./api/README.md) - Complete backend documentation
- [Frontend Documentation](./client/README.md) - React application guide
- [Docker Setup](./api/DOCKER_SETUP.md) - Container deployment guide
- [Celery Setup](./api/CELERY_SETUP.md) - Task processing configuration

## 🔐 Environment Setup

1. Copy `api/env.example` to `api/.env`
2. Configure your OpenAI API key and database settings
3. Run `docker-compose up -d` to start all services


---

Check the detailed documentation in the `api/` and `client/` directories.
