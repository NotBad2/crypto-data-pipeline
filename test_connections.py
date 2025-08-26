import psycopg2
import redis
import requests
import time

def test_postgres():
    """Teste de conexão PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='crypto_data',
            user='crypto_user',
            password='crypto_pass'
        )
        print("✅ PostgreSQL: Conectado com sucesso!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"   Versão: {version[0]}")
        
        # Criar tabela de teste se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coin_market_data (
                id SERIAL PRIMARY KEY,
                coin_id VARCHAR(50),
                symbol VARCHAR(10),
                name VARCHAR(100),
                current_price DECIMAL(20,8),
                market_cap BIGINT,
                market_cap_rank INTEGER,
                price_change_24h DECIMAL(20,8),
                price_change_percentage_24h DECIMAL(10,2),
                total_volume BIGINT,
                circulating_supply DECIMAL(20,2),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS global_market_data (
                id SERIAL PRIMARY KEY,
                total_market_cap BIGINT,
                total_volume_24h BIGINT,
                market_cap_change_percentage_24h DECIMAL(10,2),
                total_cryptocurrencies INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Tabelas criadas/verificadas com sucesso!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro PostgreSQL: {e}")
        return False

def test_redis():
    """Teste de conexão Redis"""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis: Conectado com sucesso!")
        
        # Teste básico
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        print(f"   Teste básico: {value.decode()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro Redis: {e}")
        return False

def collect_sample_data():
    """Coleta dados de exemplo da API CoinGecko"""
    try:
        print("🔄 Coletando dados da API CoinGecko...")
        
        # Dados das moedas
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        coins_data = response.json()
        
        # Dados globais
        global_url = "https://api.coingecko.com/api/v3/global"
        global_response = requests.get(global_url, timeout=10)
        global_response.raise_for_status()
        global_data = global_response.json()['data']
        
        print(f"✅ Coletados dados de {len(coins_data)} moedas")
        return coins_data, global_data
        
    except Exception as e:
        print(f"❌ Erro na coleta de dados: {e}")
        return None, None

def insert_data(coins_data, global_data):
    """Insere dados no PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='crypto_data',
            user='crypto_user',
            password='crypto_pass'
        )
        cursor = conn.cursor()
        
        # Inserir dados das moedas
        for coin in coins_data:
            cursor.execute("""
                INSERT INTO coin_market_data (
                    coin_id, symbol, name, current_price, market_cap, 
                    market_cap_rank, price_change_24h, price_change_percentage_24h,
                    total_volume, circulating_supply
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                coin['id'], coin['symbol'], coin['name'],
                coin['current_price'], coin['market_cap'],
                coin['market_cap_rank'], coin['price_change_24h'],
                coin['price_change_percentage_24h'], coin['total_volume'],
                coin['circulating_supply']
            ))
        
        # Inserir dados globais
        cursor.execute("""
            INSERT INTO global_market_data (
                total_market_cap, total_volume_24h, 
                market_cap_change_percentage_24h, total_cryptocurrencies
            ) VALUES (%s, %s, %s, %s)
        """, (
            global_data['total_market_cap']['usd'],
            global_data['total_volume']['usd'],
            global_data['market_cap_change_percentage_24h_usd'],
            global_data['active_cryptocurrencies']
        ))
        
        conn.commit()
        print("✅ Dados inseridos no PostgreSQL com sucesso!")
        
        # Cache no Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.set('last_update', time.time())
        r.set('total_coins', len(coins_data))
        print("✅ Cache atualizado no Redis!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")
        return False

def main():
    print("🚀 TESTE DE CONEXÃO E POPULAÇÃO DE DADOS")
    print("=" * 50)
    
    # Teste PostgreSQL
    print("\n1. Testando PostgreSQL...")
    if not test_postgres():
        print("❌ Falha no PostgreSQL. Verifique se o container está rodando.")
        return
    
    # Teste Redis
    print("\n2. Testando Redis...")
    if not test_redis():
        print("❌ Falha no Redis. Verifique se o container está rodando.")
        return
    
    # Coleta dados
    print("\n3. Coletando dados da API...")
    coins_data, global_data = collect_sample_data()
    
    if coins_data and global_data:
        print("\n4. Inserindo dados no banco...")
        if insert_data(coins_data, global_data):
            print("\n🎉 SUCESSO! Todos os sistemas funcionando!")
            print("   Agora você pode acessar o dashboard:")
            print("   http://localhost:8501")
        else:
            print("❌ Falha ao inserir dados")
    else:
        print("❌ Falha na coleta de dados")

if __name__ == "__main__":
    main()
