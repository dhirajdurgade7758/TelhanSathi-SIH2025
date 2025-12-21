"""
Redemption Store Routes
Manages gamified coin rewards and redemption offers for farmers.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect
from datetime import datetime, timedelta
from extensions import db
from models import Farmer, CoinBalance, CoinTransaction, RedemptionOffer, FarmerRedemption
import random
import string
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

redemption_bp = Blueprint('redemption', __name__, url_prefix='/redemption')

# ===== UTILITY FUNCTIONS =====

def get_current_farmer():
    """Get the current logged-in farmer from session."""
    farmer_id_verified = session.get('farmer_id_verified')
    logger.debug(f"Session farmer_id_verified: {farmer_id_verified}")
    logger.debug(f"Session keys: {list(session.keys())}")
    
    if not farmer_id_verified:
        logger.warning("No farmer_id_verified in session")
        return None
    
    # farmer_id_verified is the farmer's UUID, not the farmer_id (12-digit)
    farmer = Farmer.query.get(farmer_id_verified)
    logger.debug(f"Farmer query result: {farmer}")
    return farmer

def ensure_coin_balance(farmer):
    """Ensure farmer has a coin balance record."""
    if not farmer.coin_balance:
        coin_balance = CoinBalance(farmer_id=farmer.id)
        db.session.add(coin_balance)
        db.session.commit()
    return farmer.coin_balance

def generate_redemption_code():
    """Generate a unique redemption code."""
    code = 'TS' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    # Ensure uniqueness
    while FarmerRedemption.query.filter_by(redemption_code=code).first():
        code = 'TS' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return code

def initialize_redemption_offers():
    """Initialize default redemption offers in database."""
    # Check if offers already exist
    if RedemptionOffer.query.first():
        return
    
    offers = [
        # Category 1: Farm Inputs (Direct Savings)
        {
            'title': '20% Off on Hybrid Mustard Seeds',
            'description': 'Get quality hybrid mustard seeds at 20% discount. Perfect for oilseed cultivation.',
            'category': 'Farm Inputs',
            'coin_cost': 150,
            'icon': '🌱',
            'color': '#4CAF50',
            'offer_type': 'discount',
            'actual_value': '20% Off',
            'validity_days': 90
        },
        {
            'title': 'Free Bio-Pesticide Bottle (Neem Oil 500ml)',
            'description': 'Organic neem oil pesticide to protect your crops naturally.',
            'category': 'Farm Inputs',
            'coin_cost': 300,
            'icon': '🧪',
            'color': '#66BB6A',
            'offer_type': 'free',
            'actual_value': 'Free (Worth ₹300)',
            'validity_days': 60
        },
        {
            'title': '₹200 Discount on NPK Fertilizer Bag',
            'description': 'Save ₹200 on premium NPK fertilizer bags for better crop yield.',
            'category': 'Farm Inputs',
            'coin_cost': 250,
            'icon': '💰',
            'color': '#81C784',
            'offer_type': 'discount',
            'actual_value': '₹200 Off',
            'validity_days': 90
        },
        {
            'title': 'Free Micronutrient Mix Packet',
            'description': 'Zinc and Sulphur micronutrient mix for improved crop health.',
            'category': 'Farm Inputs',
            'coin_cost': 200,
            'icon': '⚗️',
            'color': '#2E7D32',
            'offer_type': 'free',
            'actual_value': 'Free (Worth ₹150)',
            'validity_days': 90
        },
        {
            'title': '"Buy 1 Get 1 Free" on Seed Treatment Chemicals',
            'description': 'Get 2 bottles of seed treatment chemicals for the price of one.',
            'category': 'Farm Inputs',
            'coin_cost': 100,
            'icon': '🎁',
            'color': '#4CAF50',
            'offer_type': 'bogo',
            'actual_value': 'Buy 1 Get 1 Free',
            'validity_days': 60
        },
        
        # Category 2: Services & Expert Access
        {
            'title': 'Free "Home Pickup" for Soil Testing',
            'description': 'We come to your farm for soil testing. No need to visit the lab!',
            'category': 'Services',
            'coin_cost': 200,
            'icon': '🚗',
            'color': '#2196F3',
            'offer_type': 'service',
            'actual_value': 'Free Service (Worth ₹500)',
            'validity_days': 30
        },
        {
            'title': 'Priority Video Call with KVK Scientist',
            'description': 'Get personalized advice from agriculture expert in 15-minute priority video call.',
            'category': 'Services',
            'coin_cost': 300,
            'icon': '👨‍🌾',
            'color': '#1976D2',
            'offer_type': 'service',
            'actual_value': 'Free 15-min Call',
            'validity_days': 30
        },
        {
            'title': 'Unlock "Premium Weather" (15-Day Forecast)',
            'description': 'Extended weather forecast for better planning. Standard is 5 days.',
            'category': 'Services',
            'coin_cost': 100,
            'icon': '🌤️',
            'color': '#0288D1',
            'offer_type': 'service',
            'actual_value': '15-Day Access',
            'validity_days': 60
        },
        {
            'title': 'Personalized Crop Doctor Report (PDF)',
            'description': 'Detailed analysis of your crop health with actionable recommendations.',
            'category': 'Services',
            'coin_cost': 50,
            'icon': '📋',
            'color': '#1565C0',
            'offer_type': 'service',
            'actual_value': 'Free Report',
            'validity_days': 90
        },
        {
            'title': 'Free SMS Alerts for Mandi Prices (1 Season)',
            'description': 'Get daily SMS alerts on crop prices at nearby mandis for one season.',
            'category': 'Services',
            'coin_cost': 50,
            'icon': '📱',
            'color': '#0D47A1',
            'offer_type': 'service',
            'actual_value': 'Free 1 Season',
            'validity_days': 150
        },
        
        # Category 3: Yantra Sathi (Rentals & Mechanization)
        {
            'title': '₹100 Off on Tractor Rental',
            'description': 'Save ₹100 on farm tractor rental for plowing or transportation.',
            'category': 'Yantra Sathi',
            'coin_cost': 150,
            'icon': '🚜',
            'color': '#FF6F00',
            'offer_type': 'discount',
            'actual_value': '₹100 Off',
            'validity_days': 60
        },
        {
            'title': 'Free Seed Drill Rental (1 Hour)',
            'description': 'Rent a seed drill machine for free for one hour.',
            'category': 'Yantra Sathi',
            'coin_cost': 400,
            'icon': '⚙️',
            'color': '#F57C00',
            'offer_type': 'free',
            'actual_value': 'Free 1 Hour',
            'validity_days': 30
        },
        {
            'title': '50% Off on Drone Spraying (Per Acre)',
            'description': 'Save 50% on drone pesticide spraying for efficient crop coverage.',
            'category': 'Yantra Sathi',
            'coin_cost': 500,
            'icon': '🚁',
            'color': '#FB8C00',
            'offer_type': 'discount',
            'actual_value': '50% Off',
            'validity_days': 45
        },
        {
            'title': 'Priority Booking for Harvester (Skip Waitlist)',
            'description': 'Skip the queue and get immediate booking for harvester service.',
            'category': 'Yantra Sathi',
            'coin_cost': 250,
            'icon': '✂️',
            'color': '#FFA726',
            'offer_type': 'service',
            'actual_value': 'Priority Booking',
            'validity_days': 60
        },
        {
            'title': 'Free Moisture Meter Usage (1 Day)',
            'description': 'Borrow a digital soil moisture meter for one day to check soil moisture.',
            'category': 'Yantra Sathi',
            'coin_cost': 100,
            'icon': '💧',
            'color': '#FFB74D',
            'offer_type': 'free',
            'actual_value': 'Free 1 Day',
            'validity_days': 30
        },
        
        # Category 4: Technology & Hardware
        {
            'title': '10% Off on Telhan Sathi IoT Sensor Kit',
            'description': 'Get our flagship IoT sensor kit at 10% discount. Smart farming made affordable.',
            'category': 'Technology',
            'coin_cost': 500,
            'icon': '📡',
            'color': '#5E35B1',
            'offer_type': 'discount',
            'actual_value': '10% Off',
            'validity_days': 90
        },
        {
            'title': 'Free Screen Guard for Smartphone',
            'description': 'Protect your phone screen while using Telhan Sathi app on field.',
            'category': 'Technology',
            'coin_cost': 150,
            'icon': '📱',
            'color': '#6A1B9A',
            'offer_type': 'free',
            'actual_value': 'Free',
            'validity_days': 30
        },
        {
            'title': 'Free Mobile Recharge (Data Pack - 1GB)',
            'description': 'Get 1GB data pack recharge to stay connected while farming.',
            'category': 'Technology',
            'coin_cost': 300,
            'icon': '📶',
            'color': '#7B1FA2',
            'offer_type': 'free',
            'actual_value': 'Free 1GB Data',
            'validity_days': 60
        },
        {
            'title': 'Discounted Soil pH Strips (Pack of 10)',
            'description': 'Test your soil pH easily with pack of 10 pH indicator strips.',
            'category': 'Technology',
            'coin_cost': 100,
            'icon': '📏',
            'color': '#8E24AA',
            'offer_type': 'discount',
            'actual_value': '30% Off',
            'validity_days': 90
        },
        
        # Category 5: VIP Status & Recognition
        {
            'title': '"Verified Seller" Badge on Marketplace (30 Days)',
            'description': 'Display a green verified badge on your marketplace profile. Buyers trust verified sellers!',
            'category': 'VIP',
            'coin_cost': 200,
            'icon': '✅',
            'color': '#C62828',
            'offer_type': 'badge',
            'actual_value': '30-Day Badge',
            'validity_days': 30
        },
        {
            'title': 'Digital "Progressive Farmer" Certificate',
            'description': 'Earn a shareable digital certificate to showcase on WhatsApp and social media.',
            'category': 'VIP',
            'coin_cost': 100,
            'icon': '🏆',
            'color': '#E53935',
            'offer_type': 'certificate',
            'actual_value': 'Digital Certificate',
            'validity_days': 365
        },
        {
            'title': 'Early Access to New Subsidy Schemes',
            'description': 'Get 24-hour early notification before subsidies are announced to the public.',
            'category': 'VIP',
            'coin_cost': 800,
            'icon': '⚡',
            'color': '#F44336',
            'offer_type': 'service',
            'actual_value': 'Early 24-hr Access',
            'validity_days': 180
        },
        {
            'title': 'Telhan Sathi Cap/T-Shirt (Merchandise)',
            'description': 'Official Telhan Sathi merchandise. Show your farming pride! Free shipping included.',
            'category': 'VIP',
            'coin_cost': 600,
            'icon': '👕',
            'color': '#D32F2F',
            'offer_type': 'merchandise',
            'actual_value': 'Free Merchandise',
            'validity_days': 30
        },
    ]
    
    for offer_data in offers:
        offer = RedemptionOffer(**offer_data)
        db.session.add(offer)
    
    db.session.commit()
    print(f"Initialized {len(offers)} redemption offers")


# ===== ROUTE HANDLERS =====

@redemption_bp.route('/store', methods=['GET'])
def redemption_store():
    """Display the redemption store page."""
    logger.debug(f"Redemption store page - Session: {dict(session)}")
    
    farmer = get_current_farmer()
    if not farmer:
        logger.warning("No farmer found in redemption_store - redirecting to login")
        return redirect('/login')
    
    # Initialize coin balance if needed
    coin_balance = ensure_coin_balance(farmer)
    
    # Initialize default offers if needed
    initialize_redemption_offers()
    
    # Render store page
    return render_template('redemption_store.html', farmer=farmer, coin_balance=coin_balance)


@redemption_bp.route('/api/offers', methods=['GET'])
def get_offers():
    """API endpoint to get all redemption offers with filters."""
    logger.debug(f"Getting offers - Session: {dict(session)}")
    
    farmer = get_current_farmer()
    if not farmer:
        logger.warning("No farmer found in get_offers")
        return jsonify({'error': 'Unauthorized'}), 401
    
    coin_balance = ensure_coin_balance(farmer)
    category = request.args.get('category')
    
    query = RedemptionOffer.query.filter_by(is_active=True)
    
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    offers = query.order_by(RedemptionOffer.created_at).all()
    
    return jsonify({
        'offers': [offer.to_dict() for offer in offers],
        'available_coins': coin_balance.available_coins,
        'total_coins': coin_balance.total_coins
    })


@redemption_bp.route('/api/balance', methods=['GET'])
def get_coin_balance():
    """Get current farmer's coin balance."""
    logger.debug(f"Getting coin balance - Session: {dict(session)}")
    
    farmer = get_current_farmer()
    if not farmer:
        logger.warning("No farmer found in get_coin_balance")
        return jsonify({'error': 'Unauthorized'}), 401
    
    logger.debug(f"Found farmer: {farmer.farmer_id}")
    coin_balance = ensure_coin_balance(farmer)
    
    return jsonify({
        'total_coins': coin_balance.total_coins,
        'available_coins': coin_balance.available_coins,
        'redeemed_coins': coin_balance.redeemed_coins,
        'farmer_name': farmer.name,
        'farmer_id': farmer.farmer_id
    })


@redemption_bp.route('/api/best-offer', methods=['GET'])
def get_best_offer():
    """Get the best affordable offer for the farmer."""
    logger.debug(f"Getting best offer - Session: {dict(session)}")
    
    farmer = get_current_farmer()
    if not farmer:
        logger.warning("No farmer found in get_best_offer")
        return jsonify({'error': 'Unauthorized'}), 401
    
    coin_balance = ensure_coin_balance(farmer)
    available_coins = coin_balance.available_coins
    
    # Get all active offers sorted by coin cost (ascending)
    offers = RedemptionOffer.query.filter_by(is_active=True).order_by(RedemptionOffer.coin_cost).all()
    
    if not offers:
        return jsonify({
            'has_offer': False,
            'available_coins': available_coins,
            'message': 'No offers available'
        })
    
    # Find best offer within budget
    best_offer = None
    for offer in offers:
        if available_coins >= offer.coin_cost:
            best_offer = offer
            break  # Get the cheapest one they can afford
    
    if best_offer:
        return jsonify({
            'has_offer': True,
            'available_coins': available_coins,
            'offer': best_offer.to_dict(),
            'can_redeem': True
        })
    else:
        # No offer within budget, recommend the cheapest one
        cheapest_offer = offers[0]
        coins_needed = cheapest_offer.coin_cost - available_coins
        
        return jsonify({
            'has_offer': True,
            'available_coins': available_coins,
            'offer': cheapest_offer.to_dict(),
            'can_redeem': False,
            'coins_needed': coins_needed,
            'message': f'Earn {coins_needed} more coins to redeem this offer!'
        })


@redemption_bp.route('/api/redeem', methods=['POST'])
def redeem_offer():
    """Redeem an offer using coins."""
    logger.debug(f"Redeem offer - Session: {dict(session)}")
    
    farmer = get_current_farmer()
    if not farmer:
        logger.warning("No farmer found in redeem_offer")
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    offer_id = data.get('offer_id')
    
    # Validate offer exists
    offer = RedemptionOffer.query.get(offer_id)
    if not offer:
        return jsonify({'error': 'Offer not found'}), 404
    
    if not offer.is_active:
        return jsonify({'error': 'Offer is no longer active'}), 400
    
    # Check stock availability
    if offer.stock_limit and offer.stock_redeemed >= offer.stock_limit:
        return jsonify({'error': 'Out of stock'}), 400
    
    # Get coin balance
    coin_balance = ensure_coin_balance(farmer)
    
    # Check if farmer has enough coins
    if coin_balance.available_coins < offer.coin_cost:
        return jsonify({'error': 'Insufficient coins', 'required': offer.coin_cost, 'available': coin_balance.available_coins}), 400
    
    try:
        # Create redemption record
        redemption_code = generate_redemption_code()
        expires_at = datetime.utcnow() + timedelta(days=offer.validity_days)
        
        redemption = FarmerRedemption(
            farmer_id=farmer.id,
            offer_id=offer_id,
            coins_spent=offer.coin_cost,
            redemption_code=redemption_code,
            expires_at=expires_at,
            status='active'
        )
        
        # Update coin balance
        coin_balance.available_coins -= offer.coin_cost
        coin_balance.redeemed_coins += offer.coin_cost
        coin_balance.updated_at = datetime.utcnow()
        
        # Update offer stock
        offer.stock_redeemed += 1
        
        # Record transaction
        transaction = CoinTransaction(
            coin_balance_id=coin_balance.id,
            transaction_type='redeemed',
            amount=offer.coin_cost,
            reason=f'Redeemed: {offer.title}',
            related_type='redemption_offer',
            related_id=offer_id
        )
        
        db.session.add(redemption)
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'redemption_code': redemption_code,
            'offer_title': offer.title,
            'expires_at': expires_at.isoformat(),
            'remaining_coins': coin_balance.available_coins
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@redemption_bp.route('/api/my-redemptions', methods=['GET'])
def get_my_redemptions():
    """Get farmer's redemption history."""
    logger.debug(f"Getting my redemptions - Session: {dict(session)}")
    
    farmer = get_current_farmer()
    if not farmer:
        logger.warning("No farmer found in get_my_redemptions")
        return jsonify({'error': 'Unauthorized'}), 401
    
    status = request.args.get('status', 'all')
    
    query = FarmerRedemption.query.filter_by(farmer_id=farmer.id)
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    redemptions = query.order_by(FarmerRedemption.redeemed_at.desc()).all()
    
    return jsonify({
        'redemptions': [redemption.to_dict() for redemption in redemptions]
    })


@redemption_bp.route('/my-orders', methods=['GET'])
def my_redemptions():
    """Display farmer's redemption history page."""
    farmer = get_current_farmer()
    if not farmer:
        return redirect('/login')
    
    coin_balance = ensure_coin_balance(farmer)
    
    return render_template('redemption_orders.html', farmer=farmer, coin_balance=coin_balance)


@redemption_bp.route('/api/add-coins', methods=['POST'])
def add_coins_manual():
    """Admin endpoint to add coins to farmer (for testing/admin purposes)."""
    farmer = get_current_farmer()
    if not farmer:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    amount = data.get('amount', 0)
    reason = data.get('reason', 'Manual Addition')
    
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    try:
        coin_balance = ensure_coin_balance(farmer)
        
        coin_balance.total_coins += amount
        coin_balance.available_coins += amount
        coin_balance.updated_at = datetime.utcnow()
        
        transaction = CoinTransaction(
            coin_balance_id=coin_balance.id,
            transaction_type='earned',
            amount=amount,
            reason=reason
        )
        
        farmer.coins_earned += amount
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'total_coins': coin_balance.total_coins,
            'available_coins': coin_balance.available_coins
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
