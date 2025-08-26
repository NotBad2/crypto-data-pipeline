#!/usr/bin/env python3
"""
Script para configurar Grafana via API
"""

import requests
import json
import time

def wait_for_grafana():
    """Aguarda o Grafana ficar disponível"""
    print("🔄 Aguardando Grafana inicializar...")
    for i in range(30):
        try:
            response = requests.get('http://localhost:3000/api/health', timeout=2)
            if response.status_code == 200:
                print("✅ Grafana está disponível!")
                return True
        except:
            pass
        time.sleep(2)
        print(f"   Tentativa {i+1}/30...")
    return False

def create_datasource():
    """Cria o datasource PostgreSQL"""
    print("📊 Criando datasource PostgreSQL...")
    
    # Primeiro, verificar se já existe
    try:
        response = requests.get(
            'http://localhost:3000/api/datasources/name/PostgreSQL-CryptoData',
            auth=('admin', 'admin')
        )
        if response.status_code == 200:
            print("✅ Datasource PostgreSQL já existe!")
            return True
    except:
        pass
    
    datasource_config = {
        "name": "PostgreSQL-CryptoData",
        "type": "postgres", 
        "url": "postgres:5432",
        "database": "crypto_data",
        "user": "crypto_user",
        "secureJsonData": {
            "password": "crypto_pass"
        },
        "jsonData": {
            "sslmode": "disable",
            "postgresVersion": 1500
        },
        "access": "proxy",
        "isDefault": True
    }
    
    try:
        response = requests.post(
            'http://localhost:3000/api/datasources',
            json=datasource_config,
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201, 409]:  # 409 = já existe
            print("✅ Datasource PostgreSQL configurado!")
            return True
        else:
            print(f"❌ Erro ao criar datasource: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
            # Tentar listar datasources existentes
            print("📋 Listando datasources existentes...")
            list_response = requests.get(
                'http://localhost:3000/api/datasources',
                auth=('admin', 'admin')
            )
            if list_response.status_code == 200:
                datasources = list_response.json()
                print(f"   Total: {len(datasources)} datasources")
                for ds in datasources:
                    print(f"   - {ds.get('name', 'N/A')} ({ds.get('type', 'N/A')})")
            
            return False
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def import_dashboard(dashboard_file, title):
    """Importa um dashboard"""
    print(f"📈 Importando dashboard: {title}...")
    
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            dashboard_json = json.load(f)
        
        # Preparar payload para import
        import_payload = {
            "dashboard": dashboard_json,
            "overwrite": True,
            "inputs": [
                {
                    "name": "DS_POSTGRESQL-CRYPTODATA",
                    "type": "datasource",
                    "pluginId": "postgres",
                    "value": "PostgreSQL-CryptoData"
                }
            ]
        }
        
        response = requests.post(
            'http://localhost:3000/api/dashboards/import',
            json=import_payload,
            auth=('admin', 'admin'),
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dashboard importado! URL: http://localhost:3000{result['importedUrl']}")
            return True
        else:
            print(f"❌ Erro ao importar dashboard: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao importar dashboard: {e}")
        return False

def main():
    print("🚀 CONFIGURAÇÃO DO GRAFANA VIA API")
    print("=" * 50)
    
    if not wait_for_grafana():
        print("❌ Grafana não ficou disponível")
        return
    
    # Criar datasource
    if not create_datasource():
        print("❌ Falha ao criar datasource")
        return
    
    # Importar dashboards
    dashboards = [
        ("dashboards/crypto-main-dashboard.json", "Main Dashboard"),
        ("dashboards/crypto-performance-dashboard.json", "Performance Dashboard")
    ]
    
    for dashboard_file, title in dashboards:
        try:
            import_dashboard(dashboard_file, title)
        except Exception as e:
            print(f"⚠️ Erro ao importar {title}: {e}")
    
    print("\n🎉 Configuração completa!")
    print("📊 Acesse: http://localhost:3000")
    print("👤 Login: admin / admin")

if __name__ == "__main__":
    main()
