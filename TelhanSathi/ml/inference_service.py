"""
Inference Service for Oilseed Price Forecasting
Uses trained ARIMA models to make price predictions based on:
- State, District, Land Size (acres), Current Date
"""

import pandas as pd
import numpy as np
import pickle
import os
import json
from datetime import datetime
from statsmodels.tsa.arima.model import ARIMA

# Configuration - use absolute path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASETS_DIR = os.path.join(SCRIPT_DIR, "datasets")
MODELS_DIR = os.path.join(SCRIPT_DIR, "models")


class OilseedPricePredictor:
    """Make price predictions for oilseeds based on trained models."""
    
    def __init__(self):
        self.models = {}
        self.forecasts = {}
        self.metrics = {}
        self.data_summary = {}
        self.available_regions = {}  # Store available regions
        self.load_models()
    
    def get_available_regions(self):
        """Return list of available state-district combinations."""
        return self.available_regions
    
    def load_models(self):
        """Load trained forecasts and metrics."""
        print("📂 Loading trained models and forecasts...")
        
        # Load metrics and extract available regions
        metrics_files = [f for f in os.listdir(DATASETS_DIR) 
                        if f.startswith('arima_metrics') and f.endswith('.csv')]
        
        if metrics_files:
            for mfile in metrics_files:
                key = mfile.replace('arima_metrics_', '').replace('.csv', '')
                self.metrics[key] = pd.read_csv(os.path.join(DATASETS_DIR, mfile))
                
                # Extract state and district from filename
                parts = key.split('_')
                if len(parts) >= 2:
                    state = parts[0]
                    district = '_'.join(parts[1:])
                    if state not in self.available_regions:
                        self.available_regions[state] = []
                    if district not in self.available_regions[state]:
                        self.available_regions[state].append(district)
                
                print(f"  ✓ Loaded metrics for: {key}")
        
        # Load forecasts
        forecast_files = [f for f in os.listdir(DATASETS_DIR) 
                         if f.startswith('arima_forecasts_12m') and f.endswith('.csv')]
        
        if forecast_files:
            for ffile in forecast_files:
                key = ffile.replace('arima_forecasts_12m_', '').replace('.csv', '')
                self.forecasts[key] = pd.read_csv(os.path.join(DATASETS_DIR, ffile))
                self.forecasts[key]['Date'] = pd.to_datetime(self.forecasts[key]['Date'])
                print(f"  ✓ Loaded forecasts for: {key}")
        
        # Load data summary
        summary_files = [f for f in os.listdir(DATASETS_DIR) 
                        if f.startswith('data_summary') and f.endswith('.json')]
        
        if summary_files:
            for sfile in summary_files:
                key = sfile.replace('data_summary_', '').replace('.json', '')
                with open(os.path.join(DATASETS_DIR, sfile), 'r') as f:
                    self.data_summary[key] = json.load(f)
                print(f"  ✓ Loaded summary for: {key}")
        
        if not self.forecasts:
            print("  ⚠️  No trained models found!")
    
    def get_commodity_forecast(self, commodity, state=None, district=None, months_ahead=3):
        """
        Get price forecast for a specific commodity.
        
        Args:
            commodity: Name of the oilseed commodity (e.g., 'Soybean', 'Mustard')
            state: State name (optional, used to select regional model)
            district: District name (optional, used to select regional model)
            months_ahead: Number of months to forecast (default 3)
        
        Returns:
            DataFrame with Date and Forecast_Price
            OR None if region/commodity data not available
        """
        # Select forecast dataset based on state/district
        forecast_key = f"{state}_{district}" if state and district else list(self.forecasts.keys())[0]
        
        # DO NOT fallback - return None if region not available
        if forecast_key not in self.forecasts:
            raise ValueError(f"डेटा उपलब्ध नहीं है: {state} - {district}")
        
        forecasts_df = self.forecasts[forecast_key]
        
        # Filter by commodity
        commodity_forecast = forecasts_df[forecasts_df['Commodity'] == commodity].copy()
        
        if commodity_forecast.empty:
            raise ValueError(f"फसल के लिए डेटा उपलब्ध नहीं है: {commodity}")
        
        # Return only the requested number of months
        return commodity_forecast.head(months_ahead)
    
    def calculate_profitability(self, commodity, land_size_acres, cost_per_acre, 
                               yield_qt_per_acre, state=None, district=None):
        """
        Calculate projected profit based on forecasted price.
        
        Args:
            commodity: Name of the oilseed commodity
            land_size_acres: Farm size in acres
            cost_per_acre: Production cost per acre (₹)
            yield_qt_per_acre: Expected yield per acre (quintals)
            state: State name
            district: District name
        
        Returns:
            DataFrame with profit projections
        """
        forecast = self.get_commodity_forecast(commodity, state, district, months_ahead=12)
        
        if forecast is None:
            return None
        
        # Calculate revenue and profit
        forecast['Revenue'] = forecast['ARIMA_Forecast_Price'] * yield_qt_per_acre * land_size_acres
        forecast['Total_Cost'] = cost_per_acre * land_size_acres
        forecast['Profit'] = forecast['Revenue'] - forecast['Total_Cost']
        forecast['Profit_Per_Acre'] = forecast['Profit'] / land_size_acres
        forecast['ROI_%'] = (forecast['Profit'] / forecast['Total_Cost']) * 100
        
        return forecast[['Date', 'ARIMA_Forecast_Price', 'Revenue', 'Total_Cost', 'Profit', 'ROI_%']]
    
    def get_model_accuracy(self, state=None, district=None):
        """Get model accuracy metrics."""
        key = f"{state}_{district}" if state and district else list(self.metrics.keys())[0]
        
        if key not in self.metrics:
            print(f"⚠️  Metrics for {key} not found.")
            return None
        
        return self.metrics[key]
    
    def forecast_all_commodities(self, state=None, district=None, months_ahead=3):
        """Get forecasts for all oilseed commodities."""
        forecast_key = f"{state}_{district}" if state and district else list(self.forecasts.keys())[0]
        
        if forecast_key not in self.forecasts:
            forecast_key = list(self.forecasts.keys())[0]
        
        forecasts_df = self.forecasts[forecast_key]
        
        all_forecasts = {}
        for commodity in forecasts_df['Commodity'].unique():
            forecast = forecasts_df[forecasts_df['Commodity'] == commodity].head(months_ahead)
            all_forecasts[commodity] = forecast
        
        return all_forecasts
    
    def get_current_price_trends(self, state=None, district=None):
        """Get current price trends from raw data."""
        data_files = [f for f in os.listdir(DATASETS_DIR) 
                     if f.startswith('oilseeds_10year_data') and f.endswith('.csv')]
        
        if not data_files:
            return None
        
        # Select data file based on state/district
        data_key = f"oilseeds_10year_data_{state}_{district}" if state and district else data_files[0]
        
        if os.path.exists(os.path.join(DATASETS_DIR, f"{data_key}.csv")):
            df = pd.read_csv(os.path.join(DATASETS_DIR, f"{data_key}.csv"))
        else:
            df = pd.read_csv(os.path.join(DATASETS_DIR, data_files[0]))
        
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Get latest 30 days of data
        latest_data = df[df['Date'] >= df['Date'].max() - pd.Timedelta(days=30)]
        
        trends = {}
        for commodity in latest_data['Commodity'].unique():
            commodity_data = latest_data[latest_data['Commodity'] == commodity].sort_values('Date')
            if len(commodity_data) > 0:
                trends[commodity] = {
                    'Current_Price': commodity_data['Price'].iloc[-1],
                    'Min_30Days': commodity_data['Price'].min(),
                    'Max_30Days': commodity_data['Price'].max(),
                    'Avg_30Days': commodity_data['Price'].mean(),
                    'Latest_Date': commodity_data['Date'].iloc[-1]
                }
        
        return trends


def demo_predictions():
    """Demo function to show sample predictions."""
    print("\n" + "="*80)
    print("OILSEED PRICE FORECASTING - INFERENCE SERVICE DEMO")
    print("="*80)
    
    # Initialize predictor
    predictor = OilseedPricePredictor()
    
    # Parameters
    STATE = "Maharashtra"
    DISTRICT = "Indore"
    LAND_SIZE_ACRES = 50
    COST_PER_ACRE = 15000  # ₹
    YIELD_PER_ACRE = 12  # quintals
    
    print(f"\n📋 Prediction Parameters:")
    print(f"   State: {STATE}")
    print(f"   District: {DISTRICT}")
    print(f"   Land Size: {LAND_SIZE_ACRES} acres")
    print(f"   Cost per acre: ₹{COST_PER_ACRE}")
    print(f"   Expected yield: {YIELD_PER_ACRE} qt/acre")
    
    # 1. Get forecasts for all commodities
    print("\n" + "-"*80)
    print("1️⃣ COMMODITY PRICE FORECASTS (Next 3 Months)")
    print("-"*80)
    
    forecasts = predictor.forecast_all_commodities(STATE, DISTRICT, months_ahead=3)
    
    for commodity, forecast_df in forecasts.items():
        print(f"\n{commodity}:")
        print(forecast_df[['Date', 'ARIMA_Forecast_Price']].to_string(index=False))
    
    # 2. Get model accuracy
    print("\n" + "-"*80)
    print("2️⃣ MODEL ACCURACY METRICS")
    print("-"*80)
    
    metrics = predictor.get_model_accuracy(STATE, DISTRICT)
    if metrics is not None:
        print(metrics.to_string(index=False))
    
    # 3. Calculate profitability for a specific commodity
    print("\n" + "-"*80)
    print("3️⃣ PROFIT PROJECTION - SOYBEAN (12 Months)")
    print("-"*80)
    
    profit_projection = predictor.calculate_profitability(
        commodity='Soybean',
        land_size_acres=LAND_SIZE_ACRES,
        cost_per_acre=COST_PER_ACRE,
        yield_qt_per_acre=YIELD_PER_ACRE,
        state=STATE,
        district=DISTRICT
    )
    
    if profit_projection is not None:
        print(profit_projection.to_string(index=False))
        avg_profit = profit_projection['Profit'].mean()
        total_profit = profit_projection['Profit'].sum()
        print(f"\n📊 Summary:")
        print(f"   Average Monthly Profit: ₹{avg_profit:,.2f}")
        print(f"   Projected 12-Month Profit: ₹{total_profit:,.2f}")
    
    # 4. Get current price trends
    print("\n" + "-"*80)
    print("4️⃣ CURRENT PRICE TRENDS (Last 30 Days)")
    print("-"*80)
    
    trends = predictor.get_current_price_trends(STATE, DISTRICT)
    if trends:
        for commodity, trend_data in trends.items():
            print(f"\n{commodity}:")
            print(f"   Current Price: ₹{trend_data['Current_Price']:.2f}/quintal")
            print(f"   Min (30 days): ₹{trend_data['Min_30Days']:.2f}")
            print(f"   Max (30 days): ₹{trend_data['Max_30Days']:.2f}")
            print(f"   Avg (30 days): ₹{trend_data['Avg_30Days']:.2f}")
            print(f"   Latest Date: {trend_data['Latest_Date'].date()}")
    
    print("\n" + "="*80)
    print("✓ DEMO COMPLETED")
    print("="*80)


if __name__ == "__main__":
    demo_predictions()
