@echo off
echo 🚀 Starting Crypto Data Pipeline with Airflow
echo =============================================

REM Create necessary directories
if not exist ".\data" mkdir ".\data"
if not exist ".\logs" mkdir ".\logs"

echo 🐳 Starting Docker services...

REM Stop any existing containers
docker-compose down --remove-orphans

REM Build and start database services first
docker-compose up --build -d postgres redis

echo ⏳ Waiting for databases to be ready...
timeout /t 15 /nobreak > nul

REM Check services
echo 🔍 Checking services...
docker-compose ps

REM Initialize Airflow
echo 🎯 Initializing Airflow...
docker-compose up -d airflow-init

timeout /t 20 /nobreak > nul

REM Start Airflow services
echo 🚁 Starting Airflow Webserver and Scheduler...
docker-compose up -d airflow-webserver airflow-scheduler

REM Start other services
echo 📊 Starting Grafana and ClickHouse...
docker-compose up -d grafana clickhouse

echo.
echo ✅ Setup completed!
echo.
echo 🌐 Access URLs:
echo    📊 Grafana:        http://localhost:3000 (admin/admin)
echo    🚁 Airflow:        http://localhost:8080 (admin/admin)
echo    🗄️ PostgreSQL:     localhost:5432 (crypto_user/crypto_pass)
echo    📈 ClickHouse:     http://localhost:8123
echo    🔴 Redis:          localhost:6379
echo.
echo 📋 Next steps:
echo    1. Open Airflow UI: http://localhost:8080
echo    2. Enable DAGs: simple_crypto_collection
echo    3. Monitor execution in Airflow
echo    4. Check data in PostgreSQL
echo.
echo 🔍 Monitor logs with:
echo    docker-compose logs -f airflow-scheduler
echo    docker-compose logs -f airflow-webserver

pause
