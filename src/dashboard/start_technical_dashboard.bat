@echo off
echo ======================================
echo   Analise Tecnica Dashboard
echo ======================================
echo.

echo Iniciando dashboard de analise tecnica...
echo Acesse: http://localhost:8502
echo.
echo Para parar: Ctrl+C
echo.

cd /d "%~dp0"
streamlit run technical_analysis.py --server.port 8502
