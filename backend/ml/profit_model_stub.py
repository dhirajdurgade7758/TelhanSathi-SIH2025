"""
Profit prediction ML model stub.
Input format matches ML developer's expected signature:
{
    "crop_name": "Mustard",
    "state": "Rajasthan",
    "market_district": "Bharatpur",
    "harvest_month": "March" or 3,
    "soil_type": "Loamy",
    "water_type": "Freshwater/Salt water/Brackish water",
    "area_in_acres": 2.5
}

Output:
{
    "yield_per_acre": 8.5,
    "price_per_quintal": 5100.0,
    "input_cost": 22500.0,
    "gross_income": 108375.0,
    "net_profit": 85875.0
}
"""
import random


def predict_profit(crop_name, state, market_district, harvest_month, soil_type, water_type, area_in_acres):
    """
    Stub ML model to predict yield, price, costs, and profit.
    Returns profit metrics as a dict.
    """
    
    # Base yield per acre (quintals) for different crops
    base_yield = {
        'Mustard': 8.5,
        'Soybean': 10.0,
        'Groundnut': 12.0,
        'Sunflower': 9.0,
        'Safflower': 7.5,
        'Sesame': 5.5
    }
    
    yield_per_acre = base_yield.get(crop_name, 8.0)
    
    # Adjustments based on soil type
    if soil_type:
        st = soil_type.lower()
        if 'black' in st:
            yield_per_acre *= 1.15
        elif 'loamy' in st:
            yield_per_acre *= 1.10
        elif 'sandy' in st:
            yield_per_acre *= 0.85
    
    # Adjustments based on water type
    if water_type:
        wt = water_type.lower()
        if 'freshwater' in wt:
            yield_per_acre *= 1.10
        elif 'brackish' in wt:
            yield_per_acre *= 0.95
        elif 'salt' in wt:
            yield_per_acre *= 0.80
    
    yield_per_acre = round(yield_per_acre, 2)
    
    # Base market price per quintal (₹)
    base_price = {
        'Mustard': 5100,
        'Soybean': 4650,
        'Groundnut': 6100,
        'Sunflower': 4800,
        'Safflower': 5500,
        'Sesame': 7200
    }
    
    price_per_quintal = base_price.get(crop_name, 5000)
    
    # Small randomization for variation (stub only)
    price_per_quintal += random.randint(-200, 200)
    price_per_quintal = round(price_per_quintal, 2)
    
    # Input costs per acre (₹)
    base_input_cost = {
        'Mustard': 15000,
        'Soybean': 16000,
        'Groundnut': 18000,
        'Sunflower': 14000,
        'Safflower': 16500,
        'Sesame': 12000
    }
    
    input_cost_per_acre = base_input_cost.get(crop_name, 15000)
    
    # Adjust costs by water type (irrigation costs differ)
    if water_type:
        wt = water_type.lower()
        if 'saltwater' in wt or 'salt water' in wt:
            input_cost_per_acre += 3000  # Additional desalination/treatment
        elif 'brackish' in wt:
            input_cost_per_acre += 1500
    
    total_input_cost = round(input_cost_per_acre * area_in_acres, 2)
    
    # Calculate income and profit
    total_yield_quintals = round(yield_per_acre * area_in_acres, 2)
    gross_income = round(total_yield_quintals * price_per_quintal, 2)
    net_profit = round(gross_income - total_input_cost, 2)
    
    return {
        'yield_per_acre': yield_per_acre,
        'total_yield_quintals': total_yield_quintals,
        'price_per_quintal': price_per_quintal,
        'input_cost': total_input_cost,
        'gross_income': gross_income,
        'net_profit': net_profit
    }
