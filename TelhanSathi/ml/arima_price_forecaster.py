"""
ARIMA Price Forecaster for Indian Oilseeds Commodities
Predicts commodity prices for profit simulator
"""

import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# Suppress ARIMA convergence warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=ConvergenceWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArimaPriceForecaster:
    """
    ARIMA-based price forecaster for commodities across different markets.
    Trains market-specific models for each commodity.
    """
    
    def __init__(self, data_path=None, model_dir=None):
        """
        Initialize the forecaster.
        
        Args:
            data_path (str): Path to the CSV dataset
            model_dir (str): Directory to save trained models
        """
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), 'datasets', 'indian_oilseeds_prices.csv')
        
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), 'models')
        
        self.data_path = data_path
        self.model_dir = model_dir
        self.df = None
        self.models = {}  # Store trained models: {market}_{commodity} -> model
        self.arima_params = {}  # Store ARIMA parameters: {market}_{commodity} -> (p, d, q)
        
        # Create model directory if it doesn't exist
        Path(self.model_dir).mkdir(parents=True, exist_ok=True)
        
        self._load_data()
    
    def _load_data(self):
        """Load and preprocess the dataset."""
        logger.info(f"Loading data from {self.data_path}")
        self.df = pd.read_csv(self.data_path)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df = self.df.sort_values('Date').reset_index(drop=True)
        logger.info(f"Data loaded: {len(self.df)} records")
    
    def get_unique_markets(self):
        """Get list of unique markets in dataset."""
        if self.df is None:
            self._load_data()
        return sorted(self.df['Market'].unique().tolist())
    
    def get_unique_commodities(self):
        """Get list of unique commodities in dataset."""
        if self.df is None:
            self._load_data()
        return sorted(self.df['Commodity'].unique().tolist())
    
    def get_markets_for_commodity(self, commodity):
        """Get markets that have data for a specific commodity."""
        if self.df is None:
            self._load_data()
        markets = self.df[self.df['Commodity'] == commodity]['Market'].unique().tolist()
        return sorted(markets)
    
    def get_commodities_for_market(self, market):
        """Get commodities available in a specific market."""
        if self.df is None:
            self._load_data()
        commodities = self.df[self.df['Market'] == market]['Commodity'].unique().tolist()
        return sorted(commodities)
    
    def _get_time_series_data(self, market, commodity):
        """Extract time series data for a specific market and commodity."""
        data = self.df[(self.df['Market'] == market) & (self.df['Commodity'] == commodity)].copy()
        data = data.sort_values('Date')
        
        # Set date as index
        data.set_index('Date', inplace=True)
        
        # Resample to daily frequency (fill missing dates with forward fill)
        data = data.asfreq('D')
        
        # Forward fill missing prices (use new pandas API)
        price_series = data['Price'].ffill().bfill()
        
        return price_series
    
    def _find_arima_parameters(self, price_series, max_p=5, max_d=2, max_q=5):
        """
        Find optimal ARIMA parameters using AIC.
        
        Args:
            price_series: Time series data
            max_p, max_d, max_q: Maximum values to test
            
        Returns:
            Tuple of (p, d, q)
        """
        best_aic = np.inf
        best_params = (1, 1, 1)
        
        logger.info("Finding optimal ARIMA parameters...")
        
        for p in range(0, max_p + 1):
            for d in range(0, max_d + 1):
                for q in range(0, max_q + 1):
                    try:
                        model = ARIMA(price_series, order=(p, d, q))
                        results = model.fit()
                        if results.aic < best_aic:
                            best_aic = results.aic
                            best_params = (p, d, q)
                        logger.debug(f"ARIMA{(p, d, q)} - AIC: {results.aic:.2f}")
                    except:
                        continue
        
        logger.info(f"Best parameters: ARIMA{best_params} with AIC: {best_aic:.2f}")
        return best_params
    
    def train_model(self, market, commodity, order=None):
        """
        Train ARIMA model for a specific market and commodity.
        
        Args:
            market (str): Market name
            commodity (str): Commodity name
            order (tuple): Optional (p, d, q) parameters. If None, will use default (1, 1, 1).
            
        Returns:
            dict: Training metrics including MAE and RMSE
        """
        logger.info(f"Training model for {market} - {commodity}")
        
        # Get time series data
        price_series = self._get_time_series_data(market, commodity)
        
        if len(price_series) < 50:
            logger.warning(f"Insufficient data for {market} - {commodity} ({len(price_series)} points)")
            return None
        
        # Use default parameters (works well for commodity prices)
        if order is None:
            order = (1, 1, 1)
        
        try:
            # Train model on full dataset
            model = ARIMA(price_series, order=order)
            results = model.fit()
            
            # Store model and parameters
            model_key = f"{market}_{commodity}"
            self.models[model_key] = results
            self.arima_params[model_key] = order
            
            # Calculate metrics
            predictions = results.fittedvalues
            mae = mean_absolute_error(price_series[len(order) * 2:], predictions[len(order) * 2:])
            rmse = np.sqrt(mean_squared_error(price_series[len(order) * 2:], predictions[len(order) * 2:]))
            
            metrics = {
                'market': market,
                'commodity': commodity,
                'order': order,
                'aic': results.aic,
                'bic': results.bic,
                'mae': mae,
                'rmse': rmse,
                'data_points': len(price_series)
            }
            
            logger.info(f"✓ {market} - {commodity}: MAE={mae:.2f}, RMSE={rmse:.2f}")
            return metrics
        except Exception as e:
            logger.error(f"Failed to train {market} - {commodity}: {str(e)}")
            return None
    
    def train_all_combinations(self):
        """Train models for all market-commodity combinations."""
        markets = self.get_unique_markets()
        commodities = self.get_unique_commodities()
        
        all_metrics = []
        
        for market in markets:
            for commodity in commodities:
                metrics = self.train_model(market, commodity)
                if metrics:
                    all_metrics.append(metrics)
        
        logger.info(f"Training complete! {len(all_metrics)} models trained successfully")
        return all_metrics
    
    def forecast(self, market, commodity, periods=30):
        """
        Forecast future prices for a market-commodity combination.
        
        Args:
            market (str): Market name
            commodity (str): Commodity name
            periods (int): Number of days to forecast
            
        Returns:
            dict: Contains forecast values, confidence intervals, and last actual price
        """
        model_key = f"{market}_{commodity}"
        
        if model_key not in self.models:
            logger.error(f"Model not found for {market} - {commodity}")
            return None
        
        model = self.models[model_key]
        
        # Get forecast
        forecast_result = model.get_forecast(steps=periods)
        forecast_df = forecast_result.conf_int()
        forecast_df['forecast'] = forecast_result.predicted_mean
        
        # Get last actual price
        price_series = self._get_time_series_data(market, commodity)
        last_price = price_series.iloc[-1]
        
        return {
            'market': market,
            'commodity': commodity,
            'last_price': float(last_price),
            'forecast': forecast_df['forecast'].tolist(),
            'lower_ci': forecast_df.iloc[:, 0].tolist(),
            'upper_ci': forecast_df.iloc[:, 1].tolist(),
            'periods': periods
        }
    
    def save_models(self):
        """Save all trained models to disk."""
        for model_key, model in self.models.items():
            model_path = os.path.join(self.model_dir, f"{model_key}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Model saved: {model_path}")
        
        # Save parameters
        params_path = os.path.join(self.model_dir, 'arima_params.pkl')
        with open(params_path, 'wb') as f:
            pickle.dump(self.arima_params, f)
        logger.info(f"Parameters saved: {params_path}")
    
    def load_models(self):
        """Load trained models from disk."""
        params_path = os.path.join(self.model_dir, 'arima_params.pkl')
        if os.path.exists(params_path):
            with open(params_path, 'rb') as f:
                self.arima_params = pickle.load(f)
        
        # Load individual models
        for model_key in self.arima_params.keys():
            model_path = os.path.join(self.model_dir, f"{model_key}.pkl")
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.models[model_key] = pickle.load(f)
        
        logger.info(f"Loaded {len(self.models)} models from disk")


def initialize_and_train_forecaster():
    """
    Utility function to initialize and train all models.
    Call this once to train and save all models.
    """
    forecaster = ArimaPriceForecaster()
    metrics_list = forecaster.train_all_combinations()
    forecaster.save_models()
    
    # Print summary
    metrics_df = pd.DataFrame(metrics_list)
    logger.info("\nTraining Summary:")
    logger.info(metrics_df.to_string())
    
    return forecaster


def get_forecaster():
    """
    Get a forecaster instance with pre-trained models.
    If models don't exist, train them first.
    """
    forecaster = ArimaPriceForecaster()
    
    # Try to load existing models
    params_path = os.path.join(forecaster.model_dir, 'arima_params.pkl')
    if os.path.exists(params_path):
        logger.info("Loading pre-trained models...")
        forecaster.load_models()
    else:
        logger.info("No pre-trained models found. Training new models...")
        initialize_and_train_forecaster()
        forecaster.load_models()
    
    return forecaster


if __name__ == "__main__":
    # Example usage
    initialize_and_train_forecaster()
    
    # Test forecast
    forecaster = get_forecaster()
    forecast = forecaster.forecast("Delhi", "Soybean", periods=30)
    
    if forecast:
        print("\nForecast Example:")
        print(f"Market: {forecast['market']}")
        print(f"Commodity: {forecast['commodity']}")
        print(f"Last Price: ₹{forecast['last_price']:.2f}")
        print(f"Next 5 days forecast (average): ₹{np.mean(forecast['forecast'][:5]):.2f}")
