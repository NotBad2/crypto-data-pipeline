@echo off
echo ======================================
echo   Crypto Data Pipeline - Unified App
echo ======================================
echo.

echo Iniciando dashboard unificado...
echo.
echo URL: http://localhost:8520
echo.
echo Para parar: Ctrl+C ou feche esta janela
echo.

cd /d "%~dp0"

streamlit run crypto_app_unified.py --server.port 8520

pause
