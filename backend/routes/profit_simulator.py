from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensions import db
from models import Farmer
from models_marketplace import SellRequest
from datetime import datetime
import sys
import os

profit_bp = Blueprint('profit', __name__, url_prefix='/profit')

# Import the ML model stub
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml.profit_model_stub import predict_profit


def get_market_price(crop_name):
    """Fetch average market price from SellRequest listings or return fallback."""
    try:
        listings = SellRequest.query.filter_by(crop_name=crop_name).all()
        if listings:
            prices = [l.expected_price for l in listings if l.expected_price]
            if prices:
                return round(sum(prices) / len(prices), 2)
    except Exception:
        pass

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
    
    # Extract state from farmer if available, default to farmer's state
    state = farmer.state or 'Maharashtra'
    harvest_month = farmer.harvest_date.strftime('%B') if farmer.harvest_date else 'October'

    return jsonify({
        'farmer': {
            'id': farmer.id,
            'name': farmer.name,
            'district': farmer.district or '',
            'state': state,
            'soil_type': farmer.soil_type or '',
            'water_type': farmer.water_type or 'Freshwater',
            'current_crop': current_crop,
            'area_in_acres': area_acres,
            'harvest_month': harvest_month
        },
        'oilseeds_list': ['Mustard', 'Soybean', 'Groundnut', 'Sunflower', 'Safflower', 'Sesame'],
        'harvest_months': ['January', 'February', 'March', 'April', 'May', 'June', 
                           'July', 'August', 'September', 'October', 'November', 'December']
    })


@profit_bp.route('/api/simulate', methods=['POST'])
def api_simulate():
    """
    Accepts oilseed simulation parameters and calls ML model to predict profit.
    Input format matches ML model signature.
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
        return jsonify({'error': 'Invalid input', 'details': str(e)}), 400

    # Call ML model to predict profit
    try:
        prediction = predict_profit(
            crop_name=crop_name,
            state=state,
            market_district=market_district,
            harvest_month=harvest_month,
            soil_type=soil_type,
            water_type=water_type,
            area_in_acres=area_in_acres
        )
    except Exception as e:
        return jsonify({'error': 'ML model error', 'details': str(e)}), 500

    # Return the prediction with additional context for the UI
    return jsonify({
        'crop_name': crop_name,
        'area_in_acres': area_in_acres,
        'soil_type': soil_type,
        'water_type': water_type,
        'harvest_month': harvest_month,
        'prediction': prediction
    })
