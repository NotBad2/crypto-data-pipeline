# 🚀 Guia de Deploy Simplificado - Streamlit Cloud

## Opção 1: Deploy com App Completo (Recomendado)

### Passo 1: Verificar arquivos necessários
```
crypto-data-pipeline/
├── src/dashboard/crypto_app_unified.py  # App principal
├── requirements.txt                     # Dependências
├── packages.txt                        # Dependências sistema (opcional)
└── README.md                           # Documentação
```

### Passo 2: Fazer commit das alterações
```bash
git add .
git commit -m "Fix: ML libraries error handling for Streamlit Cloud"
git push origin main
```

### Passo 3: Deploy no Streamlit Cloud
1. Aceder: https://share.streamlit.io/
2. Conectar GitHub
3. Selecionar repositório: `crypto-data-pipeline`
4. Definir main file: `src/dashboard/crypto_app_unified.py`
5. Definir branch: `main`
6. Clicar "Deploy!"

---

## Opção 2: Deploy com App Simplificado (Backup)

Se a Opção 1 não funcionar, use a versão simplificada:

### Arquivos para esta opção:
- `src/dashboard/crypto_app_simple.py` (apenas dashboard principal)
- `requirements_simple.txt` (dependências mínimas)

### Deploy:
1. No Streamlit Cloud, usar main file: `src/dashboard/crypto_app_simple.py`
2. Renomear `requirements_simple.txt` para `requirements.txt`

---

## 🔧 Troubleshooting

### Erro: ModuleNotFoundError
✅ **Solução aplicada**: Mock classes para bibliotecas ML
✅ **Resultado**: App funciona mesmo sem scikit-learn

### Erro: Package not found
1. Verificar `requirements.txt` - usar nomes básicos:
   ```
   streamlit
   pandas
   plotly
   requests
   numpy
   scikit-learn
   joblib
   ```

2. Se persistir, usar `requirements_simple.txt`:
   ```
   streamlit
   pandas
   plotly
   requests
   numpy
   ```

### Erro: Build failed
1. Verificar logs no Streamlit Cloud
2. Usar versão simplificada como backup
3. Contactar suporte Streamlit se necessário

---

## 📊 Funcionalidades por Versão

### App Completo (`crypto_app_unified.py`)
- ✅ Dashboard Principal (sempre funciona)
- ⚠️ ML Analytics (funciona se bibliotecas disponíveis)
- ✅ Análise Técnica (sempre funciona)

### App Simplificado (`crypto_app_simple.py`)
- ✅ Dashboard Principal apenas
- 🚀 Garantia de funcionamento em qualquer ambiente

---

## 🎯 Próximos Passos

1. **Testar deploy**: Opção 1 primeiro, depois Opção 2 se necessário
2. **Verificar funcionalidade**: Testar todas as páginas no deploy
3. **Atualizar README**: Adicionar link do app live quando funcionando
4. **Documentar**: Adicionar screenshots para portfolio

---

## 📞 Suporte

- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Community Forum**: https://discuss.streamlit.io/
- **GitHub Issues**: Para problemas específicos do projeto
