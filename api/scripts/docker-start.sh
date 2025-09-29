#!/bin/bash
# Docker Compose Management Script for Financial Document Analyzer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
}

# Function to create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_warning "Please edit .env file with your configuration before running the services."
        print_warning "Default MongoDB credentials: admin/password123"
        print_warning "Default Flower credentials: admin/admin"
    fi
}

# Function to start all services
start_services() {
    print_status "Starting Financial Document Analyzer services..."
    
    check_docker
    check_docker_compose
    create_env_file
    
    # Build and start services
    docker-compose up --build -d
    
    print_success "All services started successfully!"
    echo ""
    print_status "Service URLs:"
    echo "  📊 FastAPI Application: http://localhost:8000"
    echo "  📚 API Documentation: http://localhost:8000/docs"
    echo "  🌸 Flower Monitoring: http://localhost:5555 (admin:admin)"
    echo "  🗄️  MongoDB Express: http://localhost:8081"
    echo "  🔴 Redis: localhost:6379"
    echo "  🍃 MongoDB: localhost:27017"
    echo ""
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop services: docker-compose down"
}

# Function to start with scaling
start_with_scaling() {
    print_status "Starting services with additional workers for scaling..."
    
    check_docker
    check_docker_compose
    create_env_file
    
    # Start with scaling profile
    docker-compose --profile scaling up --build -d
    
    print_success "All services started with scaling!"
    echo ""
    print_status "Service URLs:"
    echo "  📊 FastAPI Application: http://localhost:8000"
    echo "  📚 API Documentation: http://localhost:8000/docs"
    echo "  🌸 Flower Monitoring: http://localhost:5555 (admin:admin)"
    echo "  🗄️  MongoDB Express: http://localhost:8081"
    echo "  🔴 Redis: localhost:6379"
    echo "  🍃 MongoDB: localhost:27017"
    echo ""
    print_status "Workers running: 2 (with scaling enabled)"
    print_status "To view logs: docker-compose logs -f"
    print_status "To stop services: docker-compose down"
}

# Function to stop services
stop_services() {
    print_status "Stopping Financial Document Analyzer services..."
    docker-compose down
    print_success "All services stopped successfully!"
}

# Function to restart services
restart_services() {
    print_status "Restarting Financial Document Analyzer services..."
    docker-compose restart
    print_success "All services restarted successfully!"
}

# Function to view logs
view_logs() {
    if [ -n "$1" ]; then
        print_status "Viewing logs for service: $1"
        docker-compose logs -f "$1"
    else
        print_status "Viewing logs for all services..."
        docker-compose logs -f
    fi
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
    echo ""
    print_status "Service Health:"
    docker-compose exec api curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "API health check failed"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Financial Document Analyzer services..."
    docker-compose down -v
    docker system prune -f
    print_success "Cleanup completed!"
}

# Function to show help
show_help() {
    echo "Financial Document Analyzer - Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services (default)"
    echo "  start-scale Start services with additional workers for scaling"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  logs        View logs (optionally specify service name)"
    echo "  status      Show service status and health"
    echo "  cleanup     Stop services and clean up volumes"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 start-scale"
    echo "  $0 logs api"
    echo "  $0 logs celery-worker"
    echo "  $0 status"
}

# Main script logic
case "${1:-start}" in
    start)
        start_services
        ;;
    start-scale)
        start_with_scaling
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        view_logs "$2"
        ;;
    status)
        show_status
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
