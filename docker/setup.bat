@echo off
REM Docker environment setup script for Windows
REM Crypto Data Pipeline

echo 🐳 Setting up Crypto Data Pipeline Docker Environment
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Check if docker-compose is available
docker-compose version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Docker Compose is not available
        pause
        exit /b 1
    ) else (
        set COMPOSE_CMD=docker compose
    )
) else (
    set COMPOSE_CMD=docker-compose
)
echo ✅ Docker Compose is available

REM Create necessary directories
echo ℹ️ Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "logs\scheduler" mkdir logs\scheduler
if not exist "logs\webserver" mkdir logs\webserver
if not exist "logs\worker" mkdir logs\worker
if not exist "data" mkdir data
if not exist "data\postgres" mkdir data\postgres
if not exist "data\clickhouse" mkdir data\clickhouse
if not exist "data\grafana" mkdir data\grafana
if not exist "plugins" mkdir plugins
echo ✅ Directories created

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ℹ️ Creating .env file from template...
    copy .env.example .env >nul
    echo ⚠️ Please edit .env file to configure your API keys
) else (
    echo ✅ .env file already exists
)

REM Ask if user wants to rebuild images
set /p rebuild="Do you want to rebuild Docker images? (y/N): "
if /i "%rebuild%"=="y" (
    echo ℹ️ Building Docker images...
    %COMPOSE_CMD% build airflow-webserver
    if %errorlevel% neq 0 (
        echo ❌ Failed to build Docker images
        pause
        exit /b 1
    )
    echo ✅ Docker images built successfully
)

REM Start services
echo ℹ️ Starting Docker services...
%COMPOSE_CMD% up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)
echo ✅ Services started

REM Wait for services
echo ℹ️ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check if this is first time setup
%COMPOSE_CMD% exec postgres pg_isready -U crypto_user -d crypto_data >nul 2>&1
if %errorlevel% neq 0 (
    echo ℹ️ First time setup detected, initializing Airflow...
    timeout /t 10 /nobreak >nul
    %COMPOSE_CMD% run --rm airflow-webserver airflow db init
    
    echo ℹ️ Creating Airflow admin user...
    %COMPOSE_CMD% run --rm airflow-webserver airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin
)

REM Show service URLs
echo.
echo ℹ️ Service URLs:
echo 🌐 Airflow Web UI:    http://localhost:8080 (admin/admin)
echo 📊 Grafana:          http://localhost:3000 (admin/admin)
echo 🗄️ PostgreSQL:       localhost:5432 (crypto_user/crypto_pass)
echo ⚡ ClickHouse:       http://localhost:8123
echo 🔴 Redis:            localhost:6379
echo.

echo ✅ Setup completed successfully!
echo ℹ️ Run 'docker-compose logs -f' to view logs
echo ℹ️ Run 'docker-compose down' to stop all services
echo.

pause
