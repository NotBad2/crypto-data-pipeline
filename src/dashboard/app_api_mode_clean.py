import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
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

def main():
    st.title("₿ Crypto Dashboard - API Mode")
    
    # Botões de navegação no topo
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
        "📈 Análise Técnica": "Em desenvolvimento"
    }
    
    for name, link in nav_options.items():
        if link.startswith("http"):
            st.sidebar.markdown(f"[{name}]({link})")
        elif link == "✅ Atual":
            st.sidebar.success(f"{name} {link}")
        else:
            st.sidebar.info(f"{name}: {link}")
    
    st.sidebar.markdown("---")
    
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
            display_columns = [
                'name', 'symbol', 'current_price', 'market_cap', 
                'price_change_percentage_24h', 'price_change_percentage_7d'
            ]
            
            st.dataframe(
                filtered_df[display_columns],
                column_config={
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
                    ),
                    "price_change_percentage_7d": st.column_config.NumberColumn(
                        "Variação 7d (%)",
                        format="%.2f%%"
                    )
                },
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
                fig_market_cap.update_xaxis(tickangle=45)
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
                fig_performance.update_xaxis(tickangle=45)
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
    
    # Rodapé
    st.markdown("---")
    st.markdown("**Dados fornecidos por:** CoinGecko API")
    st.markdown(f"**Última atualização:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
