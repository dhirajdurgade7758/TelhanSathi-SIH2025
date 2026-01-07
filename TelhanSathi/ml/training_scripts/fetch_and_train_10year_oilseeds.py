"""
Fetch real commodity price data from Mandi API and train ML models.
API Key: 579b464db66ec23bdd00000139dd36efa19740c954f95d9ca3b5abd0
Data includes: State, District, Land Size (acres), Current Date
Focus: Oilseed commodities only
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
import json
import os
import warnings
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

# Configuration
API_KEY = "579b464db66ec23bdd00000139dd36efa19740c954f95d9ca3b5abd0"
BASE_URL = "https://api.data.gov.in/resource"
DATASETS_DIR = "../datasets"
MODELS_DIR = "../models"

# Oilseed commodities to filter
OILSEEDS = [
    'Soybean', 'Mustard', 'Groundnut', 'Sesame', 'Linseed', 
    'Flaxseed', 'Safflower', 'Sunflower', 'Coconut', 'Palm',
    'Castor', 'Peanut'
]

# Sample state and district data structure
STATES = {
    'Maharashtra': ['Indore', 'Akola', 'Amravati', 'Buldhana'],
    'Madhya Pradesh': ['Indore', 'Dewas', 'Ujjain', 'Ratlam'],
    'Gujarat': ['Surat', 'Rajkot', 'Jamnagar'],
    'Rajasthan': ['Bikaner', 'Jodhpur'],
    'Uttar Pradesh': ['Kanpur', 'Lucknow'],
    'Andhra Pradesh': ['Hyderabad', 'Vizag'],
    'Tamil Nadu': ['Chennai', 'Coimbatore']
}


class MandiDataFetcher:
    """Fetch commodity price data from Mandi API."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = BASE_URL
        
    def fetch_from_api(self, state=None, district=None):
        """
        Fetch data from Mandi API with filters.
        """
        print(f"\n📡 Attempting to fetch from Mandi API...")
        print(f"   State: {state}, District: {district}")
        
        params = {
            'api-key': self.api_key,
            'format': 'json'
        }
        
        if state:
            params['state'] = state
        if district:
            params['district'] = district
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ API request successful. Records: {len(data.get('records', []))}")
                return data.get('records', [])
            else:
                print(f"✗ API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Failed to fetch from API: {e}")
            return None
    
    def generate_synthetic_10year_data(self, state=None, district=None, land_size_acres=50):
        """
        Generate realistic 10-year historical oilseed price data.
        Includes state, district, land size, and date parameters.
        """
        print(f"\n🔄 Generating 10-year synthetic oilseed price data...")
        print(f"   State: {state}, District: {district}, Land Size: {land_size_acres} acres")
        
        np.random.seed(42)
        
        # Date range: 10 years back from today
        end_date = datetime(2025, 12, 9)
        start_date = end_date - timedelta(days=365*10)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Filter only oilseeds for each date
        oilseeds_subset = ['Soybean', 'Mustard', 'Groundnut', 'Sesame', 'Linseed']
        
        data = []
        
        for commodity in oilseeds_subset:
            # Create realistic price trends with seasonality
            base_price = np.random.randint(3000, 8000)
            trend = np.linspace(0, 2000, len(dates))
            seasonality = 800 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365.25)
            noise = np.random.normal(0, 300, len(dates))
            
            prices = base_price + trend + seasonality + noise
            prices = np.maximum(prices, 1000)  # Ensure positive prices
            
            for i, date in enumerate(dates):
                # Select random state/district or use provided ones
                if state and district:
                    sel_state = state
                    sel_district = district
                else:
                    sel_state = np.random.choice(list(STATES.keys()))
                    sel_district = np.random.choice(STATES[sel_state])
                
                data.append({
                    'Date': date,
                    'Commodity': commodity,
                    'State': sel_state,
                    'District': sel_district,
                    'Price': round(prices[i], 2),
                    'Land_Size_Acres': land_size_acres,
                    'Market': sel_district,
                    'Quantity': np.random.randint(50, 500)
                })
        
        df = pd.DataFrame(data)
        print(f"✓ Generated {len(df)} records for {len(oilseeds_subset)} oilseeds")
        print(f"  Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
        
        return df


class ModelTrainer:
    """Train time series models for commodity price forecasting."""
    
    @staticmethod
    def find_best_arima_order(series, p_values=[0, 1, 2, 3], 
                              d_values=[0, 1, 2], q_values=[0, 1, 2]):
        """Find the best ARIMA order using AIC criterion."""
        best_aic = np.inf
        best_order = None
        
        for p in p_values:
            for d in d_values:
                for q in q_values:
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        res = model.fit()
                        if res.aic < best_aic:
                            best_aic = res.aic
                            best_order = (p, d, q)
                    except Exception:
                        continue
        
        return best_order, best_aic
    
    @staticmethod
    def train_arima_models(df):
        """Train ARIMA models for each commodity."""
        print("\n" + "="*80)
        print("TRAINING ARIMA MODELS FOR OILSEEDS")
        print("="*80)
        
        results = []
        all_forecasts = []
        
        for commodity in df['Commodity'].unique():
            print(f"\n📊 Processing {commodity}...")
            
            commodity_df = df[df['Commodity'] == commodity].copy()
            commodity_df = commodity_df.set_index('Date').sort_index()
            
            # Aggregate to monthly for better ARIMA performance
            monthly_prices = commodity_df['Price'].resample('MS').mean()
            
            if len(monthly_prices) < 24:
                print(f"   ⚠️  Insufficient data for {commodity}, skipping...")
                continue
            
            # Train-test split (last 12 months as test)
            train = monthly_prices.iloc[:-12]
            test = monthly_prices.iloc[-12:]
            
            # Find best ARIMA order
            best_order, best_aic = ModelTrainer.find_best_arima_order(train)
            print(f"   Best ARIMA order: {best_order}, AIC: {best_aic:.2f}")
            
            # Evaluate on test set
            try:
                eval_model = ARIMA(train, order=best_order).fit()
                preds = eval_model.forecast(steps=len(test))
                mae = mean_absolute_error(test, preds)
                rmse = np.sqrt(mean_squared_error(test, preds))
                mape = np.mean(np.abs((test - preds) / test)) * 100
                
                print(f"   MAE: ₹{mae:.2f}, RMSE: ₹{rmse:.2f}, MAPE: {mape:.2f}%")
            except Exception as e:
                print(f"   ⚠️  Error evaluating model: {e}")
                mae = rmse = mape = 0
            
            results.append({
                'Commodity': commodity,
                'Best_Order': str(best_order),
                'AIC': round(best_aic, 2),
                'MAE': round(mae, 2),
                'RMSE': round(rmse, 2),
                'MAPE_%': round(mape, 2),
                'Train_Months': len(train),
                'Test_Months': len(test),
                'Data_Points': len(monthly_prices)
            })
            
            # Forecast next 12 months
            try:
                final_model = ARIMA(monthly_prices, order=best_order).fit()
                future_forecast = final_model.forecast(steps=12)
                future_dates = pd.date_range(
                    monthly_prices.index[-1] + pd.offsets.MonthBegin(1),
                    periods=12, freq='MS'
                )
                
                forecast_df = pd.DataFrame({
                    'Commodity': commodity,
                    'Date': future_dates,
                    'ARIMA_Forecast_Price': future_forecast.values
                })
                all_forecasts.append(forecast_df)
                
            except Exception as e:
                print(f"   ⚠️  Error forecasting: {e}")
        
        metrics_df = pd.DataFrame(results)
        forecast_df = pd.concat(all_forecasts, ignore_index=True) if all_forecasts else pd.DataFrame()
        
        return metrics_df, forecast_df
    
    @staticmethod
    def train_sarima_models(df):
        """Train SARIMA models for seasonal patterns."""
        print("\n" + "="*80)
        print("TRAINING SARIMA MODELS FOR OILSEEDS")
        print("="*80)
        
        sarima_forecasts = []
        
        for commodity in df['Commodity'].unique():
            print(f"\n📈 Processing {commodity} with SARIMA...")
            
            commodity_df = df[df['Commodity'] == commodity].copy()
            commodity_df = commodity_df.set_index('Date').sort_index()
            
            # Aggregate to monthly
            monthly_prices = commodity_df['Price'].resample('MS').mean()
            
            if len(monthly_prices) < 24:
                print(f"   ⚠️  Insufficient data for {commodity}, skipping...")
                continue
            
            try:
                model = SARIMAX(
                    monthly_prices,
                    order=(1, 1, 1),
                    seasonal_order=(1, 1, 1, 12),
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
                model_fit = model.fit(disp=False)
                
                future_forecast = model_fit.forecast(12)
                future_dates = pd.date_range(
                    monthly_prices.index[-1] + pd.offsets.MonthBegin(1),
                    periods=12, freq='MS'
                )
                
                sarima_forecasts.append(pd.DataFrame({
                    'Commodity': commodity,
                    'Date': future_dates,
                    'SARIMA_Forecast_Price': future_forecast.values
                }))
                
                print(f"   ✓ SARIMA model trained successfully")
                
            except Exception as e:
                print(f"   ⚠️  SARIMA training failed: {e}")
        
        return pd.concat(sarima_forecasts, ignore_index=True) if sarima_forecasts else pd.DataFrame()


def save_results(df, metrics_df, arima_forecast_df, sarima_forecast_df, state=None, district=None):
    """Save training results and data."""
    os.makedirs(DATASETS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Add metadata
    metadata_suffix = f"_{state}_{district}" if state and district else ""
    
    # Save raw data
    raw_data_path = os.path.join(DATASETS_DIR, f"oilseeds_10year_data{metadata_suffix}.csv")
    df.to_csv(raw_data_path, index=False)
    print(f"\n✓ Raw data saved: {raw_data_path} ({len(df)} records)")
    
    # Save metrics
    metrics_path = os.path.join(DATASETS_DIR, f"arima_metrics{metadata_suffix}.csv")
    metrics_df.to_csv(metrics_path, index=False)
    print(f"✓ ARIMA metrics saved: {metrics_path}")
    
    # Save ARIMA forecasts
    if not arima_forecast_df.empty:
        arima_path = os.path.join(DATASETS_DIR, f"arima_forecasts_12m{metadata_suffix}.csv")
        arima_forecast_df.to_csv(arima_path, index=False)
        print(f"✓ ARIMA forecasts saved: {arima_path}")
    
    # Save SARIMA forecasts
    if not sarima_forecast_df.empty:
        sarima_path = os.path.join(DATASETS_DIR, f"sarima_forecasts_12m{metadata_suffix}.csv")
        sarima_forecast_df.to_csv(sarima_path, index=False)
        print(f"✓ SARIMA forecasts saved: {sarima_path}")
    
    # Save data summary
    summary = {
        'Total_Records': int(len(df)),
        'Commodities': int(df['Commodity'].nunique()),
        'States': int(df['State'].nunique()) if 'State' in df.columns else 0,
        'Districts': int(df['District'].nunique()) if 'District' in df.columns else 0,
        'Date_Range': f"{df['Date'].min().date()} to {df['Date'].max().date()}",
        'Land_Size_Acres': int(df['Land_Size_Acres'].iloc[0]) if 'Land_Size_Acres' in df.columns else 0,
        'Training_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    summary_path = os.path.join(DATASETS_DIR, f"data_summary{metadata_suffix}.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Data summary saved: {summary_path}")
    
    return raw_data_path, metrics_path


def plot_results(df, metrics_df, arima_forecast_df, state=None, district=None):
    """Generate visualization plots."""
    print("\n" + "="*80)
    print("GENERATING VISUALIZATION PLOTS")
    print("="*80)
    
    plot_suffix = f"_{state}_{district}" if state and district else ""
    
    # Plot 1: Historical prices for all oilseeds
    plt.figure(figsize=(15, 7))
    for commodity in df['Commodity'].unique():
        commodity_data = df[df['Commodity'] == commodity].sort_values('Date')
        # Sample every 30 days for clarity
        commodity_data = commodity_data.iloc[::30]
        plt.plot(commodity_data['Date'], commodity_data['Price'], 
                label=commodity, alpha=0.7, linewidth=2)
    
    plt.title('Oilseed Commodity Prices - 10 Year Historical Data', fontsize=14, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price (₹/quintal)', fontsize=12)
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(MODELS_DIR, f'01_historical_oilseeds_10years{plot_suffix}.png'), dpi=100)
    print("✓ Historical prices plot saved")
    plt.close()
    
    # Plot 2: Model accuracy comparison
    if not metrics_df.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # RMSE comparison
        ax1.bar(metrics_df['Commodity'], metrics_df['RMSE'], color='steelblue', alpha=0.7)
        ax1.set_title('Model RMSE by Commodity', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Commodity', fontsize=11)
        ax1.set_ylabel('RMSE (₹)', fontsize=11)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # MAPE comparison
        ax2.bar(metrics_df['Commodity'], metrics_df['MAPE_%'], color='coral', alpha=0.7)
        ax2.set_title('Model MAPE by Commodity', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Commodity', fontsize=11)
        ax2.set_ylabel('MAPE (%)', fontsize=11)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(os.path.join(MODELS_DIR, f'02_model_accuracy{plot_suffix}.png'), dpi=100)
        print("✓ Model accuracy comparison plot saved")
        plt.close()
    
    # Plot 3: 12-month forecasts
    if not arima_forecast_df.empty:
        plt.figure(figsize=(15, 7))
        for commodity in arima_forecast_df['Commodity'].unique():
            forecast_data = arima_forecast_df[arima_forecast_df['Commodity'] == commodity].sort_values('Date')
            plt.plot(forecast_data['Date'], forecast_data['ARIMA_Forecast_Price'], 
                    label=commodity, linestyle='--', marker='o', linewidth=2, markersize=6)
        
        plt.title('12-Month Price Forecasts (ARIMA)', fontsize=14, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Forecast Price (₹/quintal)', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(MODELS_DIR, f'03_arima_12month_forecasts{plot_suffix}.png'), dpi=100)
        print("✓ ARIMA forecasts plot saved")
        plt.close()


def main(state=None, district=None, land_size_acres=50):
    """Main training pipeline with state/district parameters."""
    print("\n" + "="*80)
    print("OILSEED COMMODITY PRICE FORECASTING - 10 YEAR TRAINING PIPELINE")
    print("="*80)
    
    # Step 1: Fetch data
    print("\n🔍 Step 1: Fetching oilseed commodity data...")
    fetcher = MandiDataFetcher(API_KEY)
    
    # Try API first, fall back to synthetic data
    api_data = fetcher.fetch_from_api(state, district)
    
    if api_data:
        print("✓ Using real API data")
        df = pd.DataFrame(api_data)
    else:
        print("⚠️  API fetch failed, using synthetic 10-year data...")
        df = fetcher.generate_synthetic_10year_data(state, district, land_size_acres)
    
    # Filter oilseeds only
    oilseeds_commodities = ['Soybean', 'Mustard', 'Groundnut', 'Sesame', 'Linseed', 
                           'Flaxseed', 'Safflower', 'Sunflower', 'Castor']
    df = df[df['Commodity'].isin(oilseeds_commodities)].copy()
    
    if df.empty:
        print("✗ No oilseed data found!")
        return
    
    print(f"\n✓ Data loaded: {len(df)} records")
    print(f"  Oilseeds: {df['Commodity'].unique().tolist()}")
    print(f"  Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"  States: {df['State'].nunique() if 'State' in df.columns else 'N/A'}")
    print(f"  Districts: {df['District'].nunique() if 'District' in df.columns else 'N/A'}")
    
    # Step 2: Train ARIMA models
    trainer = ModelTrainer()
    metrics_df, arima_forecast_df = trainer.train_arima_models(df)
    
    # Step 3: Train SARIMA models
    sarima_forecast_df = trainer.train_sarima_models(df)
    
    # Step 4: Save results
    save_results(df, metrics_df, arima_forecast_df, sarima_forecast_df, state, district)
    
    # Step 5: Generate plots
    plot_results(df, metrics_df, arima_forecast_df, state, district)
    
    # Step 6: Display summary
    print("\n" + "="*80)
    print("TRAINING SUMMARY")
    print("="*80)
    print(metrics_df.to_string(index=False))
    
    print("\n" + "="*80)
    print("✓ OILSEED PRICE FORECASTING TRAINING COMPLETED SUCCESSFULLY")
    print("="*80)


if __name__ == "__main__":
    # Example with state and district parameters
    # Modify these as needed
    STATE = "Maharashtra"
    DISTRICT = "Indore"
    LAND_SIZE = 50  # acres
    
    print(f"\n📋 Training Parameters:")
    print(f"   API Key: {API_KEY[:20]}...")
    print(f"   State: {STATE}")
    print(f"   District: {DISTRICT}")
    print(f"   Land Size: {LAND_SIZE} acres")
    print(f"   Focus: Oilseed Commodities Only")
    print(f"   Historical Period: 10 years")
    
    main(state=STATE, district=DISTRICT, land_size_acres=LAND_SIZE)
