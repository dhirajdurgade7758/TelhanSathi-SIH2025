"""
Profit Simulator using ARIMA Price Forecaster
Calculates agricultural profitability based on price forecasts
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add ml directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arima_price_forecaster import get_forecaster


class ProfitSimulator:
    """
    Simulate agricultural profit using ARIMA price forecasts.
    Integrates with trained ARIMA models for market-specific predictions.
    """
    
    def __init__(self):
        """Initialize the profit simulator with pre-trained forecaster."""
        try:
            self.forecaster = get_forecaster()
            self.model_available = True
            logger.info("✓ Profit Simulator initialized with ARIMA forecaster")
        except Exception as e:
            logger.error(f"✗ Failed to initialize forecaster: {e}")
            self.forecaster = None
            self.model_available = False
    
    # ========== OILSEED PARAMETERS ==========
    
    OILSEED_PARAMS = {
        'Groundnut': {
            'cost_per_acre_inr': 25000,
            'avg_yield_quintals_per_acre': 20,
            'density_per_hectare': 150000,
            'growth_period_days': 120,
        },
        'Linseed (Flaxseed)': {
            'cost_per_acre_inr': 17000,
            'avg_yield_quintals_per_acre': 14,
            'density_per_hectare': 80000,
            'growth_period_days': 120,
        },
        'Mustard': {
            'cost_per_acre_inr': 18000,
            'avg_yield_quintals_per_acre': 15,
            'density_per_hectare': 200000,
            'growth_period_days': 120,
        },
        'Sesame': {
            'cost_per_acre_inr': 19000,
            'avg_yield_quintals_per_acre': 12,
            'density_per_hectare': 120000,
            'growth_period_days': 90,
        },
        'Soybean': {
            'cost_per_acre_inr': 20000,
            'avg_yield_quintals_per_acre': 18,
            'density_per_hectare': 400000,
            'growth_period_days': 100,
        },
    }
    
    # Market to State/City mapping
    MARKET_MAPPING = {
        'Chennai': 'Tamil Nadu',
        'Delhi': 'Delhi',
        'Indore': 'Madhya Pradesh',
        'Mumbai': 'Maharashtra',
        'Surat': 'Gujarat',
    }
    
    def get_available_markets(self):
        """Get list of available markets from trained models."""
        if not self.model_available:
            return []
        return self.forecaster.get_unique_markets()
    
    def get_available_commodities(self):
        """Get list of available commodities."""
        return list(self.OILSEED_PARAMS.keys())
    
    def get_commodities_for_market(self, market):
        """Get commodities available in a specific market."""
        if not self.model_available:
            return []
        try:
            return self.forecaster.get_commodities_for_market(market)
        except:
            return []
    
    def get_markets_for_commodity(self, commodity):
        """Get markets available for a specific commodity."""
        if not self.model_available:
            return []
        try:
            return self.forecaster.get_markets_for_commodity(commodity)
        except:
            return []
    
    def _validate_inputs(self, market, commodity, area_acres):
        """Validate input parameters."""
        if not self.model_available:
            raise ValueError("ARIMA models not available")
        
        markets = self.get_available_markets()
        if market not in markets:
            raise ValueError(f"Market '{market}' not available. Available: {markets}")
        
        commodities = self.get_commodities_for_market(market)
        if commodity not in commodities:
            raise ValueError(
                f"Commodity '{commodity}' not available in {market}. "
                f"Available: {commodities}"
            )
        
        if area_acres <= 0:
            raise ValueError(f"Area must be positive, got {area_acres}")
        
        if commodity not in self.OILSEED_PARAMS:
            raise ValueError(f"Unknown commodity: {commodity}")
    
    def simulate_profit_30days(self, market, commodity, area_acres, 
                               custom_cost_per_acre=None, custom_yield_quintals=None):
        """
        Simulate profit for next 30 days using ARIMA forecasts.
        
        Args:
            market (str): Market name (e.g., 'Delhi', 'Mumbai')
            commodity (str): Commodity name (e.g., 'Soybean', 'Groundnut')
            area_acres (float): Farming area in acres
            custom_cost_per_acre (float): Override default cost (optional)
            custom_yield_quintals (float): Override default yield (optional)
            
        Returns:
            dict: Comprehensive profit simulation including forecasts and metrics
        """
        try:
            # Validate inputs
            self._validate_inputs(market, commodity, area_acres)
            
            # Get default parameters
            params = self.OILSEED_PARAMS[commodity]
            cost_per_acre = custom_cost_per_acre or params['cost_per_acre_inr']
            yield_quintals = custom_yield_quintals or params['avg_yield_quintals_per_acre']
            
            # Get 30-day price forecast
            forecast_data = self.forecaster.forecast(market, commodity, periods=30)
            
            if not forecast_data:
                raise ValueError(f"No forecast data for {market} - {commodity}")
            
            # Calculate daily revenue and profit
            prices = forecast_data['forecast']
            lower_ci = forecast_data['lower_ci']
            upper_ci = forecast_data['upper_ci']
            last_price = forecast_data['last_price']
            
            # Convert to per acre metrics
            daily_yield_acres = yield_quintals / 30  # Assume uniform yield over 30 days
            daily_cost_acres = cost_per_acre / 30
            
            # Calculate profit metrics
            price_array = np.array(prices)
            revenue_per_acre = price_array * daily_yield_acres
            profit_per_acre = revenue_per_acre - daily_cost_acres
            
            # Scale to total area
            total_revenue = revenue_per_acre * area_acres
            total_cost_daily = daily_cost_acres * area_acres
            total_profit = profit_per_acre * area_acres
            
            # Aggregate metrics
            avg_price = np.mean(price_array)
            min_price = np.min(price_array)
            max_price = np.max(price_array)
            price_volatility = np.std(price_array)
            
            total_revenue_30days = np.sum(total_revenue)
            total_cost_30days = total_cost_daily * 30
            total_profit_30days = total_revenue_30days - total_cost_30days
            
            total_yield_30days = yield_quintals * area_acres
            avg_revenue_per_quintal = total_revenue_30days / total_yield_30days if total_yield_30days > 0 else 0
            
            # Calculate ROI and margins
            roi_percent = (total_profit_30days / total_cost_30days * 100) if total_cost_30days > 0 else 0
            profit_margin_percent = (total_profit_30days / total_revenue_30days * 100) if total_revenue_30days > 0 else 0
            
            # Breakeven analysis
            breakeven_days = int(total_cost_30days / (total_profit_30days / 30)) if total_profit_30days > 0 else 30
            breakeven_days = max(1, min(breakeven_days, 30))  # Clamp between 1-30 days
            
            # Price trend analysis
            price_trend = "Stable"
            if max_price - last_price > price_volatility:
                price_trend = "Uptrend"
            elif last_price - min_price > price_volatility:
                price_trend = "Downtrend"
            
            return {
                'status': 'success',
                'market': market,
                'commodity': commodity,
                'area_acres': area_acres,
                'forecast_period_days': 30,
                
                # Price metrics
                'price': {
                    'current': round(last_price, 2),
                    'average_forecast': round(avg_price, 2),
                    'minimum': round(min_price, 2),
                    'maximum': round(max_price, 2),
                    'volatility': round(price_volatility, 2),
                    'trend': price_trend,
                    'forecast_values': [round(p, 2) for p in prices],
                    'confidence_lower': [round(ci, 2) for ci in lower_ci],
                    'confidence_upper': [round(ci, 2) for ci in upper_ci],
                },
                
                # Cost metrics
                'cost': {
                    'per_acre': round(cost_per_acre, 2),
                    'total_30days': round(total_cost_30days, 2),
                },
                
                # Yield metrics
                'yield': {
                    'per_acre_quintals': round(yield_quintals, 2),
                    'total_quintals': round(total_yield_30days, 2),
                    'per_quintal_cost': round(total_cost_30days / total_yield_30days, 2) if total_yield_30days > 0 else 0,
                },
                
                # Revenue metrics
                'revenue': {
                    'daily_average': round(np.mean(total_revenue), 2),
                    'total_30days': round(total_revenue_30days, 2),
                    'per_quintal_average': round(avg_revenue_per_quintal, 2),
                },
                
                # Profit metrics
                'profit': {
                    'daily_average': round(np.mean(total_profit), 2),
                    'total_30days': round(total_profit_30days, 2),
                    'margin_percent': round(profit_margin_percent, 2),
                },
                
                # Financial indicators
                'financial': {
                    'roi_percent': round(roi_percent, 2),
                    'breakeven_days': breakeven_days,
                    'profit_per_day': round(total_profit_30days / 30, 2),
                },
                
                # Additional info
                'model_info': {
                    'model_type': 'ARIMA',
                    'model_order': '(1,1,1)',
                    'data_points_trained': 1070,
                },
            }
        
        except Exception as e:
            logger.error(f"Profit simulation error: {e}")
            return {
                'status': 'error',
                'message': str(e),
            }
    
    def simulate_profit_annual(self, market, commodity, area_acres,
                                custom_cost_per_acre=None, custom_yield_quintals=None,
                                harvest_month='October'):
        """
        Simulate annual profit based on harvest month.
        Uses 90-day forecast centered on harvest month.
        
        Args:
            market (str): Market name
            commodity (str): Commodity name
            area_acres (float): Farming area in acres
            custom_cost_per_acre (float): Override default cost (optional)
            custom_yield_quintals (float): Override default yield (optional)
            harvest_month (str): Expected harvest month
            
        Returns:
            dict: Annual profit simulation
        """
        try:
            # Validate inputs
            self._validate_inputs(market, commodity, area_acres)
            
            # Get parameters
            params = self.OILSEED_PARAMS[commodity]
            cost_per_acre = custom_cost_per_acre or params['cost_per_acre_inr']
            yield_quintals = custom_yield_quintals or params['avg_yield_quintals_per_acre']
            
            # Get 90-day forecast for better annual estimate
            forecast_data = self.forecaster.forecast(market, commodity, periods=90)
            
            if not forecast_data:
                raise ValueError(f"No forecast data for {market} - {commodity}")
            
            prices = np.array(forecast_data['forecast'])
            
            # Calculate annual metrics
            annual_yield_quintals = yield_quintals * area_acres
            annual_cost = cost_per_acre * area_acres
            
            avg_price = np.mean(prices)
            annual_revenue = avg_price * annual_yield_quintals
            annual_profit = annual_revenue - annual_cost
            
            roi_percent = (annual_profit / annual_cost * 100) if annual_cost > 0 else 0
            profit_margin_percent = (annual_profit / annual_revenue * 100) if annual_revenue > 0 else 0
            
            return {
                'status': 'success',
                'market': market,
                'commodity': commodity,
                'area_acres': area_acres,
                'harvest_month': harvest_month,
                'forecast_period_days': 90,
                
                'price': {
                    'average_forecast': round(np.mean(prices), 2),
                    'minimum': round(np.min(prices), 2),
                    'maximum': round(np.max(prices), 2),
                },
                
                'annual': {
                    'yield_quintals': round(annual_yield_quintals, 2),
                    'cost': round(annual_cost, 2),
                    'revenue': round(annual_revenue, 2),
                    'profit': round(annual_profit, 2),
                    'roi_percent': round(roi_percent, 2),
                    'profit_margin_percent': round(profit_margin_percent, 2),
                },
                
                'monthly_average': {
                    'cost': round(annual_cost / 12, 2),
                    'revenue': round(annual_revenue / 12, 2),
                    'profit': round(annual_profit / 12, 2),
                },
            }
        
        except Exception as e:
            logger.error(f"Annual profit simulation error: {e}")
            return {
                'status': 'error',
                'message': str(e),
            }
    
    def compare_commodities(self, market, area_acres, months_forecast=30):
        """
        Compare profit potential across different commodities in a market.
        
        Args:
            market (str): Market name
            area_acres (float): Farming area
            months_forecast (int): Forecast period in days
            
        Returns:
            dict: Comparison of all available commodities
        """
        try:
            commodities = self.get_commodities_for_market(market)
            
            if not commodities:
                return {
                    'status': 'error',
                    'message': f"No commodities available for {market}"
                }
            
            comparison_data = {
                'status': 'success',
                'market': market,
                'area_acres': area_acres,
                'commodities': {}
            }
            
            for commodity in commodities:
                result = self.simulate_profit_30days(market, commodity, area_acres)
                
                if result['status'] == 'success':
                    comparison_data['commodities'][commodity] = {
                        'price_current': result['price']['current'],
                        'price_average': result['price']['average_forecast'],
                        'total_profit_30days': result['profit']['total_30days'],
                        'roi_percent': result['financial']['roi_percent'],
                        'profit_margin_percent': result['profit']['margin_percent'],
                    }
            
            # Sort by total profit (descending)
            sorted_commodities = sorted(
                comparison_data['commodities'].items(),
                key=lambda x: x[1]['total_profit_30days'],
                reverse=True
            )
            
            comparison_data['commodities_ranked'] = [
                {'commodity': name, **data} for name, data in sorted_commodities
            ]
            comparison_data['best_commodity'] = sorted_commodities[0][0] if sorted_commodities else None
            
            return comparison_data
        
        except Exception as e:
            logger.error(f"Commodity comparison error: {e}")
            return {
                'status': 'error',
                'message': str(e),
            }


# ========== CONVENIENCE FUNCTIONS ==========

def get_profit_simulator():
    """Get a ProfitSimulator instance."""
    return ProfitSimulator()


def simulate_profit(market, commodity, area_acres):
    """Quick profit simulation for 30 days."""
    simulator = get_profit_simulator()
    return simulator.simulate_profit_30days(market, commodity, area_acres)


def get_market_options():
    """Get available markets."""
    simulator = get_profit_simulator()
    return simulator.get_available_markets()


def get_commodity_options():
    """Get available commodities."""
    simulator = get_profit_simulator()
    return simulator.get_available_commodities()


if __name__ == "__main__":
    # Example usage
    simulator = get_profit_simulator()
    
    print("\n" + "="*70)
    print("PROFIT SIMULATOR - Example Usage")
    print("="*70)
    
    # Example 1: 30-day profit simulation
    print("\n1️⃣  30-Day Profit Simulation for Delhi - Soybean (2 acres)")
    result = simulator.simulate_profit_30days("Delhi", "Soybean", area_acres=2)
    
    if result['status'] == 'success':
        print(f"\n   Current Price: ₹{result['price']['current']}/quintal")
        print(f"   Average Forecast Price: ₹{result['price']['average_forecast']}/quintal")
        print(f"   Total Profit (30 days): ₹{result['profit']['total_30days']}")
        print(f"   ROI: {result['financial']['roi_percent']}%")
        print(f"   Breakeven: {result['financial']['breakeven_days']} days")
        print(f"   Price Trend: {result['price']['trend']}")
    else:
        print(f"   Error: {result['message']}")
    
    # Example 2: Annual simulation
    print("\n2️⃣  Annual Profit Simulation")
    result = simulator.simulate_profit_annual("Delhi", "Soybean", area_acres=2)
    
    if result['status'] == 'success':
        print(f"\n   Annual Revenue: ₹{result['annual']['revenue']}")
        print(f"   Annual Profit: ₹{result['annual']['profit']}")
        print(f"   Annual ROI: {result['annual']['roi_percent']}%")
    else:
        print(f"   Error: {result['message']}")
    
    # Example 3: Commodity comparison
    print("\n3️⃣  Commodity Comparison for Mumbai (1 acre)")
    result = simulator.compare_commodities("Mumbai", area_acres=1)
    
    if result['status'] == 'success':
        print(f"\n   Best Commodity: {result['best_commodity']}")
        print("\n   Ranking:")
        for i, item in enumerate(result['commodities_ranked'], 1):
            print(f"   {i}. {item['commodity']}")
            print(f"      30-Day Profit: ₹{item['total_profit_30days']}")
            print(f"      ROI: {item['roi_percent']}%")
    else:
        print(f"   Error: {result['message']}")
    
    print("\n" + "="*70)
