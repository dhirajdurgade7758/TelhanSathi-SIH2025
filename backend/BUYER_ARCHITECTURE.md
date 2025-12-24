# Buyer-Side Auction System - Architecture & API Reference

**Date:** December 24, 2025  
**Version:** 1.0.0  
**Status:** Production Ready

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BUYER PORTAL                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           PRESENTATION LAYER (HTML/CSS/JS)          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ Dashboard │ Browse │ Details │ MyBids │ Won │ Notif  │   │
│  └──────────────────────────────────────────────────────┘   │
│              ↓                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         APPLICATION LAYER (Flask Routes)            │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Routes defined in /routes/bidding.py               │   │
│  │  - 14 buyer-specific endpoints                      │   │
│  │  - Session-based authentication                     │   │
│  │  - Input validation & error handling                │   │
│  └──────────────────────────────────────────────────────┘   │
│              ↓                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        DATA LAYER (SQLAlchemy ORM)                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Models: Buyer, Auction, Bid, AuctionNotification   │   │
│  │  Relationships: One-to-many, Foreign keys           │   │
│  │  Queries: Optimized with pagination                 │   │
│  └──────────────────────────────────────────────────────┘   │
│              ↓                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         DATABASE (SQLite/PostgreSQL)                │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Tables: buyers, auctions, bids, notifications      │   │
│  │  Indexes: For performance optimization              │   │
│  │  Integrity: Foreign key constraints                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### Tables & Relationships

```
┌─────────────────┐         ┌─────────────────┐
│    BUYERS       │         │    AUCTIONS     │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │         │ id (PK)         │
│ email (UNIQUE)  │         │ farmer_id (FK)  │
│ password        │         │ crop_name       │
│ buyer_name      │         │ quantity        │
│ phone           │         │ base_price      │
│ company_name    │         │ current_bid     │
│ location        │         │ start_time      │
│ district        │         │ end_time        │
│ state           │         │ status          │
│ is_active       │         │ location        │
│ created_at      │         │ created_at      │
└─────────────────┘         └─────────────────┘
        ▲                           ▲
        │                           │
        │ (1)                   (1) │
        │                           │
        │ (Many)              (Many)│
        │                           │
    ┌───────────────────────────────┘
    │
    │   ┌──────────────────┐
    │   │      BIDS        │
    │   ├──────────────────┤
    │   │ id (PK)          │
    │   │ auction_id (FK)  │
    │   │ buyer_id (FK) ───┤────┘
    │   │ bid_price        │
    │   │ bid_total        │
    │   │ status           │
    │   │ created_at       │
    │   └──────────────────┘
    │
    │   ┌──────────────────────────┐
    └───│  NOTIFICATIONS           │
        ├──────────────────────────┤
        │ id (PK)                  │
        │ user_id (FK to Buyer)    │
        │ auction_id (FK)          │
        │ notification_type        │
        │ message                  │
        │ is_read                  │
        │ created_at               │
        └──────────────────────────┘
```

### Field Specifications

**BUYERS Table:**
```python
id              VARCHAR(36) PRIMARY KEY
email           VARCHAR(255) UNIQUE, NOT NULL
password        VARCHAR(255) NOT NULL (hashed)
buyer_name      VARCHAR(255) NOT NULL
phone           VARCHAR(20)
company_name    VARCHAR(255)
location        VARCHAR(255)
district        VARCHAR(100)
state           VARCHAR(100) DEFAULT 'Maharashtra'
is_verified     BOOLEAN DEFAULT FALSE
is_active       BOOLEAN DEFAULT TRUE
created_at      TIMESTAMP DEFAULT NOW()
updated_at      TIMESTAMP DEFAULT NOW()
```

**AUCTIONS Table:**
```python
id                          VARCHAR(36) PRIMARY KEY
farmer_id                   VARCHAR(36) FOREIGN KEY (NOT NULL)
crop_name                   VARCHAR(100) NOT NULL
quantity_quintals           FLOAT NOT NULL
quality_grade               VARCHAR(50) DEFAULT 'Standard'
base_price_per_quintal      FLOAT NOT NULL
minimum_bid_increment       FLOAT DEFAULT 50
current_highest_bid         FLOAT
start_time                  TIMESTAMP NOT NULL
end_time                    TIMESTAMP NOT NULL
status                      VARCHAR(50) DEFAULT 'active'
location                    VARCHAR(255) NOT NULL
district                    VARCHAR(100) NOT NULL
state                       VARCHAR(100) DEFAULT 'Maharashtra'
description                 TEXT
harvest_date                DATE
storage_location            VARCHAR(255)
created_at                  TIMESTAMP DEFAULT NOW()
updated_at                  TIMESTAMP DEFAULT NOW()

Indexes:
- (farmer_id, status, created_at)
- (status, created_at)
```

**BIDS Table:**
```python
id                      VARCHAR(36) PRIMARY KEY
auction_id              VARCHAR(36) FOREIGN KEY (NOT NULL)
buyer_id                VARCHAR(36) FOREIGN KEY (NOT NULL)
bid_price_per_quintal   FLOAT NOT NULL
bid_total_amount        FLOAT NOT NULL
status                  VARCHAR(50) DEFAULT 'active'
created_at              TIMESTAMP DEFAULT NOW()
updated_at              TIMESTAMP DEFAULT NOW()

Indexes:
- (auction_id, buyer_id) UNIQUE
- (auction_id, bid_price DESC)
- (buyer_id, created_at DESC)
```

**AUCTION_NOTIFICATIONS Table:**
```python
id                  VARCHAR(36) PRIMARY KEY
user_id             VARCHAR(36) NOT NULL
user_type           VARCHAR(50) NOT NULL
auction_id          VARCHAR(36) FOREIGN KEY (NOT NULL)
notification_type   VARCHAR(50) NOT NULL
message             TEXT
is_read             BOOLEAN DEFAULT FALSE
created_at          TIMESTAMP DEFAULT NOW()

Indexes:
- (user_id, user_type, is_read, created_at DESC)
- (auction_id, user_type)
```

---

## 🔗 API Endpoints Reference

### Authentication (Existing)
```
POST   /buyer/login
GET    /buyer/register
POST   /buyer/register
GET    /buyer/logout
```

### Dashboard
```
GET /bidding/buyer/dashboard
Description: Render buyer dashboard page
Response: HTML page with stats
Auth: Required (buyer_id_verified in session)

GET /bidding/buyer/dashboard/stats
Description: Get dashboard statistics
Response: JSON
Status Codes: 200, 401
Response Body:
{
  "total_bids": 12,
  "active_bids": 5,
  "winning_bids": 2,
  "won_auctions": 3,
  "unread_notifications": 2
}
```

### Browse Auctions
```
GET /bidding/buyer/browse-auctions
Description: Render browse page
Response: HTML page
Auth: Required

GET /bidding/buyer/auctions/api?page=1&crop=&district=&sort=newest
Description: Get list of active auctions
Response: JSON
Status Codes: 200, 401, 500
Query Parameters:
- page: int (default 1)
- crop: string (optional search)
- district: string (optional filter)
- sort: string (default newest)

Response Body:
{
  "total": 45,
  "page": 1,
  "pages": 4,
  "auctions": [
    {
      "id": "uuid",
      "crop_name": "Mustard",
      "quantity_quintals": 100.0,
      "base_price": 5000.0,
      "highest_bid": 5500.0,
      "quality_grade": "A",
      "location": "Nashik",
      "district": "Nashik",
      "farmer_name": "Ramesh Sharma",
      "bids_count": 5,
      "status": "active",
      "time_remaining": 7200,
      "created_at": "2025-12-24T10:30:00"
    }
  ]
}
```

### Auction Details
```
GET /bidding/buyer/auction/<auction_id>
Description: Render auction details page
Response: HTML page
Auth: Required
Status Codes: 200, 401, 404

GET /bidding/buyer/auction/<auction_id>/api
Description: Get detailed auction information
Response: JSON
Status Codes: 200, 401, 404, 500

Response Body:
{
  "id": "uuid",
  "crop_name": "Groundnut",
  "quantity_quintals": 75.0,
  "quality_grade": "A",
  "base_price": 6000.0,
  "current_highest_bid": 6500.0,
  "minimum_bid_increment": 50.0,
  "location": "Indore",
  "district": "Indore",
  "state": "Madhya Pradesh",
  "description": "Fresh harvest...",
  "harvest_date": "2025-12-20",
  "storage_location": "Cold storage 5",
  "start_time": "2025-12-24T10:00:00",
  "end_time": "2025-12-24T22:00:00",
  "time_remaining": 28800,
  "status": "active",
  "farmer_name": "Priya Desai",
  "farmer_location": "Indore",
  "bids_count": 8,
  "my_bid": {
    "bid_id": "uuid",
    "bid_price": 6500.0,
    "bid_total": 487500.0,
    "status": "active",
    "created_at": "2025-12-24T15:30:00"
  },
  "top_bids": [
    {
      "buyer_id": "uuid",
      "bid_price": 6500.0,
      "bid_total": 487500.0,
      "created_at": "2025-12-24T15:30:00"
    }
  ]
}
```

### Place Bid
```
POST /bidding/buyer/auction/<auction_id>/place-bid
Description: Place or update bid on auction
Request Headers: Content-Type: application/json
Request Body:
{
  "bid_price": 6500.0
}
Response: JSON
Status Codes: 201, 400, 401, 404, 500
Auth: Required

Response Body (Success):
{
  "success": true,
  "message": "Bid placed successfully",
  "bid_id": "uuid",
  "bid_price": 6500.0,
  "bid_total": 487500.0
}

Error Responses:
{
  "error": "Bid must be at least ₹6550/q"
}
{
  "error": "This auction is no longer active"
}
{
  "error": "Auction has ended"
}
```

### My Bids
```
GET /bidding/buyer/my-bids
Description: Render my bids page
Response: HTML page
Auth: Required

GET /bidding/buyer/bids/api
Description: Get buyer's all bids
Response: JSON
Status Codes: 200, 401, 500

Response Body:
{
  "total_bids": 12,
  "bids": [
    {
      "bid_id": "uuid",
      "auction_id": "uuid",
      "crop_name": "Mustard",
      "bid_price": 5500.0,
      "bid_total": 550000.0,
      "quantity": 100.0,
      "status": "active",
      "auction_status": "active",
      "is_winning": true,
      "auction_active": true,
      "farmer_name": "Ramesh Sharma",
      "location": "Nashik",
      "bid_date": "2025-12-24T15:45:00",
      "auction_end": "2025-12-24T22:00:00"
    }
  ]
}
```

### Won Auctions
```
GET /bidding/buyer/won-auctions
Description: Render won auctions page
Response: HTML page
Auth: Required

GET /bidding/buyer/won-auctions/api
Description: Get buyer's won auctions
Response: JSON
Status Codes: 200, 401, 500

Response Body:
{
  "total_won": 5,
  "auctions": [
    {
      "auction_id": "uuid",
      "crop_name": "Mustard",
      "quantity": 100.0,
      "winning_price": 5500.0,
      "total_amount": 550000.0,
      "location": "Nashik",
      "farmer_name": "Ramesh Sharma",
      "auction_date": "2025-12-20T10:00:00",
      "completed_date": "2025-12-24T22:00:00"
    }
  ]
}
```

### Notifications
```
GET /bidding/buyer/notifications
Description: Render notifications page
Response: HTML page
Auth: Required

GET /bidding/buyer/notifications/api
Description: Get buyer's notifications
Response: JSON
Status Codes: 200, 401, 500

Response Body:
{
  "unread_count": 3,
  "total_count": 24,
  "notifications": [
    {
      "notification_id": "uuid",
      "type": "new_bid",
      "message": "New bid received: ₹5500/q",
      "auction_id": "uuid",
      "crop_name": "Mustard",
      "is_read": false,
      "created_at": "2025-12-24T16:30:00"
    }
  ]
}

POST /bidding/buyer/notifications/<notification_id>/read
Description: Mark notification as read
Response: JSON
Status Codes: 200, 401, 403, 404, 500

Response Body:
{
  "success": true
}
```

---

## 🔐 Error Response Format

### Standard Error Response
```json
{
  "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes Used

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Bid placed successfully |
| 201 | Created | New bid created |
| 400 | Bad Request | Bid validation failed |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | Trying to access other buyer's data |
| 404 | Not Found | Auction not found |
| 500 | Server Error | Database error |

---

## 🔄 Data Flow Diagrams

### Bid Placement Flow
```
┌─────────────────┐
│ Buyer enters    │
│ bid amount      │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ Frontend validation  │
│ - Check minimum      │
│ - Check increment    │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Send POST request    │
│ /place-bid with data │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Backend validation   │
│ - Check bid rules    │
│ - Check auction time │
│ - Check user auth    │
└────────┬─────────────┘
         │
    ┌────┴────┐
    │          │
   YES        NO
    │          │
    ▼          ▼
┌────────┐  ┌──────────┐
│ Update │  │ Return   │
│auction │  │error 400 │
└────┬───┘  └──────────┘
     │
     ▼
┌──────────────┐
│Create notif  │
│for farmer    │
└────┬─────────┘
     │
     ▼
┌──────────────┐
│Return success│
│to frontend   │
└──────────────┘
```

### Auction Listing Flow
```
┌──────────────────┐
│ User clicks      │
│ "Browse"         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ GET auctions/api │
│ ?page=1&sort=new │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│ Query database:      │
│ - Filter by status   │
│ - Apply search       │
│ - Sort results       │
│ - Paginate (12/page) │
└────────┬─────────────┘
         │
         ▼
┌──────────────────┐
│ Format response  │
│ as JSON          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Frontend renders │
│ auction cards    │
└──────────────────┘
```

---

## 📱 Response Time Targets

| Endpoint | Target | Notes |
|----------|--------|-------|
| Dashboard | < 2s | Stats calculation |
| Browse auctions | < 2s | With pagination |
| Auction details | < 1s | With bid lookup |
| Place bid | < 1s | Update only |
| My bids | < 2s | With filtering |
| Won auctions | < 2s | Join with auction |
| Notifications | < 2s | With sorting |

---

## 🔍 Query Optimization

### Key Database Indexes
```sql
-- AUCTIONS table
CREATE INDEX idx_auctions_farmer_status_created 
ON auctions(farmer_id, status, created_at DESC);

CREATE INDEX idx_auctions_status_created 
ON auctions(status, created_at DESC);

-- BIDS table
CREATE UNIQUE INDEX idx_bids_auction_buyer 
ON bids(auction_id, buyer_id);

CREATE INDEX idx_bids_auction_price 
ON bids(auction_id, bid_price_per_quintal DESC);

CREATE INDEX idx_bids_buyer_created 
ON bids(buyer_id, created_at DESC);

-- NOTIFICATIONS table
CREATE INDEX idx_notifications_user_read 
ON auction_notifications(user_id, is_read, created_at DESC);
```

### Query Optimization Techniques
- Use pagination to limit results
- Pre-load relationships with lazy loading
- Filter at database level, not in Python
- Use aggregate functions when possible
- Cache frequently accessed data
- Use connection pooling

---

## 🎯 Session Management

### Session Variables
```python
session['buyer_id_verified']  # UUID of buyer
session['buyer_email']        # Buyer's email
session['buyer_name']         # Buyer's name
```

### Session Lifecycle
```
1. Login page (/buyer/login)
   ↓
2. POST credentials
   ↓
3. Verify password
   ↓
4. Set session variables
   ↓
5. Redirect to dashboard
   ↓
6. All subsequent requests check session
   ↓
7. Logout clears session
```

### Session Security
- Session ID is HttpOnly cookie
- Session ID is renewed on login
- Session timeout after inactivity
- HTTPS required in production
- Secure cookie flags enabled

---

## 🚀 Deployment Considerations

### Environment Variables Needed
```bash
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/db
DEBUG=False
```

### Database Setup
```bash
# Create tables
flask db upgrade

# Create indexes
CREATE INDEX ... (see above)

# Verify schema
SELECT * FROM information_schema.tables;
```

### Performance Monitoring
- Track endpoint response times
- Monitor database query times
- Log slow queries
- Track active connections
- Monitor CPU and memory usage
- Set up error alerts

### Scaling Strategy
- Horizontal scaling: Load balancer + multiple instances
- Vertical scaling: Increase server resources
- Database optimization: Query optimization + caching
- CDN: Static assets caching
- Message queue: For notifications

---

## 📊 Data Volume Estimates

### For 1000 Buyers
- Buyers table: ~1000 rows
- Auctions: ~50/day = ~18,250/year
- Bids: ~100/auction = 1,825,000/year
- Notifications: ~500/day = 182,500/year

### Storage Requirements
- Buyers: ~500 KB
- Auctions: ~5 MB
- Bids: ~50 MB
- Notifications: ~20 MB
- Total: ~75 MB

### Query Performance
- Browse auctions: < 100ms (with indexes)
- Get my bids: < 200ms (with pagination)
- Place bid: < 50ms (single update)
- Notifications: < 150ms (with sorting)

---

## 🎓 Configuration Reference

### Flask Configuration
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
JSON_SORT_KEYS = False
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 86400
```

### Application Setup
```python
# routes/bidding.py
bidding_bp = Blueprint('bidding', __name__, url_prefix='/bidding')

# In app.py
app.register_blueprint(bidding_bp)
```

### Database Setup
```python
# extensions.py
db = SQLAlchemy()

# app.py
db.init_app(app)
```

---

## 📖 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-24 | Initial release - Complete buyer functionality |

---

## 📞 Support Resources

- **Documentation:** `/backend/BUYER_AUCTION_FEATURES.md`
- **Quick Start:** `/backend/BUYER_QUICKSTART.md`
- **Implementation:** `/backend/BUYER_IMPLEMENTATION_SUMMARY.md`
- **Checklist:** `/backend/BUYER_FEATURES_CHECKLIST.md`

---

**This architecture ensures:**
- ✅ Scalability
- ✅ Performance
- ✅ Security
- ✅ Maintainability
- ✅ Reliability

**Status:** Production Ready ✅
