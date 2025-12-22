import uuid
from datetime import datetime
from extensions import db


class Buyer(db.Model):
    """Buyer model for marketplace - stores buyer profile and credentials"""
    __tablename__ = "buyers"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Login credentials
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Profile information
    buyer_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    company_name = db.Column(db.String(255))
    
    # Location information
    location = db.Column(db.String(255))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100), default='Maharashtra')
    
    # Account status
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    buyer_offers = db.relationship('BuyerOffer', backref='buyer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Buyer {self.buyer_name} - {self.email}>'


class CropListing(db.Model):
    __tablename__ = "crop_listings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)

    crop_name = db.Column(db.String(100), nullable=False)
    quantity_quintal = db.Column(db.Float, nullable=False)
    expected_price = db.Column(db.Float, nullable=False)
    harvest_date = db.Column(db.Date)

    # Photos
    photo1_path = db.Column(db.String(255))
    photo2_path = db.Column(db.String(255))
    photo3_path = db.Column(db.String(255))

    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class SellRequest(db.Model):
    __tablename__ = "sell_requests"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)

    crop_name = db.Column(db.String(100), nullable=False)
    quantity_quintal = db.Column(db.Float, nullable=False)
    expected_price = db.Column(db.Float, nullable=False)

    harvest_date = db.Column(db.String(20))
    location = db.Column(db.String(255))
    farmer_name = db.Column(db.String(200))
    farmer_phone = db.Column(db.String(20))

    status = db.Column(db.String(20), default="pending")  
    # pending → accepted → final_confirmed → declined

    # buyer negotiation
    buyer_price = db.Column(db.Float)
    final_price = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    photos = db.relationship("SellPhoto", backref="sell_request", cascade="all,delete")


class SellPhoto(db.Model):
    __tablename__ = "sell_photos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = db.Column(db.String(36), db.ForeignKey("sell_requests.id"))
    photo_url = db.Column(db.String(255), nullable=False)


class BuyerOffer(db.Model):
    __tablename__ = "buyer_offers"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Buyer information (FK to Buyer table)
    buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=True)
    buyer_name = db.Column(db.String(255))
    buyer_mobile = db.Column(db.String(20))
    buyer_location = db.Column(db.String(255))
    buyer_company = db.Column(db.String(255))
    
    # Crop details (buyer specifies what they want to buy)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity_quintal = db.Column(db.Float, nullable=False)
    location_wanted = db.Column(db.String(255))  # Where buyer wants crop from
    district_wanted = db.Column(db.String(100))
    
    # Pricing
    initial_price = db.Column(db.Float, nullable=False)  # Buyer's offer price
    final_price = db.Column(db.Float, nullable=True)     # Negotiated final price
    
    # Optional: Reference to farmer's SellRequest if farmer responds
    sell_request_id = db.Column(db.String(36), db.ForeignKey("sell_requests.id"), nullable=True)
    
    # Status: pending → accepted (by farmer) → final_confirmed → declined
    status = db.Column(db.String(20), default="pending")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BuyerOffer {self.crop_name} by {self.buyer_name}>'


# ===== CHAT MODELS =====

class Chat(db.Model):
    __tablename__ = "chats"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Participants
    buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=False)
    farmer_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)
    
    # Context
    sell_request_id = db.Column(db.String(36), db.ForeignKey("sell_requests.id"), nullable=True)
    buyer_offer_id = db.Column(db.String(36), db.ForeignKey("buyer_offers.id"), nullable=True)
    
    crop_name = db.Column(db.String(100), nullable=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship("ChatMessage", backref="chat", cascade="all,delete", lazy=True)


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = db.Column(db.String(36), db.ForeignKey("chats.id"), nullable=False)
    
    sender_type = db.Column(db.String(10), nullable=False)  # 'buyer' or 'farmer'
    sender_id = db.Column(db.String(36), nullable=False)
    sender_name = db.Column(db.String(255))
    
    message = db.Column(db.Text, nullable=False)
    
    is_read = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ===== MARKET PRICE MODEL =====

class MarketPrice(db.Model):
    __tablename__ = "market_prices"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Commodity info (focused on oilseeds)
    commodity_name = db.Column(db.String(100), nullable=False)
    
    # Market info
    market_name = db.Column(db.String(100), nullable=False)
    market_state = db.Column(db.String(50))
    market_district = db.Column(db.String(100))
    
    # Price data
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    
    # Trading volume
    trading_volume = db.Column(db.Float)
    
    # Dates
    price_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MarketPrice {self.commodity_name} @ {self.market_name} on {self.price_date}>'


# ===== REAL-TIME BIDDING SYSTEM MODELS =====

class Auction(db.Model):
    """Model for live crop auctions"""
    __tablename__ = "auctions"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Seller (Farmer)
    seller_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)
    
    # Auction Details
    crop_name = db.Column(db.String(100), nullable=False)
    quantity_quintal = db.Column(db.Float, nullable=False)
    
    # Price Settings
    base_price = db.Column(db.Float, nullable=False)  # Mandi reference price
    min_bid_price = db.Column(db.Float, nullable=False)  # Farmer's minimum acceptable bid
    current_highest_bid = db.Column(db.Float, default=0)
    
    # Auction Duration
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="live")  # live, ended, sold, cancelled
    
    # Winning Bid
    winning_buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=True)
    final_price = db.Column(db.Float, nullable=True)
    
    # Photos & Description
    photo1_path = db.Column(db.String(255))
    photo2_path = db.Column(db.String(255))
    photo3_path = db.Column(db.String(255))
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bids = db.relationship('Bid', backref='auction', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='auction', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        bids_list = self.bids if self.bids else []
        return {
            'id': self.id,
            'crop_name': self.crop_name,
            'quantity': self.quantity_quintal,
            'base_price': self.base_price,
            'min_bid': self.min_bid_price,
            'min_bid_price': self.min_bid_price,
            'current_bid': self.current_highest_bid,
            'current_highest_bid': self.current_highest_bid,
            'time_left': self.get_time_remaining(),
            'status': self.status,
            'bids_count': len(bids_list),
            'bidders_count': len(set(bid.buyer_id for bid in bids_list)) if bids_list else 0,
            'avg_bid': round(sum(bid.bid_amount for bid in bids_list) / len(bids_list), 2) if bids_list else 0,
            'winning_buyer': self.winning_buyer_id,
            'final_price': self.final_price,
            'location': self.location,
            'description': self.description,
            'photo1': self.photo1_path,
            'photo1_path': self.photo1_path,
            'photo2_path': self.photo2_path,
            'photo3_path': self.photo3_path,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'seller_id': self.seller_id
        }
    
    def get_time_remaining(self):
        """Returns seconds remaining in auction"""
        if self.status != 'live':
            return 0
        remaining = self.end_time - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))
    
    def is_active(self):
        """Check if auction is still active"""
        return self.status == 'live' and self.get_time_remaining() > 0
    
    def __repr__(self):
        return f'<Auction {self.crop_name} - {self.status}>'


class Bid(db.Model):
    """Model for individual bids on auctions"""
    __tablename__ = "bids"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    auction_id = db.Column(db.String(36), db.ForeignKey("auctions.id"), nullable=False)
    buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=False)
    
    # Bid Details
    bid_amount = db.Column(db.Float, nullable=False)
    bid_type = db.Column(db.String(20), default="manual")  # manual, auto
    
    # For Auto-Bidding
    max_bid_amount = db.Column(db.Float, nullable=True)  # Maximum they're willing to pay
    auto_increment = db.Column(db.Float, default=100)  # Increment by ₹100
    
    # Status
    is_winning = db.Column(db.Boolean, default=False)
    is_outbid = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    outbid_at = db.Column(db.DateTime, nullable=True)  # When they were outbid
    
    # Relationships
    buyer = db.relationship('Buyer', backref='auction_bids')
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'bid_id': self.id,
            'buyer_id': self.buyer_id,
            'amount': self.bid_amount,
            'type': self.bid_type,
            'is_winning': self.is_winning,
            'is_outbid': self.is_outbid,
            'time': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Bid ₹{self.bid_amount} by {self.buyer_id}>'


class BidHistory(db.Model):
    """Audit trail for all bid placements and changes"""
    __tablename__ = "bid_history"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # References
    auction_id = db.Column(db.String(36), db.ForeignKey("auctions.id"), nullable=False)
    buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=False)
    bid_id = db.Column(db.String(36), db.ForeignKey("bids.id"), nullable=True)
    
    # History Details
    old_bid = db.Column(db.Float, nullable=True)
    new_bid = db.Column(db.Float, nullable=False)
    action = db.Column(db.String(50))  # placed, outbid, withdrawn, auto_placed
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BidHistory {self.action} ₹{self.new_bid}>'


class Transaction(db.Model):
    """Model for completed auction transactions"""
    __tablename__ = "transactions"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    auction_id = db.Column(db.String(36), db.ForeignKey("auctions.id"), nullable=False)
    seller_id = db.Column(db.String(36), db.ForeignKey("farmers.id"), nullable=False)
    buyer_id = db.Column(db.String(36), db.ForeignKey("buyers.id"), nullable=False)
    
    # Transaction Details
    crop_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)  # quantity * final_price
    
    # Payment & Delivery Status
    status = db.Column(db.String(20), default="pending")  # pending, confirmed, paid, delivered, completed
    payment_method = db.Column(db.String(50))  # bank_transfer, upi, check, cash, etc.
    payment_date = db.Column(db.DateTime, nullable=True)
    delivery_date = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    seller = db.relationship('Farmer', backref='sold_transactions')
    buyer = db.relationship('Buyer', backref='purchased_transactions')
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'transaction_id': self.id,
            'auction_id': self.auction_id,
            'crop': self.crop_name,
            'quantity': self.quantity,
            'price': self.final_price,
            'total': self.total_amount,
            'status': self.status,
            'date': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Transaction {self.crop_name} - {self.status}>'


class AuctionNotification(db.Model):
    """Model for auction-related notifications"""
    __tablename__ = "auction_notifications"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User who receives notification (farmer or buyer)
    user_id = db.Column(db.String(36), nullable=False)
    user_type = db.Column(db.String(10))  # farmer, buyer
    
    # Auction reference
    auction_id = db.Column(db.String(36), db.ForeignKey("auctions.id"), nullable=False)
    
    # Notification Details
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # outbid, auction_started, won, bid_placed, auction_ended
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<AuctionNotification {self.notification_type}>'

