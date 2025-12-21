"""
Real-Time Bidding System API Routes
Provides endpoints for auction management, bidding, and transaction handling
"""

from flask import Blueprint, jsonify, request, session, render_template
from functools import wraps
from datetime import datetime, timedelta
from extensions import db
from models_marketplace import Auction, Bid, Transaction, BidHistory, AuctionNotification, Buyer
from models import Farmer
import requests
import uuid
import os
from werkzeug.utils import secure_filename

bidding_bp = Blueprint('bidding', __name__, url_prefix='/bidding')

# Government Mandi API Configuration
GOVT_API_KEY = "579b464db66ec23bdd00000139dd36efa19740c954f95d9ca3b5abd0"
GOVT_API_BASE = "https://api.data.gov.in/resource/9ef84268-d588-465a-a5c3-375cda092f58"

# File upload configuration
UPLOAD_FOLDER = 'static/auction_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def farmer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'farmer_id_verified' not in session:
            return jsonify({'error': 'Farmer not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function


def buyer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'buyer_id_verified' not in session:
            return jsonify({'error': 'Buyer not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== UTILITY FUNCTIONS ====================

def get_base_price(crop_name):
    """Fetch base price from Government Mandi API or use defaults"""
    try:
        params = {
            'api-key': GOVT_API_KEY,
            'format': 'json',
            'filters[commodity]': crop_name,
            'limit': 10
        }
        
        response = requests.get(GOVT_API_BASE, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'records' in data and len(data['records']) > 0:
                # Calculate average price
                prices = []
                for record in data['records']:
                    price = record.get('modal_price') or record.get('price') or 0
                    if price:
                        prices.append(float(price))
                
                if prices:
                    return round(sum(prices) / len(prices), 2)
    except Exception as e:
        print(f"Error fetching base price: {str(e)}")
    
    # Default base prices for oilseeds
    default_prices = {
        'Soybean': 5500,
        'Mustard': 6200,
        'Groundnut': 7400,
        'Sunflower': 6800,
        'Safflower': 4900,
        'Sesame': 8200,
        'Coconut': 4500
    }
    
    return default_prices.get(crop_name, 5000)


def save_auction_photos(files):
    """Save uploaded photos and return paths"""
    paths = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(filepath)
            paths.append(filepath)
    return paths


@bidding_bp.route('/debug/current-user', methods=['GET'])
def debug_current_user():
    """Debug endpoint to show current logged-in farmer"""
    farmer_id = session.get('farmer_id_verified')
    buyer_id = session.get('buyer_id_verified')
    
    if farmer_id:
        farmer = Farmer.query.get(farmer_id)
        farmer_auctions = Auction.query.filter_by(seller_id=farmer_id).count()
        return jsonify({
            'user_type': 'farmer',
            'user_id': farmer_id,
            'phone': farmer.phone_number if hasattr(farmer, 'phone_number') else 'N/A',
            'auctions_created': farmer_auctions
        }), 200
    elif buyer_id:
        buyer = Buyer.query.get(buyer_id)
        return jsonify({
            'user_type': 'buyer',
            'user_id': buyer_id,
            'phone': buyer.phone_number if hasattr(buyer, 'phone_number') else 'N/A'
        }), 200
    else:
        return jsonify({
            'user_type': 'none',
            'message': 'Not logged in'
        }), 401


# ==================== FARMER ROUTES ====================

@bidding_bp.route('/farmer/create-auction', methods=['POST'])
@farmer_login_required
def create_auction():
    """Create new auction for crop"""
    farmer_id = session['farmer_id_verified']
    
    try:
        # Parse form data
        crop_name = request.form.get('crop_name', '').strip()
        quantity_str = request.form.get('quantity', '0')
        min_bid_price_str = request.form.get('min_bid_price', '0')
        duration_hours_str = request.form.get('duration_hours', '24')
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate required fields
        if not crop_name:
            return jsonify({'error': 'Crop name is required'}), 400
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        if not duration_hours_str:
            return jsonify({'error': 'Duration is required'}), 400
            
        # Parse numeric values
        try:
            quantity = float(quantity_str)
            min_bid_price = float(min_bid_price_str)
            duration_hours = int(duration_hours_str)
        except ValueError as e:
            return jsonify({'error': f'Invalid numeric input: {str(e)}'}), 400
        
        # Validate numeric ranges
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400
        if min_bid_price <= 0:
            return jsonify({'error': 'Minimum bid price must be greater than 0'}), 400
        if duration_hours <= 0:
            return jsonify({'error': 'Duration must be greater than 0'}), 400
        
        # Get base price from mandi
        base_price = get_base_price(crop_name)
        
        # Handle photo uploads - look for photo1, photo2, photo3
        photo_paths = [None, None, None]
        for i in range(1, 4):
            photo_field = f'photo{i}'
            if photo_field in request.files:
                file = request.files[photo_field]
                if file and file.filename and allowed_file(file.filename):
                    try:
                        filename = secure_filename(file.filename)
                        unique_filename = f"{uuid.uuid4()}_{filename}"
                        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                        file.save(filepath)
                        photo_paths[i-1] = filepath
                    except Exception as e:
                        print(f"Error saving photo {i}: {str(e)}")
        
        # At least one photo is required
        if not photo_paths[0]:
            return jsonify({'error': 'At least one photo is required'}), 400
        
        # Create auction
        auction = Auction(
            id=str(uuid.uuid4()),
            seller_id=farmer_id,
            crop_name=crop_name,
            quantity_quintal=quantity,
            base_price=base_price,
            min_bid_price=min_bid_price,
            end_time=datetime.utcnow() + timedelta(hours=duration_hours),
            location=location,
            description=description,
            status='live',
            photo1_path=photo_paths[0],
            photo2_path=photo_paths[1],
            photo3_path=photo_paths[2],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(auction)
        db.session.commit()
        
        print(f"✅ Auction created: ID={auction.id}, Crop={crop_name}, Quantity={quantity}")
        
        return jsonify({
            'success': True,
            'auction_id': auction.id,
            'base_price': base_price,
            'message': '✅ Auction created successfully'
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        print(f"ValueError in create_auction: {str(e)}")
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Exception in create_auction: {str(e)}")
        return jsonify({'error': f'Error creating auction: {str(e)}'}), 500


@bidding_bp.route('/farmer/my-auctions', methods=['GET'])
@farmer_login_required
def farmer_auctions():
    """Get farmer's all auctions with filters"""
    farmer_id = session['farmer_id_verified']
    
    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'newest')  # newest, ending_soon
    
    query = Auction.query.filter_by(seller_id=farmer_id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Sorting
    if sort_by == 'ending_soon':
        query = query.order_by(Auction.end_time.asc())
    else:  # newest
        query = query.order_by(Auction.created_at.desc())
    
    auctions = query.all()
    
    return jsonify({
        'auctions': [auction.to_dict() for auction in auctions],
        'total': len(auctions),
        'filters': {
            'status': status_filter,
            'sort': sort_by
        }
    }), 200


@bidding_bp.route('/farmer/auctions/with-bids', methods=['GET'])
@farmer_login_required
def farmer_auctions_with_bids():
    """Get farmer's auctions that have received bids"""
    farmer_id = session['farmer_id_verified']
    
    # Get farmer's auctions that have bids
    auctions = Auction.query.filter_by(seller_id=farmer_id).all()
    
    # Filter only those with bids
    auctions_with_bids = []
    for auction in auctions:
        bid_count = Bid.query.filter_by(auction_id=auction.id).count()
        if bid_count > 0:
            auction_dict = auction.to_dict()
            auction_dict['has_bids'] = True
            auctions_with_bids.append(auction_dict)
    
    return jsonify({
        'auctions': auctions_with_bids,
        'total': len(auctions_with_bids)
    }), 200


@bidding_bp.route('/farmer/auction/<auction_id>', methods=['GET'])
@farmer_login_required
def farmer_auction_detail(auction_id):
    """Get auction details with all bids for farmer"""
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != session['farmer_id_verified']:
        return jsonify({'error': 'Not your auction'}), 403
    
    bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.created_at.desc()).all()
    
    return jsonify({
        'auction': auction.to_dict(),
        'bids': [bid.to_dict() for bid in bids],
        'statistics': {
            'bid_count': len(bids),
            'unique_bidders': len(set(bid.buyer_id for bid in bids)),
            'avg_bid': round(sum(b.bid_amount for b in bids) / len(bids), 2) if bids else 0,
            'highest_bid': max(b.bid_amount for b in bids) if bids else 0,
            'lowest_bid': min(b.bid_amount for b in bids) if bids else 0
        }
    }), 200


@bidding_bp.route('/farmer/auction/<auction_id>/end', methods=['POST'])
@farmer_login_required
def end_auction_manual(auction_id):
    """End auction manually (farmer action)"""
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != session['farmer_id_verified']:
        return jsonify({'error': 'Not your auction'}), 403
    
    if auction.status != 'live':
        return jsonify({'error': 'Auction is not live'}), 400
    
    try:
        # End auction
        auction.status = 'ended'
        
        # Check for winning bid
        winning_bid = Bid.query.filter_by(auction_id=auction_id, is_winning=True).first()
        
        if winning_bid and winning_bid.bid_amount >= auction.min_bid_price:
            auction.status = 'sold'
            auction.final_price = winning_bid.bid_amount
            auction.winning_buyer_id = winning_bid.buyer_id
            
            # Create transaction
            transaction = Transaction(
                auction_id=auction_id,
                seller_id=auction.seller_id,
                buyer_id=winning_bid.buyer_id,
                crop_name=auction.crop_name,
                quantity=auction.quantity_quintal,
                final_price=winning_bid.bid_amount,
                total_amount=auction.quantity_quintal * winning_bid.bid_amount
            )
            db.session.add(transaction)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'status': auction.status,
            'message': f'✅ Auction ended - Status: {auction.status}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500


# ==================== BUYER ROUTES ====================

@bidding_bp.route('/buyer/auctions', methods=['GET'])
@buyer_login_required
def buyer_browse_auctions():
    """Browse all active auctions with filters"""
    crop_filter = request.args.get('crop', None)
    max_price = request.args.get('max_price', None)
    sort_by = request.args.get('sort', 'newest')
    
    query = Auction.query.filter_by(status='live').filter(Auction.end_time > datetime.utcnow())
    
    if crop_filter:
        query = query.filter_by(crop_name=crop_filter)
    
    if max_price:
        try:
            max_price_val = float(max_price)
            query = query.filter(Auction.min_bid_price <= max_price_val)
        except ValueError:
            pass
    
    # Sorting
    if sort_by == 'price_low':
        query = query.order_by(Auction.current_highest_bid.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Auction.current_highest_bid.desc())
    elif sort_by == 'ending_soon':
        query = query.order_by(Auction.end_time.asc())
    else:  # newest
        query = query.order_by(Auction.created_at.desc())
    
    auctions = query.all()
    
    return jsonify({
        'auctions': [auction.to_dict() for auction in auctions],
        'total': len(auctions),
        'filters': {
            'crop': crop_filter,
            'max_price': max_price,
            'sort': sort_by
        }
    }), 200


@bidding_bp.route('/buyer/auction/<auction_id>', methods=['GET'])
@buyer_login_required
def buyer_auction_detail(auction_id):
    """Get auction details for buyer"""
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    buyer_id = session['buyer_id_verified']
    
    # Get buyer's bids
    my_bids = Bid.query.filter_by(auction_id=auction_id, buyer_id=buyer_id).all()
    
    # Get all bids count
    all_bids = Bid.query.filter_by(auction_id=auction_id).all()
    
    return jsonify({
        'auction': auction.to_dict(),
        'my_bids': [bid.to_dict() for bid in my_bids],
        'total_bids': len(all_bids),
        'unique_bidders': len(set(bid.buyer_id for bid in all_bids)),
        'my_status': {
            'is_winning': any(bid.is_winning for bid in my_bids),
            'highest_bid': max([bid.bid_amount for bid in my_bids]) if my_bids else 0,
            'bid_count': len(my_bids)
        }
    }), 200


@bidding_bp.route('/buyer/my-bids', methods=['GET'])
@buyer_login_required
def buyer_my_bids():
    """Get buyer's bid history"""
    buyer_id = session['buyer_id_verified']
    
    bids = Bid.query.filter_by(buyer_id=buyer_id).order_by(Bid.created_at.desc()).all()
    
    # Organize by auction
    auctions_dict = {}
    for bid in bids:
        if bid.auction_id not in auctions_dict:
            auction = Auction.query.get(bid.auction_id)
            auctions_dict[bid.auction_id] = {
                'auction': auction.to_dict() if auction else {},
                'bids': []
            }
        auctions_dict[bid.auction_id]['bids'].append(bid.to_dict())
    
    return jsonify({
        'auctions': list(auctions_dict.values()),
        'total_auctions': len(auctions_dict),
        'total_bids': len(bids)
    }), 200


@bidding_bp.route('/buyer/won-auctions', methods=['GET'])
@buyer_login_required
def buyer_won_auctions():
    """Get auctions won by buyer"""
    buyer_id = session['buyer_id_verified']
    
    transactions = Transaction.query.filter_by(buyer_id=buyer_id).all()
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions],
        'total_won': len(transactions),
        'total_amount': sum(t.total_amount for t in transactions),
        'summary': {
            'completed': len([t for t in transactions if t.status == 'completed']),
            'pending': len([t for t in transactions if t.status == 'pending']),
            'paid': len([t for t in transactions if t.status == 'paid'])
        }
    }), 200


# ==================== SHARED ROUTES ====================

@bidding_bp.route('/auction/<auction_id>/live-updates', methods=['GET'])
def auction_live_updates(auction_id):
    """Get live updates for auction (polling fallback)"""
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    winning_bid = Bid.query.filter_by(auction_id=auction_id, is_winning=True).first()
    
    return jsonify({
        'auction': auction.to_dict(),
        'latest_bid': winning_bid.to_dict() if winning_bid else None,
        'time_remaining': auction.get_time_remaining()
    }), 200


@bidding_bp.route('/get-base-price/<crop>', methods=['GET'])
def get_base_price_endpoint(crop):
    """Get base price from government mandi API"""
    try:
        price = get_base_price(crop)
        return jsonify({
            'crop': crop,
            'base_price': price,
            'success': True
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Error fetching price: {str(e)}',
            'crop': crop
        }), 500


@bidding_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall bidding system statistics"""
    active_auctions = Auction.query.filter_by(status='live').filter(
        Auction.end_time > datetime.utcnow()
    ).count()
    
    total_auctions = Auction.query.count()
    total_bids = Bid.query.count()
    completed_transactions = Transaction.query.filter_by(status='completed').count()
    
    # Total trading value
    total_value = sum(t.total_amount for t in Transaction.query.all())
    
    return jsonify({
        'active_auctions': active_auctions,
        'total_auctions': total_auctions,
        'total_bids': total_bids,
        'completed_transactions': completed_transactions,
        'total_trading_value': round(total_value, 2),
        'system_health': 'healthy'
    }), 200


@bidding_bp.route('/crop-prices', methods=['GET'])
def get_crop_base_prices():
    """Get base prices for all oilseeds"""
    crops = ['Soybean', 'Mustard', 'Groundnut', 'Sunflower', 'Safflower', 'Sesame', 'Coconut']
    
    prices = {}
    for crop in crops:
        prices[crop] = get_base_price(crop)
    
    return jsonify({
        'prices': prices,
        'timestamp': datetime.utcnow().isoformat(),
        'source': 'Government Mandi API'
    }), 200


# ==================== TRANSACTION ROUTES ====================

@bidding_bp.route('/transaction/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction details"""
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    # Check authorization
    user_id = session.get('farmer_id_verified') or session.get('buyer_id_verified')
    if transaction.seller_id != user_id and transaction.buyer_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    return jsonify({
        'transaction': transaction.to_dict(),
        'auction': Auction.query.get(transaction.auction_id).to_dict(),
        'seller': {
            'id': transaction.seller_id,
            'name': Farmer.query.get(transaction.seller_id).farmer_name if Farmer.query.get(transaction.seller_id) else 'Unknown'
        },
        'buyer': {
            'id': transaction.buyer_id,
            'name': Buyer.query.get(transaction.buyer_id).buyer_name if Buyer.query.get(transaction.buyer_id) else 'Unknown'
        }
    }), 200


@bidding_bp.route('/transaction/<transaction_id>/update-status', methods=['POST'])
def update_transaction_status(transaction_id):
    """Update transaction status"""
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    # Check authorization
    user_id = session.get('farmer_id_verified') or session.get('buyer_id_verified')
    if transaction.seller_id != user_id and transaction.buyer_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['pending', 'confirmed', 'paid', 'delivered', 'completed']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        transaction.status = new_status
        if new_status == 'paid':
            transaction.payment_date = datetime.utcnow()
        elif new_status == 'delivered':
            transaction.delivery_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict(),
            'message': f'✅ Status updated to {new_status}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500


# ==================== NOTIFICATIONS ====================

@bidding_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Get user's notifications"""
    user_id = session.get('farmer_id_verified') or session.get('buyer_id_verified')
    
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    notifications = AuctionNotification.query.filter_by(
        user_id=user_id
    ).order_by(AuctionNotification.created_at.desc()).all()
    
    return jsonify({
        'notifications': [
            {
                'id': n.id,
                'message': n.message,
                'type': n.notification_type,
                'is_read': n.is_read,
                'auction_id': n.auction_id,
                'created_at': n.created_at.isoformat()
            } for n in notifications
        ],
        'total': len(notifications),
        'unread': len([n for n in notifications if not n.is_read])
    }), 200


@bidding_bp.route('/notification/<notification_id>/mark-read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = AuctionNotification.query.get(notification_id)
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    user_id = session.get('farmer_id_verified') or session.get('buyer_id_verified')
    if notification.user_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True}), 200


# ==================== PAGE RENDERING ROUTES ====================

@bidding_bp.route('/create-auction', methods=['GET'])
@farmer_login_required
def create_auction_page():
    """Render create auction page for farmers"""
    return render_template('create_auction.html')


@bidding_bp.route('/my-auctions', methods=['GET'])
@farmer_login_required
def farmer_auctions_page():
    """Render farmer's auctions list page"""
    farmer_id = session['farmer_id_verified']
    auctions = Auction.query.filter_by(seller_id=farmer_id).order_by(Auction.created_at.desc()).all()
    return render_template('my_auctions.html', auctions=auctions)


@bidding_bp.route('/browse-auctions', methods=['GET'])
@buyer_login_required
def buyer_auctions_page():
    """Render auction browsing page for buyers"""
    crop_filter = request.args.get('crop')
    price_filter = request.args.get('max_price', type=int)
    
    # Get all live auctions
    query = Auction.query.filter_by(status='LIVE').order_by(Auction.created_at.desc())
    
    if crop_filter:
        query = query.filter_by(crop_name=crop_filter)
    
    auctions = query.all()
    
    # Apply price filter if provided
    if price_filter:
        auctions = [a for a in auctions if a.current_highest_bid <= price_filter]
    
    return render_template('auction_browse.html', auctions=auctions)


@bidding_bp.route('/auction/<auction_id>/detail', methods=['GET'])
def auction_detail_page(auction_id):
    """Render auction detail page with live updates and bidding interface"""
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    # Get all bids for this auction
    bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.created_at.desc()).all()
    
    # Get bid history
    bid_history = BidHistory.query.filter_by(auction_id=auction_id).order_by(BidHistory.created_at.desc()).all()
    
    user_id = session.get('buyer_id_verified')
    is_buyer = user_id is not None
    
    return render_template('auction_detail.html', 
                         auction=auction, 
                         bids=bids, 
                         bid_history=bid_history,
                         is_buyer=is_buyer,
                         user_id=user_id)


@bidding_bp.route('/my-bids', methods=['GET'])
@buyer_login_required
def buyer_my_bids_page():
    """Render buyer's bids page"""
    buyer_id = session['buyer_id_verified']
    
    # Get all bids placed by this buyer
    bids = Bid.query.filter_by(buyer_id=buyer_id).order_by(Bid.created_at.desc()).all()
    
    # Get associated auctions
    auction_ids = [bid.auction_id for bid in bids]
    auctions = Auction.query.filter(Auction.id.in_(auction_ids)).all() if auction_ids else []
    
    return render_template('my_bids.html', bids=bids, auctions=auctions)


@bidding_bp.route('/won-auctions', methods=['GET'])
@buyer_login_required
def buyer_won_auctions_page():
    """Render buyer's won auctions page"""
    buyer_id = session['buyer_id_verified']
    
    # Get all auctions where this buyer has the winning bid
    won_auctions = Auction.query.filter_by(winning_buyer_id=buyer_id, status='SOLD').all()
    
    # Get transactions related to these auctions
    transaction_ids = [a.id for a in won_auctions]
    transactions = Transaction.query.filter(Transaction.auction_id.in_(transaction_ids)).all() if transaction_ids else []
    
    return render_template('won_auctions.html', auctions=won_auctions, transactions=transactions)


# ==================== FARMER-SIDE BIDDING LOGIC ====================

@bidding_bp.route('/farmer/auction/<auction_id>/bids', methods=['GET'])
@farmer_login_required
def farmer_auction_bids(auction_id):
    """Get all bids for farmer's auction with detailed analytics"""
    farmer_id = session['farmer_id_verified']
    
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != farmer_id:
        return jsonify({'error': 'Not your auction'}), 403
    
    # Get all bids for this auction
    bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.bid_amount.desc()).all()
    
    # Calculate analytics
    bid_analytics = {
        'total_bids': len(bids),
        'unique_bidders': len(set(bid.buyer_id for bid in bids)),
        'highest_bid': max([bid.bid_amount for bid in bids]) if bids else 0,
        'lowest_bid': min([bid.bid_amount for bid in bids]) if bids else 0,
        'average_bid': round(sum([bid.bid_amount for bid in bids]) / len(bids), 2) if bids else 0,
        'winning_bid': auction.current_highest_bid or 0,
        'meets_minimum': auction.current_highest_bid >= auction.min_bid_price if auction.current_highest_bid else False
    }
    
    return jsonify({
        'auction_id': auction_id,
        'crop_name': auction.crop_name,
        'quantity': auction.quantity_quintal,
        'min_bid_price': auction.min_bid_price,
        'bids': [
            {
                'bid_id': bid.id,
                'buyer_id': bid.buyer_id,
                'bid_amount': bid.bid_amount,
                'bid_time': bid.created_at.isoformat(),
                'is_winning': bid.is_winning,
                'auto_bid': getattr(bid, 'auto_bid_max', None)
            }
            for bid in bids
        ],
        'analytics': bid_analytics,
        'status': auction.status,
        'auction_end_time': auction.end_time.isoformat()
    }), 200


@bidding_bp.route('/farmer/auction/<auction_id>/accept-bid', methods=['POST'])
@farmer_login_required
def farmer_accept_bid(auction_id):
    """Farmer accepts a specific bid (if auto-accept not enabled)"""
    farmer_id = session['farmer_id_verified']
    
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != farmer_id:
        return jsonify({'error': 'Not your auction'}), 403
    
    try:
        data = request.get_json()
        bid_id = data.get('bid_id')
        
        bid = Bid.query.get(bid_id)
        if not bid:
            return jsonify({'error': 'Bid not found'}), 404
        
        if bid.auction_id != auction_id:
            return jsonify({'error': 'Bid does not belong to this auction'}), 400
        
        # Check if bid meets minimum
        if bid.bid_amount < auction.min_bid_price:
            return jsonify({'error': f'Bid amount (₹{bid.bid_amount}) is below minimum (₹{auction.min_bid_price})'}), 400
        
        # Accept the bid
        bid.is_winning = True
        auction.status = 'sold'
        auction.final_price = bid.bid_amount
        auction.winning_buyer_id = bid.buyer_id
        auction.current_highest_bid = bid.bid_amount
        
        # Create transaction
        transaction = Transaction(
            id=str(uuid.uuid4()),
            auction_id=auction_id,
            seller_id=farmer_id,
            buyer_id=bid.buyer_id,
            crop_name=auction.crop_name,
            quantity=auction.quantity_quintal,
            final_price=bid.bid_amount,
            total_amount=auction.quantity_quintal * bid.bid_amount,
            status='pending'
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'✅ Bid accepted for ₹{bid.bid_amount}',
            'transaction_id': transaction.id,
            'auction_status': auction.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/reject-bid', methods=['POST'])
@farmer_login_required
def farmer_reject_bid(auction_id):
    """Farmer rejects a specific bid"""
    farmer_id = session['farmer_id_verified']
    
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != farmer_id:
        return jsonify({'error': 'Not your auction'}), 403
    
    try:
        data = request.get_json()
        bid_id = data.get('bid_id')
        reason = data.get('reason', 'No reason provided')
        
        bid = Bid.query.get(bid_id)
        if not bid:
            return jsonify({'error': 'Bid not found'}), 404
        
        if bid.auction_id != auction_id:
            return jsonify({'error': 'Bid does not belong to this auction'}), 400
        
        # Mark bid as rejected
        bid.is_winning = False
        bid.status = 'rejected'
        
        # Store rejection reason
        if hasattr(bid, 'rejection_reason'):
            bid.rejection_reason = reason
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'✅ Bid rejected for ₹{bid.bid_amount}',
            'bid_id': bid_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/counter-offer', methods=['POST'])
@farmer_login_required
def farmer_counter_offer(auction_id):
    """Farmer sends counter offer to a buyer"""
    farmer_id = session['farmer_id_verified']
    
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != farmer_id:
        return jsonify({'error': 'Not your auction'}), 403
    
    try:
        data = request.get_json()
        buyer_id = data.get('buyer_id')
        counter_price = float(data.get('counter_price', 0))
        message = data.get('message', '')
        
        if counter_price <= 0:
            return jsonify({'error': 'Counter price must be greater than 0'}), 400
        
        buyer = Buyer.query.get(buyer_id)
        if not buyer:
            return jsonify({'error': 'Buyer not found'}), 404
        
        # Create counter offer notification
        notification = AuctionNotification(
            id=str(uuid.uuid4()),
            user_id=buyer_id,
            auction_id=auction_id,
            notification_type='counter_offer',
            message=f'Counter offer received: ₹{counter_price} for {auction.crop_name}',
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'✅ Counter offer sent to {buyer.buyer_name}',
            'counter_price': counter_price,
            'notification_id': notification.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/extend', methods=['POST'])
@farmer_login_required
def farmer_extend_auction(auction_id):
    """Farmer extends auction duration"""
    farmer_id = session['farmer_id_verified']
    
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != farmer_id:
        return jsonify({'error': 'Not your auction'}), 403
    
    if auction.status != 'live':
        return jsonify({'error': 'Can only extend live auctions'}), 400
    
    try:
        data = request.get_json()
        extend_hours = int(data.get('extend_hours', 12))
        
        if extend_hours <= 0 or extend_hours > 72:
            return jsonify({'error': 'Extension must be between 1 and 72 hours'}), 400
        
        # Extend auction
        old_end_time = auction.end_time
        auction.end_time = auction.end_time + timedelta(hours=extend_hours)
        
        # Notify bidders
        bids = Bid.query.filter_by(auction_id=auction_id).distinct(Bid.buyer_id).all()
        for bid in bids:
            notification = AuctionNotification(
                id=str(uuid.uuid4()),
                user_id=bid.buyer_id,
                auction_id=auction_id,
                notification_type='auction_extended',
                message=f'Auction extended by {extend_hours} hours. New end time: {auction.end_time.strftime("%Y-%m-%d %H:%M")}',
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'✅ Auction extended by {extend_hours} hours',
            'old_end_time': old_end_time.isoformat(),
            'new_end_time': auction.end_time.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/update-minimum', methods=['POST'])
@farmer_login_required
def farmer_update_minimum_bid(auction_id):
    """Farmer updates minimum bid price (before any bids)"""
    farmer_id = session['farmer_id_verified']
    
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != farmer_id:
        return jsonify({'error': 'Not your auction'}), 403
    
    # Check if auction has any bids
    bid_count = Bid.query.filter_by(auction_id=auction_id).count()
    if bid_count > 0:
        return jsonify({'error': 'Cannot update minimum bid after bids have been placed'}), 400
    
    try:
        data = request.get_json()
        new_minimum = float(data.get('new_minimum', 0))
        
        if new_minimum <= 0:
            return jsonify({'error': 'Minimum bid must be greater than 0'}), 400
        
        old_minimum = auction.min_bid_price
        auction.min_bid_price = new_minimum
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'✅ Minimum bid updated from ₹{old_minimum} to ₹{new_minimum}',
            'old_minimum': old_minimum,
            'new_minimum': new_minimum
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/cancel', methods=['POST'])
@farmer_login_required
def farmer_cancel_auction(auction_id):
    """Farmer cancels auction and notifies all bidders"""
    farmer_id = session['farmer_id_verified']
    
    auction = Auction.query.get(auction_id)
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.seller_id != farmer_id:
        return jsonify({'error': 'Not your auction'}), 403
    
    if auction.status != 'live':
        return jsonify({'error': 'Can only cancel live auctions'}), 400
    
    try:
        reason = request.get_json().get('reason', 'No reason provided') if request.is_json else 'No reason provided'
        
        # Cancel auction
        auction.status = 'cancelled'
        
        # Notify all bidders
        bids = Bid.query.filter_by(auction_id=auction_id).all()
        unique_bidders = set(bid.buyer_id for bid in bids)
        
        for buyer_id in unique_bidders:
            notification = AuctionNotification(
                id=str(uuid.uuid4()),
                user_id=buyer_id,
                auction_id=auction_id,
                notification_type='auction_cancelled',
                message=f'Auction for {auction.crop_name} has been cancelled. Reason: {reason}',
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'✅ Auction cancelled. Notified {len(unique_bidders)} bidders',
            'auction_status': auction.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error: {str(e)}'}), 500


@bidding_bp.route('/farmer/auctions/active', methods=['GET'])
@farmer_login_required
def farmer_active_auctions():
    """Get farmer's active (live) auctions with real-time stats"""
    farmer_id = session['farmer_id_verified']
    
    # Get live auctions that haven't ended yet
    auctions = Auction.query.filter_by(
        seller_id=farmer_id,
        status='live'
    ).filter(Auction.end_time > datetime.utcnow()).all()
    
    auctions_data = []
    for auction in auctions:
        bids = Bid.query.filter_by(auction_id=auction.id).all()
        
        auction_info = {
            'auction_id': auction.id,
            'crop_name': auction.crop_name,
            'quantity': auction.quantity_quintal,
            'min_bid_price': auction.min_bid_price,
            'current_highest_bid': auction.current_highest_bid or 0,
            'total_bids': len(bids),
            'unique_bidders': len(set(bid.buyer_id for bid in bids)),
            'meets_minimum': (auction.current_highest_bid >= auction.min_bid_price) if auction.current_highest_bid else False,
            'time_remaining': (auction.end_time - datetime.utcnow()).total_seconds(),
            'end_time': auction.end_time.isoformat(),
            'created_at': auction.created_at.isoformat()
        }
        auctions_data.append(auction_info)
    
    return jsonify({
        'total_active': len(auctions_data),
        'auctions': auctions_data
    }), 200


@bidding_bp.route('/farmer/auctions/closed', methods=['GET'])
@farmer_login_required
def farmer_closed_auctions():
    """Get farmer's closed/ended auctions"""
    farmer_id = session['farmer_id_verified']
    
    # Get closed auctions (sold, ended, or cancelled)
    auctions = Auction.query.filter_by(seller_id=farmer_id).filter(
        Auction.status.in_(['sold', 'ended', 'cancelled'])
    ).order_by(Auction.end_time.desc()).all()
    
    auctions_data = []
    for auction in auctions:
        bids = Bid.query.filter_by(auction_id=auction.id).all()
        winning_bid = Bid.query.filter_by(auction_id=auction.id, is_winning=True).first()
        
        auction_info = {
            'auction_id': auction.id,
            'crop_name': auction.crop_name,
            'quantity': auction.quantity_quintal,
            'min_bid_price': auction.min_bid_price,
            'final_price': auction.final_price,
            'status': auction.status,
            'total_bids': len(bids),
            'winning_buyer_id': auction.winning_buyer_id,
            'winning_bid_amount': winning_bid.bid_amount if winning_bid else None,
            'end_time': auction.end_time.isoformat(),
            'created_at': auction.created_at.isoformat()
        }
        auctions_data.append(auction_info)
    
    return jsonify({
        'total_closed': len(auctions_data),
        'auctions': auctions_data
    }), 200


@bidding_bp.route('/farmer/dashboard/stats', methods=['GET'])
@farmer_login_required
def farmer_dashboard_stats():
    """Get farmer's bidding dashboard statistics"""
    farmer_id = session['farmer_id_verified']
    
    # Count auctions by status
    total_auctions = Auction.query.filter_by(seller_id=farmer_id).count()
    active_auctions = Auction.query.filter_by(
        seller_id=farmer_id,
        status='live'
    ).filter(Auction.end_time > datetime.utcnow()).count()
    sold_auctions = Auction.query.filter_by(seller_id=farmer_id, status='sold').count()
    ended_auctions = Auction.query.filter_by(seller_id=farmer_id, status='ended').count()
    cancelled_auctions = Auction.query.filter_by(seller_id=farmer_id, status='cancelled').count()
    
    # Get total bids and total value
    farmer_auctions = Auction.query.filter_by(seller_id=farmer_id).all()
    auction_ids = [a.id for a in farmer_auctions]
    total_bids = Bid.query.filter(Bid.auction_id.in_(auction_ids)).count() if auction_ids else 0
    
    # Calculate total trading value
    transactions = Transaction.query.filter_by(seller_id=farmer_id).all()
    total_value = sum(t.total_amount for t in transactions) if transactions else 0
    
    # Get average bid price
    all_bids = Bid.query.filter(Bid.auction_id.in_(auction_ids)).all() if auction_ids else []
    avg_bid_price = round(sum(b.bid_amount for b in all_bids) / len(all_bids), 2) if all_bids else 0
    
    return jsonify({
        'auction_stats': {
            'total': total_auctions,
            'active': active_auctions,
            'sold': sold_auctions,
            'ended': ended_auctions,
            'cancelled': cancelled_auctions
        },
        'bid_stats': {
            'total_bids': total_bids,
            'average_bid_price': avg_bid_price
        },
        'financial_stats': {
            'total_trading_value': round(total_value, 2),
            'completed_transactions': len(transactions)
        }
    }), 200

