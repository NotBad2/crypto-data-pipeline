@echo off
title Crypto Data Pipeline - Ativador de Serviços
color 0a

echo.
echo ===============================================
echo    CRYPTO DATA PIPELINE - ATIVADOR COMPLETO
echo ===============================================
echo.

echo [INFO] Verificando estrutura do projeto...

REM Verificar se estamos no diretório correto
if not exist "src" (
    echo [ERRO] Execute este script a partir da raiz do projeto crypto-data-pipeline
    echo [INFO] Estrutura esperada: crypto-data-pipeline\src\...
    pause
    exit /b 1
)

echo [OK] Estrutura do projeto encontrada
echo.

REM ===== 1. VERIFICAR E INSTALAR DEPENDÊNCIAS =====
echo ===============================================
echo          ETAPA 1: DEPENDÊNCIAS PYTHON
echo ===============================================
echo.

echo [INFO] Verificando instalação do Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não encontrado! Instale o Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

echo.
echo [INFO] Instalando/Atualizando dependências...
cd src\dashboard
if exist requirements.txt (
    echo [INFO] Instalando pacotes do requirements.txt...
    pip install -r requirements.txt
) else (
    echo [INFO] Instalando pacotes essenciais...
    pip install streamlit pandas plotly requests scikit-learn joblib numpy
)

echo [OK] Dependências instaladas
echo.

REM ===== 2. VERIFICAR DATA WAREHOUSE =====
echo ===============================================
echo        ETAPA 2: VERIFICAR DATA WAREHOUSE
echo ===============================================
echo.

cd ..\data_warehouse
if exist crypto_warehouse.db (
    echo [OK] Data Warehouse encontrado
    echo [INFO] Tamanho da base de dados:
    dir crypto_warehouse.db | find ".db"
) else (
    echo [AVISO] Data Warehouse não encontrado
    echo [INFO] Criando dados históricos para ML...
    
    if exist data_warehouse.py (
        echo [INFO] Executando coleta de dados históricos...
        python data_warehouse.py
        echo [OK] Dados históricos coletados
    ) else (
        echo [AVISO] Script de data warehouse não encontrado
        echo [INFO] O dashboard funcionará apenas com dados da API
    )
)

echo.

REM ===== 3. TREINAR MODELOS ML =====
echo ===============================================
echo           ETAPA 3: MODELOS ML
echo ===============================================
echo.

if exist ml_models.py (
    echo [INFO] Verificando modelos ML...
    python -c "import os; print('[OK] Modelos encontrados:' if any('model' in f for f in os.listdir('.')) else '[INFO] Treinando novos modelos...')"
    
    echo [INFO] Executando pipeline de ML...
    python ml_models.py
    echo [OK] Modelos ML atualizados
) else (
    echo [AVISO] Pipeline ML não encontrado - funcionalidades ML limitadas
)

echo.

REM ===== 4. INICIAR DASHBOARD =====
echo ===============================================
echo         ETAPA 4: INICIAR DASHBOARD
echo ===============================================
echo.

cd ..\dashboard

echo [INFO] Parando processos Streamlit existentes...
taskkill /f /im streamlit.exe > nul 2>&1

echo [INFO] Aguardando limpeza de processos...
timeout /t 3 > nul

echo [INFO] Iniciando Dashboard Unificado...
echo.
echo ===============================================
echo              DASHBOARD ATIVO!
echo ===============================================
echo.
echo    URL Principal: http://localhost:8510
echo.
echo    Páginas Disponíveis:
echo    📊 Dashboard Principal - Dados em tempo real
echo    🤖 ML Analytics       - Machine Learning
echo    📈 Análise Técnica    - Em desenvolvimento
echo.
echo    Para parar: Ctrl+C ou feche esta janela
echo.
echo ===============================================

REM Iniciar o dashboard
streamlit run crypto_app_unified.py --server.port 8510 --server.headless true

REM Se chegou aqui, o streamlit foi fechado
echo.
echo [INFO] Dashboard encerrado
echo [INFO] Limpando processos...
taskkill /f /im streamlit.exe > nul 2>&1

echo [INFO] Serviços encerrados com sucesso
pause
