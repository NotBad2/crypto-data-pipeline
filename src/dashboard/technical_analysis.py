import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
import numpy as np
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Análise Técnica - Crypto Dashboard",
    page_icon="📈",
    layout="wide"
)

# Configurações de conexão
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'crypto_data',
    'user': 'crypto_user',
    'password': 'crypto_pass'
}

@st.cache_resource
def get_db_connection():
    """Cria conexão com PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar com PostgreSQL: {e}")
        return None

@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_historical_data(coin_id="bitcoin", limit=100):
    """Simula dados históricos (em produção viria da API ou tabela histórica)"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        # Por enquanto, vamos usar os dados atuais e simular variação histórica
        query = """
        SELECT 
            coin_id,
            current_price,
            market_cap,
            total_volume,
            last_updated
        FROM coin_market_data 
        WHERE coin_id = %s
        ORDER BY last_updated DESC
        LIMIT 1
        """
        cursor = conn.cursor()
        cursor.execute(query, (coin_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Simular dados históricos para demonstração
            base_price = result[1]
            dates = pd.date_range(end=datetime.now(), periods=limit, freq='H')
            
            # Gerar preços com variação aleatória
            np.random.seed(42)  # Para reprodutibilidade
            price_changes = np.random.normal(0, 0.02, limit)  # 2% volatilidade
            prices = [base_price]
            
            for change in price_changes[1:]:
                new_price = prices[-1] * (1 + change)
                prices.append(max(new_price, 0.01))  # Evitar preços negativos
            
            df = pd.DataFrame({
                'timestamp': dates,
                'price': prices,
                'volume': np.random.uniform(base_price * 1000000, base_price * 5000000, limit),
                'market_cap': [p * 19000000 for p in prices]  # Simular market cap
            })
            
            return df
        
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Erro ao buscar dados históricos: {e}")
        return pd.DataFrame()

def calculate_technical_indicators(df):
    """Calcula indicadores técnicos"""
    if df.empty:
        return df
    
    # Médias móveis
    df['sma_20'] = df['price'].rolling(window=20).mean()
    df['sma_50'] = df['price'].rolling(window=50).mean()
    
    # Bandas de Bollinger
    df['bb_middle'] = df['sma_20']
    bb_std = df['price'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    
    # RSI
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['price'].ewm(span=12).mean()
    exp2 = df['price'].ewm(span=26).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    return df

@st.cache_data(ttl=60)
def get_coin_list():
    """Busca lista de moedas disponíveis"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        query = "SELECT DISTINCT coin_id, name FROM coin_market_data ORDER BY market_cap_rank"
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return [(row[0], row[1]) for row in results]
    except:
        return [("bitcoin", "Bitcoin")]

def main():
    st.title("📈 Análise Técnica de Criptomoedas")
    st.markdown("---")
    
    # Sidebar para seleção
    st.sidebar.header("⚙️ Configurações")
    
    # Seleção de moeda
    coin_options = get_coin_list()
    if coin_options:
        coin_names = [f"{name} ({coin_id})" for coin_id, name in coin_options]
        selected_index = st.sidebar.selectbox(
            "Selecione a Criptomoeda:",
            range(len(coin_names)),
            format_func=lambda x: coin_names[x]
        )
        selected_coin_id = coin_options[selected_index][0]
        selected_coin_name = coin_options[selected_index][1]
    else:
        selected_coin_id = "bitcoin"
        selected_coin_name = "Bitcoin"
    
    # Período de análise
    period = st.sidebar.selectbox(
        "Período de Análise:",
        [24, 48, 72, 168],  # 1, 2, 3 dias, 1 semana
        format_func=lambda x: f"{x}h" if x < 168 else f"{x//24} dias"
    )
    
    # Indicadores para mostrar
    st.sidebar.subheader("📊 Indicadores Técnicos")
    show_sma = st.sidebar.checkbox("Médias Móveis (SMA)", value=True)
    show_bollinger = st.sidebar.checkbox("Bandas de Bollinger", value=True)
    show_rsi = st.sidebar.checkbox("RSI", value=True)
    show_macd = st.sidebar.checkbox("MACD", value=True)
    
    # Buscar e processar dados
    with st.spinner(f"Carregando dados de {selected_coin_name}..."):
        df = get_historical_data(selected_coin_id, period)
        
        if not df.empty:
            df = calculate_technical_indicators(df)
            
            # Informações básicas
            st.header(f"💰 {selected_coin_name} ({selected_coin_id.upper()})")
            
            current_price = df['price'].iloc[-1]
            price_change = df['price'].iloc[-1] - df['price'].iloc[-2] if len(df) > 1 else 0
            price_change_pct = (price_change / df['price'].iloc[-2] * 100) if len(df) > 1 and df['price'].iloc[-2] != 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Preço Atual", f"${current_price:.2f}", f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
            
            with col2:
                st.metric("Máximo 24h", f"${df['price'].max():.2f}")
            
            with col3:
                st.metric("Mínimo 24h", f"${df['price'].min():.2f}")
            
            with col4:
                st.metric("Volume Médio", f"${df['volume'].mean():,.0f}")
            
            # Gráfico principal
            st.subheader("📊 Gráfico de Preços")
            
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=('Preço', 'Volume', 'RSI', 'MACD'),
                row_width=[0.4, 0.2, 0.2, 0.2]
            )
            
            # Preço e médias móveis
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df['price'], name='Preço', line=dict(color='blue')),
                row=1, col=1
            )
            
            if show_sma:
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['sma_20'], name='SMA 20', line=dict(color='orange')),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['sma_50'], name='SMA 50', line=dict(color='red')),
                    row=1, col=1
                )
            
            if show_bollinger:
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['bb_upper'], name='BB Superior', 
                              line=dict(color='gray', dash='dash')),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['bb_lower'], name='BB Inferior',
                              line=dict(color='gray', dash='dash'), fill='tonexty'),
                    row=1, col=1
                )
            
            # Volume
            fig.add_trace(
                go.Bar(x=df['timestamp'], y=df['volume'], name='Volume', marker_color='lightblue'),
                row=2, col=1
            )
            
            # RSI
            if show_rsi:
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['rsi'], name='RSI', line=dict(color='purple')),
                    row=3, col=1
                )
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            
            # MACD
            if show_macd:
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['macd'], name='MACD', line=dict(color='blue')),
                    row=4, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['macd_signal'], name='Signal', line=dict(color='red')),
                    row=4, col=1
                )
                fig.add_trace(
                    go.Bar(x=df['timestamp'], y=df['macd_histogram'], name='Histogram', marker_color='gray'),
                    row=4, col=1
                )
            
            fig.update_layout(height=800, showlegend=True, title_text=f"Análise Técnica - {selected_coin_name}")
            fig.update_xaxes(title_text="Tempo", row=4, col=1)
            fig.update_yaxes(title_text="Preço ($)", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="RSI", row=3, col=1)
            fig.update_yaxes(title_text="MACD", row=4, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Análise dos indicadores
            st.subheader("🔍 Análise dos Indicadores")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Sinais Técnicos:**")
                
                # RSI
                current_rsi = df['rsi'].iloc[-1] if not df['rsi'].isna().iloc[-1] else 50
                if current_rsi > 70:
                    st.write("🔴 RSI: Sobrecomprado")
                elif current_rsi < 30:
                    st.write("🟢 RSI: Sobrevendido")
                else:
                    st.write("🟡 RSI: Neutro")
                
                # MACD
                current_macd = df['macd'].iloc[-1] if not df['macd'].isna().iloc[-1] else 0
                current_signal = df['macd_signal'].iloc[-1] if not df['macd_signal'].isna().iloc[-1] else 0
                
                if current_macd > current_signal:
                    st.write("🟢 MACD: Sinal de Compra")
                else:
                    st.write("🔴 MACD: Sinal de Venda")
                
                # Médias Móveis
                current_sma20 = df['sma_20'].iloc[-1] if not df['sma_20'].isna().iloc[-1] else current_price
                current_sma50 = df['sma_50'].iloc[-1] if not df['sma_50'].isna().iloc[-1] else current_price
                
                if current_price > current_sma20 > current_sma50:
                    st.write("🟢 Tendência: Altista")
                elif current_price < current_sma20 < current_sma50:
                    st.write("🔴 Tendência: Baixista")
                else:
                    st.write("🟡 Tendência: Lateral")
            
            with col2:
                st.write("**Estatísticas do Período:**")
                st.write(f"• Volatilidade: {df['price'].std():.2f}")
                st.write(f"• Variação Total: {((df['price'].iloc[-1] / df['price'].iloc[0] - 1) * 100):+.2f}%")
                st.write(f"• Volume Máximo: ${df['volume'].max():,.0f}")
                st.write(f"• Volume Mínimo: ${df['volume'].min():,.0f}")
                
                # Suporte e Resistência (simplificado)
                recent_prices = df['price'].tail(24)  # Últimas 24 horas
                support = recent_prices.min()
                resistance = recent_prices.max()
                
                st.write(f"• Suporte: ${support:.2f}")
                st.write(f"• Resistência: ${resistance:.2f}")
        
        else:
            st.error("❌ Não foi possível carregar os dados. Verifique a conexão com o banco de dados.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Análise Técnica Dashboard** | "
        f"Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        "⚠️ *Dados para fins educacionais apenas*"
    )

if __name__ == "__main__":
    main()
