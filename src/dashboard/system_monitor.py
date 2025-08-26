import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import redis
import json
import time
from datetime import datetime, timedelta
import subprocess
import psutil

# Configuração da página
st.set_page_config(
    page_title="System Monitor - Crypto Pipeline",
    page_icon="🖥️",
    layout="wide"
)

# Configurações
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

@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar com PostgreSQL: {e}")
        return None

@st.cache_resource
def get_redis_connection():
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()
        return r
    except Exception as e:
        st.error(f"Erro ao conectar com Redis: {e}")
        return None

def get_system_metrics():
    """Coleta métricas do sistema"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'boot_time': datetime.fromtimestamp(psutil.boot_time()),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total / (1024**3),  # GB
        'disk_total': psutil.disk_usage('/').total / (1024**3)  # GB
    }

def get_database_metrics():
    """Coleta métricas do banco de dados"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor()
        
        # Tamanho do banco
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size('crypto_data')) as db_size
        """)
        db_size = cursor.fetchone()[0]
        
        # Número de conexões
        cursor.execute("""
            SELECT count(*) as connections 
            FROM pg_stat_activity 
            WHERE datname = 'crypto_data'
        """)
        connections = cursor.fetchone()[0]
        
        # Estatísticas das tabelas
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_stat_user_tables
        """)
        table_stats = cursor.fetchall()
        
        # Queries mais lentas (se existirem)
        cursor.execute("""
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                rows
            FROM pg_stat_statements 
            ORDER BY mean_time DESC 
            LIMIT 5
        """)
        slow_queries = cursor.fetchall()
        
        conn.close()
        
        return {
            'db_size': db_size,
            'connections': connections,
            'table_stats': table_stats,
            'slow_queries': slow_queries
        }
        
    except Exception as e:
        st.error(f"Erro ao coletar métricas do banco: {e}")
        return {}

def get_redis_metrics():
    """Coleta métricas do Redis"""
    r = get_redis_connection()
    if not r:
        return {}
    
    try:
        info = r.info()
        
        return {
            'used_memory': info.get('used_memory', 0),
            'used_memory_human': info.get('used_memory_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 0),
            'total_commands_processed': info.get('total_commands_processed', 0),
            'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'expired_keys': info.get('expired_keys', 0),
            'evicted_keys': info.get('evicted_keys', 0),
            'uptime_in_seconds': info.get('uptime_in_seconds', 0),
            'redis_version': info.get('redis_version', 'N/A')
        }
        
    except Exception as e:
        st.error(f"Erro ao coletar métricas do Redis: {e}")
        return {}

def check_docker_containers():
    """Verifica status dos containers Docker"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    containers.append(json.loads(line))
            return containers
        else:
            return []
            
    except Exception as e:
        st.error(f"Erro ao verificar containers Docker: {e}")
        return []

def main():
    st.title("🖥️ Monitor do Sistema - Crypto Data Pipeline")
    st.markdown("---")
    
    # Auto-refresh
    if st.sidebar.checkbox("Auto-refresh (10s)", value=False):
        time.sleep(10)
        st.rerun()
    
    if st.sidebar.button("🔄 Atualizar Agora"):
        st.rerun()
    
    # Métricas do Sistema
    st.header("📊 Métricas do Sistema")
    system_metrics = get_system_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔥 CPU", f"{system_metrics['cpu_percent']:.1f}%")
        # Indicador visual para CPU
        if system_metrics['cpu_percent'] > 80:
            st.error("Alto uso de CPU!")
        elif system_metrics['cpu_percent'] > 60:
            st.warning("Uso moderado de CPU")
        else:
            st.success("CPU OK")
    
    with col2:
        st.metric("💾 Memória", f"{system_metrics['memory_percent']:.1f}%")
        if system_metrics['memory_percent'] > 80:
            st.error("Pouca memória disponível!")
        elif system_metrics['memory_percent'] > 60:
            st.warning("Uso moderado de memória")
        else:
            st.success("Memória OK")
    
    with col3:
        st.metric("💿 Disco", f"{system_metrics['disk_percent']:.1f}%")
        if system_metrics['disk_percent'] > 90:
            st.error("Disco quase cheio!")
        elif system_metrics['disk_percent'] > 80:
            st.warning("Pouco espaço em disco")
        else:
            st.success("Disco OK")
    
    with col4:
        uptime = datetime.now() - system_metrics['boot_time']
        st.metric("⏱️ Uptime", f"{uptime.days}d {uptime.seconds//3600}h")
    
    # Gráficos de sistema
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge para CPU
        fig_cpu = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = system_metrics['cpu_percent'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "CPU Usage (%)"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_cpu.update_layout(height=300)
        st.plotly_chart(fig_cpu, use_container_width=True)
    
    with col2:
        # Gauge para Memória
        fig_mem = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = system_metrics['memory_percent'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Memory Usage (%)"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_mem.update_layout(height=300)
        st.plotly_chart(fig_mem, use_container_width=True)
    
    st.markdown("---")
    
    # Métricas do Banco de Dados
    st.header("🐘 PostgreSQL Status")
    db_metrics = get_database_metrics()
    
    if db_metrics:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📦 Tamanho do DB", db_metrics['db_size'])
        
        with col2:
            st.metric("🔗 Conexões Ativas", db_metrics['connections'])
        
        with col3:
            st.success("✅ PostgreSQL Online")
        
        # Estatísticas das tabelas
        if db_metrics['table_stats']:
            st.subheader("📋 Estatísticas das Tabelas")
            df_tables = pd.DataFrame(db_metrics['table_stats'], 
                                   columns=['Schema', 'Tabela', 'Inserts', 'Updates', 'Deletes', 'Tamanho'])
            st.dataframe(df_tables, use_container_width=True)
    else:
        st.error("❌ PostgreSQL Offline ou Inacessível")
    
    st.markdown("---")
    
    # Métricas do Redis
    st.header("⚡ Redis Status")
    redis_metrics = get_redis_metrics()
    
    if redis_metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💾 Memória Usada", redis_metrics['used_memory_human'])
        
        with col2:
            st.metric("👥 Clientes", redis_metrics['connected_clients'])
        
        with col3:
            st.metric("⚡ Ops/seg", redis_metrics['instantaneous_ops_per_sec'])
        
        with col4:
            st.metric("🎯 Hit Rate", 
                     f"{(redis_metrics['keyspace_hits'] / (redis_metrics['keyspace_hits'] + redis_metrics['keyspace_misses']) * 100):.1f}%"
                     if (redis_metrics['keyspace_hits'] + redis_metrics['keyspace_misses']) > 0 else "0%")
        
        # Mais detalhes do Redis
        st.subheader("📊 Detalhes do Redis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Estatísticas de Comando:**")
            st.write(f"• Total de comandos: {redis_metrics['total_commands_processed']:,}")
            st.write(f"• Cache hits: {redis_metrics['keyspace_hits']:,}")
            st.write(f"• Cache misses: {redis_metrics['keyspace_misses']:,}")
            st.write(f"• Chaves expiradas: {redis_metrics['expired_keys']:,}")
            st.write(f"• Chaves removidas: {redis_metrics['evicted_keys']:,}")
        
        with col2:
            st.write("**Informações do Sistema:**")
            st.write(f"• Versão: {redis_metrics['redis_version']}")
            st.write(f"• Uptime: {redis_metrics['uptime_in_seconds']//3600}h {(redis_metrics['uptime_in_seconds']%3600)//60}m")
            st.write(f"• Memória usada: {redis_metrics['used_memory']:,} bytes")
        
        st.success("✅ Redis Online")
    else:
        st.error("❌ Redis Offline ou Inacessível")
    
    st.markdown("---")
    
    # Status dos Containers Docker
    st.header("🐳 Docker Containers")
    containers = check_docker_containers()
    
    if containers:
        df_containers = pd.DataFrame([
            {
                'Nome': container.get('Names', ''),
                'Imagem': container.get('Image', ''),
                'Status': container.get('Status', ''),
                'Portas': container.get('Ports', ''),
                'Criado': container.get('CreatedAt', '')
            }
            for container in containers
        ])
        
        st.dataframe(df_containers, use_container_width=True)
        st.success(f"✅ {len(containers)} containers rodando")
    else:
        st.warning("⚠️ Nenhum container Docker encontrado ou Docker não está rodando")
    
    # Pipeline Status
    st.markdown("---")
    st.header("🔄 Status do Pipeline")
    
    # Verificar última execução
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    MAX(last_updated) as last_update
                FROM coin_market_data
            """)
            result = cursor.fetchone()
            total_records = result[0]
            last_update = result[1]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Total de Registros", f"{total_records:,}")
            
            with col2:
                if last_update:
                    time_diff = datetime.now() - last_update.replace(tzinfo=None)
                    st.metric("🕐 Última Atualização", f"{time_diff.seconds//60}min atrás")
                else:
                    st.metric("🕐 Última Atualização", "N/A")
            
            with col3:
                # Status baseado na última atualização
                if last_update and time_diff.seconds < 3600:  # Menos de 1 hora
                    st.success("✅ Pipeline Ativo")
                else:
                    st.error("❌ Pipeline Inativo")
            
            conn.close()
            
        except Exception as e:
            st.error(f"Erro ao verificar status do pipeline: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"**System Monitor** | Atualizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

if __name__ == "__main__":
    main()
