@echo off
echo ======================================
echo   Crypto Data Pipeline - Unified
echo ======================================
echo.

echo Iniciando dashboard unificado...
echo.
echo Dashboard Unificado: http://localhost:8501
echo   - Dashboard Principal
echo   - ML Analytics  
echo   - Analise Tecnica (em desenvolvimento)
echo.
echo Para parar: Feche esta janela
echo.

cd /d "%~dp0"

start "Crypto Dashboard" cmd /c "streamlit run unified_dashboard.py --server.port 8501"

echo.
echo Dashboard unificado iniciado!
echo Aguarde alguns segundos para que inicialize completamente.
echo.
pause
