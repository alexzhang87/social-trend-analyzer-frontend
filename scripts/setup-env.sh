#!/bin/bash

# ========================================
# Environment Setup Script for Social Trend Analyzer
# ========================================

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

# Function to show usage
show_usage() {
    echo "Usage: $0 [ENVIRONMENT]"
    echo ""
    echo "ENVIRONMENT:"
    echo "  dev         Setup development environment"
    echo "  test        Setup testing environment"
    echo "  prod        Setup production environment"
    echo "  clean       Clean all environments"
    echo "  status      Show environment status"
    echo ""
    echo "Examples:"
    echo "  $0 dev      # Setup development environment"
    echo "  $0 prod     # Setup production environment"
    echo "  $0 clean    # Clean all Docker containers and volumes"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup development environment
setup_dev() {
    print_status "Setting up development environment..."
    
    # Copy environment file
    if [ ! -f .env ]; then
        cp .env.development .env
        print_success "Development environment file created"
    else
        print_warning "Environment file already exists"
    fi
    
    # Build and start services
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
    
    print_success "Development environment is ready!"
    print_status "Frontend: http://localhost:3001"
    print_status "Backend API: http://localhost:8001"
    print_status "API Docs: http://localhost:8001/docs"
}

# Function to setup testing environment
setup_test() {
    print_status "Setting up testing environment..."
    
    # Copy environment file
    cp .env.testing .env.test
    
    # Build and start services for testing
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Run tests
    print_status "Running tests..."
    docker-compose exec backend python -m pytest
    
    print_success "Testing environment setup complete!"
}

# Function to setup production environment
setup_prod() {
    print_status "Setting up production environment..."
    
    # Check if production environment file exists
    if [ ! -f .env.production ]; then
        print_error "Production environment file (.env.production) not found!"
        print_status "Please create .env.production with your production settings"
        exit 1
    fi
    
    # Copy environment file
    cp .env.production .env
    
    # Generate SSL certificates if they don't exist
    if [ ! -f ssl/cert.pem ]; then
        print_status "Generating self-signed SSL certificates..."
        mkdir -p ssl
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem \
            -out ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        print_success "SSL certificates generated"
    fi
    
    # Build and start production services
    docker-compose -f docker-compose.prod.yml up --build -d
    
    print_success "Production environment is ready!"
    print_status "Application: https://localhost"
    print_warning "Remember to replace self-signed certificates with real ones in production!"
}

# Function to clean environment
clean_env() {
    print_status "Cleaning environment..."
    
    # Stop and remove all containers
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v --remove-orphans
    docker-compose -f docker-compose.prod.yml down -v --remove-orphans
    
    # Remove unused images
    docker image prune -f
    
    # Remove environment files
    rm -f .env .env.test
    
    print_success "Environment cleaned!"
}

# Function to show environment status
show_status() {
    print_status "Environment Status:"
    echo ""
    
    # Show running containers
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # Show disk usage
    print_status "Docker disk usage:"
    docker system df
}

# Function to backup environment
backup_env() {
    print_status "Creating environment backup..."
    
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup environment files
    cp .env* "$BACKUP_DIR/" 2>/dev/null || true
    
    # Backup Docker volumes
    docker run --rm -v "$(pwd)":/backup -v social_trends_postgres_data:/data alpine tar czf /backup/"$BACKUP_DIR"/postgres_data.tar.gz -C /data .
    docker run --rm -v "$(pwd)":/backup -v social_trends_redis_data:/data alpine tar czf /backup/"$BACKUP_DIR"/redis_data.tar.gz -C /data .
    
    print_success "Backup created in $BACKUP_DIR"
}

# Function to restore environment
restore_env() {
    if [ -z "$2" ]; then
        print_error "Please specify backup directory"
        echo "Usage: $0 restore [BACKUP_DIR]"
        exit 1
    fi
    
    BACKUP_DIR="$2"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_error "Backup directory $BACKUP_DIR not found"
        exit 1
    fi
    
    print_status "Restoring environment from $BACKUP_DIR..."
    
    # Restore environment files
    cp "$BACKUP_DIR"/.env* . 2>/dev/null || true
    
    # Restore Docker volumes
    if [ -f "$BACKUP_DIR/postgres_data.tar.gz" ]; then
        docker run --rm -v "$(pwd)":/backup -v social_trends_postgres_data:/data alpine tar xzf /backup/"$BACKUP_DIR"/postgres_data.tar.gz -C /data
    fi
    
    if [ -f "$BACKUP_DIR/redis_data.tar.gz" ]; then
        docker run --rm -v "$(pwd)":/backup -v social_trends_redis_data:/data alpine tar xzf /backup/"$BACKUP_DIR"/redis_data.tar.gz -C /data
    fi
    
    print_success "Environment restored from $BACKUP_DIR"
}



# Main script logic
case "${1:-}" in
    "dev")
        check_prerequisites
        setup_dev
        show_status
        ;;
    "test")
        check_prerequisites
        setup_test
        ;;
    "prod")
        check_prerequisites
        setup_prod
        show_status
        ;;
    "clean")
        clean_env
        ;;
    "status")
        show_status
        ;;
    "backup")
        backup_env
        ;;
    "restore")
        restore_env "$@"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac