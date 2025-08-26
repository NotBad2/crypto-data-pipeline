@echo off
echo ======================================
echo   Crypto Data Pipeline Dashboard
echo ======================================
echo.

echo Verificando dependencias...
python -c "import streamlit, plotly" 2>nul
if errorlevel 1 (
    echo Instalando dependencias...
    pip install streamlit plotly psycopg2-binary redis pandas numpy
) else (
    echo Dependencias OK!
)

echo.
echo Iniciando dashboard principal...
echo Acesse: http://localhost:8501
echo.
echo Para parar: Ctrl+C
echo.

cd /d "%~dp0"
streamlit run app.py --server.port 8501
