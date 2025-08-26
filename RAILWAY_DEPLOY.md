# 🚂 Deploy no Railway - Guia Completo

## 📋 Pré-requisitos

1. **Conta no Railway**: [railway.app](https://railway.app)
2. **Projeto no GitHub**: Push do código para um repositório
3. **Ficheiros configurados** (já incluídos neste projeto)

## 🛠️ Ficheiros de Configuração

### ✅ `railway.json` (já criado)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run src/dashboard/crypto_app_unified.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

### ✅ `requirements.txt` (já existe)
- Todas as dependências necessárias já estão listadas

### ✅ `.streamlit/config.toml` (verificar se existe)
- Configurações do Streamlit para produção

## 🚀 Passos para Deploy

### 1. **Preparar o Repositório GitHub**

```bash
# Se ainda não fizeste push para o GitHub
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. **Criar Projeto no Railway**

1. Acede a [railway.app](https://railway.app)
2. Clica em **"Start a New Project"**
3. Seleciona **"Deploy from GitHub repo"**
4. Escolhe o repositório `crypto-data-pipeline`
5. Railway irá automaticamente detectar que é uma aplicação Python

### 3. **Configurar Variáveis de Ambiente**

No painel do Railway, vai a **Variables** e adiciona:

```env
PORT=8080
PYTHONPATH=/app/src
STREAMLIT_SERVER_PORT=8080
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

### 4. **Deploy Automático**

- Railway irá automaticamente:
  - Detectar `requirements.txt`
  - Instalar dependências
  - Executar o comando definido em `railway.json`
  - Gerar um URL público

## 🔧 Configurações Adicionais

### Port Configuration
Railway atribui automaticamente uma porta através da variável `$PORT`. O nosso `railway.json` já está configurado para usar esta variável.

### Health Check
O Railway irá verificar se a aplicação está healthy através do path `/` configurado.

### Build Time
- Tempo estimado: 2-5 minutos
- Railway oferece builds mais rápidos que outras plataformas

## 📊 Monitorização

### Logs
```bash
# No painel Railway, podes ver os logs em tempo real
# Ou usar Railway CLI:
railway logs
```

### Métricas
- CPU usage
- Memory usage
- Request count
- Response times

## 💰 Custos

### Plano Gratuito
- **$5 USD/mês de créditos grátis**
- Suficiente para projetos de demonstração
- Sem sleeping (ao contrário do Heroku)

### Estimativa para este Projeto
- ~$3-4 USD/mês com tráfego moderado
- Ideal para portfolio e demonstrações

## 🔍 Troubleshooting

### Build Errors
```bash
# Verificar se requirements.txt está correto
pip install -r requirements.txt

# Testar localmente antes do deploy
streamlit run src/dashboard/crypto_app_unified.py --server.port=8080
```

### Application Errors
- Verificar logs no Railway dashboard
- Confirmar que todas as dependências estão em `requirements.txt`
- Verificar paths dos ficheiros (usar paths relativos)

### Performance Issues
- Railway oferece upgrade automático de recursos
- Monitoring integrado para identificar bottlenecks

## 🎯 Vantagens do Railway vs Outras Plataformas

| Feature | Railway | Heroku | Render |
|---------|---------|---------|---------|
| **Preço** | $5/mês créditos | $7/mês mínimo | Free com limitações |
| **Sleeping** | ❌ Nunca | ✅ 30min inatividade | ✅ 15min inatividade |
| **Deploy Speed** | ⚡ Muito rápido | 🐌 Lento | 🐌 Lento |
| **Database** | ✅ PostgreSQL/Redis | ✅ PostgreSQL | ✅ PostgreSQL |
| **Custom Domain** | ✅ Grátis | 💰 Pago | ✅ Grátis |

## 🚀 Deploy em 1 Comando (Railway CLI)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

## 🔗 URLs Úteis

- **Railway Dashboard**: [railway.app/dashboard](https://railway.app/dashboard)
- **Documentation**: [docs.railway.app](https://docs.railway.app)
- **Community**: [Discord Railway](https://discord.gg/railway)

## ✅ Checklist Final

- [ ] Código no GitHub
- [ ] `railway.json` configurado
- [ ] `requirements.txt` atualizado
- [ ] Teste local funcionando
- [ ] Deploy no Railway
- [ ] URL público funcional
- [ ] Monitorização ativa

---

**🎉 O teu projeto estará online e acessível 24/7!**

**URL exemplo**: `https://crypto-data-pipeline-production.up.railway.app`
