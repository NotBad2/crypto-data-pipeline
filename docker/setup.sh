#!/bin/bash
# Docker environment setup and initialization script for Windows (Git Bash)

echo "🐳 Setting up Crypto Data Pipeline Docker Environment"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed and running
check_docker() {
    print_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    print_status "Docker is installed and running"
}

# Check if docker-compose is available
check_docker_compose() {
    print_info "Checking Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        print_error "Docker Compose is not available"
        exit 1
    fi
    
    print_status "Docker Compose is available"
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    mkdir -p logs/scheduler logs/webserver logs/worker
    mkdir -p data/postgres data/clickhouse data/grafana
    mkdir -p plugins
    
    print_status "Directories created"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please edit .env file to configure your API keys"
    else
        print_status ".env file already exists"
    fi
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."
    
    echo "Building Airflow image..."
    $COMPOSE_CMD build airflow-webserver
    
    if [ $? -eq 0 ]; then
        print_status "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Initialize Airflow database
init_airflow() {
    print_info "Initializing Airflow database..."
    
    $COMPOSE_CMD run --rm airflow-webserver airflow db init
    
    if [ $? -eq 0 ]; then
        print_status "Airflow database initialized"
    else
        print_error "Failed to initialize Airflow database"
        exit 1
    fi
}

# Create Airflow admin user
create_airflow_user() {
    print_info "Creating Airflow admin user..."
    
    $COMPOSE_CMD run --rm airflow-webserver airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin
    
    if [ $? -eq 0 ]; then
        print_status "Airflow admin user created (admin/admin)"
    else
        print_warning "Airflow user might already exist"
    fi
}

# Start services
start_services() {
    print_info "Starting Docker services..."
    
    $COMPOSE_CMD up -d
    
    if [ $? -eq 0 ]; then
        print_status "All services started successfully"
    else
        print_error "Failed to start some services"
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_services() {
    print_info "Waiting for services to be healthy..."
    
    # Wait for PostgreSQL
    echo "Waiting for PostgreSQL..."
    timeout 60 bash -c 'until $COMPOSE_CMD exec postgres pg_isready -U crypto_user -d crypto_data; do sleep 2; done'
    
    # Wait for ClickHouse
    echo "Waiting for ClickHouse..."
    timeout 60 bash -c 'until curl -s http://localhost:8123/ >/dev/null; do sleep 2; done'
    
    # Wait for Airflow
    echo "Waiting for Airflow..."
    timeout 120 bash -c 'until curl -s http://localhost:8080/health >/dev/null; do sleep 5; done'
    
    print_status "All services are healthy"
}

# Validate services
validate_services() {
    print_info "Validating services..."
    
    # Check PostgreSQL
    if $COMPOSE_CMD exec postgres pg_isready -U crypto_user -d crypto_data &> /dev/null; then
        print_status "PostgreSQL is ready"
    else
        print_error "PostgreSQL is not ready"
    fi
    
    # Check ClickHouse
    if curl -s http://localhost:8123/ | grep -q "Ok."; then
        print_status "ClickHouse is ready"
    else
        print_error "ClickHouse is not ready"
    fi
    
    # Check Redis
    if $COMPOSE_CMD exec redis redis-cli ping | grep -q "PONG"; then
        print_status "Redis is ready"
    else
        print_error "Redis is not ready"
    fi
    
    # Check Airflow
    if curl -s http://localhost:8080/health | grep -q "healthy"; then
        print_status "Airflow is ready"
    else
        print_error "Airflow is not ready"
    fi
    
    # Check Grafana
    if curl -s http://localhost:3000/ &> /dev/null; then
        print_status "Grafana is ready"
    else
        print_error "Grafana is not ready"
    fi
}

# Show service URLs
show_urls() {
    echo ""
    print_info "Service URLs:"
    echo "🌐 Airflow Web UI:    http://localhost:8080 (admin/admin)"
    echo "📊 Grafana:          http://localhost:3000 (admin/admin)"
    echo "🗄️  PostgreSQL:       localhost:5432 (crypto_user/crypto_pass)"
    echo "⚡ ClickHouse:       http://localhost:8123"
    echo "🔴 Redis:            localhost:6379"
    echo ""
}

# Main execution
main() {
    check_docker
    check_docker_compose
    create_directories
    create_env_file
    
    # Ask user if they want to rebuild images
    read -p "Do you want to rebuild Docker images? (y/N): " rebuild
    if [[ $rebuild =~ ^[Yy]$ ]]; then
        build_images
    fi
    
    # Check if Airflow needs initialization
    if ! $COMPOSE_CMD ps | grep -q airflow-webserver; then
        print_info "First time setup detected"
        start_services
        sleep 10
        init_airflow
        create_airflow_user
    else
        start_services
    fi
    
    wait_for_services
    validate_services
    show_urls
    
    print_status "Setup completed successfully!"
    print_info "Run 'docker-compose logs -f' to view logs"
    print_info "Run 'docker-compose down' to stop all services"
}

# Run main function
main "$@"
