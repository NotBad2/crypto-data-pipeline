import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
import redis
import json
from datetime import datetime, timedelta
import time

# Configuração da página
st.set_page_config(
    page_title="Crypto Data Pipeline Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações de conexão
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'crypto_data',
    'user': 'crypto_user',
    'password': 'crypto_pass'
}

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

# Cache para conexões
@st.cache_resource
def get_db_connection():
    """Cria conexão com PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar com PostgreSQL: {e}")
        return None

@st.cache_resource
def get_redis_connection():
    """Cria conexão com Redis"""
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()  # Testa a conexão
        return r
    except Exception as e:
        st.error(f"Erro ao conectar com Redis: {e}")
        return None

# Funções para buscar dados
@st.cache_data(ttl=60)  # Cache por 1 minuto
def get_market_data():
    """Busca dados de mercado do PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT 
            coin_id,
            symbol,
            name,
            current_price,
            market_cap,
            market_cap_rank,
            price_change_24h,
            price_change_percentage_24h,
            total_volume,
            circulating_supply,
            last_updated
        FROM coin_market_data 
        ORDER BY market_cap_rank ASC
        LIMIT 50
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_global_market_stats():
    """Busca estatísticas globais do mercado"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        query = """
        SELECT 
            total_market_cap,
            total_volume_24h,
            market_cap_change_percentage_24h,
            total_cryptocurrencies,
            last_updated
        FROM global_market_data 
        ORDER BY last_updated DESC 
        LIMIT 1
        """
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'total_market_cap': result[0],
                'total_volume_24h': result[1],
                'market_cap_change_24h': result[2],
                'total_cryptocurrencies': result[3],
                'last_updated': result[4]
            }
        return {}
    except Exception as e:
        st.error(f"Erro ao buscar estatísticas globais: {e}")
        return {}

def get_redis_stats():
    """Busca estatísticas do Redis"""
    r = get_redis_connection()
    if not r:
        return {}
    
    try:
        info = r.info()
        return {
            'used_memory': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 0),
            'total_commands_processed': info.get('total_commands_processed', 0),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0)
        }
    except Exception as e:
        st.error(f"Erro ao buscar estatísticas do Redis: {e}")
        return {}

# Interface principal
def main():
    st.title("₿ Crypto Data Pipeline Dashboard")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Configurações")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Botão de refresh manual
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
    
    # Métricas globais
    st.header("📊 Métricas Globais do Mercado")
    global_stats = get_global_market_stats()
    
    if global_stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "💰 Market Cap Total",
                f"${global_stats.get('total_market_cap', 0):,.0f}",
                delta=f"{global_stats.get('market_cap_change_24h', 0):.2f}%"
            )
        
        with col2:
            st.metric(
                "📈 Volume 24h",
                f"${global_stats.get('total_volume_24h', 0):,.0f}"
            )
        
        with col3:
            st.metric(
                "🪙 Total de Cryptos",
                f"{global_stats.get('total_cryptocurrencies', 0):,}"
            )
        
        with col4:
            redis_stats = get_redis_stats()
            st.metric(
                "💾 Redis Memory",
                redis_stats.get('used_memory', 'N/A')
            )
    
    st.markdown("---")
    
    # Dados das moedas
    st.header("🏆 Top 50 Criptomoedas")
    df = get_market_data()
    
    if not df.empty:
        # Tabs para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Tabela", "📊 Gráficos", "💹 Performance", "🔍 Análise"])
        
        with tab1:
            # Formatação da tabela
            df_display = df.copy()
            df_display['current_price'] = df_display['current_price'].apply(lambda x: f"${x:,.2f}")
            df_display['market_cap'] = df_display['market_cap'].apply(lambda x: f"${x:,.0f}")
            df_display['total_volume'] = df_display['total_volume'].apply(lambda x: f"${x:,.0f}")
            df_display['price_change_percentage_24h'] = df_display['price_change_percentage_24h'].apply(lambda x: f"{x:.2f}%")
            
            st.dataframe(
                df_display[['market_cap_rank', 'name', 'symbol', 'current_price', 
                           'market_cap', 'price_change_percentage_24h', 'total_volume']],
                use_container_width=True,
                hide_index=True
            )
        
        with tab2:
            # Gráfico de Market Cap
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💰 Market Cap Top 10")
                df_top10 = df.head(10)
                fig_market_cap = px.bar(
                    df_top10, 
                    x='name', 
                    y='market_cap',
                    title="Market Cap das Top 10 Moedas",
                    color='market_cap',
                    color_continuous_scale='viridis'
                )
                fig_market_cap.update_xaxis(tickangle=45)
                st.plotly_chart(fig_market_cap, use_container_width=True)
            
            with col2:
                st.subheader("📊 Distribuição de Preços")
                fig_pie = px.pie(
                    df_top10, 
                    values='market_cap', 
                    names='symbol',
                    title="Distribuição de Market Cap"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab3:
            # Performance 24h
            st.subheader("📈 Performance 24h")
            
            # Separar gainers e losers
            gainers = df[df['price_change_percentage_24h'] > 0].head(10)
            losers = df[df['price_change_percentage_24h'] < 0].head(10)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("🟢 **Top Gainers**")
                if not gainers.empty:
                    fig_gainers = px.bar(
                        gainers,
                        x='price_change_percentage_24h',
                        y='name',
                        orientation='h',
                        title="Maiores Altas 24h (%)",
                        color='price_change_percentage_24h',
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig_gainers, use_container_width=True)
                else:
                    st.write("Nenhum gainer encontrado")
            
            with col2:
                st.write("🔴 **Top Losers**")
                if not losers.empty:
                    fig_losers = px.bar(
                        losers,
                        x='price_change_percentage_24h',
                        y='name',
                        orientation='h',
                        title="Maiores Quedas 24h (%)",
                        color='price_change_percentage_24h',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig_losers, use_container_width=True)
                else:
                    st.write("Nenhum loser encontrado")
        
        with tab4:
            # Análise detalhada
            st.subheader("🔍 Análise Detalhada")
            
            # Seletor de moeda
            selected_coin = st.selectbox("Selecione uma moeda:", df['name'].tolist())
            
            if selected_coin:
                coin_data = df[df['name'] == selected_coin].iloc[0]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Preço Atual", f"${coin_data['current_price']:,.2f}")
                    st.metric("Rank", f"#{coin_data['market_cap_rank']}")
                
                with col2:
                    st.metric("Market Cap", f"${coin_data['market_cap']:,.0f}")
                    st.metric("Volume 24h", f"${coin_data['total_volume']:,.0f}")
                
                with col3:
                    st.metric(
                        "Mudança 24h", 
                        f"{coin_data['price_change_percentage_24h']:.2f}%",
                        delta=f"${coin_data['price_change_24h']:,.2f}"
                    )
                    st.metric("Supply Circulante", f"{coin_data['circulating_supply']:,.0f}")
    
    else:
        st.warning("⚠️ Nenhum dado encontrado. Verifique se o pipeline está rodando.")
    
    # Informações do sistema
    st.markdown("---")
    st.header("🔧 Status do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🐘 PostgreSQL")
        conn = get_db_connection()
        if conn:
            st.success("✅ Conectado")
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM coin_market_data")
                count = cursor.fetchone()[0]
                st.info(f"📊 {count} registros na base de dados")
                conn.close()
            except:
                st.warning("⚠️ Erro ao contar registros")
        else:
            st.error("❌ Desconectado")
    
    with col2:
        st.subheader("⚡ Redis")
        r = get_redis_connection()
        if r:
            st.success("✅ Conectado")
            redis_stats = get_redis_stats()
            st.info(f"👥 {redis_stats.get('connected_clients', 0)} clientes conectados")
            st.info(f"🎯 {redis_stats.get('keyspace_hits', 0)} cache hits")
        else:
            st.error("❌ Desconectado")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Crypto Data Pipeline Dashboard** | "
        f"Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    main()
