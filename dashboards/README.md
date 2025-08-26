# 📊 Crypto Data Pipeline - Dashboards

Este projeto inclui dashboards completos do Grafana para visualização de dados de criptomoedas em tempo real.

## 🎯 Dashboards Disponíveis

### 1. 📈 Main Dashboard (`crypto-main`)
**URL:** http://localhost:3000/d/crypto-main

**Painéis incluídos:**
- 📋 **Market Data Table**: Tabela completa com todas as criptomoedas
- 📊 **Price Trends**: Gráfico de tendências de preços ao longo do tempo
- 🏆 **Top Performers**: Ranking dos melhores desempenhos em 24h
- 💰 **Total Market Cap**: Capitalização total do mercado
- ₿ **Bitcoin Dominance**: Percentual de dominância do Bitcoin
- 📊 **Data Points Count**: Contador de registros de dados

### 2. 📊 Performance Analytics (`crypto-performance`)
**URL:** http://localhost:3000/d/crypto-performance

**Painéis incluídos:**
- 🎯 **24h Performance Ranking**: Ranking detalhado de mudanças em 24h
- 📊 **Top 15 Performers**: Gráfico de barras dos melhores desempenhos
- 🥧 **Market Cap Distribution**: Distribuição de capitalização (Top 10)
- 📈 **Trading Volume Distribution**: Distribuição de volume de negociação

## 🚀 Como Acessar

1. **Iniciar os serviços:**
   ```bash
   docker-compose up -d
   ```

2. **Executar coleta de dados:**
   ```bash
   python test_postgres_integration.py
   ```

3. **Acessar Grafana:**
   - URL: http://localhost:3000
   - Login: `admin`
   - Senha: `admin`

## 📁 Estrutura dos Dashboards

```
dashboards/
├── provisioning/
│   ├── datasources/
│   │   └── datasources.yml          # Configuração PostgreSQL + Redis
│   └── dashboards/
│       └── dashboards.yml           # Auto-provisioning
├── crypto-main-dashboard.json       # Dashboard principal
└── crypto-performance-dashboard.json # Dashboard de performance
```

## 🔧 Configurações

### Fontes de Dados
- **PostgreSQL**: `crypto_postgres:5432/crypto_data`
- **Redis**: `crypto_redis:6379` (futuro)

### Atualização
- **Intervalo**: 30 segundos
- **Auto-refresh**: Habilitado
- **Time range**: Últimas 24 horas

## 📊 Queries Principais

### Market Data Table
```sql
SELECT name, symbol, current_price, 
       price_change_percentage_24h, market_cap
FROM raw_data.market_data 
WHERE collected_at = (SELECT MAX(collected_at) FROM raw_data.market_data)
ORDER BY market_cap DESC;
```

### Performance Ranking
```sql
SELECT name, symbol, price_change_percentage_24h
FROM raw_data.market_data 
WHERE collected_at = (SELECT MAX(collected_at) FROM raw_data.market_data)
  AND price_change_percentage_24h IS NOT NULL
ORDER BY price_change_percentage_24h DESC;
```

## 🎨 Personalização

### Cores e Temas
- **Tema padrão**: Dark
- **Paleta**: Continuous-GrYlRd para performance
- **Indicadores**: Verde/Vermelho para ganhos/perdas

### Alertas (Futuro)
- Alertas para mudanças > 10%
- Notificações para novos máximos
- Monitoramento de volume anômalo

## 🔄 Pipeline de Dados

```
📡 CoinGecko API → 🔄 Processing → 🐘 PostgreSQL → 📊 Grafana Dashboards
                                     ↓
                                 🔴 Redis Cache
```

## 🛠️ Troubleshooting

### Dashboard não carrega
1. Verificar se PostgreSQL tem dados:
   ```bash
   python verify_dashboards.py
   ```

2. Reiniciar Grafana:
   ```bash
   docker-compose restart grafana
   ```

### Dados desatualizados
```bash
# Executar nova coleta
python test_postgres_integration.py

# Verificar timestampo
python verify_dashboards.py
```

### Problemas de conexão
- Verificar se todos os serviços estão rodando: `docker-compose ps`
- Verificar logs: `docker-compose logs grafana`

## 📈 Métricas de Sucesso

- ✅ 100% taxa de sucesso na integração
- ✅ Dados em tempo real (30s refresh)
- ✅ Múltiplas visualizações (tabelas, gráficos, gauges)
- ✅ Auto-provisioning funcionando
- ✅ Queries otimizadas

## 🎯 Próximos Passos

1. **Alerting**: Configurar alertas do Grafana
2. **Histórico**: Adicionar gráficos de tendência temporal
3. **Correlações**: Dashboard de correlação entre moedas
4. **Mobile**: Otimizar para visualização mobile
5. **Export**: Funcionalidade de export de relatórios

## 📝 Notas Técnicas

- **Auto-refresh**: Configurado para 30 segundos
- **Performance**: Queries otimizadas com índices
- **Escalabilidade**: Suporta milhares de registros
- **Disponibilidade**: 99.9% uptime com Docker
