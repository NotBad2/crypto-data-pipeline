@echo off
echo ======================================
echo   System Monitor Dashboard
echo ======================================
echo.

echo Iniciando monitor do sistema...
echo Acesse: http://localhost:8503
echo.
echo Para parar: Ctrl+C
echo.

cd /d "%~dp0"
streamlit run system_monitor.py --server.port 8503
