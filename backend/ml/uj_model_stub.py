def get_farm_analysis(district, acres, crop, extra_context=None):
    """
    Stub for Ujjwal's ML model.
    Returns deterministic sample analysis so frontend/backend can be integrated now.
    Replace this with the real model call when available.
    """
    # Basic deterministic mock logic
    try:
        acres = float(acres or 2.0)
    except Exception:
        acres = 2.0

    # Mock yields and profits (per acre)
    base_yield_q_per_acre = {
        'paddy': 20,
        'wheat': 18,
        'maize': 10,
        'chickpea': 8,
        'cotton': 6
    }

    base_profit_per_acre = {
        'paddy': 15000,
        'wheat': 12000,
        'maize': 10000,
        'chickpea': 9000,
        'cotton': 25000,
        'mustard': 30000
    }

    crop_key = (crop or '').lower()
    current_yield = base_yield_q_per_acre.get(crop_key, 10)
    current_profit = base_profit_per_acre.get(crop_key, 10000) * acres

    # Mock suggested oilseed
    suggested_oilseed = 'mustard'
    oilseed_yield = 12 * acres
    oilseed_profit = base_profit_per_acre.get('mustard', 30000) * acres

    analysis = {
        'current_yield_q_per_acre': current_yield,
        'current_profit_total': round(current_profit, 2),
        'oilseed_recommendation': suggested_oilseed,
        'oilseed_yield_total_q': round(oilseed_yield, 2),
        'oilseed_profit_total': round(oilseed_profit, 2),
        'weather_risk': 'Low',
        'soil_suitability_score': 0.78,
        'subsidy_estimate': 5000 * acres,
        'analysis_note': f'Mock analysis for {crop} in {district} for {acres} acres.'
    }

    return analysis
