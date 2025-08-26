# 🚀 Deploy Guide - Como Colocar Online

## 🆓 Opção 1: Streamlit Community Cloud (RECOMENDADO)

### Passos:

1. **📝 Preparar o repositório GitHub:**
   ```bash
   # No teu computador
   cd crypto-data-pipeline
   git add .
   git commit -m "Preparado para deploy"
   git push origin main
   ```

2. **🌐 Deploy no Streamlit Cloud:**
   - Vai a [share.streamlit.io](https://share.streamlit.io)
   - Clica em "New app"
   - Conecta a tua conta GitHub
   - Seleciona o repositório: `crypto-data-pipeline`
   - Main file path: `src/dashboard/crypto_app_unified.py`
   - Clica "Deploy!"

3. **🎉 URL final:**
   - `https://crypto-data-pipeline.streamlit.app`
   - Ou similar com o teu username

### ⚡ Vantagens:
- ✅ 100% Grátis
- ✅ Deploy automático
- ✅ URL bonita
- ✅ Suporta SQLite
- ✅ Reboot automático

---

## 💰 Opção 2: Railway ($5/mês)

### Passos:

1. **Vai a [railway.app](https://railway.app)**
2. **Conecta GitHub**
3. **Deploy from GitHub repo**
4. **Seleciona crypto-data-pipeline**
5. **Adiciona variável de ambiente:**
   - `PORT=8000`
6. **URL final:** `https://crypto-data-pipeline.up.railway.app`

---

## 🆓 Opção 3: Render (Grátis com limitações)

### Passos:

1. **Vai a [render.com](https://render.com)**
2. **New Web Service**
3. **Connect repository**
4. **Configurações:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run src/dashboard/crypto_app_unified.py --server.port=$PORT --server.address=0.0.0.0`

### ⚠️ Limitação:
- App "dorme" após 15 min de inatividade
- Demora ~30s para "acordar"

---

## 📝 Ficheiros importantes para deploy:

✅ `requirements.txt` - Dependências Python
✅ `.streamlit/config.toml` - Configuração Streamlit  
✅ `README.md` - Documentação bonita
✅ `setup.py` - Script de inicialização

---

## 🎯 Recomendação:

**Use Streamlit Community Cloud** - é grátis, fácil e profissional!

Depois de fazer o deploy, podes partilhar o link:
- No teu CV
- No LinkedIn
- Com recrutadores
- No GitHub README

### 🔗 Link para o teu portfólio:
`https://[teu-projeto].streamlit.app`
