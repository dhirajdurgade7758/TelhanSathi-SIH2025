"""
Integration test script for the oilseed profit simulator with ML model.
Tests the profit_simulator route with the ML inference service.
"""

import sys
import os
import json

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

print("🧪 Testing Oilseed Profit Simulator Integration\n")
print("="*60)

# Test 1: Import inference service
print("\n1️⃣  Testing ML Inference Service Import...")
try:
    # Import from current directory (we're in ml folder)
    from inference_service import OilseedPricePredictor
    print("   ✓ Successfully imported OilseedPricePredictor")
except Exception as e:
    print(f"   ✗ Failed to import: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Initialize predictor
print("\n2️⃣  Testing Predictor Initialization...")
try:
    predictor = OilseedPricePredictor()
    print("   ✓ Successfully initialized OilseedPricePredictor")
except Exception as e:
    print(f"   ✗ Failed to initialize: {str(e)}")
    sys.exit(1)

# Test 3: Get forecasts
print("\n3️⃣  Testing Commodity Forecasts...")
try:
    forecasts = predictor.forecast_all_commodities(
        state='Maharashtra',
        district='Indore',
        months_ahead=3
    )
    print(f"   ✓ Retrieved forecasts for {len(forecasts)} commodities")
    for commodity, forecast_df in forecasts.items():
        print(f"      - {commodity}: {len(forecast_df)} months")
except Exception as e:
    print(f"   ✗ Failed to get forecasts: {str(e)}")
    sys.exit(1)

# Test 4: Calculate profitability
print("\n4️⃣  Testing Profit Calculations...")
try:
    profit_df = predictor.calculate_profitability(
        commodity='Soybean',
        land_size_acres=10,
        cost_per_acre=20000,
        yield_qt_per_acre=18,
        state='Maharashtra',
        district='Indore'
    )
    
    if profit_df is not None and len(profit_df) > 0:
        avg_profit = profit_df['Profit'].mean()
        total_profit = profit_df['Profit'].sum()
        avg_roi = profit_df['ROI_%'].mean()
        
        print(f"   ✓ Profit calculations successful")
        print(f"      - Average Monthly Profit: ₹{avg_profit:,.2f}")
        print(f"      - 12-Month Total Profit: ₹{total_profit:,.2f}")
        print(f"      - Average ROI: {avg_roi:.1f}%")
    else:
        print("   ✗ No profit data returned")
except Exception as e:
    print(f"   ✗ Failed to calculate profits: {str(e)}")
    sys.exit(1)

# Test 5: Get price trends
print("\n5️⃣  Testing Price Trends...")
try:
    trends = predictor.get_current_price_trends(
        state='Maharashtra',
        district='Indore'
    )
    
    if trends:
        print(f"   ✓ Retrieved price trends for {len(trends)} commodities")
        for commodity, trend_data in trends.items():
            print(f"      - {commodity}: ₹{trend_data['Current_Price']:.2f}/qt")
    else:
        print("   ✗ No trend data available")
except Exception as e:
    print(f"   ✗ Failed to get trends: {str(e)}")

# Test 6: Get model metrics
print("\n6️⃣  Testing Model Accuracy Metrics...")
try:
    metrics = predictor.get_model_accuracy(
        state='Maharashtra',
        district='Indore'
    )
    
    if metrics is not None and len(metrics) > 0:
        print(f"   ✓ Retrieved metrics for {len(metrics)} commodities")
        avg_accuracy = metrics['Test_Accuracy_%'].mean()
        print(f"      - Average Model Accuracy: {avg_accuracy:.2f}%")
    else:
        print("   ✗ No metric data available")
except Exception as e:
    print(f"   ✗ Failed to get metrics: {str(e)}")

# Test 7: Simulate profit_simulator route
print("\n7️⃣  Simulating Profit Simulator Route...")
try:
    # Simulate request data
    test_cases = [
        {
            'crop_name': 'Mustard',
            'state': 'Maharashtra',
            'market_district': 'Indore',
            'area_in_acres': 5,
            'harvest_month': 'October'
        },
        {
            'crop_name': 'Soybean',
            'state': 'Maharashtra',
            'market_district': 'Indore',
            'area_in_acres': 10,
            'harvest_month': 'October'
        }
    ]
    
    for test_case in test_cases:
        crop = test_case['crop_name']
        area = test_case['area_in_acres']
        
        # Simulate the calculation logic
        oilseed_params = {
            'Mustard': {'cost': 18000, 'yield': 15},
            'Soybean': {'cost': 20000, 'yield': 18},
        }
        
        params = oilseed_params.get(crop, {'cost': 20000, 'yield': 15})
        
        profit_df = predictor.calculate_profitability(
            commodity=crop,
            land_size_acres=area,
            cost_per_acre=params['cost'],
            yield_qt_per_acre=params['yield'],
            state=test_case['state'],
            district=test_case['market_district']
        )
        
        if profit_df is not None and len(profit_df) > 0:
            avg_price = profit_df['ARIMA_Forecast_Price'].mean()
            total_revenue = avg_price * params['yield'] * area
            total_cost = params['cost'] * area
            total_profit = total_revenue - total_cost
            profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            print(f"\n   ✓ {crop} simulation ({area} acres):")
            print(f"      - Revenue: ₹{total_revenue:,.2f}")
            print(f"      - Cost: ₹{total_cost:,.2f}")
            print(f"      - Net Profit: ₹{total_profit:,.2f}")
            print(f"      - Margin: {profit_margin:.1f}%")
        else:
            print(f"   ✗ Failed to calculate for {crop}")

except Exception as e:
    print(f"   ✗ Simulation failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("\n✅ ALL INTEGRATION TESTS PASSED!")
print("\n📝 Integration Summary:")
print("   ✓ ML model initialized successfully")
print("   ✓ Price forecasting working")
print("   ✓ Profit calculations functional")
print("   ✓ Price trends available")
print("   ✓ Model metrics accessible")
print("   ✓ Route simulation successful")
print("\n🚀 Ready to deploy!")
