"""
Real-Time Bidding WebSocket Server
Handles live bid updates, auction management, and real-time notifications
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import session
from extensions import db
from models_marketplace import Auction, Bid, BidHistory, AuctionNotification, Transaction
from datetime import datetime
import json

socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

# Track active auction rooms and watchers
active_auctions = {}
user_sessions = {}  # Track user connections


# ==================== CONNECTION EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection to WebSocket server"""
    user_id = session.get('farmer_id_verified') or session.get('buyer_id_verified')
    user_type = 'farmer' if session.get('farmer_id_verified') else 'buyer'
    
    print(f"✅ Client connected: {user_id} ({user_type})")
    
    # Track user session
    user_sessions[user_id] = {
        'sid': id,
        'user_type': user_type,
        'active_auctions': []
    }
    
    emit('connection_response', {
        'status': 'connected',
        'data': 'Connected to bidding server',
        'user_id': user_id,
        'user_type': user_type
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    user_id = session.get('farmer_id_verified') or session.get('buyer_id_verified')
    print(f"❌ Client disconnected: {user_id}")
    
    # Clean up user session
    if user_id in user_sessions:
        del user_sessions[user_id]


# ==================== AUCTION ROOM MANAGEMENT ====================

@socketio.on('join_auction')
def on_join_auction(data):
    """User joins an auction room to receive live updates"""
    auction_id = data.get('auction_id')
    user_id = session.get('farmer_id_verified') or session.get('buyer_id_verified')
    user_type = 'farmer' if session.get('farmer_id_verified') else 'buyer'
    
    print(f"📍 {user_type.upper()} {user_id} joined auction {auction_id}")
    
    # Join WebSocket room for this auction
    join_room(f"auction_{auction_id}")
    
    # Track in active auctions
    if auction_id not in active_auctions:
        active_auctions[auction_id] = {
            'watchers': [],
            'farmers': [],
            'buyers': [],
            'start_time': datetime.utcnow()
        }
    
    # Add user to appropriate list
    if user_type == 'farmer':
        active_auctions[auction_id]['farmers'].append(user_id)
    else:
        active_auctions[auction_id]['buyers'].append(user_id)
    
    active_auctions[auction_id]['watchers'].append(user_id)
    
    # Send auction state to joining user
    auction = Auction.query.get(auction_id)
    if auction:
        # Get latest bids
        latest_bids = Bid.query.filter_by(auction_id=auction_id).order_by(Bid.created_at.desc()).limit(10).all()
        
        emit('auction_state', {
            'auction': auction.to_dict(),
            'latest_bids': [bid.to_dict() for bid in latest_bids],
            'watchers_count': len(active_auctions[auction_id]['watchers']),
            'buyer_count': len(active_auctions[auction_id]['buyers'])
        })
        
        # Broadcast to all that a new watcher joined
        emit('watcher_joined', {
            'watchers_count': len(active_auctions[auction_id]['watchers']),
            'message': f'Total watchers: {len(active_auctions[auction_id]["watchers"])}'
        }, room=f"auction_{auction_id}")


@socketio.on('leave_auction')
def on_leave_auction(data):
    """User leaves an auction room"""
    auction_id = data.get('auction_id')
    user_id = session.get('farmer_id_verified') or session.get('buyer_id_verified')
    
    print(f"👋 {user_id} left auction {auction_id}")
    
    # Remove from tracking
    if auction_id in active_auctions:
        if user_id in active_auctions[auction_id]['watchers']:
            active_auctions[auction_id]['watchers'].remove(user_id)
        if user_id in active_auctions[auction_id]['farmers']:
            active_auctions[auction_id]['farmers'].remove(user_id)
        if user_id in active_auctions[auction_id]['buyers']:
            active_auctions[auction_id]['buyers'].remove(user_id)
    
    # Leave WebSocket room
    leave_room(f"auction_{auction_id}")


# ==================== BIDDING EVENTS ====================

@socketio.on('place_bid')
def on_place_bid(data):
    """Handle new bid placement with real-time validation"""
    auction_id = data.get('auction_id')
    buyer_id = session.get('buyer_id_verified')
    bid_amount = float(data.get('bid_amount', 0))
    
    # Validate buyer is authenticated
    if not buyer_id:
        emit('error', {
            'message': 'Not authenticated as buyer',
            'code': 'NOT_AUTHENTICATED'
        })
        return
    
    # Get and validate auction
    auction = Auction.query.get(auction_id)
    if not auction:
        emit('error', {
            'message': 'Auction not found',
            'code': 'AUCTION_NOT_FOUND'
        })
        return
    
    # Check if auction is still active
    if not auction.is_active():
        emit('error', {
            'message': 'Auction is not active',
            'code': 'AUCTION_INACTIVE'
        })
        return
    
    # Validate bid amount
    if bid_amount <= 0:
        emit('error', {
            'message': 'Bid amount must be positive',
            'code': 'INVALID_BID_AMOUNT'
        })
        return
    
    # Check minimum bid
    min_required = max(auction.current_highest_bid + 1, auction.min_bid_price)
    if bid_amount < min_required:
        emit('error', {
            'message': f'Bid must be at least ₹{min_required}',
            'code': 'BID_TOO_LOW',
            'min_required': min_required
        })
        return
    
    try:
        # Get current winning bid
        old_winning = Bid.query.filter_by(auction_id=auction_id, is_winning=True).first()
        
        # Check if bidder is trying to outbid themselves
        if old_winning and old_winning.buyer_id == buyer_id:
            # Update their existing winning bid
            old_winning.bid_amount = bid_amount
            old_winning.updated_at = datetime.utcnow()
            db.session.commit()
            new_bid = old_winning
        else:
            # Create new bid
            new_bid = Bid(
                auction_id=auction_id,
                buyer_id=buyer_id,
                bid_amount=bid_amount,
                bid_type='manual',
                is_winning=True
            )
            
            # Mark old winning bid as outbid
            if old_winning:
                old_winning.is_winning = False
                old_winning.is_outbid = True
                old_winning.outbid_at = datetime.utcnow()
            
            db.session.add(new_bid)
        
        # Update auction
        auction.current_highest_bid = bid_amount
        auction.winning_buyer_id = buyer_id
        auction.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Create bid history
        history = BidHistory(
            auction_id=auction_id,
            buyer_id=buyer_id,
            bid_id=new_bid.id,
            old_bid=old_winning.bid_amount if old_winning and old_winning.buyer_id != buyer_id else None,
            new_bid=bid_amount,
            action='placed'
        )
        db.session.add(history)
        db.session.commit()
        
        print(f"✅ Bid placed: ₹{bid_amount} by {buyer_id} on {auction_id}")
        
        # Broadcast to all users in auction
        emit('bid_placed', {
            'bid': new_bid.to_dict(),
            'auction': auction.to_dict(),
            'message': f'💰 New bid: ₹{bid_amount}',
            'bidder_count': len(set(bid.buyer_id for bid in Bid.query.filter_by(auction_id=auction_id).all()))
        }, room=f"auction_{auction_id}")
        
        # Send success confirmation to bidder
        emit('bid_success', {
            'bid_id': new_bid.id,
            'amount': bid_amount,
            'is_winning': True,
            'message': '✅ Your bid is now the highest!'
        })
        
        # Notify previous bidder if outbid
        if old_winning and old_winning.buyer_id != buyer_id:
            emit('you_were_outbid', {
                'auction_id': auction_id,
                'amount': bid_amount,
                'outbid_by': buyer_id,
                'message': f'❌ You were outbid! New highest bid: ₹{bid_amount}'
            }, to=f"user_{old_winning.buyer_id}")
        
    except Exception as e:
        print(f"❌ Error placing bid: {str(e)}")
        emit('error', {
            'message': f'Error placing bid: {str(e)}',
            'code': 'BID_ERROR'
        })


@socketio.on('auto_bid')
def on_auto_bid(data):
    """Set up automatic bidding"""
    auction_id = data.get('auction_id')
    buyer_id = session.get('buyer_id_verified')
    max_amount = float(data.get('max_amount', 0))
    increment = float(data.get('increment', 100))
    
    if not buyer_id:
        emit('error', {'message': 'Not authenticated'})
        return
    
    auction = Auction.query.get(auction_id)
    if not auction or not auction.is_active():
        emit('error', {'message': 'Auction not found or not active'})
        return
    
    try:
        # Create auto-bid with initial bid
        initial_bid = min(auction.current_highest_bid + increment, max_amount)
        
        auto_bid = Bid(
            auction_id=auction_id,
            buyer_id=buyer_id,
            bid_amount=initial_bid,
            bid_type='auto',
            max_bid_amount=max_amount,
            auto_increment=increment,
            is_winning=True
        )
        
        db.session.add(auto_bid)
        db.session.commit()
        
        print(f"🤖 Auto-bid set: {buyer_id} up to ₹{max_amount} on {auction_id}")
        
        emit('auto_bid_activated', {
            'max_amount': max_amount,
            'increment': increment,
            'initial_bid': initial_bid,
            'message': f'🤖 Auto-bidding activated up to ₹{max_amount}'
        })
        
    except Exception as e:
        print(f"❌ Error setting auto-bid: {str(e)}")
        emit('error', {'message': f'Error: {str(e)}'})


# ==================== AUCTION MANAGEMENT ====================

@socketio.on('end_auction')
def on_end_auction(data):
    """Farmer ends auction (manual or automatic timer)"""
    auction_id = data.get('auction_id')
    farmer_id = session.get('farmer_id_verified')
    
    auction = Auction.query.get(auction_id)
    
    if not auction:
        emit('error', {'message': 'Auction not found'})
        return
    
    if auction.seller_id != farmer_id:
        emit('error', {'message': 'You are not the seller of this auction'})
        return
    
    if auction.status != 'live':
        emit('error', {'message': 'Auction is not live'})
        return
    
    try:
        # Mark auction as ended
        auction.status = 'ended'
        
        # Check if there's a winning bid
        winning_bid = Bid.query.filter_by(auction_id=auction_id, is_winning=True).first()
        
        if winning_bid and winning_bid.bid_amount >= auction.min_bid_price:
            # Auction was sold
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
            
            # Create notification for buyer
            buyer_notif = AuctionNotification(
                user_id=winning_bid.buyer_id,
                user_type='buyer',
                auction_id=auction_id,
                message=f'🎉 Congratulations! You won the auction for {auction.crop_name}!',
                notification_type='won'
            )
            db.session.add(buyer_notif)
        else:
            # No valid bids
            seller_notif = AuctionNotification(
                user_id=auction.seller_id,
                user_type='farmer',
                auction_id=auction_id,
                message=f'⚠️ Auction ended with no valid bids',
                notification_type='auction_ended'
            )
            db.session.add(seller_notif)
        
        db.session.commit()
        
        print(f"🏁 Auction ended: {auction_id} - Status: {auction.status}")
        
        # Notify all users in auction
        emit('auction_ended', {
            'auction_id': auction_id,
            'status': auction.status,
            'winning_buyer': auction.winning_buyer_id,
            'final_price': auction.final_price,
            'message': f'🏁 Auction ended - Status: {auction.status}'
        }, room=f"auction_{auction_id}")
        
        emit('success', {
            'message': 'Auction ended successfully'
        })
        
    except Exception as e:
        print(f"❌ Error ending auction: {str(e)}")
        emit('error', {'message': f'Error: {str(e)}'})


# ==================== GET AUCTION UPDATES (Polling Fallback) ====================

@socketio.on('get_auction_update')
def on_get_auction_update(data):
    """Get current auction state (for polling fallback)"""
    auction_id = data.get('auction_id')
    
    auction = Auction.query.get(auction_id)
    if not auction:
        emit('error', {'message': 'Auction not found'})
        return
    
    # Get winning bid
    winning_bid = Bid.query.filter_by(auction_id=auction_id, is_winning=True).first()
    
    emit('auction_update', {
        'auction': auction.to_dict(),
        'winning_bid': winning_bid.to_dict() if winning_bid else None,
        'bid_count': Bid.query.filter_by(auction_id=auction_id).count()
    })


# ==================== UTILITY FUNCTIONS ====================

def process_auto_bids(auction_id):
    """Process auto-bids when a new manual bid is placed"""
    auction = Auction.query.get(auction_id)
    
    # Get all active auto-bids
    auto_bids = Bid.query.filter_by(
        auction_id=auction_id,
        bid_type='auto',
        is_winning=False
    ).all()
    
    for auto_bid in auto_bids:
        # Check if auto bidder can still outbid
        if auto_bid.max_bid_amount > auction.current_highest_bid:
            # Calculate next bid
            next_bid = min(
                auction.current_highest_bid + auto_bid.auto_increment,
                auto_bid.max_bid_amount
            )
            
            # Create auto bid placement
            new_bid = Bid(
                auction_id=auction_id,
                buyer_id=auto_bid.buyer_id,
                bid_amount=next_bid,
                bid_type='auto',
                max_bid_amount=auto_bid.max_bid_amount,
                auto_increment=auto_bid.auto_increment,
                is_winning=True
            )
            
            # Update auction
            old_winning = Bid.query.filter_by(auction_id=auction_id, is_winning=True).first()
            if old_winning:
                old_winning.is_winning = False
                old_winning.is_outbid = True
            
            auction.current_highest_bid = next_bid
            auction.winning_buyer_id = auto_bid.buyer_id
            
            db.session.add(new_bid)
            db.session.commit()
            
            print(f"🤖 Auto-bid placed: ₹{next_bid} by {auto_bid.buyer_id}")
            
            # Broadcast to all
            socketio.emit('bid_placed', {
                'bid': new_bid.to_dict(),
                'auction': auction.to_dict(),
                'auto_placed': True,
                'message': f'🤖 Auto bid: ₹{next_bid}'
            }, room=f"auction_{auction_id}")


def broadcast_auction_update(auction_id):
    """Broadcast auction state to all watchers"""
    auction = Auction.query.get(auction_id)
    if not auction:
        return
    
    socketio.emit('auction_update', {
        'auction': auction.to_dict(),
        'time_left': auction.get_time_remaining()
    }, room=f"auction_{auction_id}")
