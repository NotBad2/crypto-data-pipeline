import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Adicionar o caminho do módulo ML
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ml'))

# Configuração da página
st.set_page_config(
    page_title="Crypto ML Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_db_connection():
    """Conexão com o Data Warehouse"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'crypto_warehouse.db')
    if not os.path.exists(db_path):
        st.error("❌ Data Warehouse não encontrado. Execute primeiro o script de coleta de dados.")
        return None
    return sqlite3.connect(db_path)

@st.cache_data(ttl=300)
def get_available_coins():
    """Lista moedas disponíveis no Data Warehouse"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        df = pd.read_sql_query("SELECT DISTINCT coin_id FROM historical_prices ORDER BY coin_id", conn)
        return df['coin_id'].tolist()
    except:
        return []

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
        return df.sort_values('date')
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_ml_predictions(coin_id=None):
    """Busca previsões ML"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        if coin_id:
            query = """
            SELECT * FROM ml_predictions 
            WHERE coin_id = ?
            ORDER BY created_at DESC
            LIMIT 50
            """
            df = pd.read_sql_query(query, conn, params=(coin_id,))
        else:
            query = """
            SELECT * FROM ml_predictions 
            ORDER BY created_at DESC
            LIMIT 100
            """
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Erro ao buscar previsões: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_ml_features(coin_id, days=30):
    """Busca features ML"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = """
        SELECT * FROM ml_features 
        WHERE coin_id = ?
        ORDER BY date DESC
        LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(coin_id, days))
        return df.sort_values('date')
    except Exception as e:
        st.error(f"Erro ao buscar features: {e}")
        return pd.DataFrame()

def plot_price_with_indicators(df, coin_id):
    """Gráfico de preço com indicadores técnicos"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{coin_id.upper()} - Preço e Indicadores', 'RSI', 'MACD'),
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Preço e médias móveis
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['price'], name='Preço', line=dict(color='blue', width=2)),
        row=1, col=1
    )
    
    if 'sma_7' in df.columns and not df['sma_7'].isna().all():
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['sma_7'], name='SMA 7', line=dict(color='orange')),
            row=1, col=1
        )
    
    if 'sma_30' in df.columns and not df['sma_30'].isna().all():
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['sma_30'], name='SMA 30', line=dict(color='red')),
            row=1, col=1
        )
    
    # Bandas de Bollinger
    if 'bollinger_upper' in df.columns and not df['bollinger_upper'].isna().all():
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['bollinger_upper'], name='BB Superior', 
                      line=dict(color='gray', dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['bollinger_lower'], name='BB Inferior',
                      line=dict(color='gray', dash='dash'), fill='tonexty'),
            row=1, col=1
        )
    
    # RSI
    if 'rsi_14' in df.columns and not df['rsi_14'].isna().all():
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['rsi_14'], name='RSI', line=dict(color='purple')),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # MACD
    if 'macd' in df.columns and not df['macd'].isna().all():
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['macd'], name='MACD', line=dict(color='blue')),
            row=3, col=1
        )
        if 'macd_signal' in df.columns and not df['macd_signal'].isna().all():
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['macd_signal'], name='Signal', line=dict(color='red')),
                row=3, col=1
            )
    
    fig.update_layout(height=800, showlegend=True)
    fig.update_xaxes(title_text="Data", row=3, col=1)
    fig.update_yaxes(title_text="Preço ($)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    
    return fig

def plot_ml_features_correlation(df):
    """Heatmap de correlação das features ML"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if not col.startswith('id')]
    
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Correlação entre Features ML",
            color_continuous_scale='RdBu_r'
        )
        
        fig.update_layout(height=600)
        return fig
    
    return None

def main():
    st.title("🤖 Crypto ML Analytics Dashboard")
    
    # Botões de navegação no topo
    st.markdown("### 🧭 Navegação")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("**📊 Dashboard Principal**")
        st.markdown("[🚀 Abrir Dashboard](http://localhost:8505)")
    
    with col2:
        st.markdown("**🤖 ML Analytics**")
        st.success("✅ Ativo")
    
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
        "📊 Dashboard Principal": "http://localhost:8505",
        "🤖 ML Analytics": "✅ Atual",
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
    
    # Verificar se o Data Warehouse existe
    available_coins = get_available_coins()
    
    if not available_coins:
        st.error("❌ Data Warehouse não encontrado!")
        st.markdown("""
        ### 🔧 Como configurar:
        
        1. **Execute o Data Warehouse:**
        ```bash
        cd src/ml
        python data_warehouse.py
        ```
        
        2. **Treine os modelos ML:**
        ```bash
        python ml_models.py
        ```
        
        3. **Recarregue esta página**
        """)
        return
    
    # Seleção de moeda
    selected_coin = st.sidebar.selectbox(
        "Selecione a Criptomoeda:",
        available_coins,
        index=0 if 'bitcoin' not in available_coins else available_coins.index('bitcoin')
    )
    
    # Período de análise
    analysis_period = st.sidebar.selectbox(
        "Período de Análise:",
        [30, 60, 90, 180, 365],
        index=2,
        format_func=lambda x: f"{x} dias"
    )
    
    # Tipo de análise
    analysis_type = st.sidebar.selectbox(
        "Tipo de Análise:",
        ["Análise Técnica", "Features ML", "Previsões", "Performance dos Modelos"]
    )
    
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
    
    # Conteúdo principal
    if analysis_type == "Análise Técnica":
        st.header(f"📊 Análise Técnica - {selected_coin.upper()}")
        
        df = get_historical_data(selected_coin, analysis_period)
        
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            current_price = df['price'].iloc[-1]
            price_change = df['price'].iloc[-1] - df['price'].iloc[-2] if len(df) > 1 else 0
            price_change_pct = (price_change / df['price'].iloc[-2] * 100) if len(df) > 1 else 0
            
            with col1:
                st.metric("Preço Atual", f"${current_price:.2f}", f"{price_change:+.2f} ({price_change_pct:+.2f}%)")
            
            with col2:
                st.metric("Máximo", f"${df['price'].max():.2f}")
            
            with col3:
                st.metric("Mínimo", f"${df['price'].min():.2f}")
            
            with col4:
                volatility = df['volatility'].iloc[-1] if 'volatility' in df.columns and not df['volatility'].isna().iloc[-1] else 0
                st.metric("Volatilidade", f"{volatility:.4f}")
            
            # Gráfico principal
            fig = plot_price_with_indicators(df, selected_coin)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("⚠️ Nenhum dado histórico encontrado para esta moeda.")
    
    elif analysis_type == "Features ML":
        st.header(f"🔬 Features ML - {selected_coin.upper()}")
        
        df_features = get_ml_features(selected_coin, analysis_period)
        
        if not df_features.empty:
            # Mostrar últimas features
            st.subheader("📋 Features Recentes")
            display_cols = ['date', 'price_current', 'rsi_14', 'volatility_7d', 'trend_direction']
            available_cols = [col for col in display_cols if col in df_features.columns]
            st.dataframe(df_features[available_cols].head(10), use_container_width=True)
            
            # Correlação entre features
            st.subheader("🔗 Correlação entre Features")
            corr_fig = plot_ml_features_correlation(df_features)
            if corr_fig:
                st.plotly_chart(corr_fig, use_container_width=True)
            
            # Distribuição de features importantes
            st.subheader("📊 Distribuição das Features")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'rsi_14' in df_features.columns:
                    fig_rsi = px.histogram(df_features, x='rsi_14', title="Distribuição RSI", nbins=20)
                    st.plotly_chart(fig_rsi, use_container_width=True)
            
            with col2:
                if 'volatility_7d' in df_features.columns:
                    fig_vol = px.histogram(df_features, x='volatility_7d', title="Distribuição Volatilidade 7d", nbins=20)
                    st.plotly_chart(fig_vol, use_container_width=True)
        
        else:
            st.warning("⚠️ Nenhuma feature ML encontrada para esta moeda.")
    
    elif analysis_type == "Previsões":
        st.header(f"🔮 Previsões ML - {selected_coin.upper()}")
        
        df_predictions = get_ml_predictions(selected_coin)
        
        if not df_predictions.empty:
            # Previsões recentes
            st.subheader("📋 Previsões Recentes")
            
            display_df = df_predictions[['prediction_date', 'target_date', 'predicted_price', 'confidence_score']].head(10)
            display_df['predicted_price'] = display_df['predicted_price'].apply(lambda x: f"${x:.2f}")
            display_df['confidence_score'] = display_df['confidence_score'].apply(lambda x: f"{x:.2%}")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Gráfico de confiança das previsões
            st.subheader("📊 Análise de Confiança")
            
            fig_conf = px.scatter(
                df_predictions, 
                x='prediction_date', 
                y='confidence_score',
                size='predicted_price',
                title="Confiança das Previsões ao Longo do Tempo"
            )
            st.plotly_chart(fig_conf, use_container_width=True)
        
        else:
            st.warning("⚠️ Nenhuma previsão encontrada para esta moeda.")
            st.info("💡 Execute o script de ML para gerar previsões: `python src/ml/ml_models.py`")
    
    elif analysis_type == "Performance dos Modelos":
        st.header("🎯 Performance dos Modelos ML")
        
        # Buscar todas as previsões
        all_predictions = get_ml_predictions()
        
        if not all_predictions.empty:
            # Estatísticas por moeda
            st.subheader("📊 Estatísticas por Moeda")
            
            stats = all_predictions.groupby('coin_id').agg({
                'predicted_price': 'count',
                'confidence_score': 'mean'
            }).round(3)
            stats.columns = ['Total Previsões', 'Confiança Média']
            
            st.dataframe(stats, use_container_width=True)
            
            # Distribuição de confiança
            st.subheader("📈 Distribuição de Confiança")
            
            fig_conf_dist = px.histogram(
                all_predictions, 
                x='confidence_score', 
                color='coin_id',
                title="Distribuição de Confiança por Moeda",
                nbins=20
            )
            st.plotly_chart(fig_conf_dist, use_container_width=True)
        
        else:
            st.warning("⚠️ Nenhuma previsão encontrada.")
    
    # Footer com informações do sistema
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Data Warehouse")
        if available_coins:
            st.success(f"✅ {len(available_coins)} moedas disponíveis")
        else:
            st.error("❌ Data Warehouse vazio")
    
    with col2:
        st.subheader("🤖 Modelos ML")
        models_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'models')
        if os.path.exists(models_path):
            model_files = [f for f in os.listdir(models_path) if f.endswith('.pkl')]
            st.success(f"✅ {len(model_files)} modelos salvos")
        else:
            st.warning("⚠️ Nenhum modelo treinado")
    
    with col3:
        st.subheader("🔮 Previsões")
        total_predictions = len(get_ml_predictions())
        if total_predictions > 0:
            st.success(f"✅ {total_predictions} previsões")
        else:
            st.warning("⚠️ Nenhuma previsão")
    
    st.markdown(f"**ML Analytics Dashboard** | Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
