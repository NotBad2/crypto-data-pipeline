#!/bin/bash
# Docker environment setup script for Linux/macOS
# Crypto Data Pipeline - Clean Version

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

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi
print_status "Docker is running"

# Check if docker-compose is available
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose is not available"
    exit 1
fi
print_status "Docker Compose is available"

# Create required directories
print_info "Creating required directories..."
mkdir -p data logs

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please configure your .env file with the appropriate values"
    else
        print_warning "No .env file found. Please create one with your configuration."
    fi
fi

print_info "Building Docker services..."
$COMPOSE_CMD build

print_info "Starting services..."
$COMPOSE_CMD up -d

print_status "Setup completed!"
echo
echo "📊 Streamlit Dashboard: http://localhost:8501"
echo
echo "To view logs: $COMPOSE_CMD logs -f"
echo "To stop services: $COMPOSE_CMD down"
