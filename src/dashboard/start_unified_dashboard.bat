@echo off
echo ======================================
echo   Crypto Data Pipeline - Unified
echo ======================================
echo.

echo Iniciando dashboard unificado...
echo.
echo URL: http://localhost:8501
echo.

cd /d "%~dp0"

streamlit run unified_dashboard.py --server.port 8501

pause
