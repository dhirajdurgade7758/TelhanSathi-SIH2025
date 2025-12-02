from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from datetime import datetime
from functools import wraps
import sys
import os

# Avoid circular imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Farmer, OTPRecord
from extensions import db
from utils import generate_otp, send_otp_sms, calculate_otp_expiry, is_farmer_eligible_for_subsidy

auth_bp = Blueprint('auth', __name__)

# ===== AUTHENTICATION DECORATOR =====
def login_required(f):
    """Decorator to check if user is logged in (OTP verified)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if farmer_id_verified exists in session (means OTP was verified)
        if 'farmer_id_verified' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== LOGIN FLOW ROUTES (Jinja2 Templating) =====

@auth_bp.route('/login', methods=['GET'])
def login():
    """Serve login page"""
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    """Handle login form submission - Farmer ID input"""
    farmer_id = request.form.get('farmer_id', '').strip()
    
    if not farmer_id:
        return render_template('login.html', error='Please enter your Farmer ID')
    
    # Check if farmer exists
    farmer = Farmer.query.filter_by(farmer_id=farmer_id).first()
    if not farmer:
        return render_template('login.html', error='Farmer not found. Please register first.')
    
    # Generate and send OTP
    otp_code = generate_otp()
    otp_record = OTPRecord(
        farmer_id=farmer.id,
        otp_code=otp_code,
        expires_at=calculate_otp_expiry()
    )
    
    db.session.add(otp_record)
    db.session.commit()
    
    # Send OTP
    send_otp_sms(farmer.phone_number, otp_code)
    
    # Store farmer_id in session
    session['farmer_id'] = farmer_id
    session['phone_number'] = farmer.phone_number
    
    # Redirect to OTP verification page
    phone_masked = farmer.phone_number[-4:] + '****'
    return render_template('otp.html', farmer_id=farmer_id, phone_masked=phone_masked)


@auth_bp.route('/otp', methods=['GET'])
def otp():
    """Serve OTP page - called from login"""
    farmer_id = session.get('farmer_id')
    phone_masked = session.get('phone_number', '')
    if phone_masked:
        phone_masked = phone_masked[-4:] + '****'
    
    if not farmer_id:
        return redirect(url_for('auth.login'))
    
    return render_template('otp.html', farmer_id=farmer_id, phone_masked=phone_masked)


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp_post():
    """Handle OTP verification"""
    farmer_id = request.form.get('farmer_id', '').strip()
    otp_code = request.form.get('otp_code', '').strip()
    
    if not farmer_id or not otp_code:
        phone_masked = session.get('phone_number', '')
        if phone_masked:
            phone_masked = phone_masked[-4:] + '****'
        return render_template('otp.html', farmer_id=farmer_id, phone_masked=phone_masked, error='Invalid OTP input')
    
    # Find farmer
    farmer = Farmer.query.filter_by(farmer_id=farmer_id).first()
    if not farmer:
        phone_masked = session.get('phone_number', '')
        if phone_masked:
            phone_masked = phone_masked[-4:] + '****'
        return render_template('otp.html', farmer_id=farmer_id, phone_masked=phone_masked, error='Farmer not found')
    
    # Find latest OTP record
    otp_record = OTPRecord.query.filter_by(
        farmer_id=farmer.id,
        otp_code=otp_code,
        is_verified=False
    ).order_by(OTPRecord.created_at.desc()).first()
    
    if not otp_record:
        phone_masked = session.get('phone_number', '')
        if phone_masked:
            phone_masked = phone_masked[-4:] + '****'
        return render_template('otp.html', farmer_id=farmer_id, phone_masked=phone_masked, error='Invalid OTP')
    
    # Check expiry
    if otp_record.is_expired():
        phone_masked = session.get('phone_number', '')
        if phone_masked:
            phone_masked = phone_masked[-4:] + '****'
        return render_template('otp.html', farmer_id=farmer_id, phone_masked=phone_masked, error='OTP has expired')
    
    # Mark OTP as verified
    otp_record.is_verified = True
    otp_record.verified_at = datetime.utcnow()
    farmer.is_verified = True
    farmer.verification_timestamp = datetime.utcnow()
    
    db.session.commit()
    
    # Store farmer info in session
    session['farmer_id_verified'] = farmer.id
    session['farmer_kisan_id'] = farmer.farmer_id
    
    # If the farmer has completed onboarding previously, go to dashboard.
    # Otherwise start onboarding to collect minimal context.
    try:
        if getattr(farmer, 'onboarding_completed', False):
            return redirect(url_for('dashboard'))
    except Exception:
        # If any issue accessing the flag, fall back to onboarding
        pass

    return redirect(url_for('onboarding.onboarding'))


@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Serve profile page after OTP verification (login required)"""
    farmer_id = session.get('farmer_id_verified')
    
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    if not farmer:
        session.clear()
        return redirect(url_for('auth.login'))
    
    return render_template('profile.html', farmer=farmer)


@auth_bp.route('/continue-to-dashboard', methods=['POST'])
@login_required
def continue_to_dashboard():
    """Handle continue button - routes based on farmer status"""
    farmer_id = session.get('farmer_id_verified')
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    
    if not farmer:
        session.clear()
        return redirect(url_for('auth.login'))
    # Route to dashboard (Sahayak) for all users - bot will handle suggestions
    return redirect(url_for('dashboard'))


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP via JSON API"""
    data = request.get_json()
    farmer_id = data.get('farmer_id', '').strip()
    
    farmer = Farmer.query.filter_by(farmer_id=farmer_id).first()
    if not farmer:
        return jsonify({'success': False, 'error': 'Farmer not found'}), 404
    
    # Generate and send new OTP
    otp_code = generate_otp()
    otp_record = OTPRecord(
        farmer_id=farmer.id,
        otp_code=otp_code,
        expires_at=calculate_otp_expiry()
    )
    
    db.session.add(otp_record)
    db.session.commit()
    
    send_otp_sms(farmer.phone_number, otp_code)
    
    return jsonify({'success': True, 'message': 'OTP resent successfully'}), 200


@auth_bp.route('/register', methods=['GET'])
def register():
    """Serve registration page (placeholder)"""
    return render_template('register.html')
