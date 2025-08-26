#!/usr/bin/env python3
"""
Railway Deploy Checker
Verifica se o projeto está pronto para deploy no Railway
"""

import os
import sys
import json

def check_file_exists(filepath, required=True):
    """Verifica se um ficheiro existe"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else ("❌" if required else "⚠️")
    requirement = "REQUIRED" if required else "OPTIONAL"
    print(f"{status} {filepath} ({requirement})")
    return exists

def check_railway_config():
    """Verifica configuração do Railway"""
    print("🚂 RAILWAY DEPLOY CHECKER")
    print("=" * 40)
    
    # Ficheiros obrigatórios
    print("\n📁 Required Files:")
    required_files = [
        "railway.json",
        "requirements.txt", 
        "Procfile",
        "src/dashboard/crypto_app_unified.py"
    ]
    
    all_required = True
    for file in required_files:
        if not check_file_exists(file, required=True):
            all_required = False
    
    # Ficheiros opcionais mas recomendados
    print("\n📁 Recommended Files:")
    optional_files = [
        ".streamlit/config.toml",
        "start_railway.sh",
        ".env.example"
    ]
    
    for file in optional_files:
        check_file_exists(file, required=False)
    
    # Verificar conteúdo do railway.json
    print("\n⚙️ Railway Configuration:")
    if os.path.exists("railway.json"):
        try:
            with open("railway.json", 'r') as f:
                config = json.load(f)
            
            if 'deploy' in config and 'startCommand' in config['deploy']:
                print("✅ Start command configured")
            else:
                print("❌ Start command missing")
                all_required = False
                
        except json.JSONDecodeError:
            print("❌ railway.json is not valid JSON")
            all_required = False
    
    # Verificar requirements.txt
    print("\n📦 Dependencies:")
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
        
        essential_deps = ['streamlit', 'pandas', 'plotly', 'requests', 'scikit-learn']
        missing_deps = []
        
        for dep in essential_deps:
            if dep not in requirements.lower():
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
            all_required = False
        else:
            print("✅ All essential dependencies present")
    
    # Resultado final
    print("\n" + "=" * 40)
    if all_required:
        print("🎉 PROJECT READY FOR RAILWAY DEPLOY!")
        print("\n🚀 Next Steps:")
        print("1. git add . && git commit -m 'Deploy to Railway'")
        print("2. git push origin main")
        print("3. Visit railway.app and deploy from GitHub")
        return True
    else:
        print("❌ Project needs fixes before deploy")
        return False

if __name__ == "__main__":
    success = check_railway_config()
    sys.exit(0 if success else 1)
