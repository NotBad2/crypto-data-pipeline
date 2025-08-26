"""
Data Warehouse para dados históricos de criptomoedas
Coleta e armazena dados para análise ML
"""

import pandas as pd
import sqlite3
import requests
import time
from datetime import datetime, timedelta
import json
import os

class CryptoDataWarehouse:
    def __init__(self, db_path="crypto_warehouse.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de preços históricos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                date TEXT NOT NULL,
                price REAL NOT NULL,
                market_cap REAL,
                volume REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(coin_id, timestamp)
            )
        ''')
        
        # Tabela de indicadores técnicos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL,
                date TEXT NOT NULL,
                sma_7 REAL,
                sma_14 REAL,
                sma_30 REAL,
                ema_12 REAL,
                ema_26 REAL,
                rsi_14 REAL,
                macd REAL,
                macd_signal REAL,
                bollinger_upper REAL,
                bollinger_lower REAL,
                volatility REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(coin_id, date)
            )
        ''')
        
        # Tabela de features para ML
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL,
                date TEXT NOT NULL,
                price_current REAL NOT NULL,
                price_1d_ago REAL,
                price_7d_ago REAL,
                price_30d_ago REAL,
                volume_avg_7d REAL,
                volume_avg_30d REAL,
                volatility_7d REAL,
                volatility_30d REAL,
                rsi_14 REAL,
                macd_signal_strength REAL,
                trend_direction INTEGER,
                support_level REAL,
                resistance_level REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(coin_id, date)
            )
        ''')
        
        # Tabela de previsões
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id TEXT NOT NULL,
                prediction_date TEXT NOT NULL,
                target_date TEXT NOT NULL,
                predicted_price REAL NOT NULL,
                confidence_score REAL,
                model_version TEXT,
                actual_price REAL,
                error_percentage REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Data Warehouse inicializado!")
    
    def collect_historical_data(self, coin_id="bitcoin", days=365):
        """Coleta dados históricos da CoinGecko"""
        print(f"🔄 Coletando dados históricos de {coin_id} ({days} dias)...")
        
        try:
            # CoinGecko API para dados históricos
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Processar dados
            prices = data['prices']
            market_caps = data['market_caps']
            volumes = data['total_volumes']
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Inserir dados históricos
            for i, (timestamp, price) in enumerate(prices):
                date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                market_cap = market_caps[i][1] if i < len(market_caps) else None
                volume = volumes[i][1] if i < len(volumes) else None
                
                cursor.execute('''
                    INSERT OR REPLACE INTO historical_prices 
                    (coin_id, symbol, timestamp, date, price, market_cap, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (coin_id, coin_id.upper(), timestamp, date, price, market_cap, volume))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Coletados {len(prices)} pontos de dados para {coin_id}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao coletar dados históricos: {e}")
            return False
    
    def calculate_technical_indicators(self, coin_id="bitcoin"):
        """Calcula indicadores técnicos"""
        print(f"📊 Calculando indicadores técnicos para {coin_id}...")
        
        conn = sqlite3.connect(self.db_path)
        
        # Buscar dados históricos
        df = pd.read_sql_query('''
            SELECT date, price, volume
            FROM historical_prices 
            WHERE coin_id = ?
            ORDER BY date
        ''', conn, params=(coin_id,))
        
        if df.empty:
            print("❌ Nenhum dado histórico encontrado")
            return False
        
        # Calcular indicadores
        df['sma_7'] = df['price'].rolling(window=7).mean()
        df['sma_14'] = df['price'].rolling(window=14).mean()
        df['sma_30'] = df['price'].rolling(window=30).mean()
        
        # EMA
        df['ema_12'] = df['price'].ewm(span=12).mean()
        df['ema_26'] = df['price'].ewm(span=26).mean()
        
        # RSI
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Bandas de Bollinger
        df['bb_middle'] = df['sma_14']
        bb_std = df['price'].rolling(window=14).std()
        df['bollinger_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bollinger_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Volatilidade
        df['volatility'] = df['price'].rolling(window=14).std() / df['price'].rolling(window=14).mean()
        
        # Inserir indicadores no banco
        cursor = conn.cursor()
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO technical_indicators 
                (coin_id, date, sma_7, sma_14, sma_30, ema_12, ema_26, rsi_14, 
                 macd, macd_signal, bollinger_upper, bollinger_lower, volatility)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (coin_id, row['date'], row['sma_7'], row['sma_14'], row['sma_30'],
                  row['ema_12'], row['ema_26'], row['rsi_14'], row['macd'],
                  row['macd_signal'], row['bollinger_upper'], row['bollinger_lower'],
                  row['volatility']))
        
        conn.commit()
        conn.close()
        print(f"✅ Indicadores calculados para {coin_id}")
        return True
    
    def create_ml_features(self, coin_id="bitcoin"):
        """Cria features para Machine Learning"""
        print(f"🤖 Criando features ML para {coin_id}...")
        
        conn = sqlite3.connect(self.db_path)
        
        # Buscar dados com indicadores
        df = pd.read_sql_query('''
            SELECT h.date, h.price, h.volume, t.rsi_14, t.macd, t.macd_signal,
                   t.volatility, t.bollinger_upper, t.bollinger_lower
            FROM historical_prices h
            LEFT JOIN technical_indicators t ON h.coin_id = t.coin_id AND h.date = t.date
            WHERE h.coin_id = ?
            ORDER BY h.date
        ''', conn, params=(coin_id,))
        
        if df.empty:
            print("❌ Nenhum dado encontrado para features")
            return False
        
        # Criar features de lag
        df['price_1d_ago'] = df['price'].shift(1)
        df['price_7d_ago'] = df['price'].shift(7)
        df['price_30d_ago'] = df['price'].shift(30)
        
        # Médias móveis de volume
        df['volume_avg_7d'] = df['volume'].rolling(window=7).mean()
        df['volume_avg_30d'] = df['volume'].rolling(window=30).mean()
        
        # Volatilidade em diferentes períodos
        df['volatility_7d'] = df['price'].rolling(window=7).std()
        df['volatility_30d'] = df['price'].rolling(window=30).std()
        
        # MACD signal strength
        df['macd_signal_strength'] = abs(df['macd'] - df['macd_signal'])
        
        # Trend direction (1 = up, -1 = down, 0 = sideways)
        df['price_change_7d'] = df['price'].pct_change(7)
        df['trend_direction'] = df['price_change_7d'].apply(
            lambda x: 1 if x > 0.05 else (-1 if x < -0.05 else 0)
        )
        
        # Support and Resistance (simplified)
        df['support_level'] = df['price'].rolling(window=30).min()
        df['resistance_level'] = df['price'].rolling(window=30).max()
        
        # Inserir features no banco
        cursor = conn.cursor()
        for _, row in df.iterrows():
            if pd.notna(row['price_1d_ago']):  # Skip rows with insufficient data
                cursor.execute('''
                    INSERT OR REPLACE INTO ml_features 
                    (coin_id, date, price_current, price_1d_ago, price_7d_ago, price_30d_ago,
                     volume_avg_7d, volume_avg_30d, volatility_7d, volatility_30d, rsi_14,
                     macd_signal_strength, trend_direction, support_level, resistance_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (coin_id, row['date'], row['price'], row['price_1d_ago'],
                      row['price_7d_ago'], row['price_30d_ago'], row['volume_avg_7d'],
                      row['volume_avg_30d'], row['volatility_7d'], row['volatility_30d'],
                      row['rsi_14'], row['macd_signal_strength'], row['trend_direction'],
                      row['support_level'], row['resistance_level']))
        
        conn.commit()
        conn.close()
        print(f"✅ Features ML criadas para {coin_id}")
        return True
    
    def get_ml_data(self, coin_id="bitcoin"):
        """Retorna dados para treinamento ML"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM ml_features 
            WHERE coin_id = ?
            ORDER BY date
        ''', conn, params=(coin_id,))
        conn.close()
        return df
    
    def get_historical_data(self, coin_id="bitcoin", days=30):
        """Retorna dados históricos para visualização"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT h.*, t.rsi_14, t.macd, t.macd_signal, t.bollinger_upper, t.bollinger_lower
            FROM historical_prices h
            LEFT JOIN technical_indicators t ON h.coin_id = t.coin_id AND h.date = t.date
            WHERE h.coin_id = ? 
            ORDER BY h.date DESC
            LIMIT ?
        ''', conn, params=(coin_id, days))
        conn.close()
        return df.sort_values('date')

def main():
    """Função principal para popular o Data Warehouse"""
    dw = CryptoDataWarehouse()
    
    # Lista de principais criptomoedas
    coins = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana', 
             'polkadot', 'dogecoin', 'avalanche-2', 'chainlink', 'polygon']
    
    for coin in coins:
        print(f"\n🔄 Processando {coin}...")
        
        # Coletar dados históricos (1 ano)
        if dw.collect_historical_data(coin, days=365):
            # Calcular indicadores técnicos
            dw.calculate_technical_indicators(coin)
            # Criar features ML
            dw.create_ml_features(coin)
        
        # Pequena pausa para não sobrecarregar a API
        time.sleep(2)
    
    print("\n🎉 Data Warehouse populado com sucesso!")
    print(f"📁 Banco de dados salvo em: {os.path.abspath(dw.db_path)}")

if __name__ == "__main__":
    main()
