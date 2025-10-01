#!/bin/bash

# ========================================
# Health Check Script for Social Trend Analyzer
# ========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="http://localhost:3001"
BACKEND_URL="http://localhost:8001"
API_HEALTH_ENDPOINT="/health"
API_DOCS_ENDPOINT="/docs"
TIMEOUT=10

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

# Function to check HTTP endpoint
check_http_endpoint() {
    local url="$1"
    local name="$2"
    local expected_status="${3:-200}"
    
    print_status "Checking $name at $url..."
    
    if command -v curl &> /dev/null; then
        local response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$url" 2>/dev/null || echo "000")
        
        if [ "$response" = "$expected_status" ]; then
            print_success "$name is healthy (HTTP $response)"
            return 0
        else
            print_error "$name is unhealthy (HTTP $response)"
            return 1
        fi
    else
        print_warning "curl not available, skipping HTTP check for $name"
        return 1
    fi
}

# Function to check Docker containers
check_docker_containers() {
    print_status "Checking Docker containers..."
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not available"
        return 1
    fi
    
    local containers=$(docker ps --format "{{.Names}}" 2>/dev/null || echo "")
    
    if [ -z "$containers" ]; then
        print_warning "No Docker containers running"
        return 1
    fi
    
    echo -e "${BLUE}Running containers:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true
    
    # Check specific containers
    local expected_containers=("frontend" "backend" "postgres" "redis")
    local all_healthy=true
    
    for container in "${expected_containers[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "^${container}$" 2>/dev/null; then
            local status=$(docker ps --filter "name=^${container}$" --format "{{.Status}}" 2>/dev/null)
            if [[ "$status" == *"Up"* ]]; then
                print_success "$container container is running"
            else
                print_error "$container container is not healthy: $status"
                all_healthy=false
            fi
        else
            print_warning "$container container not found"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    print_status "Checking database connectivity..."
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not available, skipping database check"
        return 1
    fi
    
    # Check if postgres container is running
    if docker ps --format "{{.Names}}" | grep -q "postgres" 2>/dev/null; then
        # Try to connect to database
        if docker exec -i $(docker ps --filter "name=postgres" --format "{{.ID}}" | head -1) psql -U postgres -d social_trends -c "SELECT 1;" &>/dev/null; then
            print_success "Database is accessible"
            return 0
        else
            print_error "Database connection failed"
            return 1
        fi
    else
        print_warning "PostgreSQL container not running"
        return 1
    fi
}

# Function to check Redis connectivity
check_redis() {
    print_status "Checking Redis connectivity..."
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not available, skipping Redis check"
        return 1
    fi
    
    # Check if redis container is running
    if docker ps --format "{{.Names}}" | grep -q "redis" 2>/dev/null; then
        # Try to ping Redis
        if docker exec -i $(docker ps --filter "name=redis" --format "{{.ID}}" | head -1) redis-cli ping | grep -q "PONG" 2>/dev/null; then
            print_success "Redis is accessible"
            return 0
        else
            print_error "Redis connection failed"
            return 1
        fi
    else
        print_warning "Redis container not running"
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    print_status "Checking disk space..."
    
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 80 ]; then
        print_success "Disk space is healthy ($usage% used)"
        return 0
    elif [ "$usage" -lt 90 ]; then
        print_warning "Disk space is getting low ($usage% used)"
        return 1
    else
        print_error "Disk space is critically low ($usage% used)"
        return 1
    fi
}

# Function to check memory usage
check_memory() {
    print_status "Checking memory usage..."
    
    if command -v free &> /dev/null; then
        local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        
        if [ "$mem_usage" -lt 80 ]; then
            print_success "Memory usage is healthy ($mem_usage% used)"
            return 0
        elif [ "$mem_usage" -lt 90 ]; then
            print_warning "Memory usage is high ($mem_usage% used)"
            return 1
        else
            print_error "Memory usage is critically high ($mem_usage% used)"
            return 1
        fi
    else
        print_warning "Memory check not available on this system"
        return 1
    fi
}

# Function to generate health report
generate_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="health_report_$(date '+%Y%m%d_%H%M%S').txt"
    
    print_status "Generating health report..."
    
    {
        echo "========================================="
        echo "Social Trend Analyzer Health Report"
        echo "Generated: $timestamp"
        echo "========================================="
        echo ""
        
        echo "System Information:"
        echo "- OS: $(uname -s)"
        echo "- Kernel: $(uname -r)"
        echo "- Architecture: $(uname -m)"
        echo ""
        
        echo "Docker Information:"
        if command -v docker &> /dev/null; then
            echo "- Docker Version: $(docker --version 2>/dev/null || echo 'Not available')"
            echo "- Docker Compose Version: $(docker-compose --version 2>/dev/null || echo 'Not available')"
            echo ""
            echo "Running Containers:"
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "No containers running"
            echo ""
            echo "Docker System Info:"
            docker system df 2>/dev/null || echo "Docker system info not available"
        else
            echo "- Docker: Not available"
        fi
        echo ""
        
        echo "Resource Usage:"
        if command -v free &> /dev/null; then
            echo "Memory:"
            free -h
        fi
        echo ""
        echo "Disk Usage:"
        df -h
        echo ""
        
        echo "Network Connectivity:"
        echo "- Frontend: $(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$FRONTEND_URL" 2>/dev/null || echo "Failed")"
        echo "- Backend: $(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$BACKEND_URL$API_HEALTH_ENDPOINT" 2>/dev/null || echo "Failed")"
        echo ""
        
    } > "$report_file"
    
    print_success "Health report saved to $report_file"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --quick         Quick health check (containers and endpoints only)"
    echo "  --full          Full health check (default)"
    echo "  --report        Generate detailed health report"
    echo "  --continuous    Run continuous monitoring (every 30 seconds)"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Run full health check"
    echo "  $0 --quick     # Run quick health check"
    echo "  $0 --report    # Generate health report"
}

# Function for continuous monitoring
continuous_monitoring() {
    print_status "Starting continuous monitoring (Press Ctrl+C to stop)..."
    
    while true; do
        clear
        echo "========================================="
        echo "Social Trend Analyzer - Live Monitoring"
        echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "========================================="
        echo ""
        
        run_health_checks "quick"
        
        echo ""
        print_status "Next check in 30 seconds..."
        sleep 30
    done
}

# Function to run health checks
run_health_checks() {
    local mode="${1:-full}"
    local overall_status=0
    
    echo "========================================="
    echo "Social Trend Analyzer Health Check"
    echo "Mode: $mode"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================="
    echo ""
    
    # Always check containers and endpoints
    check_docker_containers || overall_status=1
    echo ""
    
    check_http_endpoint "$BACKEND_URL$API_HEALTH_ENDPOINT" "Backend API" || overall_status=1
    check_http_endpoint "$FRONTEND_URL" "Frontend" || overall_status=1
    echo ""
    
    if [ "$mode" = "full" ]; then
        check_database || overall_status=1
        check_redis || overall_status=1
        echo ""
        
        check_disk_space || overall_status=1
        check_memory || overall_status=1
        echo ""
    fi
    
    echo "========================================="
    if [ $overall_status -eq 0 ]; then
        print_success "Overall system health: HEALTHY"
    else
        print_error "Overall system health: UNHEALTHY"
    fi
    echo "========================================="
    
    return $overall_status
}

# Main script logic
case "${1:-}" in
    "--quick")
        run_health_checks "quick"
        ;;
    "--full"|"")
        run_health_checks "full"
        ;;
    "--report")
        generate_report
        ;;
    "--continuous")
        continuous_monitoring
        ;;
    "--help")
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac