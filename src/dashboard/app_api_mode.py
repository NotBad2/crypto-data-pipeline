import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_    # Botões de navegação no topo
    st.markdown("### 🧭 Navegação")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**📊 Dashboard Principal**")
        st.success("✅ Ativo")
    
    with col2:
        st.markdown("**🤖 ML Analytics**")
        st.markdown("[🚀 Abrir ML Dashboard](http://localhost:8504)")
    
    with col3:
        st.markdown("**📈 Análise Técnica**")
        st.info("ℹ️ Em desenvolvimento")rt requests
import time
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_crypto_data():
    """Busca dados diretamente da API CoinGecko"""
    try:
        # Dados das moedas
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 50,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Erro ao buscar dados da API: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_global_data():
    """Busca dados globais do mercado"""
    try:
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()['data']
        
    except Exception as e:
        st.error(f"Erro ao buscar dados globais: {e}")
        return {}

def test_database_connections():
    """Testa conexões com banco de dados"""
    db_status = {"postgres": False, "redis": False, "postgres_available": False, "redis_available": False}
    
    # Testar se as bibliotecas estão disponíveis
    try:
        import psycopg2
        db_status["postgres_available"] = True
        try:
            conn = psycopg2.connect(
                host='localhost',
                port='5432',
                database='crypto_data',
                user='crypto_user',
                password='crypto_pass'
            )
            conn.close()
            db_status["postgres"] = True
        except:
            pass
    except ImportError:
        pass
    
    try:
        import redis
        db_status["redis_available"] = True
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            db_status["redis"] = True
        except:
            pass
    except ImportError:
        pass
    
    return db_status

def main():
    st.title("₿ Crypto Dashboard - API Mode")
    
    # Botões de navegação no topo
    st.markdown("### 🧭 Navegação")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.markdown("**📊 Dashboard Principal**")
        st.success("✅ Ativo")
    
    with col2:
        st.markdown("**🤖 ML Analytics**")
        st.markdown("[🚀 Abrir ML Dashboard](http://localhost:8504)")
    
    with col3:
        st.markdown("**📈 Análise Técnica**")
        st.info("ℹ️ Em desenvolvimento")
    
    with col4:
        st.markdown("**�️ Monitor Sistema**")
        st.info("ℹ️ Em desenvolvimento")
    
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Configurações")
    
    # Menu de navegação no sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧭 Navegação Rápida")
    
    nav_options = {
        "📊 Dashboard Principal": "✅ Atual",
        "🤖 ML Analytics": "http://localhost:8504",
        "📈 Análise Técnica": "Em desenvolvimento",
        "🖥️ Monitor Sistema": "Em desenvolvimento"
    }
    
    for name, link in nav_options.items():
        if link.startswith("http"):
            st.sidebar.markdown(f"[{name}]({link})")
        elif link == "✅ Atual":
            st.sidebar.success(f"{name} {link}")
        else:
            st.sidebar.info(f"{name}: {link}")
    
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Botão de refresh manual
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
    
    # Dados globais
    st.header("📊 Métricas Globais do Mercado")
    global_data = get_global_data()
    
    if global_data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            market_cap = global_data.get('total_market_cap', {}).get('usd', 0)
            market_cap_change = global_data.get('market_cap_change_percentage_24h_usd', 0)
            st.metric(
                "💰 Market Cap Total",
                f"${market_cap:,.0f}",
                delta=f"{market_cap_change:.2f}%"
            )
        
        with col2:
            volume = global_data.get('total_volume', {}).get('usd', 0)
            st.metric(
                "📈 Volume 24h",
                f"${volume:,.0f}"
            )
        
        with col3:
            total_cryptos = global_data.get('active_cryptocurrencies', 0)
            st.metric(
                "🪙 Total de Cryptos",
                f"{total_cryptos:,}"
            )
        
        with col4:
            btc_dominance = global_data.get('market_cap_percentage', {}).get('btc', 0)
            st.metric(
                "₿ Dominância BTC",
                f"{btc_dominance:.1f}%"
            )
    
    st.markdown("---")
    
    # Dados das moedas
    st.header("🏆 Top 50 Criptomoedas")
    df = get_crypto_data()
    
    if not df.empty:
        # Tabs para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Tabela", "📊 Gráficos", "💹 Performance", "🔍 Análise"])
        
        with tab1:
            # Formatação da tabela
            df_display = df.copy()
            df_display = df_display[['market_cap_rank', 'name', 'symbol', 'current_price', 
                                   'market_cap', 'price_change_percentage_24h', 'total_volume']]
            
            # Formatação de números
            df_display['current_price'] = df_display['current_price'].apply(lambda x: f"${x:,.4f}" if x < 1 else f"${x:,.2f}")
            df_display['market_cap'] = df_display['market_cap'].apply(lambda x: f"${x:,.0f}")
            df_display['total_volume'] = df_display['total_volume'].apply(lambda x: f"${x:,.0f}")
            df_display['price_change_percentage_24h'] = df_display['price_change_percentage_24h'].apply(lambda x: f"{x:.2f}%")
            
            # Renomear colunas
            df_display.columns = ['Rank', 'Nome', 'Símbolo', 'Preço', 'Market Cap', 'Mudança 24h', 'Volume']
            
            st.dataframe(
                df_display,
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
                fig_market_cap.update_xaxes(tickangle=45)
                fig_market_cap.update_layout(height=400)
                st.plotly_chart(fig_market_cap, use_container_width=True)
            
            with col2:
                st.subheader("📊 Distribuição de Market Cap")
                fig_pie = px.pie(
                    df_top10, 
                    values='market_cap', 
                    names='symbol',
                    title="Distribuição Top 10"
                )
                fig_pie.update_layout(height=400)
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
                        gainers.sort_values('price_change_percentage_24h', ascending=True),
                        x='price_change_percentage_24h',
                        y='name',
                        orientation='h',
                        title="Maiores Altas 24h (%)",
                        color='price_change_percentage_24h',
                        color_continuous_scale='Greens'
                    )
                    fig_gainers.update_layout(height=400)
                    st.plotly_chart(fig_gainers, use_container_width=True)
                else:
                    st.write("Nenhum gainer encontrado")
            
            with col2:
                st.write("🔴 **Top Losers**")
                if not losers.empty:
                    fig_losers = px.bar(
                        losers.sort_values('price_change_percentage_24h', ascending=False),
                        x='price_change_percentage_24h',
                        y='name',
                        orientation='h',
                        title="Maiores Quedas 24h (%)",
                        color='price_change_percentage_24h',
                        color_continuous_scale='Reds'
                    )
                    fig_losers.update_layout(height=400)
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
                    st.metric("Preço Atual", f"${coin_data['current_price']:,.4f}" if coin_data['current_price'] < 1 else f"${coin_data['current_price']:,.2f}")
                    st.metric("Rank", f"#{coin_data['market_cap_rank']}")
                
                with col2:
                    st.metric("Market Cap", f"${coin_data['market_cap']:,.0f}")
                    st.metric("Volume 24h", f"${coin_data['total_volume']:,.0f}")
                
                with col3:
                    st.metric(
                        "Mudança 24h", 
                        f"{coin_data['price_change_percentage_24h']:.2f}%",
                        delta=f"${coin_data['price_change_24h']:,.4f}" if abs(coin_data['price_change_24h']) < 1 else f"${coin_data['price_change_24h']:,.2f}"
                    )
                    if 'circulating_supply' in coin_data and coin_data['circulating_supply']:
                        st.metric("Supply Circulante", f"{coin_data['circulating_supply']:,.0f}")
    
    else:
        st.warning("⚠️ Não foi possível carregar dados da API CoinGecko.")
    
    # Status do sistema
    st.markdown("---")
    st.header("🔧 Status do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌐 API CoinGecko")
        if not df.empty:
            st.success("✅ Conectado")
            st.info(f"📊 {len(df)} moedas carregadas")
        else:
            st.error("❌ Erro na API")
    
    with col2:
        st.subheader("💾 Base de Dados")
        db_status = test_database_connections()
        
        # PostgreSQL Status
        if db_status["postgres_available"]:
            if db_status["postgres"]:
                st.success("✅ PostgreSQL conectado")
            else:
                st.warning("⚠️ PostgreSQL desconectado")
        else:
            st.info("ℹ️ PostgreSQL não configurado")
        
        # Redis Status
        if db_status["redis_available"]:
            if db_status["redis"]:
                st.success("✅ Redis conectado")
            else:
                st.warning("⚠️ Redis desconectado")
        else:
            st.info("ℹ️ Redis não configurado")
        
        # Modo de operação
        if not db_status["postgres_available"] and not db_status["redis_available"]:
            st.success("🌐 Modo API ativo")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Crypto Dashboard** | "
        f"Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        "Dados: CoinGecko API"
    )

if __name__ == "__main__":
    main()
