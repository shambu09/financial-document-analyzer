#!/bin/bash
# Start all services for the Financial Document Analyzer

set -e

echo "Starting Financial Document Analyzer services..."

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

# Start Celery worker
echo "Starting Celery worker..."
python start_worker.py &
WORKER_PID=$!

# Start Flower monitoring
echo "Starting Flower monitoring..."
python start_flower.py &
FLOWER_PID=$!

# Start FastAPI application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

echo "All services started!"
echo "FastAPI: http://localhost:8000"
echo "Flower: http://localhost:5555 (admin:admin)"
echo "API Docs: http://localhost:8000/docs"

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $WORKER_PID $FLOWER_PID $API_PID 2>/dev/null || true
    exit 0
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM

# Wait for any process to exit
wait
