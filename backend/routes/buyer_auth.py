from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sys
import os
import requests

# Avoid circular imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models_marketplace import Buyer, SellRequest, BuyerOffer, Chat, ChatMessage, MarketPrice
from extensions import db

buyer_auth_bp = Blueprint('buyer_auth', __name__, url_prefix='/buyer')

# ===== BUYER LOGIN ROUTES =====

@buyer_auth_bp.route('/login', methods=['GET'])
def buyer_login():
    """Render buyer login page"""
    return render_template('buyer_login.html')


@buyer_auth_bp.route('/login', methods=['POST'])
def buyer_login_post():
    """Handle buyer login"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    
    if not email or not password:
        return render_template('buyer_login.html', error='Email and password are required')
    
    # Find buyer by email
    buyer = Buyer.query.filter_by(email=email).first()
    
    if not buyer:
        return render_template('buyer_login.html', error='Email not found')
    
    # Check if buyer is active
    if not buyer.is_active:
        return render_template('buyer_login.html', error='This account has been deactivated')
    
    # Verify password
    if not check_password_hash(buyer.password, password):
        return render_template('buyer_login.html', error='Invalid password')
    
    # Set session
    session['buyer_id_verified'] = buyer.id
    session['buyer_email'] = buyer.email
    session['buyer_name'] = buyer.buyer_name
    
    # Redirect to buyer dashboard
    return redirect(url_for('buyer_auth.buyer_dashboard'))


@buyer_auth_bp.route('/register', methods=['GET'])
def buyer_register():
    """Render buyer registration page"""
    return render_template('buyer_register.html')


@buyer_auth_bp.route('/register', methods=['POST'])
def buyer_register_post():
    """Handle buyer registration"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    buyer_name = request.form.get('buyer_name', '').strip()
    phone = request.form.get('phone', '').strip()
    company_name = request.form.get('company_name', '').strip()
    district = request.form.get('district', '').strip()
    state = request.form.get('state', 'Maharashtra').strip()
    
    # Validation
    if not email or not password or not buyer_name:
        return render_template('buyer_register.html', error='Email, password, and name are required')
    
    if password != confirm_password:
        return render_template('buyer_register.html', error='Passwords do not match')
    
    if len(password) < 6:
        return render_template('buyer_register.html', error='Password must be at least 6 characters')
    
    # Check if email already exists
    existing_buyer = Buyer.query.filter_by(email=email).first()
    if existing_buyer:
        return render_template('buyer_register.html', error='Email already registered')
    
    try:
        # Create new buyer
        buyer = Buyer(
            email=email,
            password=generate_password_hash(password),
            buyer_name=buyer_name,
            phone=phone,
            company_name=company_name,
            district=district,
            state=state,
            is_verified=True,
            is_active=True
        )
        
        db.session.add(buyer)
        db.session.commit()
        
        # Set session
        session['buyer_id_verified'] = buyer.id
        session['buyer_email'] = buyer.email
        session['buyer_name'] = buyer.buyer_name
        
        # Redirect to dashboard
        return redirect(url_for('buyer_auth.buyer_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating buyer: {str(e)}")
        return render_template('buyer_register.html', error='Error creating account. Please try again.')


@buyer_auth_bp.route('/logout')
def buyer_logout():
    """Handle buyer logout"""
    session.clear()
    return redirect(url_for('buyer_auth.buyer_login'))


# ===== BUYER DASHBOARD =====

@buyer_auth_bp.route('/dashboard')
def buyer_dashboard():
    """Render buyer dashboard"""
    if 'buyer_id_verified' not in session:
        return redirect(url_for('buyer_auth.buyer_login'))
    
    buyer = Buyer.query.filter_by(id=session.get('buyer_id_verified')).first()
    if not buyer:
        session.clear()
        return redirect(url_for('buyer_auth.buyer_login'))
    
    return render_template('buyer_dashboard.html', buyer=buyer)


@buyer_auth_bp.route('/api/profile')
def buyer_profile():
    """Get buyer profile as JSON"""
    if 'buyer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    buyer = Buyer.query.filter_by(id=session.get('buyer_id_verified')).first()
    if not buyer:
        return jsonify({'error': 'Buyer not found'}), 404
    
    return jsonify({
        'id': buyer.id,
        'email': buyer.email,
        'buyer_name': buyer.buyer_name,
        'phone': buyer.phone,
        'company_name': buyer.company_name,
        'location': buyer.location,
        'district': buyer.district,
        'state': buyer.state,
        'is_verified': buyer.is_verified,
        'created_at': buyer.created_at.isoformat() if buyer.created_at else None
    })


@buyer_auth_bp.route('/api/my-offers')
def buyer_my_offers():
    """Get buyer's own offers (buyer-created independent offers)"""
    if 'buyer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    buyer_id = session.get('buyer_id_verified')
    
    # Import here to avoid circular imports
    from models_marketplace import BuyerOffer
    
    # Get all buyer offers for this buyer (independent offers, not linked to sell requests)
    offers = BuyerOffer.query.filter_by(buyer_id=buyer_id).all()
    
    offers_data = []
    for offer in offers:
        offers_data.append({
            'id': offer.id,
            'crop_name': offer.crop_name,
            'quantity_quintal': offer.quantity_quintal,
            'location_wanted': offer.location_wanted,
            'district_wanted': offer.district_wanted,
            'initial_price': offer.initial_price,
            'final_price': offer.final_price,
            'status': offer.status,
            'buyer_name': offer.buyer_name,
            'buyer_mobile': offer.buyer_mobile,
            'buyer_location': offer.buyer_location,
            'buyer_company': offer.buyer_company,
            'created_at': offer.created_at.isoformat() if offer.created_at else None,
            'updated_at': offer.updated_at.isoformat() if offer.updated_at else None
        })
    
    return jsonify(offers_data)


@buyer_auth_bp.route('/api/create-offer', methods=['POST'])
def create_offer():
    """Create a new independent buyer offer (not linked to farmer's listing)"""
    if 'buyer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        buyer_id = session.get('buyer_id_verified')
        buyer_email = session.get('buyer_email')
        buyer_name = session.get('buyer_name')
        
        data = request.get_json()
        
        # Required fields
        crop_name = data.get('crop_name')
        quantity_quintal = data.get('quantity_quintal')
        initial_price = data.get('initial_price')
        
        # Optional fields
        location_wanted = data.get('location_wanted', '')
        district_wanted = data.get('district_wanted', '')
        
        # Validation
        if not crop_name or not quantity_quintal or not initial_price:
            return jsonify({'error': 'crop_name, quantity_quintal, and initial_price are required'}), 400
        
        # Validate quantity and price
        try:
            quantity_quintal = float(quantity_quintal)
            initial_price = float(initial_price)
            
            if quantity_quintal <= 0:
                return jsonify({'error': 'Quantity must be greater than 0'}), 400
            if initial_price <= 0:
                return jsonify({'error': 'Price must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid quantity or price format'}), 400
        
        # Import models
        from models_marketplace import BuyerOffer, Buyer
        import uuid
        
        # Get buyer info
        buyer = Buyer.query.get(buyer_id)
        
        # Create new independent offer
        new_offer = BuyerOffer(
            id=str(uuid.uuid4()),
            buyer_id=buyer_id,
            buyer_name=buyer_name or (buyer.buyer_name if buyer else 'Unknown'),
            buyer_mobile=buyer.phone if buyer else '',
            buyer_location=buyer.location if buyer else '',
            buyer_company=buyer.company_name if buyer else '',
            crop_name=crop_name,
            quantity_quintal=quantity_quintal,
            location_wanted=location_wanted,
            district_wanted=district_wanted,
            initial_price=initial_price,
            final_price=None,
            status='pending'
        )
        
        db.session.add(new_offer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Offer created successfully! Farmers in the marketplace can now see your offer.',
            'offer': {
                'id': new_offer.id,
                'crop_name': new_offer.crop_name,
                'quantity_quintal': new_offer.quantity_quintal,
                'initial_price': new_offer.initial_price,
                'status': new_offer.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create offer: {str(e)}'}), 500


@buyer_auth_bp.route('/api/marketplace-offers')
def marketplace_offers():
    """Get all buyer offers available in the marketplace (for farmers to see)
    
    Optional query parameters:
    - crop_name: Filter by crop name
    - district: Filter by district_wanted
    - location: Filter by location_wanted
    """
    from models_marketplace import BuyerOffer
    
    # Get query parameters for filtering
    crop_name = request.args.get('crop_name', '').strip().lower()
    district = request.args.get('district', '').strip().lower()
    location = request.args.get('location', '').strip().lower()
    
    # Get all pending buyer offers (that haven't been accepted yet)
    query = BuyerOffer.query.filter_by(status='pending')
    
    # Apply filters if provided
    if crop_name:
        query = query.filter(BuyerOffer.crop_name.ilike(f'%{crop_name}%'))
    
    if district:
        query = query.filter(BuyerOffer.district_wanted.ilike(f'%{district}%'))
    
    if location:
        query = query.filter(BuyerOffer.location_wanted.ilike(f'%{location}%'))
    
    offers = query.all()
    
    offers_data = []
    for offer in offers:
        offers_data.append({
            'id': offer.id,
            'crop_name': offer.crop_name,
            'quantity_quintal': offer.quantity_quintal,
            'location_wanted': offer.location_wanted,
            'district_wanted': offer.district_wanted,
            'initial_price': offer.initial_price,
            'buyer_name': offer.buyer_name,
            'buyer_mobile': offer.buyer_mobile,
            'buyer_company': offer.buyer_company,
            'buyer_location': offer.buyer_location,
            'status': offer.status,
            'created_at': offer.created_at.isoformat() if offer.created_at else None
        })
    
    return jsonify(offers_data)


@buyer_auth_bp.route('/api/offers/<offer_id>', methods=['DELETE'])
def delete_offer(offer_id):
    """Delete a buyer offer"""
    if 'buyer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    from models_marketplace import BuyerOffer
    
    buyer_id = session.get('buyer_id_verified')
    offer = BuyerOffer.query.filter_by(id=offer_id, buyer_id=buyer_id).first()
    
    if not offer:
        return jsonify({'error': 'Offer not found or unauthorized'}), 404
    
    try:
        db.session.delete(offer)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Offer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@buyer_auth_bp.route('/api/offers/<offer_id>', methods=['PUT'])
def update_offer(offer_id):
    """Update a buyer offer"""
    if 'buyer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    from models_marketplace import BuyerOffer
    
    try:
        buyer_id = session.get('buyer_id_verified')
        offer = BuyerOffer.query.filter_by(id=offer_id, buyer_id=buyer_id).first()
        
        if not offer:
            return jsonify({'error': 'Offer not found or unauthorized'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'crop_name' in data:
            offer.crop_name = data['crop_name']
        if 'quantity_quintal' in data:
            offer.quantity_quintal = float(data['quantity_quintal'])
        if 'initial_price' in data:
            offer.initial_price = float(data['initial_price'])
        if 'location_wanted' in data:
            offer.location_wanted = data['location_wanted']
        if 'district_wanted' in data:
            offer.district_wanted = data['district_wanted']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Offer updated successfully',
            'offer': {
                'id': offer.id,
                'crop_name': offer.crop_name,
                'quantity_quintal': offer.quantity_quintal,
                'initial_price': offer.initial_price,
                'status': offer.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@buyer_auth_bp.route('/api/sell-requests', methods=['GET'])
def get_sell_requests():
    """Get sell requests that match buyer's offer crops"""
    try:
        # Check if buyer is logged in
        buyer_id = session.get('buyer_id_verified')
        if not buyer_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get all crops the buyer has offers for
        buyer_offers = BuyerOffer.query.filter_by(buyer_id=buyer_id).all()
        
        if not buyer_offers:
            return jsonify([]), 200
        
        # Extract unique crop names from buyer's offers
        buyer_crops = set(offer.crop_name.lower() for offer in buyer_offers)
        
        # Fetch all pending sell requests
        all_sell_requests = SellRequest.query.filter_by(status='pending').order_by(SellRequest.created_at.desc()).all()
        
        # Filter to only show sell requests for crops the buyer is interested in
        matching_requests = [
            sr for sr in all_sell_requests 
            if sr.crop_name.lower() in buyer_crops
        ]
        
        # Format response
        requests_data = []
        for sr in matching_requests:
            # Get photos for this sell request
            photos = [photo.photo_url for photo in sr.photos] if sr.photos else []
            
            requests_data.append({
                'id': sr.id,
                'farmer_id': sr.farmer_id,
                'crop_name': sr.crop_name,
                'quantity_quintal': sr.quantity_quintal,
                'expected_price': sr.expected_price,
                'harvest_date': sr.harvest_date,
                'location': sr.location,
                'farmer_name': sr.farmer_name,
                'farmer_phone': sr.farmer_phone,
                'status': sr.status,
                'photos': photos,
                'created_at': sr.created_at.isoformat() if sr.created_at else None
            })
        
        return jsonify(requests_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== CHAT API =====

@buyer_auth_bp.route('/api/chats', methods=['GET'])
def get_buyer_chats():
    """Get all chats initiated by buyer"""
    try:
        buyer_id = session.get('buyer_id_verified')
        if not buyer_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get all chats for this buyer
        chats = Chat.query.filter_by(buyer_id=buyer_id, is_active=True).order_by(Chat.last_message_at.desc()).all()
        
        chats_data = []
        for chat in chats:
            # Get last message
            last_message = ChatMessage.query.filter_by(chat_id=chat.id).order_by(ChatMessage.created_at.desc()).first()
            
            chats_data.append({
                'id': chat.id,
                'farmer_id': chat.farmer_id,
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


@buyer_auth_bp.route('/api/chats', methods=['POST'])
def create_chat():
    """Create or get existing chat with farmer"""
    try:
        buyer_id = session.get('buyer_id_verified')
        if not buyer_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        farmer_id = data.get('farmer_id')
        sell_request_id = data.get('sell_request_id')
        crop_name = data.get('crop_name')
        
        if not farmer_id or not crop_name:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if chat already exists
        existing_chat = Chat.query.filter_by(
            buyer_id=buyer_id,
            farmer_id=farmer_id,
            crop_name=crop_name
        ).first()
        
        if existing_chat:
            return jsonify({'id': existing_chat.id}), 200
        
        # Create new chat
        new_chat = Chat(
            buyer_id=buyer_id,
            farmer_id=farmer_id,
            sell_request_id=sell_request_id,
            crop_name=crop_name
        )
        
        db.session.add(new_chat)
        db.session.commit()
        
        return jsonify({'id': new_chat.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@buyer_auth_bp.route('/api/chats/<chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id):
    """Get all messages in a chat"""
    try:
        buyer_id = session.get('buyer_id_verified')
        if not buyer_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Verify chat belongs to buyer
        chat = Chat.query.filter_by(id=chat_id, buyer_id=buyer_id).first()
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


@buyer_auth_bp.route('/api/chats/<chat_id>/messages', methods=['POST'])
def send_chat_message(chat_id):
    """Send a message in chat"""
    try:
        buyer_id = session.get('buyer_id_verified')
        buyer_name = session.get('buyer_name')
        if not buyer_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Verify chat belongs to buyer
        chat = Chat.query.filter_by(id=chat_id, buyer_id=buyer_id).first()
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        data = request.get_json()
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Create message
        new_message = ChatMessage(
            chat_id=chat_id,
            sender_type='buyer',
            sender_id=buyer_id,
            sender_name=buyer_name,
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


# ===== MARKET PRICE ENDPOINTS =====

# Oilseed commodity mappings for Data.gov.in API
OILSEED_COMMODITIES = {
    'Soybean': 'Soyabean',
    'Sunflower': 'Sunflower',
    'Mustard': 'Mustard/Rape seed',
    'Groundnut': 'Groundnut',
    'Safflower': 'Safflower',
    'Castor': 'Castor'
}

API_KEY = '579b464db66ec23bdd00000139dd36efa19740c954f95d9ca3b5abd0'


@buyer_auth_bp.route('/api/sync-prices', methods=['POST'])
def sync_market_prices():
    """
    Sync commodity prices from Data.gov.in API
    Fetches latest prices for oilseed commodities
    """
    try:
        synced_count = 0
        errors = []
        
        # Call Data.gov.in API for each commodity
        for commodity_key, commodity_api_name in OILSEED_COMMODITIES.items():
            try:
                # Data.gov.in API endpoint
                api_url = "https://api.data.gov.in/resource/5e4ff2f1-d728-49b5-b92e-12640c4e3ede"
                
                params = {
                    'api-key': API_KEY,
                    'format': 'json',
                    'filters[commodity_name]': commodity_api_name,
                    'limit': 1000
                }
                
                response = requests.get(api_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if 'records' in data:
                    for record in data['records']:
                        try:
                            # Extract data from API response
                            commodity_name = record.get('commodity_name', commodity_key)
                            market_name = record.get('market', '')
                            market_state = record.get('state', '')
                            market_district = record.get('district', '')
                            
                            # Parse prices
                            open_price = float(record.get('arrival_date', 0)) if record.get('arrival_date') else None
                            close_price = float(record.get('modal_price', 0)) if record.get('modal_price') else None
                            high_price = float(record.get('max_price', 0)) if record.get('max_price') else None
                            low_price = float(record.get('min_price', 0)) if record.get('min_price') else None
                            
                            # Price date
                            price_date_str = record.get('arrival_date', '')
                            try:
                                price_date = datetime.strptime(price_date_str, '%d/%m/%Y').date()
                            except:
                                price_date = datetime.utcnow().date()
                            
                            # Check if record exists
                            existing = MarketPrice.query.filter_by(
                                commodity_name=commodity_name,
                                market_name=market_name,
                                price_date=price_date
                            ).first()
                            
                            if existing:
                                # Update existing record
                                existing.open_price = open_price
                                existing.close_price = close_price
                                existing.high_price = high_price
                                existing.low_price = low_price
                                existing.updated_at = datetime.utcnow()
                                db.session.add(existing)
                            else:
                                # Create new record
                                new_price = MarketPrice(
                                    commodity_name=commodity_name,
                                    market_name=market_name,
                                    market_state=market_state,
                                    market_district=market_district,
                                    open_price=open_price,
                                    high_price=high_price,
                                    low_price=low_price,
                                    close_price=close_price,
                                    price_date=price_date
                                )
                                db.session.add(new_price)
                                synced_count += 1
                        except Exception as e:
                            errors.append(f"Error processing record: {str(e)}")
                            continue
                
                db.session.commit()
                
            except requests.exceptions.RequestException as e:
                errors.append(f"API error for {commodity_key}: {str(e)}")
            except Exception as e:
                errors.append(f"Processing error for {commodity_key}: {str(e)}")
        
        return jsonify({
            'success': True,
            'synced_count': synced_count,
            'errors': errors if errors else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@buyer_auth_bp.route('/api/prices/<commodity>', methods=['GET'])
def get_commodity_prices(commodity):
    """
    Get market prices for a specific commodity
    Returns last 7 days of prices across all mandis
    """
    try:
        # Normalize commodity name
        commodity = commodity.strip()
        
        # Find prices
        prices = MarketPrice.query.filter_by(commodity_name=commodity).order_by(
            MarketPrice.price_date.desc()
        ).limit(1000).all()
        
        if not prices:
            return jsonify({
                'commodity': commodity,
                'prices': [],
                'message': 'No price data available'
            }), 200
        
        # Group by market and get latest prices
        market_prices = {}
        for price in prices:
            market_key = f"{price.market_name}, {price.market_state}"
            if market_key not in market_prices:
                market_prices[market_key] = {
                    'market_name': price.market_name,
                    'market_state': price.market_state,
                    'market_district': price.market_district,
                    'prices': []
                }
            
            market_prices[market_key]['prices'].append({
                'date': price.price_date.isoformat(),
                'open': price.open_price,
                'high': price.high_price,
                'low': price.low_price,
                'close': price.close_price,
                'volume': price.trading_volume
            })
        
        return jsonify({
            'commodity': commodity,
            'markets': list(market_prices.values()),
            'total_records': len(prices)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


