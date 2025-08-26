@echo off
REM Docker environment setup script for Windows
REM Crypto Data Pipeline - Clean Version

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
    )
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)
echo ✅ Docker Compose is available

REM Create required directories
echo ℹ️ Creating required directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Check if .env file exists
if not exist ".env" (
    if exist ".env.example" (
        echo ℹ️ Creating .env file from template...
        copy .env.example .env >nul
        echo ⚠️ Please configure your .env file with the appropriate values
    ) else (
        echo ⚠️ No .env file found. Please create one with your configuration.
    )
)

echo ℹ️ Building Docker services...
%COMPOSE_CMD% build

echo ℹ️ Starting services...
%COMPOSE_CMD% up -d

echo 🎉 Setup completed!
echo.
echo 📊 Streamlit Dashboard: http://localhost:8501
echo.
echo To view logs: %COMPOSE_CMD% logs -f
echo To stop services: %COMPOSE_CMD% down
pause
