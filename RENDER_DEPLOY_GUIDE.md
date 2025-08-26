# 🚀 Guia de Deploy no Render.com

## ✅ Ficheiros Preparados
- `render.yaml` - Configuração do Render
- `requirements.txt` - Dependências Python com versões específicas
- `.streamlit/config.toml` - Configuração Streamlit para Render
- `start.sh` - Script de inicialização

## 📋 Passo a Passo

### 1. Fazer Commit das Alterações
```bash
git add .
git commit -m "feat: Add Render.com deployment configuration"
git push origin main
```

### 2. Criar Conta no Render
1. Aceder: https://render.com/
2. Fazer signup (pode usar GitHub)
3. Verificar email se necessário

### 3. Conectar GitHub
1. No dashboard do Render, clicar "New +"
2. Escolher "Web Service"
3. Conectar repositório GitHub
4. Selecionar `crypto-data-pipeline`

### 4. Configurar o Serviço
**Configurações importantes:**
- **Name**: `crypto-data-pipeline`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run src/dashboard/crypto_app_unified.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
- **Plan**: `Free` (para começar)

### 5. Variáveis de Ambiente (Opcional)
Se precisares, podes adicionar:
- `PYTHON_VERSION`: `3.11.0`
- `STREAMLIT_SERVER_PORT`: `$PORT`

### 6. Deploy!
1. Clicar "Create Web Service"
2. O Render vai:
   - Clonar o repositório
   - Instalar dependências
   - Executar a aplicação
3. Aguardar 3-5 minutos

## 🎯 URLs Importantes
- **Dashboard Render**: https://dashboard.render.com/
- **Logs em tempo real**: Disponíveis no dashboard
- **URL da aplicação**: `https://crypto-data-pipeline-XXXX.onrender.com`

## 🔧 Troubleshooting

### Erro: Port not specified
- Verificar se `$PORT` está na start command
- Render define automaticamente a variável `$PORT`

### Erro: Module not found
- Verificar `requirements.txt`
- Logs mostrarão qual biblioteca falta

### Erro: Permission denied
- Tornar `start.sh` executável (se usares)
- No Windows: `git update-index --chmod=+x start.sh`

### Base de dados não funciona
- Render tem filesystem efémero, mas permite volumes
- Para persistência total, considerar PostgreSQL (grátis)

## 🚀 Próximos Passos

1. **Testar a aplicação** no URL fornecido
2. **Verificar todas as funcionalidades**:
   - ✅ Dashboard Principal (deve funcionar)
   - ✅ ML Analytics (deve funcionar com scikit-learn)
   - ✅ Análise Técnica (deve funcionar)
3. **Atualizar README.md** com o link live
4. **Configurar domínio customizado** (opcional)

## 💡 Dicas Importantes

### Performance
- Render Free tem 750h/mês (mais que suficiente)
- App "dorme" após 15min inatividade
- Primeiro acesso pode ser lento (cold start)

### Upgrades
- Se precisares de mais performance: $7/mês (Starter)
- Para base de dados persistente: PostgreSQL gratuito
- SSL/HTTPS incluído automaticamente

### Monitorização
- Logs em tempo real no dashboard
- Métricas de performance disponíveis
- Alertas via email

## 🏆 Vantagens vs Streamlit Cloud

| Funcionalidade | Streamlit Cloud | Render |
|---|---|---|
| Bibliotecas ML | ❌ Limitado | ✅ Completo |
| Base de dados | ❌ Read-only | ✅ Funciona |
| Performance | ⚠️ Limitada | ✅ Boa |
| Controlo | ❌ Mínimo | ✅ Total |
| SSL/HTTPS | ✅ Incluído | ✅ Incluído |
| Custom domain | ❌ Não | ✅ Sim |

O Render resolve todos os problemas que tiveste! 🎉
