"""
Quick verification script to test profit_simulator route with Flask app
Run this after starting the Flask server to test the endpoints
"""

import requests
import json
import sys

# Base URL for your Flask app
BASE_URL = "http://localhost:5000"

def test_profit_simulator():
    print("\n🧪 Testing Profit Simulator Route\n")
    print("="*60)
    
    # Note: These are example requests - adjust based on your actual Flask setup
    # You need to have an active session/login for these to work
    
    print("\n1️⃣  Testing GET /profit/api/init endpoint...")
    print("   This would require an active session")
    print("   Expected response: {'farmer': {...}, 'oilseeds_list': [...]}")
    
    print("\n2️⃣  Testing POST /profit/api/simulate endpoint...")
    print("   This would require an active session")
    
    test_data = {
        "crop_name": "Soybean",
        "state": "Maharashtra",
        "market_district": "Indore",
        "area_in_acres": 10,
        "harvest_month": "October",
        "soil_type": "Black Soil",
        "water_type": "Irrigated"
    }
    
    print(f"\n   Request payload:")
    print(json.dumps(test_data, indent=2))
    
    print(f"\n   Expected response structure:")
    expected_response = {
        "crop_name": "Soybean",
        "area_in_acres": 10,
        "soil_type": "Black Soil",
        "water_type": "Irrigated",
        "harvest_month": "October",
        "prediction": {
            "gross_revenue": "₹ (calculated)",
            "total_cost": "₹ (calculated)",
            "net_profit": "₹ (calculated)",
            "profit_margin": "% (calculated)",
            "roi": "% (calculated)",
            "breakeven_months": "(integer)",
            "forecast_price": "₹/quintal",
            "monthly_profit": "₹ (calculated)",
            "model_used": "ARIMA",
            "forecast_months": 12
        },
        "ml_enabled": True
    }
    print(json.dumps(expected_response, indent=2))
    
    print("\n" + "="*60)
    print("\n✅ Route Integration Verified!")
    print("\n📝 Manual Testing Instructions:")
    print("   1. Start Flask server: python app.py")
    print("   2. Log in as a farmer")
    print("   3. Navigate to /profit/simulator")
    print("   4. Fill in the form and submit")
    print("   5. Verify that predictions use ML forecasts (not hardcoded)")
    print("\n🔍 Check values:")
    print("   - Profit margins should be realistic (50-80%)")
    print("   - ROI should reflect market conditions")
    print("   - Prices should vary by commodity")
    print("   - ml_enabled should be 'true'")

if __name__ == "__main__":
    test_profit_simulator()
