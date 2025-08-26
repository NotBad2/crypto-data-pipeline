import os
import subprocess
import sys

def setup_environment():
    """Setup do ambiente para o deploy"""
    print("🔧 Configurando ambiente...")
    
    # Verificar se a base de dados existe
    db_path = "src/crypto_warehouse.db"
    if not os.path.exists(db_path):
        print("📊 Criando base de dados...")
        try:
            # Executar o script de data warehouse
            subprocess.run([sys.executable, "src/ml/data_warehouse.py"], check=True)
            print("✅ Base de dados criada!")
        except Exception as e:
            print(f"❌ Erro ao criar base de dados: {e}")
    
    print("🚀 Ambiente configurado!")

if __name__ == "__main__":
    setup_environment()
