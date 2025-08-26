"""
Script de automação para configurar e executar o pipeline completo de ML
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description):
    """Executa um comando e mostra o progresso"""
    print(f"\n🔄 {description}...")
    print(f"   Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Concluído!")
            if result.stdout:
                print(f"   Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ {description} - Erro!")
            print(f"   Erro: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exceção: {e}")
        return False

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'pandas', 'numpy', 'scikit-learn', 'sqlite3', 'requests', 'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - FALTANDO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Instalando pacotes faltantes: {', '.join(missing_packages)}")
        install_cmd = f"pip install {' '.join(missing_packages)}"
        return run_command(install_cmd, "Instalação de dependências")
    
    print("✅ Todas as dependências estão instaladas!")
    return True

def setup_ml_pipeline():
    """Configura o pipeline completo de ML"""
    print("🚀 CONFIGURAÇÃO DO PIPELINE ML")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        print("❌ Falha na verificação de dependências")
        return False
    
    # Navegar para o diretório correto
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    ml_dir = os.path.join(script_dir, 'ml')
    
    print(f"📁 Diretório do projeto: {project_root}")
    print(f"📁 Diretório ML: {ml_dir}")
    
    # Criar diretório ML se não existir
    os.makedirs(ml_dir, exist_ok=True)
    os.makedirs(os.path.join(ml_dir, 'models'), exist_ok=True)
    
    # 1. Executar Data Warehouse
    print("\n" + "="*30)
    print("ETAPA 1: COLETA DE DADOS")
    print("="*30)
    
    data_warehouse_script = os.path.join(ml_dir, 'data_warehouse.py')
    if os.path.exists(data_warehouse_script):
        os.chdir(ml_dir)
        success = run_command("python data_warehouse.py", "Coleta de dados históricos")
        if not success:
            print("❌ Falha na coleta de dados")
            return False
    else:
        print(f"❌ Script não encontrado: {data_warehouse_script}")
        return False
    
    # 2. Treinar modelos ML
    print("\n" + "="*30)
    print("ETAPA 2: TREINAMENTO ML")
    print("="*30)
    
    ml_models_script = os.path.join(ml_dir, 'ml_models.py')
    if os.path.exists(ml_models_script):
        success = run_command("python ml_models.py", "Treinamento de modelos ML")
        if not success:
            print("❌ Falha no treinamento de modelos")
            return False
    else:
        print(f"❌ Script não encontrado: {ml_models_script}")
        return False
    
    print("\n🎉 PIPELINE ML CONFIGURADO COM SUCESSO!")
    print("="*50)
    
    # Verificar arquivos gerados
    warehouse_db = os.path.join(ml_dir, 'crypto_warehouse.db')
    models_dir = os.path.join(ml_dir, 'models')
    
    if os.path.exists(warehouse_db):
        size_mb = os.path.getsize(warehouse_db) / (1024 * 1024)
        print(f"📊 Data Warehouse: {size_mb:.2f} MB")
    
    if os.path.exists(models_dir):
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
        print(f"🤖 Modelos treinados: {len(model_files)}")
    
    return True

def start_ml_dashboard():
    """Inicia o dashboard ML"""
    print("\n🚀 INICIANDO DASHBOARD ML")
    print("="*30)
    
    dashboard_script = os.path.join(os.path.dirname(__file__), 'dashboard', 'ml_dashboard.py')
    
    if os.path.exists(dashboard_script):
        dashboard_dir = os.path.dirname(dashboard_script)
        os.chdir(dashboard_dir)
        
        print("🌐 Iniciando Streamlit ML Dashboard...")
        print("   URL: http://localhost:8504")
        print("   Para parar: Ctrl+C")
        print("\n" + "="*30)
        
        # Executar em background para não bloquear
        command = "streamlit run ml_dashboard.py --server.port 8504"
        subprocess.Popen(command, shell=True)
        
        time.sleep(3)  # Aguardar inicialização
        print("✅ Dashboard ML iniciado!")
        print("🌐 Acesse: http://localhost:8504")
        
        return True
    else:
        print(f"❌ Dashboard não encontrado: {dashboard_script}")
        return False

def show_menu():
    """Mostra menu de opções"""
    print("\n🤖 CRYPTO ML PIPELINE")
    print("="*30)
    print("1. 🔧 Configurar pipeline completo")
    print("2. 📊 Apenas coletar dados")
    print("3. 🤖 Apenas treinar modelos")
    print("4. 🌐 Iniciar dashboard ML")
    print("5. 🚀 Configurar + Dashboard")
    print("0. ❌ Sair")
    print("="*30)

def main():
    """Função principal"""
    while True:
        show_menu()
        choice = input("\n👉 Escolha uma opção: ").strip()
        
        if choice == "0":
            print("👋 Encerrando...")
            break
        
        elif choice == "1":
            setup_ml_pipeline()
        
        elif choice == "2":
            ml_dir = os.path.join(os.path.dirname(__file__), 'ml')
            os.chdir(ml_dir)
            run_command("python data_warehouse.py", "Coleta de dados")
        
        elif choice == "3":
            ml_dir = os.path.join(os.path.dirname(__file__), 'ml')
            os.chdir(ml_dir)
            run_command("python ml_models.py", "Treinamento de modelos")
        
        elif choice == "4":
            start_ml_dashboard()
        
        elif choice == "5":
            if setup_ml_pipeline():
                start_ml_dashboard()
        
        else:
            print("❌ Opção inválida!")
        
        input("\n⏸️  Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
