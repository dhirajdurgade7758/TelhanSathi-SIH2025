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
        'water_type': farmer.water_type if farmer and farmer.water_type else '',
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
    water_type = request.form.get('water_type', '').strip()
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

        if water_type:
            farmer.water_type = water_type

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
        'water_type': water_type,
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


# ===== EXTENDED ONBOARDING FOR MOBILE USERS =====

@onboarding_bp.route('/extended-onboarding', methods=['GET'])
def extended_onboarding():
    """Render extended onboarding form for new mobile farmers"""
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))
    
    if not session.get('needs_extended_onboarding'):
        # Not a new mobile farmer, redirect to standard onboarding
        return redirect(url_for('onboarding.onboarding'))
    
    farmer = Farmer.query.filter_by(id=session.get('farmer_id_verified')).first()
    
    if not farmer:
        return redirect(url_for('auth.login'))
    
    # Pre-populate existing data if available
    pre = {
        'name': farmer.name if farmer.name else '',
        'district': farmer.district if farmer.district else '',
        'date_of_birth': farmer.date_of_birth.strftime("%Y-%m-%d") if farmer.date_of_birth else '',
        'gender': farmer.gender if farmer.gender else '',
        'caste_category': farmer.caste_category if farmer.caste_category else '',
        'permanent_address': farmer.permanent_address if farmer.permanent_address else '',
        'taluka': farmer.taluka if farmer.taluka else '',
        'village': farmer.village if farmer.village else '',
        'state': farmer.state if farmer.state else '',
        'pincode': farmer.pincode if farmer.pincode else '',
        'land_unit': farmer.land_unit if farmer.land_unit else 'acre',
        'is_oilseed_farmer': farmer.is_oilseed_farmer if farmer.is_oilseed_farmer else False,
        'land_holder_type': farmer.land_holder_type if farmer.land_holder_type else '',
    }
    
    return render_template('extended_onboarding.html', pre=pre)


@onboarding_bp.route('/extended-onboarding', methods=['POST'])
def extended_onboarding_post():
    """Process extended onboarding and save to farmer profile"""
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))
    
    farmer = Farmer.query.filter_by(id=session.get('farmer_id_verified')).first()
    if not farmer:
        return redirect(url_for('auth.login'))
    
    # Collect extended onboarding fields
    name = request.form.get('name', '').strip()
    district = request.form.get('district', '').strip()
    date_of_birth = request.form.get('date_of_birth', '').strip()
    gender = request.form.get('gender', '').strip()
    caste_category = request.form.get('caste_category', '').strip()
    permanent_address = request.form.get('permanent_address', '').strip()
    taluka = request.form.get('taluka', '').strip()
    village = request.form.get('village', '').strip()
    state = request.form.get('state', '').strip()
    pincode = request.form.get('pincode', '').strip()
    land_unit = request.form.get('land_unit', 'acre').strip()
    is_oilseed_farmer = request.form.get('is_oilseed_farmer') == 'on'
    land_holder_type = request.form.get('land_holder_type', '').strip()
    
    # Validate required fields
    if not name or not district:
        return render_template('extended_onboarding.html', pre={
            'name': name, 'district': district, 'date_of_birth': date_of_birth,
            'gender': gender, 'caste_category': caste_category, 'permanent_address': permanent_address,
            'taluka': taluka, 'village': village, 'state': state, 'pincode': pincode,
            'land_unit': land_unit, 'is_oilseed_farmer': is_oilseed_farmer, 'land_holder_type': land_holder_type
        }, error='Please fill in all required fields (Name and District)')
    
    # Update farmer with extended onboarding data
    farmer.name = name
    farmer.district = district
    if date_of_birth:
        try:
            farmer.date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d")
        except:
            pass
    if gender:
        farmer.gender = gender
    if caste_category:
        farmer.caste_category = caste_category
    if permanent_address:
        farmer.permanent_address = permanent_address
    if taluka:
        farmer.taluka = taluka
    if village:
        farmer.village = village
    if state:
        farmer.state = state
    if pincode:
        farmer.pincode = pincode
    if land_unit:
        farmer.land_unit = land_unit
    
    farmer.is_oilseed_farmer = is_oilseed_farmer
    
    if land_holder_type:
        farmer.land_holder_type = land_holder_type
    
    db.session.commit()
    
    # Clear extended onboarding flag
    session.pop('needs_extended_onboarding', None)
    
    # Redirect to standard onboarding for crop and land details
    return redirect(url_for('onboarding.onboarding'))

