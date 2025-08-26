import streamlit as st

# Configuração da página principal
st.set_page_config(
    page_title="Crypto Data Pipeline",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("₿ Crypto Data Pipeline Dashboard Suite")
    st.markdown("---")
    
    st.markdown("""
    ## 🚀 Bem-vindo ao Sistema de Análise de Criptomoedas
    
    Este é um sistema completo de coleta, armazenamento e análise de dados de criptomoedas.
    
    ### 📊 Dashboards Disponíveis:
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📈 Dashboard Principal
        **Visão geral do mercado**
        - Métricas globais
        - Top 50 criptomoedas
        - Performance 24h
        - Análise detalhada
        
        [🔗 Abrir Dashboard Principal](./app.py)
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Análise Técnica
        **Indicadores e sinais**
        - Médias móveis
        - Bandas de Bollinger
        - RSI e MACD
        - Suporte e resistência
        
        [🔗 Abrir Análise Técnica](./technical_analysis.py)
        """)
    
    with col3:
        st.markdown("""
        ### 🖥️ Monitor do Sistema
        **Status da infraestrutura**
        - Métricas do sistema
        - Status PostgreSQL
        - Status Redis
        - Containers Docker
        
        [🔗 Abrir Monitor](./system_monitor.py)
        """)
    
    st.markdown("---")
    
    # Informações do projeto
    st.markdown("""
    ## 🏗️ Arquitetura do Sistema
    
    ### 🔄 Fluxo de Dados:
    1. **Coleta**: API CoinGecko → Dados de mercado em tempo real
    2. **Processamento**: Python → Limpeza e validação
    3. **Armazenamento**: PostgreSQL → Persistência dos dados
    4. **Cache**: Redis → Acesso rápido aos dados
    5. **Visualização**: Streamlit → Dashboards interativos
    
    ### 🛠️ Tecnologias Utilizadas:
    - **Backend**: Python, PostgreSQL, Redis
    - **Frontend**: Streamlit, Plotly
    - **Infraestrutura**: Docker, Docker Compose
    - **API**: CoinGecko Free API
    """)
    
    # Status atual
    st.markdown("---")
    st.header("📊 Status Atual do Sistema")
    
    try:
        import psycopg2
        import redis
        
        # Testar PostgreSQL
        try:
            conn = psycopg2.connect(
                host='localhost',
                port='5432',
                database='crypto_data',
                user='postgres',
                password='postgres123'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM coin_market_data")
            count = cursor.fetchone()[0]
            conn.close()
            st.success(f"✅ PostgreSQL: {count} registros disponíveis")
        except:
            st.error("❌ PostgreSQL: Não conectado")
        
        # Testar Redis
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            info = r.info()
            st.success(f"✅ Redis: {info.get('connected_clients', 0)} clientes conectados")
        except:
            st.error("❌ Redis: Não conectado")
            
    except ImportError:
        st.warning("⚠️ Dependências não instaladas. Execute: `pip install psycopg2-binary redis`")
    
    # Instruções de uso
    st.markdown("---")
    st.header("🚀 Como Usar")
    
    st.markdown("""
    ### 1. Iniciar o Sistema:
    ```bash
    # Subir os containers
    docker-compose -f docker-compose-simple.yml up -d
    
    # Executar coleta de dados
    python src/demo_working_integration.py
    ```
    
    ### 2. Acessar os Dashboards:
    ```bash
    # Dashboard principal
    streamlit run src/dashboard/app.py
    
    # Análise técnica
    streamlit run src/dashboard/technical_analysis.py
    
    # Monitor do sistema
    streamlit run src/dashboard/system_monitor.py
    ```
    
    ### 3. URLs dos Dashboards:
    - **Principal**: http://localhost:8501
    - **Análise Técnica**: http://localhost:8502
    - **Monitor**: http://localhost:8503
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Crypto Data Pipeline** | Desenvolvido para aprendizado e portfólio
    
    📧 Contato | 🐙 [GitHub](https://github.com) | 📊 [Portfolio](https://portfolio.com)
    """)

if __name__ == "__main__":
    main()
