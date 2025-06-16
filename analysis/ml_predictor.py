import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import joblib
from pathlib import Path

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor

# Deep Learning
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Statistical Libraries
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

from models.enhanced_models import EnhancedInsiderTrade, BacktestResult
from utils.logging_config import logger
from config.settings import settings

class MLPredictor:
    """Advanced ML predictor with ensemble methods and deep learning"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.model_weights = {}
        self.feature_importance = {}
        
        # Model configurations
        self.model_configs = {
            'xgboost': {
                'n_estimators': 1000,
                'max_depth': 6,
                'learning_rate': 0.01,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            },
            'lightgbm': {
                'n_estimators': 1000,
                'max_depth': 6,
                'learning_rate': 0.01,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'verbose': -1
            },
            'catboost': {
                'iterations': 1000,
                'depth': 6,
                'learning_rate': 0.01,
                'random_state': 42,
                'verbose': False
            },
            'random_forest': {
                'n_estimators': 500,
                'max_depth': 10,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42
            }
        }
        
        # Feature engineering parameters
        self.lookback_periods = [1, 3, 5, 10, 20, 50]
        self.technical_periods = [5, 10, 14, 20, 50, 200]
        
    def prepare_features(self, data: pd.DataFrame, target_days: int = 1) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare comprehensive feature set for ML models"""
        
        try:
            if len(data) < 100:
                raise ValueError("Insufficient data for feature preparation")
            
            features_list = []
            
            # Ensure required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required_cols):
                data.columns = [col.lower() for col in data.columns]
            
            # Price-based features
            features_list.extend(self._create_price_features(data))
            
            # Technical indicators
            features_list.extend(self._create_technical_features(data))
            
            # Volume features
            features_list.extend(self._create_volume_features(data))
            
            # Volatility features
            features_list.extend(self._create_volatility_features(data))
            
            # Momentum features
            features_list.extend(self._create_momentum_features(data))
            
            # Pattern features
            features_list.extend(self._create_pattern_features(data))
            
            # Market microstructure features
            features_list.extend(self._create_microstructure_features(data))
            
            # Combine all features
            feature_matrix = np.column_stack(features_list)
            
            # Create target variable (future returns)
            returns = data['close'].pct_change(target_days).shift(-target_days)
            
            # Remove NaN values
            valid_indices = ~(np.isnan(feature_matrix).any(axis=1) | np.isnan(returns))
            feature_matrix = feature_matrix[valid_indices]
            target = returns[valid_indices].values
            
            logger.info(f"Prepared {feature_matrix.shape[1]} features for {len(feature_matrix)} samples")
            return feature_matrix, target
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            raise
    
    def _create_price_features(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Create price-based features"""
        features = []
        close = data['close']
        
        # Returns for different periods
        for period in self.lookback_periods:
            if len(data) > period:
                returns = close.pct_change(period)
                features.append(returns.fillna(0).values)
        
        # Log returns
        log_returns = np.log(close / close.shift(1))
        features.append(log_returns.fillna(0).values)
        
        # Price ratios
        features.append((close / data['open']).fillna(1).values)
        features.append((data['high'] / data['low']).fillna(1).values)
        features.append(((data['high'] + data['low']) / 2 / close).fillna(1).values)
        
        return features
    
    def _create_technical_features(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Create technical indicator features"""
        features = []
        close = data['close']
        high = data['high']
        low = data['low']
        
        # Moving averages
        for period in self.technical_periods:
            if len(data) > period:
                sma = close.rolling(period).mean()
                ema = close.ewm(span=period).mean()
                
                features.append((close / sma).fillna(1).values)
                features.append((close / ema).fillna(1).values)
                features.append((sma.diff() / sma).fillna(0).values)
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        features.append(rsi.fillna(50).values)
        
        # MACD
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        features.append(macd.fillna(0).values)
        features.append(signal.fillna(0).values)
        features.append((macd - signal).fillna(0).values)
        
        # Bollinger Bands
        for period in [10, 20, 50]:
            if len(data) > period:
                sma = close.rolling(period).mean()
                std = close.rolling(period).std()
                upper = sma + (std * 2)
                lower = sma - (std * 2)
                
                features.append(((close - lower) / (upper - lower)).fillna(0.5).values)
                features.append((std / sma).fillna(0).values)
        
        # Stochastic Oscillator
        for period in [14, 21]:
            if len(data) > period:
                lowest_low = low.rolling(period).min()
                highest_high = high.rolling(period).max()
                k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
                features.append(k_percent.fillna(50).values)
        
        # Williams %R
        for period in [14, 21]:
            if len(data) > period:
                highest_high = high.rolling(period).max()
                lowest_low = low.rolling(period).min()
                williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
                features.append(williams_r.fillna(-50).values)
        
        return features
    
    def _create_volume_features(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Create volume-based features"""
        features = []
        volume = data['volume']
        close = data['close']
        
        # Volume ratios
        for period in [5, 10, 20]:
            if len(data) > period:
                vol_sma = volume.rolling(period).mean()
                features.append((volume / vol_sma).fillna(1).values)
        
        # Price-Volume features
        pv = close * volume
        for period in [5, 10, 20]:
            if len(data) > period:
                pv_sma = pv.rolling(period).mean()
                features.append((pv / pv_sma).fillna(1).values)
        
        # On-Balance Volume
        obv = (volume * ((close > close.shift()).astype(int) * 2 - 1)).cumsum()
        for period in [10, 20]:
            if len(data) > period:
                obv_sma = obv.rolling(period).mean()
                features.append((obv / obv_sma).fillna(1).values)
        
        # Volume Rate of Change
        for period in [5, 10]:
            if len(data) > period:
                vol_roc = volume.pct_change(period)
                features.append(vol_roc.fillna(0).values)
        
        return features
    
    def _create_volatility_features(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Create volatility-based features"""
        features = []
        close = data['close']
        high = data['high']
        low = data['low']
        
        # Historical volatility
        returns = close.pct_change()
        for period in [5, 10, 20, 50]:
            if len(data) > period:
                vol = returns.rolling(period).std()
                features.append(vol.fillna(0).values)
        
        # True Range and ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        for period in [14, 21]:
            if len(data) > period:
                atr = true_range.rolling(period).mean()
                features.append(atr.fillna(0).values)
                features.append((true_range / atr).fillna(1).values)
        
        # Garman-Klass volatility
        gk_vol = np.log(high/low) * np.log(high/low) - (2*np.log(2)-1) * np.log(close/data['open']) * np.log(close/data['open'])
        for period in [10, 20]:
            if len(data) > period:
                gk_vol_ma = gk_vol.rolling(period).mean()
                features.append(gk_vol_ma.fillna(0).values)
        
        return features
    
    def _create_momentum_features(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Create momentum-based features"""
        features = []
        close = data['close']
        
        # Rate of Change
        for period in [1, 3, 5, 10, 20]:
            if len(data) > period:
                roc = close.pct_change(period)
                features.append(roc.fillna(0).values)
        
        # Momentum
        for period in [10, 20]:
            if len(data) > period:
                momentum = close / close.shift(period)
                features.append(momentum.fillna(1).values)
        
        # Acceleration (second derivative)
        returns = close.pct_change()
        acceleration = returns.diff()
        features.append(acceleration.fillna(0).values)
        
        # Relative strength compared to moving average
        for period in [20, 50]:
            if len(data) > period:
                sma = close.rolling(period).mean()
                relative_strength = (close - sma) / sma
                features.append(relative_strength.fillna(0).values)
        
        return features
    
    def _create_pattern_features(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Create pattern recognition features"""
        features = []
        open_price = data['open']
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Candlestick patterns (simplified)
        body = abs(close - open_price)
        upper_shadow = high - np.maximum(close, open_price)
        lower_shadow = np.minimum(close, open_price) - low
        
        # Doji pattern
        doji = (body / (high - low) < 0.1).astype(int)
        features.append(doji.fillna(0).values)
        
        # Hammer pattern
        hammer = ((lower_shadow > 2 * body) & (upper_shadow < 0.1 * body)).astype(int)
        features.append(hammer.fillna(0).values)
        
        # Shooting star pattern
        shooting_star = ((upper_shadow > 2 * body) & (lower_shadow < 0.1 * body)).astype(int)
        features.append(shooting_star.fillna(0).values)
        
        # Gap features
        gap_up = ((open_price > close.shift()) & (low > close.shift())).astype(int)
        gap_down = ((open_price < close.shift()) & (high < close.shift())).astype(int)
        features.append(gap_up.fillna(0).values)
        features.append(gap_down.fillna(0).values)
        
        # Higher highs and lower lows
        for period in [5, 10]:
            if len(data) > period:
                higher_high = (high > high.rolling(period).max().shift()).astype(int)
                lower_low = (low < low.rolling(period).min().shift()).astype(int)
                features.append(higher_high.fillna(0).values)
                features.append(lower_low.fillna(0).values)
        
        return features
    
    def _create_microstructure_features(self, data: pd.DataFrame) -> List[np.ndarray]:
        """Create market microstructure features"""
        features = []
        open_price = data['open']
        high = data['high']
        low = data['low']
        close = data['close']
        volume = data['volume']
        
        # Bid-Ask spread proxy
        spread_proxy = (high - low) / close
        features.append(spread_proxy.fillna(0).values)
        
        # Price impact
        price_change = close.pct_change()
        volume_change = volume.pct_change()
        price_impact = price_change / (volume_change + 1e-8)
        features.append(price_impact.fillna(0).values)
        
        # Amihud illiquidity measure
        amihud = abs(price_change) / (volume * close + 1e-8)
        for period in [5, 20]:
            if len(data) > period:
                amihud_ma = amihud.rolling(period).mean()
                features.append(amihud_ma.fillna(0).values)
        
        # Roll measure (effective spread)
        roll_measure = 2 * np.sqrt(-np.cov(price_change[1:], price_change[:-1])[0,1]) if len(price_change) > 1 else 0
        features.append(np.full(len(data), roll_measure))
        
        # Kyle's lambda (price impact coefficient)
        if len(data) > 20:
            kyle_lambda = []
            for i in range(20, len(data)):
                window_data = data.iloc[i-20:i]
                if len(window_data) > 10:
                    x = window_data['volume'].values.reshape(-1, 1)
                    y = window_data['close'].pct_change().abs().values
                    try:
                        from sklearn.linear_model import LinearRegression
                        reg = LinearRegression().fit(x[1:], y[1:])
                        kyle_lambda.append(reg.coef_[0])
                    except:
                        kyle_lambda.append(0)
                else:
                    kyle_lambda.append(0)
            
            kyle_lambda = [0] * 20 + kyle_lambda
            features.append(np.array(kyle_lambda))
        
        return features
    
    def train_ensemble_models(
        self, 
        X: np.ndarray, 
        y: np.ndarray, 
        validation_split: float = 0.2
    ) -> Dict[str, Any]:
        """Train ensemble of ML models"""
        
        try:
            logger.info("Training ensemble ML models...")
            
            # Split data for validation
            split_idx = int(len(X) * (1 - validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Scale features
            scaler = RobustScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            self.scalers['main'] = scaler
            
            # Feature selection
            selector = SelectKBest(score_func=f_regression, k=min(50, X_train.shape[1]))
            X_train_selected = selector.fit_transform(X_train_scaled, y_train)
            X_val_selected = selector.transform(X_val_scaled)
            self.feature_selectors['main'] = selector
            
            model_results = {}
            
            # Train XGBoost
            logger.info("Training XGBoost model...")
            xgb_model = xgb.XGBRegressor(**self.model_configs['xgboost'])
            xgb_model.fit(
                X_train_selected, y_train,
                eval_set=[(X_val_selected, y_val)],
                early_stopping_rounds=50,
                verbose=False
            )
            self.models['xgboost'] = xgb_model
            
            # Evaluate XGBoost
            xgb_pred = xgb_model.predict(X_val_selected)
            xgb_mse = mean_squared_error(y_val, xgb_pred)
            xgb_r2 = r2_score(y_val, xgb_pred)
            model_results['xgboost'] = {'mse': xgb_mse, 'r2': xgb_r2}
            
            # Train LightGBM
            logger.info("Training LightGBM model...")
            lgb_model = lgb.LGBMRegressor(**self.model_configs['lightgbm'])
            lgb_model.fit(
                X_train_selected, y_train,
                eval_set=[(X_val_selected, y_val)],
                callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
            )
            self.models['lightgbm'] = lgb_model
            
            # Evaluate LightGBM
            lgb_pred = lgb_model.predict(X_val_selected)
            lgb_mse = mean_squared_error(y_val, lgb_pred)
            lgb_r2 = r2_score(y_val, lgb_pred)
            model_results['lightgbm'] = {'mse': lgb_mse, 'r2': lgb_r2}
            
            # Train CatBoost
            logger.info("Training CatBoost model...")
            cat_model = CatBoostRegressor(**self.model_configs['catboost'])
            cat_model.fit(
                X_train_selected, y_train,
                eval_set=(X_val_selected, y_val),
                early_stopping_rounds=50
            )
            self.models['catboost'] = cat_model
            
            # Evaluate CatBoost
            cat_pred = cat_model.predict(X_val_selected)
            cat_mse = mean_squared_error(y_val, cat_pred)
            cat_r2 = r2_score(y_val, cat_pred)
            model_results['catboost'] = {'mse': cat_mse, 'r2': cat_r2}
            
            # Train Random Forest
            logger.info("Training Random Forest model...")
            rf_model = RandomForestRegressor(**self.model_configs['random_forest'])
            rf_model.fit(X_train_selected, y_train)
            self.models['random_forest'] = rf_model
            
            # Evaluate Random Forest
            rf_pred = rf_model.predict(X_val_selected)
            rf_mse = mean_squared_error(y_val, rf_pred)
            rf_r2 = r2_score(y_val, rf_pred)
            model_results['random_forest'] = {'mse': rf_mse, 'r2': rf_r2}
            
            # Train Neural Network
            if settings.AI_PREDICTIONS_ENABLED:
                logger.info("Training Neural Network model...")
                nn_model = self._build_neural_network(X_train_selected.shape[1])
                
                early_stopping = EarlyStopping(patience=20, restore_best_weights=True)
                reduce_lr = ReduceLROnPlateau(patience=10, factor=0.5)
                
                nn_model.fit(
                    X_train_selected, y_train,
                    validation_data=(X_val_selected, y_val),
                    epochs=200,
                    batch_size=32,
                    callbacks=[early_stopping, reduce_lr],
                    verbose=0
                )
                self.models['neural_network'] = nn_model
                
                # Evaluate Neural Network
                nn_pred = nn_model.predict(X_val_selected).flatten()
                nn_mse = mean_squared_error(y_val, nn_pred)
                nn_r2 = r2_score(y_val, nn_pred)
                model_results['neural_network'] = {'mse': nn_mse, 'r2': nn_r2}
            
            # Calculate model weights based on performance
            self._calculate_model_weights(model_results)
            
            # Extract feature importance
            self._extract_feature_importance()
            
            logger.info("Ensemble model training completed")
            return model_results
            
        except Exception as e:
            logger.error(f"Error training ensemble models: {e}")
            raise
    
    def _build_neural_network(self, input_dim: int) -> keras.Model:
        """Build neural network architecture"""
        
        model = keras.Sequential([
            layers.Dense(256, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            
            layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _calculate_model_weights(self, model_results: Dict[str, Dict[str, float]]):
        """Calculate ensemble weights based on model performance"""
        
        # Use inverse MSE as weights (better models get higher weights)
        mse_values = [results['mse'] for results in model_results.values()]
        inverse_mse = [1 / (mse + 1e-8) for mse in mse_values]
        total_inverse_mse = sum(inverse_mse)
        
        model_names = list(model_results.keys())
        self.model_weights = {
            name: weight / total_inverse_mse 
            for name, weight in zip(model_names, inverse_mse)
        }
        
        logger.info(f"Model weights: {self.model_weights}")
    
    def _extract_feature_importance(self):
        """Extract feature importance from tree-based models"""
        
        importance_dict = {}
        
        # XGBoost importance
        if 'xgboost' in self.models:
            importance_dict['xgboost'] = self.models['xgboost'].feature_importances_
        
        # LightGBM importance
        if 'lightgbm' in self.models:
            importance_dict['lightgbm'] = self.models['lightgbm'].feature_importances_
        
        # CatBoost importance
        if 'catboost' in self.models:
            importance_dict['catboost'] = self.models['catboost'].feature_importances_
        
        # Random Forest importance
        if 'random_forest' in self.models:
            importance_dict['random_forest'] = self.models['random_forest'].feature_importances_
        
        # Average importance across models
        if importance_dict:
            importance_arrays = list(importance_dict.values())
            self.feature_importance['average'] = np.mean(importance_arrays, axis=0)
    
    def predict_ensemble(self, X: np.ndarray) -> Tuple[float, Dict[str, float]]:
        """Make ensemble prediction"""
        
        try:
            # Scale and select features
            if 'main' not in self.scalers:
                raise ValueError("Models not trained yet")
            
            X_scaled = self.scalers['main'].transform(X)
            X_selected = self.feature_selectors['main'].transform(X_scaled)
            
            predictions = {}
            
            # Get predictions from each model
            for model_name, model in self.models.items():
                if model_name == 'neural_network':
                    pred = model.predict(X_selected, verbose=0).flatten()[0]
                else:
                    pred = model.predict(X_selected)[0]
                predictions[model_name] = pred
            
            # Calculate weighted ensemble prediction
            ensemble_pred = sum(
                pred * self.model_weights.get(model_name, 0)
                for model_name, pred in predictions.items()
            )
            
            return ensemble_pred, predictions
            
        except Exception as e:
            logger.error(f"Error making ensemble prediction: {e}")
            return 0.0, {}
    
    def predict_price_movement(
        self, 
        data: pd.DataFrame, 
        days_ahead: List[int] = [1, 7, 30]
    ) -> Dict[int, Dict[str, float]]:
        """Predict price movements for multiple time horizons"""
        
        predictions = {}
        
        try:
            for days in days_ahead:
                # Prepare features for this time horizon
                X, _ = self.prepare_features(data, target_days=days)
                
                if len(X) == 0:
                    continue
                
                # Use the most recent data point
                X_latest = X[-1:].reshape(1, -1)
                
                # Make prediction
                ensemble_pred, individual_preds = self.predict_ensemble(X_latest)
                
                # Convert to probability
                prob_up = self._convert_to_probability(ensemble_pred)
                
                predictions[days] = {
                    'return_prediction': ensemble_pred,
                    'probability_up': prob_up,
                    'individual_predictions': individual_preds
                }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting price movements: {e}")
            return {}
    
    def _convert_to_probability(self, return_prediction: float) -> float:
        """Convert return prediction to probability of positive movement"""
        
        # Use sigmoid function to convert to probability
        # Adjust the scaling factor based on typical return volatility
        scaling_factor = 10  # Adjust based on your data
        probability = 1 / (1 + np.exp(-return_prediction * scaling_factor))
        
        return max(0.1, min(0.9, probability))  # Bound between 10% and 90%
    
    def save_models(self, model_dir: Path):
        """Save trained models to disk"""
        
        try:
            model_dir.mkdir(exist_ok=True)
            
            # Save sklearn-compatible models
            for model_name in ['xgboost', 'lightgbm', 'catboost', 'random_forest']:
                if model_name in self.models:
                    joblib.dump(
                        self.models[model_name], 
                        model_dir / f"{model_name}_model.pkl"
                    )
            
            # Save neural network
            if 'neural_network' in self.models:
                self.models['neural_network'].save(model_dir / "neural_network_model.h5")
            
            # Save scalers and selectors
            joblib.dump(self.scalers, model_dir / "scalers.pkl")
            joblib.dump(self.feature_selectors, model_dir / "feature_selectors.pkl")
            joblib.dump(self.model_weights, model_dir / "model_weights.pkl")
            joblib.dump(self.feature_importance, model_dir / "feature_importance.pkl")
            
            logger.info(f"Models saved to {model_dir}")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self, model_dir: Path):
        """Load trained models from disk"""
        
        try:
            # Load sklearn-compatible models
            for model_name in ['xgboost', 'lightgbm', 'catboost', 'random_forest']:
                model_path = model_dir / f"{model_name}_model.pkl"
                if model_path.exists():
                    self.models[model_name] = joblib.load(model_path)
            
            # Load neural network
            nn_path = model_dir / "neural_network_model.h5"
            if nn_path.exists():
                self.models['neural_network'] = keras.models.load_model(nn_path)
            
            # Load scalers and selectors
            scaler_path = model_dir / "scalers.pkl"
            if scaler_path.exists():
                self.scalers = joblib.load(scaler_path)
            
            selector_path = model_dir / "feature_selectors.pkl"
            if selector_path.exists():
                self.feature_selectors = joblib.load(selector_path)
            
            weights_path = model_dir / "model_weights.pkl"
            if weights_path.exists():
                self.model_weights = joblib.load(weights_path)
            
            importance_path = model_dir / "feature_importance.pkl"
            if importance_path.exists():
                self.feature_importance = joblib.load(importance_path)
            
            logger.info(f"Models loaded from {model_dir}")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def get_feature_importance_report(self) -> Dict[str, Any]:
        """Generate feature importance report"""
        
        report = {
            'top_features': [],
            'importance_by_category': {},
            'model_performance': self.model_weights
        }
        
        try:
            if 'average' in self.feature_importance:
                importance = self.feature_importance['average']
                
                # Get top features (would need feature names)
                top_indices = np.argsort(importance)[-20:][::-1]
                report['top_features'] = [
                    {'index': int(idx), 'importance': float(importance[idx])}
                    for idx in top_indices
                ]
                
                # Categorize features (simplified)
                categories = {
                    'price_features': importance[:20],
                    'technical_features': importance[20:60],
                    'volume_features': importance[60:80],
                    'volatility_features': importance[80:100],
                    'momentum_features': importance[100:120],
                    'pattern_features': importance[120:140],
                    'microstructure_features': importance[140:]
                }
                
                report['importance_by_category'] = {
                    cat: float(np.mean(values)) if len(values) > 0 else 0.0
                    for cat, values in categories.items()
                }
        
        except Exception as e:
            logger.error(f"Error generating feature importance report: {e}")
        
        return report