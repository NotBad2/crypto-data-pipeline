#!/usr/bin/env python3
"""
Crypto Data Pipeline - Ativador de Serviços
Automatiza a inicialização de todos os componentes do projeto
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

class CryptoPipelineManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dashboard_dir = self.project_root / "src" / "dashboard"
        self.data_warehouse_dir = self.project_root / "src" / "data_warehouse"
        self.streamlit_process = None
        
    def print_header(self, title):
        """Imprime cabeçalho formatado"""
        print("\n" + "="*50)
        print(f"   {title}")
        print("="*50)
        
    def check_python(self):
        """Verifica se Python está instalado"""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                 capture_output=True, text=True)
            print(f"[OK] Python encontrado: {result.stdout.strip()}")
            return True
        except Exception as e:
            print(f"[ERRO] Python não encontrado: {e}")
            return False
    
    def install_dependencies(self):
        """Instala dependências Python"""
        self.print_header("INSTALANDO DEPENDÊNCIAS")
        
        requirements_file = self.dashboard_dir / "requirements.txt"
        
        if requirements_file.exists():
            print("[INFO] Instalando pacotes do requirements.txt...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        else:
            print("[INFO] Instalando pacotes essenciais...")
            packages = [
                "streamlit", "pandas", "plotly", "requests", 
                "scikit-learn", "joblib", "numpy"
            ]
            subprocess.run([sys.executable, "-m", "pip", "install"] + packages)
        
        print("[OK] Dependências instaladas")
    
    def setup_data_warehouse(self):
        """Verifica e configura o data warehouse"""
        self.print_header("CONFIGURANDO DATA WAREHOUSE")
        
        db_file = self.data_warehouse_dir / "crypto_warehouse.db"
        
        if db_file.exists():
            print("[OK] Data Warehouse encontrado")
            size = db_file.stat().st_size / (1024*1024)  # MB
            print(f"[INFO] Tamanho da base de dados: {size:.2f} MB")
        else:
            print("[AVISO] Data Warehouse não encontrado")
            
            data_warehouse_script = self.data_warehouse_dir / "data_warehouse.py"
            if data_warehouse_script.exists():
                print("[INFO] Criando dados históricos...")
                os.chdir(self.data_warehouse_dir)
                subprocess.run([sys.executable, "data_warehouse.py"])
                os.chdir(self.project_root)
                print("[OK] Dados históricos criados")
            else:
                print("[AVISO] Script de data warehouse não encontrado")
    
    def setup_ml_models(self):
        """Treina ou verifica modelos ML"""
        self.print_header("CONFIGURANDO MODELOS ML")
        
        ml_script = self.data_warehouse_dir / "ml_models.py"
        
        if ml_script.exists():
            print("[INFO] Executando pipeline de ML...")
            os.chdir(self.data_warehouse_dir)
            subprocess.run([sys.executable, "ml_models.py"])
            os.chdir(self.project_root)
            print("[OK] Modelos ML configurados")
        else:
            print("[AVISO] Pipeline ML não encontrado")
    
    def start_dashboard(self):
        """Inicia o dashboard Streamlit"""
        self.print_header("INICIANDO DASHBOARD")
        
        # Parar processos existentes
        print("[INFO] Parando processos Streamlit existentes...")
        if os.name == 'nt':  # Windows
            subprocess.run(["taskkill", "/f", "/im", "streamlit.exe"], 
                         capture_output=True)
        else:  # Linux/Mac
            subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        
        time.sleep(2)
        
        # Mudar para diretório do dashboard
        os.chdir(self.dashboard_dir)
        
        print("[INFO] Iniciando Dashboard Unificado...")
        print("\n" + "="*50)
        print("              DASHBOARD ATIVO!")
        print("="*50)
        print("\n    URL Principal: http://localhost:8510")
        print("\n    Páginas Disponíveis:")
        print("    📊 Dashboard Principal - Dados em tempo real")
        print("    🤖 ML Analytics       - Machine Learning")
        print("    📈 Análise Técnica    - Em desenvolvimento")
        print("\n    Para parar: Ctrl+C")
        print("\n" + "="*50)
        
        # Iniciar Streamlit
        try:
            self.streamlit_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", 
                "crypto_app_unified.py",
                "--server.port", "8510",
                "--server.headless", "false"
            ])
            
            # Aguardar o processo
            self.streamlit_process.wait()
            
        except KeyboardInterrupt:
            print("\n[INFO] Interrompido pelo usuário")
        except Exception as e:
            print(f"\n[ERRO] Erro ao iniciar dashboard: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpa processos e recursos"""
        print("\n[INFO] Encerrando serviços...")
        
        if self.streamlit_process:
            self.streamlit_process.terminate()
            time.sleep(2)
            if self.streamlit_process.poll() is None:
                self.streamlit_process.kill()
        
        # Limpar processos restantes
        if os.name == 'nt':  # Windows
            subprocess.run(["taskkill", "/f", "/im", "streamlit.exe"], 
                         capture_output=True)
        else:  # Linux/Mac
            subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        
        print("[INFO] Serviços encerrados")
    
    def run(self):
        """Executa o pipeline completo"""
        print("CRYPTO DATA PIPELINE - ATIVADOR COMPLETO")
        print("="*50)
        
        # Verificar estrutura do projeto
        if not (self.dashboard_dir.exists() and self.data_warehouse_dir.exists()):
            print("[ERRO] Estrutura do projeto não encontrada!")
            print("[INFO] Execute este script a partir da raiz do projeto crypto-data-pipeline")
            return False
        
        try:
            # Etapas de configuração
            if not self.check_python():
                return False
            
            self.install_dependencies()
            self.setup_data_warehouse()
            self.setup_ml_models()
            self.start_dashboard()
            
        except KeyboardInterrupt:
            print("\n[INFO] Processo interrompido pelo usuário")
        except Exception as e:
            print(f"\n[ERRO] Erro inesperado: {e}")
        finally:
            self.cleanup()
        
        return True

def signal_handler(sig, frame):
    """Handler para sinais de interrupção"""
    print("\n[INFO] Recebido sinal de interrupção...")
    sys.exit(0)

if __name__ == "__main__":
    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Executar o manager
    manager = CryptoPipelineManager()
    success = manager.run()
    
    sys.exit(0 if success else 1)
