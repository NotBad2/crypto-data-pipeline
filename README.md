# Crypto Data Pipeline

## 🚀 Live Demo
**[Ver Aplicação Online](https://crypto-data-pipeline.streamlit.app)** ⬅️ Clica aqui!

## 📊 Projeto de Data Engineering 

Pipeline completo de dados de criptomoedas com dashboard interativo, análise ML e indicadores técnicos.

### ✨ Funcionalidades

#### 📈 **Dashboard Principal**
- Dados em tempo real da API CoinGecko
- Métricas de mercado em tempo real
- Top 50 criptomoedas
- Análise detalhada por moeda

#### 🤖 **ML Analytics**
- Modelos de Machine Learning (Random Forest, Gradient Boosting, Linear Regression)
- Previsões de preços (1 dia e 7 dias)
- Dados históricos (365 dias)
- Indicadores técnicos (RSI, MACD, Bollinger Bands)

#### 📈 **Análise Técnica**
- Níveis de suporte e resistência automáticos
- Retração de Fibonacci
- Osciladores avançados (Estocástico, Williams %R)
- Indicadores de momentum
- Detecção de padrões de candlestick

### 🛠️ Tecnologias Utilizadas

- **Frontend**: Streamlit
- **Data Visualization**: Plotly
- **Machine Learning**: scikit-learn
- **Database**: SQLite
- **API**: CoinGecko
- **Languages**: Python

### 📁 Estrutura do Projeto

```
crypto-data-pipeline/
├── src/
│   ├── dashboard/
│   │   └── crypto_app_unified.py    # Aplicação principal
│   ├── ml/
│   │   ├── data_warehouse.py        # Coleta de dados históricos
│   │   └── ml_models.py             # Modelos ML
│   └── crypto_warehouse.db          # Base de dados SQLite
├── requirements.txt
├── DEPLOY_GUIDE.md                  # Guia de deploy
└── README.md
```

### 🚀 Como Executar Localmente

1. **Clone o repositório:**
```bash
git clone https://github.com/[teu-username]/crypto-data-pipeline.git
cd crypto-data-pipeline
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação:**
```bash
streamlit run src/dashboard/crypto_app_unified.py
```

4. **Acesse:** http://localhost:8501

### 🌐 Deploy Online (Grátis!)

Ver **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** para instruções completas.

**Opção recomendada:** Streamlit Community Cloud (100% grátis)

### 📊 Dados

- **Fonte**: API CoinGecko (dados reais)
- **Histórico**: 365 dias de dados por criptomoeda
- **Atualizações**: Dados em tempo real (cache de 5 minutos)
- **Moedas**: Bitcoin, Ethereum, BNB, Cardano, Solana

### 🤖 Machine Learning

Os modelos são treinados com dados históricos reais e fazem previsões para:
- **Curto prazo**: 1 dia
- **Médio prazo**: 7 dias

**Algoritmos utilizados:**
- Random Forest Regressor
- Gradient Boosting Regressor  
- Linear Regression

### 📈 Indicadores Técnicos

- **Médias Móveis**: SMA 7, 14, 30
- **RSI**: Relative Strength Index (14 períodos)
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Bandas de volatilidade
- **Estocástico**: %K e %D
- **Williams %R**: Oscilador de momentum
- **Fibonacci**: Níveis de retração

### 🎯 Objetivos do Projeto

Este projeto foi desenvolvido como demonstração de habilidades em:
- **Data Engineering**: Pipeline completo de dados
- **Machine Learning**: Modelos preditivos
- **Data Visualization**: Dashboards interativos
- **APIs**: Integração com APIs externas
- **Databases**: Gestão de dados históricos
- **Web Applications**: Deploy de aplicações

### 👨‍💻 Sobre

Projeto desenvolvido para demonstrar competências em Data Engineering e Machine Learning aplicados ao mercado de criptomoedas.

**Tecnologias**: Python, Streamlit, Plotly, scikit-learn, SQLite, APIs REST

---

⭐ **Se gostaste do projeto, deixa uma estrela!** ⭐

```
crypto-data-pipeline
├── src
│   ├── extractors
│   │   ├── __init__.py
│   │   └── crypto_api.py
│   ├── transformers
│   │   ├── __init__.py
│   │   └── data_processor.py
│   ├── loaders
│   │   ├── __init__.py
│   │   └── database_loader.py
│   └── pipeline
│       ├── __init__.py
│       └── main.py
├── config
│   └── config.yaml
├── sql
│   └── create_tables.sql
├── tests
│   ├── __init__.py
│   └── test_pipeline.py
├── requirements.txt
├── docker-compose.yml
└── Dockerfile
```

## Features

- **Data Extraction**: Fetches cryptocurrency data from an external API using the `CryptoAPI` class.
- **Data Transformation**: Cleans and transforms the raw data into a structured format using the `DataProcessor` class.
- **Data Loading**: Loads the transformed data into a database using the `DatabaseLoader` class.
- **Docker Support**: Easily deploy the application using Docker with the provided `Dockerfile` and `docker-compose.yml`.

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/crypto-data-pipeline.git
   cd crypto-data-pipeline
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the project:
   - Update the `config/config.yaml` file with your API keys and database connection details.

4. Create the necessary database tables:
   - Run the SQL commands in `sql/create_tables.sql` to set up your database.

5. Run the data pipeline:
   ```
   python src/pipeline/main.py
   ```

## Testing

To run the unit tests, execute:
```
pytest tests/test_pipeline.py
```

## Contributing

Feel free to submit issues or pull requests to improve the project. Contributions are welcome!

## License

This project is licensed under the MIT License. See the LICENSE file for more details.