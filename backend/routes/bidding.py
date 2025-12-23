"""
Real-Time Bidding System (NILAMI) for Oilseed Harvest
Provides auction management, bidding, and transaction handling
Farmer-side functionality
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensions import db
from models import Farmer
from models_marketplace_keep import Auction, Bid, CounterOffer, AuctionNotification, Buyer
from datetime import datetime, timedelta
import uuid

bidding_bp = Blueprint('bidding', __name__, url_prefix='/bidding')


# ==================== FARMER-SIDE ENDPOINTS ====================

@bidding_bp.route('/farmer/dashboard')
def farmer_dashboard():
    """Farmer's main bidding dashboard"""
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))
    
    farmer_id = session['farmer_id_verified']
    farmer = Farmer.query.get(farmer_id)
    
    if not farmer:
        return redirect(url_for('auth.login'))
    
    return render_template('farmer_auction_dashboard.html', farmer=farmer)


@bidding_bp.route('/farmer/create-auction', methods=['GET', 'POST'])
def create_auction():
    """Create a new auction for oilseed harvest"""
    if 'farmer_id_verified' not in session:
        return redirect(url_for('auth.login'))
    
    farmer_id = session['farmer_id_verified']
    
    if request.method == 'GET':
        farmer = Farmer.query.get(farmer_id)
        return render_template('farmer_create_auction.html', farmer=farmer)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['crop_name', 'quantity_quintals', 'base_price', 'duration_hours', 'location', 'district']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Create auction
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(hours=int(data['duration_hours']))
            
            auction = Auction(
                id=str(uuid.uuid4()),
                farmer_id=farmer_id,
                crop_name=data['crop_name'],
                quantity_quintals=float(data['quantity_quintals']),
                quality_grade=data.get('quality_grade', 'Standard'),
                base_price_per_quintal=float(data['base_price']),
                minimum_bid_increment=float(data.get('minimum_bid_increment', 50)),
                start_time=start_time,
                end_time=end_time,
                location=data['location'],
                district=data['district'],
                state=data.get('state', 'Maharashtra'),
                description=data.get('description', ''),
                harvest_date=data.get('harvest_date'),
                storage_location=data.get('storage_location', ''),
                status='active',
                current_highest_bid=float(data['base_price'])
            )
            
            db.session.add(auction)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'auction_id': auction.id,
                'message': 'Auction created successfully'
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


@bidding_bp.route('/farmer/my-auctions')
def my_auctions():
    """Get farmer's auctions"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    farmer_id = session['farmer_id_verified']
    auctions = Auction.query.filter_by(farmer_id=farmer_id).order_by(Auction.created_at.desc()).all()
    
    return jsonify({
        'auctions': [{
            'id': a.id,
            'crop_name': a.crop_name,
            'quantity_quintals': a.quantity_quintals,
            'base_price': a.base_price_per_quintal,
            'current_highest_bid': a.current_highest_bid,
            'status': a.status,
            'bids_count': len(a.bids),
            'start_time': a.start_time.isoformat(),
            'end_time': a.end_time.isoformat(),
            'created_at': a.created_at.isoformat()
        } for a in auctions]
    })


@bidding_bp.route('/farmer/auction/<auction_id>')
def auction_detail(auction_id):
    """Get auction details"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.farmer_id != session['farmer_id_verified']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': auction.id,
        'crop_name': auction.crop_name,
        'quantity_quintals': auction.quantity_quintals,
        'quality_grade': auction.quality_grade,
        'base_price': auction.base_price_per_quintal,
        'current_highest_bid': auction.current_highest_bid,
        'minimum_bid_increment': auction.minimum_bid_increment,
        'status': auction.status,
        'location': auction.location,
        'district': auction.district,
        'state': auction.state,
        'description': auction.description,
        'harvest_date': auction.harvest_date.isoformat() if auction.harvest_date else None,
        'storage_location': auction.storage_location,
        'start_time': auction.start_time.isoformat(),
        'end_time': auction.end_time.isoformat(),
        'bids_count': len(auction.bids),
        'created_at': auction.created_at.isoformat()
    })


@bidding_bp.route('/farmer/auction/<auction_id>/bids')
def auction_bids(auction_id):
    """Get all bids for an auction"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.farmer_id != session['farmer_id_verified']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.bid_price_per_quintal.desc()).all()
    
    return jsonify({
        'bids': [{
            'id': b.id,
            'buyer_id': b.buyer_id,
            'buyer_name': b.buyer.buyer_name if b.buyer else 'Unknown',
            'bid_price': b.bid_price_per_quintal,
            'bid_total': b.bid_total_amount,
            'status': b.status,
            'created_at': b.created_at.isoformat()
        } for b in bids]
    })


@bidding_bp.route('/farmer/auction/<auction_id>/accept-bid', methods=['POST'])
def accept_bid(auction_id):
    """Accept a bid and close the auction"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.farmer_id != session['farmer_id_verified']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        bid_id = data.get('bid_id')
        
        bid = Bid.query.get(bid_id)
        
        if not bid or bid.auction_id != auction_id:
            return jsonify({'error': 'Bid not found'}), 404
        
        # Update bid status
        bid.status = 'accepted'
        
        # Update auction status
        auction.status = 'completed'
        auction.current_highest_bid = bid.bid_price_per_quintal
        
        # Mark other bids as rejected
        for other_bid in auction.bids:
            if other_bid.id != bid_id:
                other_bid.status = 'rejected'
        
        # Create notifications
        notification = AuctionNotification(
            id=str(uuid.uuid4()),
            user_id=bid.buyer_id,
            user_type='buyer',
            auction_id=auction_id,
            notification_type='bid_accepted',
            message=f'Your bid of ₹{bid.bid_price_per_quintal}/quintal has been accepted!'
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bid accepted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/reject-bid', methods=['POST'])
def reject_bid(auction_id):
    """Reject a bid"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.farmer_id != session['farmer_id_verified']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        bid_id = data.get('bid_id')
        
        bid = Bid.query.get(bid_id)
        
        if not bid or bid.auction_id != auction_id:
            return jsonify({'error': 'Bid not found'}), 404
        
        bid.status = 'rejected'
        
        # Create notification for buyer
        notification = AuctionNotification(
            id=str(uuid.uuid4()),
            user_id=bid.buyer_id,
            user_type='buyer',
            auction_id=auction_id,
            notification_type='bid_rejected',
            message=f'Your bid of ₹{bid.bid_price_per_quintal}/quintal has been rejected.'
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bid rejected'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/counter-offer', methods=['POST'])
def send_counter_offer(auction_id):
    """Send a counter offer to a bid"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.farmer_id != session['farmer_id_verified']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        bid_id = data.get('bid_id')
        counter_price = float(data.get('counter_price'))
        
        bid = Bid.query.get(bid_id)
        
        if not bid or bid.auction_id != auction_id:
            return jsonify({'error': 'Bid not found'}), 404
        
        # Create counter offer
        counter_offer = CounterOffer(
            id=str(uuid.uuid4()),
            auction_id=auction_id,
            bid_id=bid_id,
            buyer_id=bid.buyer_id,
            counter_price_per_quintal=counter_price,
            status='pending'
        )
        
        # Create notification for buyer
        notification = AuctionNotification(
            id=str(uuid.uuid4()),
            user_id=bid.buyer_id,
            user_type='buyer',
            auction_id=auction_id,
            notification_type='counter_offer',
            message=f'Farmer sent a counter offer: ₹{counter_price}/quintal'
        )
        
        db.session.add(counter_offer)
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'counter_offer_id': counter_offer.id,
            'message': 'Counter offer sent'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/extend', methods=['POST'])
def extend_auction(auction_id):
    """Extend auction duration"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.farmer_id != session['farmer_id_verified']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        additional_hours = int(data.get('additional_hours', 1))
        
        auction.end_time = auction.end_time + timedelta(hours=additional_hours)
        
        # Create notifications
        for bid in auction.bids:
            notification = AuctionNotification(
                id=str(uuid.uuid4()),
                user_id=bid.buyer_id,
                user_type='buyer',
                auction_id=auction_id,
                notification_type='auction_extended',
                message=f'Auction extended by {additional_hours} hour(s)'
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_end_time': auction.end_time.isoformat(),
            'message': f'Auction extended by {additional_hours} hour(s)'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/update-minimum', methods=['POST'])
def update_minimum_price(auction_id):
    """Update minimum bid price for auction"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.farmer_id != session['farmer_id_verified']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        new_minimum = float(data.get('minimum_price'))
        
        if new_minimum <= 0:
            return jsonify({'error': 'Minimum price must be positive'}), 400
        
        auction.base_price_per_quintal = new_minimum
        db.session.commit()
        
        return jsonify({
            'success': True,
            'new_minimum': new_minimum,
            'message': 'Minimum price updated'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bidding_bp.route('/farmer/auction/<auction_id>/cancel', methods=['POST'])
def cancel_auction(auction_id):
    """Cancel an auction"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    auction = Auction.query.get(auction_id)
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    if auction.farmer_id != session['farmer_id_verified']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        auction.status = 'cancelled'
        
        # Notify all bidders
        for bid in auction.bids:
            notification = AuctionNotification(
                id=str(uuid.uuid4()),
                user_id=bid.buyer_id,
                user_type='buyer',
                auction_id=auction_id,
                notification_type='auction_cancelled',
                message='The auction has been cancelled by the farmer'
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Auction cancelled'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bidding_bp.route('/farmer/dashboard/stats')
def farmer_stats():
    """Get farmer's bidding dashboard statistics"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    farmer_id = session['farmer_id_verified']
    
    # Count auctions by status
    total_auctions = Auction.query.filter_by(farmer_id=farmer_id).count()
    active_auctions = Auction.query.filter_by(farmer_id=farmer_id, status='active').count()
    completed_auctions = Auction.query.filter_by(farmer_id=farmer_id, status='completed').count()
    cancelled_auctions = Auction.query.filter_by(farmer_id=farmer_id, status='cancelled').count()
    
    # Get best prices
    all_auctions = Auction.query.filter_by(farmer_id=farmer_id).all()
    best_price = max([a.current_highest_bid for a in all_auctions], default=0)
    
    # Total bids received
    total_bids = sum([len(a.bids) for a in all_auctions])
    
    return jsonify({
        'total_auctions': total_auctions,
        'active_auctions': active_auctions,
        'completed_auctions': completed_auctions,
        'cancelled_auctions': cancelled_auctions,
        'best_price': best_price,
        'total_bids': total_bids
    })
