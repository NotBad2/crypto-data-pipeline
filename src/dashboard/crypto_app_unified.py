import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import time
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# Configuração da página
st.set_page_config(
    page_title="Crypto Data Pipeline",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar CSS customizado
def load_css():
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Navegação por páginas
def create_navigation():
    st.sidebar.title("🚀 Crypto Data Pipeline")
    
    pages = {
        "📊 Dashboard Principal": "dashboard",
        "🤖 ML Analytics": "ml_analytics",
        "📈 Análise Técnica": "technical_analysis"
    }
    
    selected_page = st.sidebar.radio(
        "Navegação:",
        list(pages.keys()),
        key="page_selector"
    )
    
    return pages[selected_page]

# ============= DASHBOARD PRINCIPAL =============
@st.cache_data(ttl=300)
def get_crypto_data():
    """Busca dados de criptomoedas da API CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 50,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '1h,24h,7d'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data)
        
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_market_overview():
    """Busca dados gerais do mercado"""
    try:
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        return response.json()['data']
    except Exception as e:
        st.error(f"Erro ao buscar dados de mercado: {str(e)}")
        return {}

def show_dashboard_page():
    st.title("₿ Crypto Dashboard")
    
    # Dados de mercado
    market_data = get_market_overview()
    
    if market_data:
        st.header("📊 Visão Geral do Mercado")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_market_cap = market_data.get('total_market_cap', {}).get('usd', 0)
            st.metric(
                "Market Cap Total",
                f"${total_market_cap:,.0f}",
                delta=f"{market_data.get('market_cap_change_percentage_24h_usd', 0):.2f}%"
            )
        
        with col2:
            total_volume = market_data.get('total_volume', {}).get('usd', 0)
            st.metric(
                "Volume 24h",
                f"${total_volume:,.0f}"
            )
        
        with col3:
            btc_dominance = market_data.get('market_cap_percentage', {}).get('btc', 0)
            st.metric(
                "Dominância BTC",
                f"{btc_dominance:.1f}%"
            )
        
        with col4:
            active_cryptos = market_data.get('active_cryptocurrencies', 0)
            st.metric(
                "Criptos Ativas",
                f"{active_cryptos:,}"
            )
    
    # Dados das criptomoedas
    df = get_crypto_data()
    
    if not df.empty:
        st.header("💰 Top Criptomoedas")
        
        # Seleção de moedas
        selected_coins = st.sidebar.multiselect(
            "Selecionar Criptomoedas",
            options=df['name'].tolist(),
            default=df['name'].head(10).tolist()
        )
        
        if selected_coins:
            filtered_df = df[df['name'].isin(selected_coins)].copy()
            
            # Tabela principal
            display_columns = []
            available_columns = filtered_df.columns.tolist()
            
            # Verificar quais colunas estão disponíveis
            basic_columns = ['name', 'symbol', 'current_price', 'market_cap', 'price_change_percentage_24h']
            for col in basic_columns:
                if col in available_columns:
                    display_columns.append(col)
            
            # Adicionar coluna de 7 dias se disponível
            if 'price_change_percentage_7d' in available_columns:
                display_columns.append('price_change_percentage_7d')
            
            # Configuração das colunas
            column_config = {
                "name": "Nome",
                "symbol": "Símbolo",
                "current_price": st.column_config.NumberColumn(
                    "Preço Atual ($)",
                    format="$%.2f"
                ),
                "market_cap": st.column_config.NumberColumn(
                    "Market Cap",
                    format="$%.0f"
                ),
                "price_change_percentage_24h": st.column_config.NumberColumn(
                    "Variação 24h (%)",
                    format="%.2f%%"
                )
            }
            
            if 'price_change_percentage_7d' in display_columns:
                column_config["price_change_percentage_7d"] = st.column_config.NumberColumn(
                    "Variação 7d (%)",
                    format="%.2f%%"
                )
            
            st.dataframe(
                filtered_df[display_columns],
                column_config=column_config,
                use_container_width=True
            )
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de Market Cap
                fig_market_cap = px.bar(
                    filtered_df.head(10),
                    x='name',
                    y='market_cap',
                    title="Market Cap por Criptomoeda",
                    labels={'market_cap': 'Market Cap ($)', 'name': 'Criptomoeda'}
                )
                fig_market_cap.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig_market_cap, use_container_width=True)
            
            with col2:
                # Gráfico de Performance 24h
                fig_performance = px.bar(
                    filtered_df.head(10),
                    x='name',
                    y='price_change_percentage_24h',
                    title="Performance 24h (%)",
                    labels={'price_change_percentage_24h': 'Variação (%)', 'name': 'Criptomoeda'},
                    color='price_change_percentage_24h',
                    color_continuous_scale=['red', 'yellow', 'green']
                )
                fig_performance.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig_performance, use_container_width=True)
            
            # Análise detalhada
            st.header("🔍 Análise Detalhada")
            
            selected_coin = st.selectbox(
                "Selecionar criptomoeda para análise:",
                options=filtered_df['name'].tolist()
            )
            
            if selected_coin:
                coin_data = filtered_df[filtered_df['name'] == selected_coin].iloc[0]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        f"{coin_data['name']} ({coin_data['symbol'].upper()})",
                        f"${coin_data['current_price']:.2f}",
                        delta=f"{coin_data['price_change_percentage_24h']:.2f}%"
                    )
                
                with col2:
                    st.metric(
                        "Volume 24h",
                        f"${coin_data['total_volume']:,.0f}"
                    )
                
                with col3:
                    st.metric(
                        "Market Cap Rank",
                        f"#{coin_data['market_cap_rank']}"
                    )

# ============= ML ANALYTICS =============
@st.cache_resource
def get_db_connection():
    """Conexão com o Data Warehouse"""
    try:
        # Caminho que funciona tanto local quanto no cloud
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Tentar diferentes caminhos possíveis
        possible_paths = [
            os.path.join(current_dir, '..', 'crypto_warehouse.db'),  # Local
            os.path.join(current_dir, '..', '..', 'src', 'crypto_warehouse.db'),  # Cloud
            'src/crypto_warehouse.db',  # Cloud root
            'crypto_warehouse.db'  # Mesmo diretório
        ]
        
        db_path = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                db_path = abs_path
                break
        
        if not db_path:
            st.error("⚠️ Base de dados não encontrada. Criando base de dados...")
            # Tentar criar base de dados básica
            db_path = os.path.join(current_dir, 'crypto_warehouse.db')
            create_empty_db(db_path)
            st.warning("📊 Base de dados vazia criada. Para dados completos, execute o script de coleta.")
            
        conn = sqlite3.connect(db_path, check_same_thread=False)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar à base de dados: {str(e)}")
        return None

def create_empty_db(db_path):
    """Cria uma base de dados vazia com estrutura básica"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabelas básicas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT,
            date TEXT,
            price REAL,
            volume REAL,
            market_cap REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technical_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT,
            date TEXT,
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
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT,
            prediction_date TEXT,
            target_date TEXT,
            predicted_price REAL,
            confidence_score REAL,
            model_version TEXT,
            actual_price REAL,
            error_percentage REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

@st.cache_data(ttl=300)
def get_historical_data(coin_id, days=90):
    """Busca dados históricos com indicadores"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT h.date, h.price, h.volume, h.market_cap,
               t.sma_7, t.sma_14, t.sma_30, t.rsi_14, t.macd, t.macd_signal,
               t.bollinger_upper, t.bollinger_lower, t.volatility
        FROM historical_prices h
        LEFT JOIN technical_indicators t ON h.coin_id = t.coin_id AND h.date = t.date
        WHERE h.coin_id = ?
        ORDER BY h.date DESC
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=(coin_id, days))
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    except Exception as e:
        st.error(f"Erro ao buscar dados históricos: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_ml_predictions(coin_id):
    """Busca previsões ML da base de dados"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT prediction_date, predicted_price, model_version, confidence_score
        FROM ml_predictions 
        WHERE coin_id = ?
        ORDER BY prediction_date DESC
        LIMIT 30
        """
        
        df = pd.read_sql_query(query, conn, params=(coin_id,))
        if not df.empty:
            df['prediction_date'] = pd.to_datetime(df['prediction_date'])
        return df
    except Exception as e:
        st.error(f"Erro ao buscar previsões: {str(e)}")
        return pd.DataFrame()

def show_ml_analytics_page():
    st.title("🤖 ML Analytics Dashboard")
    
    # Verificar conexão
    conn = get_db_connection()
    if not conn:
        st.error("❌ Falha na conexão à base de dados")
        st.info("Execute o script de coleta de dados primeiro.")
        return
    
    # Seleção de criptomoeda
    coins_available = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana']
    selected_coin = st.sidebar.selectbox(
        "Selecionar Criptomoeda:",
        coins_available,
        format_func=lambda x: x.replace('binancecoin', 'BNB').title()
    )
    
    # Período de análise
    days = st.sidebar.slider("Período (dias):", 30, 365, 90)
    
    # Buscar dados
    df_historical = get_historical_data(selected_coin, days)
    df_predictions = get_ml_predictions(selected_coin)
    
    if not df_historical.empty:
        # Métricas principais
        st.header("📈 Métricas Principais")
        col1, col2, col3, col4 = st.columns(4)
        
        current_price = df_historical['price'].iloc[-1]
        price_change = ((current_price / df_historical['price'].iloc[0]) - 1) * 100
        volatility = df_historical['volatility'].iloc[-1] if 'volatility' in df_historical.columns else 0
        
        with col1:
            st.metric("Preço Atual", f"${current_price:.2f}")
        
        with col2:
            st.metric("Variação Período", f"{price_change:.2f}%")
        
        with col3:
            st.metric("Volume Médio", f"${df_historical['volume'].mean():,.0f}")
        
        with col4:
            st.metric("Volatilidade", f"{volatility:.2f}%" if volatility else "N/A")
        
        # Gráfico de preços com indicadores técnicos
        st.header("📊 Análise Técnica")
        
        fig = go.Figure()
        
        # Preço
        fig.add_trace(go.Scatter(
            x=df_historical['date'],
            y=df_historical['price'],
            mode='lines',
            name='Preço',
            line=dict(color='blue', width=2)
        ))
        
        # Médias móveis
        if 'sma_7' in df_historical.columns:
            fig.add_trace(go.Scatter(
                x=df_historical['date'],
                y=df_historical['sma_7'],
                mode='lines',
                name='SMA 7',
                line=dict(color='orange', width=1)
            ))
        
        if 'sma_30' in df_historical.columns:
            fig.add_trace(go.Scatter(
                x=df_historical['date'],
                y=df_historical['sma_30'],
                mode='lines',
                name='SMA 30',
                line=dict(color='red', width=1)
            ))
        
        # Bandas de Bollinger
        if 'bollinger_upper' in df_historical.columns:
            fig.add_trace(go.Scatter(
                x=df_historical['date'],
                y=df_historical['bollinger_upper'],
                mode='lines',
                name='Bollinger Superior',
                line=dict(color='gray', width=1, dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=df_historical['date'],
                y=df_historical['bollinger_lower'],
                mode='lines',
                name='Bollinger Inferior',
                line=dict(color='gray', width=1, dash='dash')
            ))
        
        fig.update_layout(
            title=f"Análise Técnica - {selected_coin.title()}",
            xaxis_title="Data",
            yaxis_title="Preço ($)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Previsões ML
        if not df_predictions.empty:
            st.header("🔮 Previsões Machine Learning")
            
            # Estatísticas das previsões
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_confidence = df_predictions['confidence_score'].mean()
                st.metric("Confiança Média", f"{avg_confidence:.2f}")
            
            with col2:
                latest_prediction = df_predictions['predicted_price'].iloc[0]
                st.metric("Última Previsão", f"${latest_prediction:.2f}")
            
            with col3:
                total_predictions = len(df_predictions)
                st.metric("Total Previsões", total_predictions)
            
            # Gráfico de previsões
            fig_pred = go.Figure()
            
            # Dados históricos (últimos 30 dias)
            recent_data = df_historical.tail(30)
            fig_pred.add_trace(go.Scatter(
                x=recent_data['date'],
                y=recent_data['price'],
                mode='lines',
                name='Preço Histórico',
                line=dict(color='blue', width=2)
            ))
            
            # Previsões por modelo
            for model in df_predictions['model_version'].unique():
                model_data = df_predictions[df_predictions['model_version'] == model]
                fig_pred.add_trace(go.Scatter(
                    x=model_data['prediction_date'],
                    y=model_data['predicted_price'],
                    mode='lines+markers',
                    name=f'Previsão {model}',
                    line=dict(width=2, dash='dash')
                ))
            
            fig_pred.update_layout(
                title=f"Previsões vs Dados Históricos - {selected_coin.title()}",
                xaxis_title="Data",
                yaxis_title="Preço ($)",
                height=400
            )
            
            st.plotly_chart(fig_pred, use_container_width=True)
            
            # Tabela de previsões
            st.subheader("📋 Últimas Previsões")
            st.dataframe(
                df_predictions.head(10),
                column_config={
                    "prediction_date": "Data Previsão",
                    "predicted_price": st.column_config.NumberColumn(
                        "Preço Previsto ($)",
                        format="$%.2f"
                    ),
                    "model_version": "Modelo",
                    "confidence_score": st.column_config.NumberColumn(
                        "Confiança",
                        format="%.2f"
                    )
                },
                use_container_width=True
            )
        
        # Indicadores técnicos
        if 'rsi_14' in df_historical.columns:
            st.header("📊 Indicadores Técnicos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # RSI
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=df_historical['date'],
                    y=df_historical['rsi_14'],
                    mode='lines',
                    name='RSI 14',
                    line=dict(color='purple', width=2)
                ))
                
                # Linhas de referência RSI
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Sobrecomprado")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Sobrevendido")
                
                fig_rsi.update_layout(
                    title="RSI (14 períodos)",
                    xaxis_title="Data",
                    yaxis_title="RSI",
                    height=300
                )
                
                st.plotly_chart(fig_rsi, use_container_width=True)
            
            with col2:
                # MACD
                if 'macd' in df_historical.columns:
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(
                        x=df_historical['date'],
                        y=df_historical['macd'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='blue', width=2)
                    ))
                    
                    if 'macd_signal' in df_historical.columns:
                        fig_macd.add_trace(go.Scatter(
                            x=df_historical['date'],
                            y=df_historical['macd_signal'],
                            mode='lines',
                            name='MACD Signal',
                            line=dict(color='red', width=1)
                        ))
                    
                    fig_macd.update_layout(
                        title="MACD",
                        xaxis_title="Data",
                        yaxis_title="MACD",
                        height=300
                    )
                    
                    st.plotly_chart(fig_macd, use_container_width=True)
    
    else:
        st.warning("Dados históricos não disponíveis. Execute o script de coleta de dados primeiro.")

# ============= ANÁLISE TÉCNICA =============
def calculate_support_resistance(df, window=20):
    """Calcula níveis de suporte e resistência"""
    highs = df['price'].rolling(window=window).max()
    lows = df['price'].rolling(window=window).min()
    
    # Encontrar pontos de pivot
    resistance_levels = []
    support_levels = []
    
    for i in range(window, len(df) - window):
        # Resistência: preço atual é máximo local
        if df['price'].iloc[i] == highs.iloc[i]:
            resistance_levels.append((df['date'].iloc[i], df['price'].iloc[i]))
        
        # Suporte: preço atual é mínimo local
        if df['price'].iloc[i] == lows.iloc[i]:
            support_levels.append((df['date'].iloc[i], df['price'].iloc[i]))
    
    return support_levels[-5:], resistance_levels[-5:]  # Últimos 5 de cada

def calculate_fibonacci_levels(df):
    """Calcula níveis de retração de Fibonacci"""
    recent_data = df.tail(100)  # Últimos 100 pontos
    high = recent_data['price'].max()
    low = recent_data['price'].min()
    
    diff = high - low
    
    levels = {
        'Fibonacci 0%': high,
        'Fibonacci 23.6%': high - diff * 0.236,
        'Fibonacci 38.2%': high - diff * 0.382,
        'Fibonacci 50%': high - diff * 0.5,
        'Fibonacci 61.8%': high - diff * 0.618,
        'Fibonacci 100%': low
    }
    
    return levels

def calculate_additional_indicators(df):
    """Calcula indicadores técnicos adicionais"""
    # Stochastic %K e %D
    low_14 = df['price'].rolling(window=14).min()
    high_14 = df['price'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['price'] - low_14) / (high_14 - low_14))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
    
    # Williams %R
    df['williams_r'] = -100 * ((high_14 - df['price']) / (high_14 - low_14))
    
    # Momentum
    df['momentum'] = df['price'] / df['price'].shift(10) * 100
    
    # Rate of Change (ROC)
    df['roc'] = ((df['price'] - df['price'].shift(12)) / df['price'].shift(12)) * 100
    
    return df

def detect_candlestick_patterns(df):
    """Detecta padrões de candlestick básicos"""
    patterns = []
    
    for i in range(2, len(df)):
        current = df.iloc[i]
        prev = df.iloc[i-1]
        prev2 = df.iloc[i-2]
        
        # Simulando OHLC com base no preço (aproximação)
        open_price = prev['price']
        close_price = current['price']
        high_price = max(open_price, close_price) * 1.01
        low_price = min(open_price, close_price) * 0.99
        
        # Doji: abertura ≈ fechamento
        if abs(open_price - close_price) / close_price < 0.001:
            patterns.append({
                'date': current['date'],
                'pattern': 'Doji',
                'signal': 'Indecisão',
                'price': close_price
            })
        
        # Martelo: corpo pequeno, sombra inferior longa
        body = abs(close_price - open_price)
        lower_shadow = min(open_price, close_price) - low_price
        if body > 0 and lower_shadow > body * 2:
            patterns.append({
                'date': current['date'],
                'pattern': 'Martelo',
                'signal': 'Possível reversão alta',
                'price': close_price
            })
    
    return patterns[-10:]  # Últimos 10 padrões

def show_technical_analysis_page():
    st.title("📈 Análise Técnica Avançada")
    
    # Verificar conexão
    conn = get_db_connection()
    if not conn:
        st.error("❌ Falha na conexão à base de dados")
        st.info("Execute o script de coleta de dados primeiro.")
        return
    
    # Seleção de criptomoeda
    coins_available = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana']
    selected_coin = st.sidebar.selectbox(
        "Selecionar Criptomoeda:",
        coins_available,
        format_func=lambda x: x.replace('binancecoin', 'BNB').title(),
        key="ta_coin_selector"
    )
    
    # Período de análise
    days = st.sidebar.slider("Período (dias):", 30, 365, 90, key="ta_days")
    
    # Buscar dados históricos
    df_historical = get_historical_data(selected_coin, days)
    
    if df_historical.empty:
        st.warning("Dados não disponíveis para esta criptomoeda.")
        return
    
    # Calcular indicadores adicionais
    df_analysis = calculate_additional_indicators(df_historical.copy())
    
    # ===== SEÇÃO 1: GRÁFICO PRINCIPAL COM SUPORTE/RESISTÊNCIA =====
    st.header("📊 Gráfico com Suporte e Resistência")
    
    support_levels, resistance_levels = calculate_support_resistance(df_historical)
    fibonacci_levels = calculate_fibonacci_levels(df_historical)
    
    fig_main = go.Figure()
    
    # Preço principal
    fig_main.add_trace(go.Scatter(
        x=df_historical['date'],
        y=df_historical['price'],
        mode='lines',
        name='Preço',
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Médias móveis
    if 'sma_7' in df_historical.columns:
        fig_main.add_trace(go.Scatter(
            x=df_historical['date'],
            y=df_historical['sma_7'],
            mode='lines',
            name='SMA 7',
            line=dict(color='orange', width=1)
        ))
    
    if 'sma_30' in df_historical.columns:
        fig_main.add_trace(go.Scatter(
            x=df_historical['date'],
            y=df_historical['sma_30'],
            mode='lines',
            name='SMA 30',
            line=dict(color='red', width=1)
        ))
    
    # Níveis de suporte (verde)
    for date, price in support_levels:
        fig_main.add_hline(
            y=price,
            line_dash="dash",
            line_color="green",
            opacity=0.5,
            annotation_text=f"Suporte: ${price:.2f}"
        )
    
    # Níveis de resistência (vermelho)
    for date, price in resistance_levels:
        fig_main.add_hline(
            y=price,
            line_dash="dash",
            line_color="red",
            opacity=0.5,
            annotation_text=f"Resistência: ${price:.2f}"
        )
    
    fig_main.update_layout(
        title=f"Análise Técnica - {selected_coin.title()} com Suporte/Resistência",
        xaxis_title="Data",
        yaxis_title="Preço ($)",
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig_main, use_container_width=True)
    
    # ===== SEÇÃO 2: NÍVEIS DE FIBONACCI =====
    st.header("🌀 Níveis de Retração de Fibonacci")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_fib = go.Figure()
        
        # Preço
        fig_fib.add_trace(go.Scatter(
            x=df_historical['date'],
            y=df_historical['price'],
            mode='lines',
            name='Preço',
            line=dict(color='blue', width=2)
        ))
        
        # Níveis de Fibonacci
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
        for i, (level, price) in enumerate(fibonacci_levels.items()):
            fig_fib.add_hline(
                y=price,
                line_dash="dot",
                line_color=colors[i % len(colors)],
                annotation_text=level
            )
        
        fig_fib.update_layout(
            title="Níveis de Fibonacci",
            xaxis_title="Data",
            yaxis_title="Preço ($)",
            height=400
        )
        
        st.plotly_chart(fig_fib, use_container_width=True)
    
    with col2:
        st.subheader("📋 Níveis de Fibonacci")
        for level, price in fibonacci_levels.items():
            st.metric(level, f"${price:.2f}")
    
    # ===== SEÇÃO 3: OSCILADORES AVANÇADOS =====
    st.header("📈 Osciladores Avançados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Stochastic
        fig_stoch = go.Figure()
        fig_stoch.add_trace(go.Scatter(
            x=df_analysis['date'],
            y=df_analysis['stoch_k'],
            mode='lines',
            name='%K',
            line=dict(color='blue', width=2)
        ))
        fig_stoch.add_trace(go.Scatter(
            x=df_analysis['date'],
            y=df_analysis['stoch_d'],
            mode='lines',
            name='%D',
            line=dict(color='red', width=2)
        ))
        
        fig_stoch.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Sobrecomprado")
        fig_stoch.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Sobrevendido")
        
        fig_stoch.update_layout(
            title="Oscilador Estocástico",
            xaxis_title="Data",
            yaxis_title="Valor",
            height=300
        )
        
        st.plotly_chart(fig_stoch, use_container_width=True)
    
    with col2:
        # Williams %R
        fig_williams = go.Figure()
        fig_williams.add_trace(go.Scatter(
            x=df_analysis['date'],
            y=df_analysis['williams_r'],
            mode='lines',
            name='Williams %R',
            line=dict(color='purple', width=2)
        ))
        
        fig_williams.add_hline(y=-20, line_dash="dash", line_color="red", annotation_text="Sobrecomprado")
        fig_williams.add_hline(y=-80, line_dash="dash", line_color="green", annotation_text="Sobrevendido")
        
        fig_williams.update_layout(
            title="Williams %R",
            xaxis_title="Data",
            yaxis_title="Valor",
            height=300
        )
        
        st.plotly_chart(fig_williams, use_container_width=True)
    
    # ===== SEÇÃO 4: MOMENTUM E ROC =====
    st.header("⚡ Indicadores de Momentum")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Momentum
        fig_momentum = go.Figure()
        fig_momentum.add_trace(go.Scatter(
            x=df_analysis['date'],
            y=df_analysis['momentum'],
            mode='lines',
            name='Momentum',
            line=dict(color='green', width=2)
        ))
        
        fig_momentum.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Linha Zero")
        
        fig_momentum.update_layout(
            title="Momentum (10 períodos)",
            xaxis_title="Data",
            yaxis_title="Momentum",
            height=300
        )
        
        st.plotly_chart(fig_momentum, use_container_width=True)
    
    with col2:
        # Rate of Change
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(
            x=df_analysis['date'],
            y=df_analysis['roc'],
            mode='lines',
            name='ROC',
            line=dict(color='orange', width=2)
        ))
        
        fig_roc.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Linha Zero")
        
        fig_roc.update_layout(
            title="Rate of Change (12 períodos)",
            xaxis_title="Data",
            yaxis_title="ROC (%)",
            height=300
        )
        
        st.plotly_chart(fig_roc, use_container_width=True)
    
    # ===== SEÇÃO 5: PADRÕES DE CANDLESTICK =====
    st.header("🕯️ Padrões de Candlestick Detectados")
    
    patterns = detect_candlestick_patterns(df_historical)
    
    if patterns:
        patterns_df = pd.DataFrame(patterns)
        
        st.dataframe(
            patterns_df,
            column_config={
                "date": "Data",
                "pattern": "Padrão",
                "signal": "Sinal",
                "price": st.column_config.NumberColumn(
                    "Preço ($)",
                    format="$%.2f"
                )
            },
            use_container_width=True
        )
    else:
        st.info("Nenhum padrão de candlestick detectado no período selecionado.")
    
    # ===== SEÇÃO 6: RESUMO DA ANÁLISE =====
    st.header("📋 Resumo da Análise Técnica")
    
    # Métricas atuais
    current_price = df_historical['price'].iloc[-1]
    current_rsi = df_historical['rsi_14'].iloc[-1] if 'rsi_14' in df_historical.columns else None
    current_stoch = df_analysis['stoch_k'].iloc[-1]
    current_williams = df_analysis['williams_r'].iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Preço Atual", f"${current_price:.2f}")
    
    with col2:
        if current_rsi:
            rsi_signal = "🔴 Sobrecomprado" if current_rsi > 70 else "🟢 Sobrevendido" if current_rsi < 30 else "🟡 Neutro"
            st.metric("RSI", f"{current_rsi:.1f}", rsi_signal)
    
    with col3:
        stoch_signal = "🔴 Sobrecomprado" if current_stoch > 80 else "🟢 Sobrevendido" if current_stoch < 20 else "🟡 Neutro"
        st.metric("Estocástico", f"{current_stoch:.1f}", stoch_signal)
    
    with col4:
        williams_signal = "🔴 Sobrecomprado" if current_williams > -20 else "🟢 Sobrevendido" if current_williams < -80 else "🟡 Neutro"
        st.metric("Williams %R", f"{current_williams:.1f}", williams_signal)
    
    # Análise de tendência
    st.subheader("🎯 Análise de Tendência")
    
    sma_7 = df_historical['sma_7'].iloc[-1] if 'sma_7' in df_historical.columns else None
    sma_30 = df_historical['sma_30'].iloc[-1] if 'sma_30' in df_historical.columns else None
    
    if sma_7 and sma_30:
        if current_price > sma_7 > sma_30:
            trend = "📈 **Tendência de Alta** - Preço acima das médias móveis"
        elif current_price < sma_7 < sma_30:
            trend = "📉 **Tendência de Baixa** - Preço abaixo das médias móveis"
        else:
            trend = "↔️ **Tendência Lateral** - Sinais mistos"
        
        st.markdown(trend)
    
    # Níveis importantes
    st.subheader("📍 Níveis Importantes")
    
    if support_levels and resistance_levels:
        nearest_support = min(support_levels, key=lambda x: abs(x[1] - current_price))[1]
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x[1] - current_price))[1]
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"🟢 **Suporte mais próximo:** ${nearest_support:.2f}")
        with col2:
            st.error(f"🔴 **Resistência mais próxima:** ${nearest_resistance:.2f}")

# ============= MAIN =============
def main():
    load_css()
    
    # Navegação
    page = create_navigation()
    
    # Informações no sidebar
    st.sidebar.markdown("---")
    st.sidebar.info(f"**Última atualização:** {datetime.now().strftime('%H:%M:%S')}")
    
    # Mostrar página selecionada
    if page == "dashboard":
        show_dashboard_page()
    elif page == "ml_analytics":
        show_ml_analytics_page()
    elif page == "technical_analysis":
        show_technical_analysis_page()
    
    # Rodapé
    st.markdown("---")
    st.markdown("**Dados fornecidos por:** CoinGecko API | **ML Data:** SQLite Data Warehouse")

if __name__ == "__main__":
    main()
