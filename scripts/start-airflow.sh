#!/bin/bash

echo "🚀 Starting Crypto Data Pipeline with Airflow"
echo "============================================="

# Create necessary directories
mkdir -p ./data
mkdir -p ./logs
mkdir -p ./airflow/dags
mkdir -p ./airflow/logs
mkdir -p ./airflow/plugins

# Set Airflow environment
export AIRFLOW_HOME=$(pwd)/airflow
export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/dags
export AIRFLOW__CORE__EXECUTOR=LocalExecutor

# Copy DAGs to Airflow directory
echo "📂 Setting up DAG files..."
cp -r ./dags/* ./airflow/dags/ 2>/dev/null || echo "DAGs will be mounted via Docker"

echo "🐳 Starting Docker services..."

# Stop any existing containers
docker-compose down --remove-orphans

# Build and start all services
docker-compose up --build -d postgres redis

echo "⏳ Waiting for databases to be ready..."
sleep 15

# Check PostgreSQL
echo "🔍 Checking PostgreSQL connection..."
docker-compose exec postgres pg_isready -U crypto_user -d crypto_data

# Check Redis
echo "🔍 Checking Redis connection..."
docker-compose exec redis redis-cli ping

# Initialize Airflow
echo "🎯 Initializing Airflow..."
docker-compose up -d airflow-init

sleep 20

# Start Airflow services
echo "🚁 Starting Airflow Webserver and Scheduler..."
docker-compose up -d airflow-webserver airflow-scheduler

# Start other services
echo "📊 Starting Grafana and ClickHouse..."
docker-compose up -d grafana clickhouse

echo ""
echo "✅ Setup completed!"
echo ""
echo "🌐 Access URLs:"
echo "   📊 Grafana:        http://localhost:3000 (admin/admin)"
echo "   🚁 Airflow:        http://localhost:8080 (admin/admin)"
echo "   🗄️ PostgreSQL:     localhost:5432 (crypto_user/crypto_pass)"
echo "   📈 ClickHouse:     http://localhost:8123"
echo "   🔴 Redis:          localhost:6379"
echo ""
echo "📋 Next steps:"
echo "   1. Open Airflow UI: http://localhost:8080"
echo "   2. Enable DAGs: simple_crypto_collection"
echo "   3. Monitor execution in Airflow"
echo "   4. Check data in PostgreSQL"
echo ""
echo "🔍 Monitor logs with:"
echo "   docker-compose logs -f airflow-scheduler"
echo "   docker-compose logs -f airflow-webserver"
