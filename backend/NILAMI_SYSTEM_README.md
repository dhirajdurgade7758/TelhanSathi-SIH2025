# 🎯 Nilami (Bidding) System - Oilseed Harvest Marketplace

A real-time bidding system for farmers to auction their oilseed harvest and buyers to place competitive bids.

## System Overview

The Nilami (bidding) system enables:
- **Farmers** to create auctions for their oilseed harvest
- **Buyers** to browse, bid, and win auctions
- **Real-time bidding** with notifications
- **Price negotiation** through counter offers
- **Transaction management** for completed sales

## Key Features

### Farmer Workflow

#### 1. **Create Auction** (`/bidding/farmer/create-auction`)
- Select crop type (Mustard, Groundnut, Sunflower, Soybean, Sesame, Safflower)
- Specify quantity in quintals (1 quintal = 100 kg)
- Set quality grade (Standard, Grade A, Grade B, Grade C)
- Define base price and minimum bid increment
- Set auction duration (1 hour to 7 days)
- Specify farm location and storage details

#### 2. **Monitor Active Auctions** (`/bidding/farmer/my-auctions`)
- View all auctions with status (active, completed, cancelled)
- Track number of bids received
- Monitor highest bid price
- View time remaining
- Quick access to manage actions

#### 3. **View Bids** (`/bidding/farmer/auction/<id>/bids`)
- See all bids sorted by price (highest first)
- View buyer details and bid amounts
- Check bid status and timestamps

#### 4. **Accept Bid** (`/bidding/farmer/auction/<id>/accept-bid`)
- Select and accept highest bid
- Automatically closes auction
- Rejects all other bids
- Notifies winning buyer

#### 5. **Reject Bid** (`/bidding/farmer/auction/<id>/reject-bid`)
- Decline bids that don't meet expectations
- Bidder receives notification
- Auction remains open for more bids

#### 6. **Send Counter Offer** (`/bidding/farmer/auction/<id>/counter-offer`)
- Propose price to interested buyers
- Keeps auction active
- Buyer can accept or continue bidding

#### 7. **Extend Duration** (`/bidding/farmer/auction/<id>/extend`)
- Extend auction time (1 to 7 additional hours)
- Useful when more bids expected
- All bidders notified of extension

#### 8. **Update Minimum Price** (`/bidding/farmer/auction/<id>/update-minimum`)
- Adjust base price during auction
- Affects new bids only
- Affects starting point for negotiations

#### 9. **Cancel Auction** (`/bidding/farmer/auction/<id>/cancel`)
- Cancel active auction
- All bidders notified
- No bids will be accepted

#### 10. **View Closed Auctions**
- See completed and cancelled auctions
- Review final prices achieved
- Track sales history

#### 11. **Dashboard Statistics** (`/bidding/farmer/dashboard/stats`)
- Total auctions created
- Active vs completed auctions
- Best price achieved
- Total bids received
- Performance metrics

### Buyer Workflow (To be implemented)

- Browse available auctions
- View auction details and quantity
- Place bids with auto-increment
- View my bids and status
- View won auctions
- Receive bid notifications

## Database Models

### Auction Model
```python
- id: UUID
- farmer_id: Reference to Farmer
- crop_name: String (Mustard, Groundnut, etc)
- quantity_quintals: Float
- quality_grade: String (A, B, C, Standard)
- base_price_per_quintal: Float
- minimum_bid_increment: Float
- current_highest_bid: Float
- start_time: DateTime
- end_time: DateTime
- status: String (active, completed, cancelled, closed)
- location: String
- district: String
- state: String
- description: Text
- harvest_date: Date
- storage_location: String
```

### Bid Model
```python
- id: UUID
- auction_id: Reference to Auction
- buyer_id: Reference to Buyer
- bid_price_per_quintal: Float
- bid_total_amount: Float
- status: String (active, accepted, rejected, expired)
- created_at: DateTime
```

### CounterOffer Model
```python
- id: UUID
- auction_id: Reference to Auction
- bid_id: Reference to Bid
- buyer_id: Reference to Buyer
- counter_price_per_quintal: Float
- status: String (pending, accepted, rejected, expired)
- created_at: DateTime
```

### AuctionNotification Model
```python
- id: UUID
- user_id: String
- user_type: String (farmer, buyer)
- auction_id: Reference to Auction
- notification_type: String
- message: Text
- is_read: Boolean
- created_at: DateTime
```

## API Endpoints

### Farmer Endpoints

```
GET    /bidding/farmer/dashboard              - Main dashboard
GET    /bidding/farmer/my-auctions            - List farmer's auctions
GET    /bidding/farmer/auction/<id>           - Get auction details
GET    /bidding/farmer/auction/<id>/bids      - View all bids
POST   /bidding/farmer/auction/<id>/accept-bid         - Accept a bid
POST   /bidding/farmer/auction/<id>/reject-bid         - Reject a bid
POST   /bidding/farmer/auction/<id>/counter-offer      - Send counter
POST   /bidding/farmer/auction/<id>/extend             - Extend duration
POST   /bidding/farmer/auction/<id>/update-minimum     - Update min price
POST   /bidding/farmer/auction/<id>/cancel             - Cancel auction
GET    /bidding/farmer/dashboard/stats        - Dashboard statistics
POST   /bidding/farmer/create-auction         - Create new auction
```

## Frontend Pages

### Farmer Side

1. **farmer_auction_dashboard.html** - Main dashboard with:
   - Statistics cards (Active, Completed, Best Price, Total Bids)
   - Auctions grid view
   - Quick action buttons
   - Real-time refresh (30 seconds)

2. **farmer_create_auction.html** - Auction creation form with:
   - Crop selection
   - Quantity and quality options
   - Pricing configuration
   - Duration selection
   - Location and logistics
   - Market price reference guide

## Workflow Examples

### Example 1: Simple Sale
```
1. Farmer creates auction for 10 quintals of Mustard
2. Farmer sets base price ₹5,200/quintal
3. Buyer 1 places bid at ₹5,300
4. Buyer 2 places higher bid at ₹5,400
5. Farmer reviews bids and accepts highest bid
6. Auction closes, buyer 2 wins
7. Transaction initiated
```

### Example 2: Negotiation
```
1. Farmer creates auction, base price ₹6,000/quintal
2. Buyer places bid at ₹5,800 (below base)
3. Farmer sends counter offer at ₹5,900
4. Buyer accepts counter offer
5. Sale completed
```

### Example 3: Active Bidding
```
1. Auction scheduled for 24 hours
2. Multiple bids received: ₹5,200, ₹5,300, ₹5,400
3. Just before end, farmer extends by 4 hours
4. New bidder places ₹5,600 bid
5. Farmer accepts final highest bid
```

## Features in Progress

- [ ] Buyer-side auction browsing and bidding
- [ ] Automated auction closure at end time
- [ ] WebSocket real-time bid notifications
- [ ] Payment integration
- [ ] Delivery tracking
- [ ] Rating and review system
- [ ] Dispute resolution
- [ ] Bulk auction uploads

## Usage

### Create Auction (Farmer)
```bash
curl -X POST /bidding/farmer/create-auction \
  -H "Content-Type: application/json" \
  -d '{
    "crop_name": "Mustard",
    "quantity_quintals": 10,
    "base_price": 5200,
    "duration_hours": 24,
    "location": "Farm Address",
    "district": "Indore"
  }'
```

### View My Auctions
```bash
curl /bidding/farmer/my-auctions
```

### Accept Bid
```bash
curl -X POST /bidding/farmer/auction/{auction_id}/accept-bid \
  -H "Content-Type: application/json" \
  -d '{"bid_id": "{bid_id}"}'
```

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Real-time**: Notifications (Email/Push)

## Security Considerations

- Session-based authentication for farmers
- Farmer can only manage their own auctions
- Buyer verification required for bidding
- Price validation and minimum bid enforcement
- Audit logs for all auction actions

## Future Enhancements

1. Real-time WebSocket updates
2. Mobile app for farmers
3. SMS notifications for farmers
4. Automated payment processing
5. Quality certification integration
6. Logistics partner integration
7. Insurance options
8. Warehouse receipt system
9. Bulk trading platform
10. Analytics and reporting

---

**Status**: Farmer-side functionality complete ✅  
**Next**: Implement buyer-side features
