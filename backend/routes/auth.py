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
from models_marketplace import Chat, ChatMessage

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
def login_with_farmer_id():
    """Handle login with Farmer ID"""
    farmer_id = request.form.get('farmer_id', '').strip()
    
    if not farmer_id:
        return render_template('login.html', error='Please enter your Farmer ID')
    
    # Check if farmer exists
    farmer = Farmer.query.filter_by(farmer_id=farmer_id).first()
    if not farmer:
        return render_template('login.html', error='Farmer not found. Please contact support.')
    
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
    session['login_method'] = 'farmer_id'
    
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


@auth_bp.route('/login-with-mobile', methods=['POST'])
def login_with_mobile():
    """Handle login with mobile number - creates new farmer if needed"""
    import re
    import random
    import string
    
    mobile_number = request.form.get('mobile_number', '').strip()
    
    if not mobile_number:
        return render_template('login.html', error='Please enter your mobile number')
    
    # Validate mobile number format (Indian: 10 digits, optionally with +91 prefix)
    mobile_pattern = r'^(\+91)?[6-9]\d{9}$'
    if not re.match(mobile_pattern, mobile_number):
        return render_template('login.html', error='Please enter a valid 10-digit mobile number')
    
    # Normalize mobile number (remove +91 if present, keep only 10 digits)
    mobile_number = mobile_number.lstrip('+91').lstrip('0')
    if len(mobile_number) != 10:
        mobile_number = mobile_number[-10:]  # Take last 10 digits
    
    # Try to find farmer with this phone number
    farmer = Farmer.query.filter_by(phone_number=mobile_number).first()
    
    # If farmer doesn't exist, create new one
    if not farmer:
        try:
            # Generate unique farmer_id (12-digit format: MMMXXXXXXXX where MMM=Maharashtra code 100, XXXXXXXX=random)
            def generate_farmer_id():
                # Maharashtra code + 8 random digits
                while True:
                    farmer_id = '100' + ''.join([str(random.randint(0, 9)) for _ in range(9)])
                    # Check if this ID already exists
                    if not Farmer.query.filter_by(farmer_id=farmer_id).first():
                        return farmer_id
            
            # Create new farmer with minimal data
            farmer = Farmer(
                farmer_id=generate_farmer_id(),
                phone_number=mobile_number,
                name=f'Farmer_{mobile_number}',  # Temporary name, will be updated in extended onboarding
                district='',  # Will be updated in extended onboarding
                onboarding_completed=False,
                is_verified=True  # Mark as verified since they'll complete onboarding
            )
            db.session.add(farmer)
            db.session.commit()
            
            # Mark for extended onboarding flow
            session['new_farmer'] = True
            session['needs_extended_onboarding'] = True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating farmer: {str(e)}")  # Log the error for debugging
            return render_template('login.html', error='Error creating farmer profile. Please try again.')
    else:
        # Clear extended onboarding flag for existing farmers
        session['new_farmer'] = False
        session['needs_extended_onboarding'] = False
    
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
    send_otp_sms(mobile_number, otp_code)
    
    # Store in session
    session['farmer_id'] = farmer.farmer_id
    session['phone_number'] = mobile_number
    session['login_method'] = 'mobile'
    session['internal_farmer_id'] = farmer.id  # Store internal ID for queries
    
    # Redirect to OTP verification page
    phone_masked = mobile_number[-4:]
    return render_template('otp.html', farmer_id=farmer.farmer_id, phone_masked=phone_masked)


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

    # Check if this is a new farmer logging in via mobile - send to extended onboarding
    if session.get('needs_extended_onboarding'):
        return redirect(url_for('onboarding.extended_onboarding'))
    
    # Else redirect to standard onboarding
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
    
    return render_template('profile.html', farmer=farmer.to_dict())



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


@auth_bp.route('/logout')
def logout():
    """Clear session and log the user out"""
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/api/me', methods=['GET'])
def api_current_farmer():
    """Return current logged-in farmer info as JSON (protected)"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Unauthorized', 'status': 401}), 401
    farmer_id = session.get('farmer_id_verified')
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    if not farmer:
        return jsonify({'error': 'Farmer not found', 'status': 404}), 404
    return jsonify({
        'id': farmer.id,
        'name': farmer.name,
        'farmer_id': farmer.farmer_id,
        'phone': farmer.phone_number,
        'village': farmer.village,
        'taluka': farmer.taluka,
        'district': farmer.district,
        'state': farmer.state,
        'total_land_area_hectares': farmer.total_land_area_hectares,
        'land_type': farmer.soil_type,
        'current_crops': farmer.current_crops,
        'water_type': farmer.water_type,
        'is_verified': farmer.is_verified,
        'photo_url': None,
        'date_of_birth': farmer.date_of_birth.isoformat() if farmer.date_of_birth else None,
        'gender': farmer.gender
    })


# ===== FARMER CHAT API =====

@auth_bp.route('/chats')
@login_required
def farmer_chats():
    """Render farmer chats page"""
    return render_template('farmer_chats.html')


@auth_bp.route('/api/farmer/chats', methods=['GET'])
def get_farmer_chats():
    """Get all chats for farmer"""
    try:
        farmer_id_verified = session.get('farmer_id_verified')
        if not farmer_id_verified:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get all chats for this farmer
        chats = Chat.query.filter_by(farmer_id=farmer_id_verified, is_active=True).order_by(Chat.last_message_at.desc()).all()
        
        chats_data = []
        for chat in chats:
            # Get last message
            last_message = ChatMessage.query.filter_by(chat_id=chat.id).order_by(ChatMessage.created_at.desc()).first()
            
            chats_data.append({
                'id': chat.id,
                'buyer_id': chat.buyer_id,
                'crop_name': chat.crop_name,
                'sell_request_id': chat.sell_request_id,
                'buyer_offer_id': chat.buyer_offer_id,
                'is_active': chat.is_active,
                'created_at': chat.created_at.isoformat(),
                'last_message': {
                    'text': last_message.message if last_message else None,
                    'sender': last_message.sender_type if last_message else None,
                    'time': last_message.created_at.isoformat() if last_message else None
                },
                'message_count': len(chat.messages)
            })
        
        return jsonify(chats_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/farmer/chats/<chat_id>/messages', methods=['GET'])
def get_farmer_chat_messages(chat_id):
    """Get all messages in a chat for farmer"""
    try:
        farmer_id_verified = session.get('farmer_id_verified')
        if not farmer_id_verified:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Verify chat belongs to farmer
        chat = Chat.query.filter_by(id=chat_id, farmer_id=farmer_id_verified).first()
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        # Get all messages
        messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.created_at.asc()).all()
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'sender_type': msg.sender_type,
                'sender_name': msg.sender_name,
                'message': msg.message,
                'created_at': msg.created_at.isoformat(),
                'is_read': msg.is_read
            })
        
        return jsonify(messages_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/api/farmer/chats/<chat_id>/messages', methods=['POST'])
def send_farmer_chat_message(chat_id):
    """Send a message in chat as farmer"""
    try:
        farmer_id_verified = session.get('farmer_id_verified')
        if not farmer_id_verified:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Verify chat belongs to farmer
        chat = Chat.query.filter_by(id=chat_id, farmer_id=farmer_id_verified).first()
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        # Get farmer name from session or database
        farmer = Farmer.query.filter_by(farmer_id=farmer_id_verified).first()
        farmer_name = farmer.name if farmer else "Farmer"
        
        data = request.get_json()
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Create message
        new_message = ChatMessage(
            chat_id=chat_id,
            sender_type='farmer',
            sender_id=farmer_id_verified,
            sender_name=farmer_name,
            message=message_text
        )
        
        # Update chat's last_message_at
        chat.last_message_at = datetime.utcnow()
        
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({
            'id': new_message.id,
            'message': new_message.message,
            'sender_type': new_message.sender_type,
            'created_at': new_message.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

