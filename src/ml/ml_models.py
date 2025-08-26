"""
Modelos de Machine Learning para previsão de preços de criptomoedas
"""

import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class CryptoPricePredictor:
    def __init__(self, db_path="../crypto_warehouse.db"):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.feature_columns = [
            'price_1d_ago', 'price_7d_ago', 'price_30d_ago',
            'volume_avg_7d', 'volume_avg_30d', 'volatility_7d', 'volatility_30d',
            'rsi_14', 'macd_signal_strength', 'trend_direction',
            'support_level', 'resistance_level'
        ]
    
    def prepare_data(self, coin_id="bitcoin", target_days=1):
        """Prepara dados para treinamento"""
        conn = sqlite3.connect(self.db_path)
        
        # Buscar dados ML
        df = pd.read_sql_query('''
            SELECT * FROM ml_features 
            WHERE coin_id = ?
            ORDER BY date
        ''', conn, params=(coin_id,))
        conn.close()
        
        if df.empty:
            raise ValueError(f"Nenhum dado encontrado para {coin_id}")
        
        # Criar target (preço futuro)
        df[f'target_price_{target_days}d'] = df['price_current'].shift(-target_days)
        
        # Remover linhas com NaN
        df = df.dropna()
        
        # Separar features e target
        X = df[self.feature_columns]
        y = df[f'target_price_{target_days}d']
        
        return X, y, df
    
    def train_models(self, coin_id="bitcoin", target_days=1):
        """Treina múltiplos modelos"""
        print(f"🤖 Treinando modelos para {coin_id} (previsão {target_days} dias)...")
        
        # Preparar dados
        X, y, df = self.prepare_data(coin_id, target_days)
        
        if len(X) < 50:
            print(f"❌ Dados insuficientes ({len(X)} amostras)")
            return False
        
        # Split dos dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Normalizar features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Modelos para treinar
        models_to_train = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        
        results = {}
        
        for name, model in models_to_train.items():
            print(f"  Treinando {name}...")
            
            # Treinar modelo
            if name == 'linear_regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Métricas
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Cross-validation
            if name == 'linear_regression':
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
            
            results[name] = {
                'model': model,
                'mae': mae,
                'mse': mse,
                'r2': r2,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'predictions': y_pred,
                'actual': y_test
            }
            
            print(f"    MAE: {mae:.4f}, R²: {r2:.4f}, CV: {cv_scores.mean():.4f}±{cv_scores.std():.4f}")
        
        # Selecionar melhor modelo
        best_model_name = max(results.keys(), key=lambda k: results[k]['r2'])
        best_model = results[best_model_name]['model']
        
        print(f"  🏆 Melhor modelo: {best_model_name}")
        
        # Salvar modelo e scaler
        model_key = f"{coin_id}_{target_days}d"
        self.models[model_key] = best_model
        self.scalers[model_key] = scaler
        
        # Salvar em arquivo
        os.makedirs('models', exist_ok=True)
        joblib.dump(best_model, f'models/{model_key}_model.pkl')
        joblib.dump(scaler, f'models/{model_key}_scaler.pkl')
        
        return results
    
    def predict_price(self, coin_id="bitcoin", target_days=1, days_ahead=1):
        """Faz previsão de preço"""
        model_key = f"{coin_id}_{target_days}d"
        
        # Carregar modelo se não estiver em memória
        if model_key not in self.models:
            try:
                self.models[model_key] = joblib.load(f'models/{model_key}_model.pkl')
                self.scalers[model_key] = joblib.load(f'models/{model_key}_scaler.pkl')
            except FileNotFoundError:
                print(f"❌ Modelo não encontrado para {coin_id}. Treine primeiro!")
                return None
        
        # Buscar dados mais recentes
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM ml_features 
            WHERE coin_id = ?
            ORDER BY date DESC
            LIMIT ?
        ''', conn, params=(coin_id, days_ahead))
        conn.close()
        
        if df.empty:
            print(f"❌ Dados não encontrados para {coin_id}")
            return None
        
        # Preparar features
        X = df[self.feature_columns].iloc[0:1]  # Dados mais recentes
        
        # Fazer previsão
        model = self.models[model_key]
        scaler = self.scalers[model_key]
        
        # Se for regressão linear, usar dados normalizados
        if isinstance(model, LinearRegression):
            X_scaled = scaler.transform(X)
            prediction = model.predict(X_scaled)[0]
        else:
            prediction = model.predict(X)[0]
        
        current_price = df['price_current'].iloc[0]
        price_change = ((prediction - current_price) / current_price) * 100
        
        return {
            'coin_id': coin_id,
            'current_price': current_price,
            'predicted_price': prediction,
            'price_change_percent': price_change,
            'prediction_date': datetime.now().strftime('%Y-%m-%d'),
            'target_date': (datetime.now() + timedelta(days=target_days)).strftime('%Y-%m-%d'),
            'confidence': self._calculate_confidence(model_key, X)
        }
    
    def _calculate_confidence(self, model_key, X):
        """Calcula confiança da previsão (simplificado)"""
        model = self.models[model_key]
        
        # Para Random Forest, usar variance das árvores
        if isinstance(model, RandomForestRegressor):
            predictions = [tree.predict(X)[0] for tree in model.estimators_]
            variance = np.var(predictions)
            confidence = max(0, min(1, 1 - (variance / np.mean(predictions))))
            return confidence
        
        # Para outros modelos, retornar confiança média
        return 0.75
    
    def batch_predict(self, coins=['bitcoin', 'ethereum'], target_days=[1, 7]):
        """Faz previsões em lote"""
        predictions = []
        
        for coin in coins:
            for days in target_days:
                prediction = self.predict_price(coin, days)
                if prediction:
                    predictions.append(prediction)
        
        return predictions
    
    def save_predictions_to_db(self, predictions):
        """Salva previsões no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for pred in predictions:
            cursor.execute('''
                INSERT INTO ml_predictions 
                (coin_id, prediction_date, target_date, predicted_price, confidence_score, model_version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (pred['coin_id'], pred['prediction_date'], pred['target_date'],
                  pred['predicted_price'], pred['confidence'], 'v1.0'))
        
        conn.commit()
        conn.close()
        print(f"✅ {len(predictions)} previsões salvas no banco")
    
    def evaluate_model_performance(self, coin_id="bitcoin", target_days=1):
        """Avalia performance do modelo"""
        conn = sqlite3.connect(self.db_path)
        
        # Buscar previsões com resultados reais
        df = pd.read_sql_query('''
            SELECT p.*, h.price as actual_price
            FROM ml_predictions p
            JOIN historical_prices h ON p.coin_id = h.coin_id AND p.target_date = h.date
            WHERE p.coin_id = ? AND p.predicted_price IS NOT NULL
        ''', conn, params=(coin_id,))
        
        conn.close()
        
        if df.empty:
            print(f"❌ Nenhuma previsão com resultado real encontrada para {coin_id}")
            return None
        
        # Calcular métricas
        mae = mean_absolute_error(df['actual_price'], df['predicted_price'])
        mse = mean_squared_error(df['actual_price'], df['predicted_price'])
        r2 = r2_score(df['actual_price'], df['predicted_price'])
        
        # Precisão direcional (acertou a direção da mudança?)
        df['actual_change'] = (df['actual_price'] - df['predicted_price']) > 0
        df['predicted_change'] = df['predicted_price'] > 0  # Simplificado
        directional_accuracy = (df['actual_change'] == df['predicted_change']).mean()
        
        return {
            'coin_id': coin_id,
            'mae': mae,
            'mse': mse,
            'r2': r2,
            'directional_accuracy': directional_accuracy,
            'total_predictions': len(df)
        }

def main():
    """Função principal para treinar modelos"""
    predictor = CryptoPricePredictor()
    
    # Moedas para treinar
    coins = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana']
    target_days = [1, 7]  # Previsões para 1 e 7 dias
    
    print("🤖 TREINAMENTO DE MODELOS ML")
    print("=" * 50)
    
    for coin in coins:
        for days in target_days:
            try:
                results = predictor.train_models(coin, days)
                if results:
                    print(f"✅ Modelo treinado: {coin} ({days} dias)")
            except Exception as e:
                print(f"❌ Erro ao treinar {coin} ({days} dias): {e}")
    
    print("\n🔮 FAZENDO PREVISÕES")
    print("=" * 30)
    
    # Fazer previsões
    predictions = predictor.batch_predict(coins, target_days)
    
    for pred in predictions:
        print(f"{pred['coin_id']:>12}: ${pred['current_price']:>8.2f} → ${pred['predicted_price']:>8.2f} "
              f"({pred['price_change_percent']:>+6.2f}%) | Confiança: {pred['confidence']:.2f}")
    
    # Salvar previsões
    predictor.save_predictions_to_db(predictions)
    
    print(f"\n🎉 Modelos treinados e previsões salvas!")
    print(f"📁 Modelos salvos em: {os.path.abspath('models')}")

if __name__ == "__main__":
    main()
