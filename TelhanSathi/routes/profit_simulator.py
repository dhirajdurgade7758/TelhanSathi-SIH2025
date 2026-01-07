from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensions import db
from models import Farmer
from datetime import datetime
import sys
import os

profit_bp = Blueprint('profit', __name__, url_prefix='/profit')

# Import the ML model stub
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the ML inference service for oilseed price prediction
try:
    from ml.inference_service import OilseedPricePredictor
    ml_predictor = OilseedPricePredictor()
    ML_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Warning: ML model not available - {str(e)}")
    print("   Falling back to default calculations")
    ML_AVAILABLE = False
    ml_predictor = None


def get_market_price(crop_name):
    """
    Return default market prices for crops (₹/quintal).
    Previously fetched from marketplace listings, now using hardcoded defaults.
    """
    # Fallback defaults (₹/quintal)
    defaults = {
        'Paddy': 2200,
        'Mustard': 5200,
        'Soybean': 4650,
        'Groundnut': 6100,
        'Sunflower': 4800
    }
    return defaults.get(crop_name, 3000)


@profit_bp.route('/simulator')
def simulator_page():
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))
    return render_template('profit_simulator.html')


@profit_bp.route('/api/init')
def api_init():
    """Return prefilled farmer data for the simulator."""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    farmer = Farmer.query.filter_by(id=session['farmer_id_verified']).first()
    if not farmer:
        return jsonify({'error': 'Farmer not found'}), 404

    # Get current crop or default to Mustard
    current_crop = farmer.current_crops.split(',')[0] if farmer.current_crops else 'Mustard'
    
    # Convert hectares to acres for display
    area_acres = round((farmer.total_land_area_hectares or 0.5) * 2.471054, 2)
    
    # Extract state from farmer if available
    state = farmer.state or 'Maharashtra'
    district = farmer.district or 'Indore'
    harvest_month = farmer.harvest_date.strftime('%B') if farmer.harvest_date else 'October'

    # Get available regions from ML model
    available_regions = ml_predictor.get_available_regions() if ML_AVAILABLE else {}
    
    # Build state and district options from available data
    state_options = list(available_regions.keys()) if available_regions else ['Maharashtra']
    selected_state = state if state in state_options else (state_options[0] if state_options else 'Maharashtra')
    
    # Get districts for selected state
    district_options = available_regions.get(selected_state, ['Indore']) if available_regions else ['Indore']
    selected_district = district if district in district_options else (district_options[0] if district_options else 'Indore')

    return jsonify({
        'farmer': {
            'id': farmer.id,
            'name': farmer.name,
            'district': selected_district,
            'state': selected_state,
            'soil_type': farmer.soil_type or '',
            'water_type': farmer.water_type or 'Freshwater',
            'current_crop': current_crop,
            'area_in_acres': area_acres,
            'harvest_month': harvest_month
        },
        'available_regions': available_regions,
        'state_options': state_options,
        'district_options': district_options,
        'selected_state': selected_state,
        'selected_district': selected_district,
        'oilseeds_list': ['Mustard', 'Soybean', 'Groundnut', 'Sunflower', 'Safflower', 'Sesame'],
        'harvest_months': ['January', 'February', 'March', 'April', 'May', 'June', 
                           'July', 'August', 'September', 'October', 'November', 'December'],
        'ml_available': ML_AVAILABLE
    })


@profit_bp.route('/api/simulate', methods=['POST'])
def api_simulate():
    """
    Accepts oilseed simulation parameters and calls ML model to predict profit.
    Input format matches ML model signature.
    DOES NOT FALLBACK - Returns error if ML fails.
    """
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.json or {}
    
    try:
        crop_name = data.get('crop_name', 'Mustard')
        state = data.get('state', 'Maharashtra')
        market_district = data.get('market_district', '')
        harvest_month = data.get('harvest_month', 'October')
        soil_type = data.get('soil_type', '')
        water_type = data.get('water_type', 'Freshwater')
        area_in_acres = float(data.get('area_in_acres', 1.0))
    except Exception as e:
        return jsonify({'error': 'अमान्य इनपुट', 'details': str(e)}), 400

    # Use ML model - NO FALLBACK
    if not ML_AVAILABLE or not ml_predictor:
        return jsonify({
            'error': 'ML मॉडल उपलब्ध नहीं है',
            'details': 'कृपया सर्वर को रीस्टार्ट करें'
        }), 503

    try:
        # Default costs and yields for oilseeds (₹/acre and quintals/acre)
        oilseed_params = {
            'Mustard': {'cost': 18000, 'yield': 15},
            'Soybean': {'cost': 20000, 'yield': 18},
            'Groundnut': {'cost': 25000, 'yield': 20},
            'Sunflower': {'cost': 22000, 'yield': 16},
            'Sesame': {'cost': 19000, 'yield': 12},
            'Linseed': {'cost': 17000, 'yield': 14},
            'Safflower': {'cost': 16000, 'yield': 13}
        }
        
        params = oilseed_params.get(crop_name, {'cost': 20000, 'yield': 15})
        
        # Get ML profit projections - WILL RAISE ERROR IF REGION NOT AVAILABLE
        profit_df = ml_predictor.calculate_profitability(
            commodity=crop_name,
            land_size_acres=area_in_acres,
            cost_per_acre=params['cost'],
            yield_qt_per_acre=params['yield'],
            state=state,
            district=market_district
        )
        
        if profit_df is None or len(profit_df) == 0:
            return jsonify({
                'error': 'पूर्वानुमान डेटा उपलब्ध नहीं',
                'details': f'{crop_name} के लिए {state} - {market_district} में कोई डेटा नहीं'
            }), 400
        
        # Get average metrics from 12-month projection
        avg_price = profit_df['ARIMA_Forecast_Price'].mean()
        avg_revenue = profit_df['Revenue'].mean()
        avg_profit = profit_df['Profit'].mean()
        avg_roi = profit_df['ROI_%'].mean()
        
        # Calculate breakeven and gross totals
        total_cost = params['cost'] * area_in_acres
        total_revenue = avg_price * params['yield'] * area_in_acres
        total_profit = total_revenue - total_cost
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        prediction = {
            'gross_revenue': round(total_revenue, 2),
            'total_cost': round(total_cost, 2),
            'net_profit': round(total_profit, 2),
            'profit_margin': f"{round(profit_margin, 1)}%",
            'roi': f"{round(avg_roi, 1)}%",
            'breakeven_months': max(1, int(total_cost / (avg_profit / 12)) if avg_profit > 0 else 12),
            'forecast_price': round(avg_price, 2),
            'monthly_profit': round(avg_profit, 2),
            'model_used': 'ARIMA',
            'forecast_months': len(profit_df)
        }
        
        # Return the prediction with additional context for the UI
        return jsonify({
            'crop_name': crop_name,
            'area_in_acres': area_in_acres,
            'soil_type': soil_type,
            'water_type': water_type,
            'harvest_month': harvest_month,
            'prediction': prediction,
            'ml_enabled': True
        })
        
    except ValueError as e:
        # Region/commodity not available
        return jsonify({
            'error': str(e),
            'details': f'{state} - {market_district} में डेटा उपलब्ध नहीं है'
        }), 400
    except Exception as e:
        # Unexpected error
        print(f"❌ ML prediction error: {str(e)}")
        return jsonify({
            'error': 'पूर्वानुमान में त्रुटि',
            'details': str(e)
        }), 500


def _get_default_prediction(crop_name, area_in_acres):
    """Fallback calculation when ML model is not available."""
    # Fallback defaults (₹/quintal)
    default_prices = {
        'Mustard': 5200,
        'Soybean': 4650,
        'Groundnut': 6100,
        'Sunflower': 4800,
        'Sesame': 7200,
        'Linseed': 5500,
        'Safflower': 5000
    }
    
    default_yields = {
        'Mustard': 15,
        'Soybean': 18,
        'Groundnut': 20,
        'Sunflower': 16,
        'Sesame': 12,
        'Linseed': 14,
        'Safflower': 13
    }
    
    default_costs = {
        'Mustard': 18000,
        'Soybean': 20000,
        'Groundnut': 25000,
        'Sunflower': 22000,
        'Sesame': 19000,
        'Linseed': 17000,
        'Safflower': 16000
    }
    
    price = default_prices.get(crop_name, 5000)
    yield_qt = default_yields.get(crop_name, 15)
    cost_per_acre = default_costs.get(crop_name, 20000)
    
    gross_revenue = price * yield_qt * area_in_acres
    total_cost = cost_per_acre * area_in_acres
    net_profit = gross_revenue - total_cost
    profit_margin = (net_profit / gross_revenue * 100) if gross_revenue > 0 else 0
    roi = (net_profit / total_cost * 100) if total_cost > 0 else 0
    
    return {
        'gross_revenue': round(gross_revenue, 2),
        'total_cost': round(total_cost, 2),
        'net_profit': round(net_profit, 2),
        'profit_margin': f"{round(profit_margin, 1)}%",
        'roi': f"{round(roi, 1)}%",
        'breakeven_months': 6,
        'forecast_price': price,
        'monthly_profit': round(net_profit / 12, 2),
        'model_used': 'Default',
        'forecast_months': 0
    }

