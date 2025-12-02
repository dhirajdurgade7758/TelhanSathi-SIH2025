from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from extensions import db
from models import Farmer
import sys, os
from datetime import datetime

# ensure imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.uj_model_stub import get_farm_analysis

onboarding_bp = Blueprint('onboarding', __name__)


# ---------------------- GET ----------------------
@onboarding_bp.route('/onboarding', methods=['GET'])
def onboarding():
    """Render short onboarding form to collect minimal context."""
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))

    farmer = Farmer.query.filter_by(id=session.get('farmer_id_verified')).first()

    pre = {
        'crop': farmer.current_crops.split(',')[0] if farmer and farmer.current_crops else '',
        'acres': round(farmer.total_land_area_hectares * 2.471054, 1)
                  if farmer and farmer.total_land_area_hectares else 2,
        'district': farmer.district if farmer and farmer.district else '',
        'irrigation': farmer.irrigation_type if farmer and farmer.irrigation_type else '',
        'soil': farmer.soil_type if farmer and farmer.soil_type else '',
        'harvest_date': farmer.harvest_date.strftime("%Y-%m") 
                        if farmer and farmer.harvest_date else ''
    }

    return render_template('onboarding.html', pre=pre)



# ---------------------- POST ----------------------
@onboarding_bp.route('/onboarding', methods=['POST'])
def onboarding_post():
    """Process onboarding inputs and store into Farmer model."""
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))

    crop = request.form.get('crop', '').strip()
    acres = request.form.get('acres', '').strip()
    district = request.form.get('district', '').strip()
    harvest_date = request.form.get('harvest_date', '').strip()
    irrigation = request.form.get('irrigation', '').strip()
    soil = request.form.get('soil', '').strip()

    # Ensure acres is numeric
    try:
        acres_float = float(acres)
    except:
        acres_float = 2.0

    # Convert acres → hectares
    hectares = round(acres_float * 0.404686, 4)

    # Convert month-year → Python date
    parsed_harvest_date = None
    if harvest_date:
        try:
            parsed_harvest_date = datetime.strptime(harvest_date, "%Y-%m")
        except:
            parsed_harvest_date = None

    # Update farmer
    farmer = Farmer.query.filter_by(id=session.get('farmer_id_verified')).first()

    if farmer:
        if crop:
            farmer.current_crops = crop

        farmer.total_land_area_hectares = hectares

        if district:
            farmer.district = district

        if irrigation:
            farmer.irrigation_type = irrigation

        if soil:
            farmer.soil_type = soil

        if parsed_harvest_date:
            farmer.harvest_date = parsed_harvest_date

        farmer.onboarding_completed = True
        db.session.commit()

    # SESSION STORAGE
    session['user_context'] = {
        'crop': crop,
        'acres': acres_float,
        'district': district,
        'irrigation': irrigation,
        'soil': soil,
        'harvest_date': harvest_date
    }

    # ML Stub → store analysis
    try:
        analysis = get_farm_analysis(
            district=district,
            acres=acres_float,
            crop=crop
        )
        session['analysis'] = analysis
    except Exception as e:
        print("ML stub error:", e)
        session['analysis'] = None

    return redirect(url_for('dashboard'))


# ---------------------- API ----------------------
@onboarding_bp.route('/api/user_context', methods=['GET'])
def get_context():
    """Return user context & analysis JSON for frontend polling."""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'unauthenticated'}), 401

    return jsonify({
        'user_context': session.get('user_context'),
        'analysis': session.get('analysis')
    })
