#!/bin/bash

# Script de inicialização para Render.com
echo "🚀 Iniciando Crypto Data Pipeline no Render..."

# Verificar se a base de dados existe, se não criar uma vazia
if [ ! -f "data/crypto_warehouse.db" ]; then
    echo "📊 Criando base de dados inicial..."
    mkdir -p data
    python -c "
import sqlite3
import os

# Criar directório se não existir
os.makedirs('data', exist_ok=True)

# Criar base de dados vazia
conn = sqlite3.connect('data/crypto_warehouse.db')
cursor = conn.cursor()

# Criar tabelas básicas
cursor.execute('''
CREATE TABLE IF NOT EXISTS historical_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coin_id TEXT NOT NULL,
    date DATE NOT NULL,
    price REAL NOT NULL,
    volume REAL,
    market_cap REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS technical_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coin_id TEXT NOT NULL,
    date DATE NOT NULL,
    sma_7 REAL,
    sma_14 REAL,
    sma_30 REAL,
    rsi_14 REAL,
    macd REAL,
    macd_signal REAL,
    bollinger_upper REAL,
    bollinger_lower REAL,
    volatility REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ml_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coin_id TEXT NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_price REAL NOT NULL,
    model_version TEXT,
    confidence_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print('✅ Base de dados criada com sucesso!')
"
fi

echo "🌐 Iniciando aplicação Streamlit..."
exec streamlit run src/dashboard/crypto_app_unified.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
