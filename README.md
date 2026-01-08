# 🌾 Telhan Sathi - SIH 2025

**Problem Statement ID:** 1604 | **Theme:** Agriculture, FoodTech & Rural Development

> **Making Oilseeds More Profitable Than Paddy.**
> A comprehensive ecosystem combining AI, IoT, and Real-time Auction to de-risk oilseed farming and boost India's edible oil independence.

---

## 🎯 Project Overview

**Telhan Sathi** (तेलहन साथी) is a farmer-centric digital marketplace that empowers oilseed farmers with:
- **Real-time Auctions (NILAMI)** - Direct buyer connections without middlemen
- **AI-powered Profit Simulator** - ARIMA forecasting for ROI calculations
- **Crop Economics Analytics** - Comprehensive profitability analysis
- **IoT Integration** - Real-time field monitoring with weather alerts
- **Government Subsidies Database** - Eligibility checks and applications
- **Redemption Store** - Gamification through earn-and-redeem system

---

## 👨‍🌾 FARMER-SIDE FEATURES (10 Major Modules)

### 1. **Authentication & Onboarding**
- Registration flow with OTP verification
- Profile setup with farm details (location, crops, area)
- Language selection and UI preferences

### 2. **Dashboard & Home**
- Personalized main interface
- Quick access to all farmer modules
- Recent activities and alerts

### 3. **Auction Management (NILAMI)**
- **Create Auctions**: List crops with quantity, reserve price, auction duration
- **Edit Auctions**: Modify details before bidding starts
- **Real-time Bidding**: Live bid tracking and updates
- **Auction History**: Past auctions and winning bids

### 4. **Bid Management**
- Incoming bids with real-time notifications
- Counter-offer negotiation system
- Leaderboards for top buyers
- Accept/reject bid interface

### 5. **Communications**
- Chat system with individual buyers
- Message history and notifications
- Bidding inquiries and Q&A

### 6. **Profit Simulator** 🤖
- **AI-Powered ARIMA Forecasting** for crop prices
- Splitscreen comparison: "Paddy vs. Oilseed" ROI
- 12-month profit projections
- Scenario planning tools

### 7. **Crop Economics**
- Crop comparison matrices (yield, cost, profit)
- 12-month profitability trends with charts
- Detailed cost breakdowns
- Market demand analysis

### 8. **Weather & Field Monitoring** 📡
- Real-time IoT sensor data (temperature, humidity, soil moisture)
- Weather alerts and forecasts
- Disease risk indicators
- Automated irrigation recommendations

### 9. **Subsidies & Benefits**
- Government schemes database
- Eligibility checkers
- Application workflow
- Subsidy tracking

### 10. **Redemption Store** 🎁
- Earn coins through successful auctions
- Redeem products/services
- Loyalty rewards program
- Transaction history

---

## 🛍️ BUYER-SIDE FEATURES

### 1. **Registration & Login**
- Email/password authentication
- OTP verification
- Profile completion

### 2. **Dashboard**
- Main buyer interface
- Purchase history
- Quick stats (active bids, won auctions)

### 3. **Browse & Bid**
- Search and filter auctions by crop, location, price range
- Detailed auction information
- Place bids with real-time updates
- Counter-offer negotiation

### 4. **Bid Management**
- Track active bids and negotiations
- Bid history and status
- Counter-offer responses

### 5. **Saved Auctions**
- Watchlist functionality
- Price alerts
- Auction reminders

### 6. **Chat with Farmers**
- Direct messaging
- Clarification on crop details
- Negotiation discussions

### 7. **Account Management**
- Profile updates
- Purchase history
- Saved preferences

---

## 🤖 AI/ML FEATURES

### **ARIMA Time-Series Price Forecasting**
- Analyzes historical oilseed prices
- 12-month future price predictions
- Confidence intervals and trend analysis
- Dataset: Indian oilseeds historical prices (CSVs in `TelhanSathi/ml/datasets/`)

### **Profitability Calculations & ROI**
- Cost of cultivation tracker
- Expected yield calculator
- Revenue projections
- ROI comparison (Oilseeds vs. Traditional crops)
- Break-even analysis

**Models Location**: `TelhanSathi/ml/`
- `arima_price_forecaster.py` - Price forecasting engine
- `profit_simulator_arima.py` - ROI calculations
- `datasets/indian_oilseeds_prices.csv` - Historical data

---

## 🏗️ Tech Stack

| Layer         | Technology                                          |
| ------------- | --------------------------------------------------- |
| **Backend**   | Flask, SQLAlchemy, SQLite/PostgreSQL                |
| **Frontend**  | HTML5, CSS3, JavaScript, Bootstrap                  |
| **AI/ML**     | Python, Scikit-Learn, ARIMA, Pandas, NumPy          |
| **Database**  | SQLite (Development), PostgreSQL (Production)       |
| **IoT**       | ESP32, DHT11, Soil Moisture Sensors, MQTT           |
| **Messaging** | Flask-SocketIO for real-time notifications          |
| **Auth**      | Flask Sessions, OTP verification (Google/Gemini)   |
| **APIs**      | Weather API, Google Translate, Google AI            |

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip/conda
- Git

### Backend Setup (Flask)

```bash
# 1. Clone the repository
git clone https://github.com/dhirajdurgade7758/TelhanSathi-SIH2025.git
cd TelhanSathi-SIH2025/TelhanSathi

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create .env file with:
# SECRET_KEY=your-secret-key
# DATABASE_URL=sqlite:///telhan_sathi.db
# GOOGLE_API_KEY=your-google-api-key

# 5. Initialize database
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()

# 6. Run the application
python app.py
# Access at http://localhost:5000
```

### Key Modules Setup

```bash
# Profit Simulator & AI Models
cd ml
python arima_price_forecaster.py

# Field Monitoring (IoT)
# Configure MQTT broker settings in .env
# Ensure ESP32 devices are connected to same network
```

---

## 📁 Project Structure

```
TelhanSathi-SIH2025/
│
├── README.md
├── documents/
│   └── screenshots/           # UI/UX Screenshots
│
└── TelhanSathi/              # Main Application
    ├── app.py                # Flask app entry point
    ├── models.py             # Database models
    ├── models_marketplace_keep.py  # Market models
    ├── extensions.py         # Flask extensions (db, migrate)
    ├── utils.py              # Helper functions
    ├── translations.py       # Multilingual support
    ├── requirements.txt      # Python dependencies
    │
    ├── routes/               # Route handlers (Blueprints)
    │   ├── auth.py          # Farmer authentication
    │   ├── buyer_auth.py    # Buyer authentication
    │   ├── onboarding.py    # Profile setup
    │   ├── bidding.py       # Auction & bid management
    │   ├── crop_economics.py # Crop analysis
    │   ├── profit_simulator.py # AI profit calculator
    │   ├── field_monitoring.py # IoT sensor data
    │   ├── weather.py       # Weather integration
    │   ├── subsidies.py     # Government schemes
    │   ├── redemption_store.py # Coin redemption
    │   ├── notifications.py # Real-time alerts
    │   ├── sahayak.py       # Chat & support
    │   └── admin.py         # Admin dashboard
    │
    ├── ml/                   # Machine Learning
    │   ├── arima_price_forecaster.py    # ARIMA model
    │   ├── profit_simulator_arima.py    # ROI calculations
    │   ├── datasets/
    │   │   └── indian_oilseeds_prices.csv
    │   └── models/          # Saved ML models
    │
    ├── templates/           # HTML templates
    │   ├── base.html       # Base template
    │   ├── login.html
    │   ├── buyer_login.html
    │   ├── buyer_register.html
    │   ├── dashboard.html  # Farmer dashboard
    │   ├── buyer_dashboard.html
    │   ├── farmer_auction_*.html  # Auction pages
    │   ├── profit_simulator.html
    │   ├── crop_economics.html
    │   ├── field_monitoring.html
    │   ├── weather.html
    │   ├── subsidies_*.html
    │   ├── redemption_store.html
    │   ├── farmer_chats.html
    │   ├── notifications_*.html
    │   └── ...
    │
    ├── static/             # Static assets
    │   ├── css/
    │   │   └── onboarding.css
    │   ├── js/
    │   │   ├── chat.js     # Real-time chat
    │   │   ├── iot_device.js  # IoT integration
    │   │   └── onboarding.js
    │   ├── img/            # Images & icons
    │   └── uploads/        # User uploads
    │       ├── auctions/   # Auction images
    │       └── profile_pics/ # Profile pictures
    │
    ├── migrations/         # Database migrations
    │   ├── alembic.ini
    │   └── versions/       # Migration files
    │
    ├── instance/           # Instance folder (local)
    ├── __pycache__/
    └── scripts/            # Utility scripts
```

---

## 📸 FEATURE SCREENSHOTS

### Farmer Interface

#### **Home Page**
![Home Page](documents/screenshots/home%20page.jpeg)

#### **Auction Dashboard - Farmer View**
Manage and monitor all auctions created
![Bidding Dashboard Farmer](documents/screenshots/bidding%20dashboard%20farmer.jpeg)

#### **View Auction Details**
Detailed auction information and bid tracking
![Auction Details Modal](documents/screenshots/winning%20bid%20details%20page%20farmer.jpeg)

#### **Winning Bid Details**
Transaction confirmation and buyer details
![Winning Bid Details](documents/screenshots/winning%20bid%20details%20page%20farmer.jpeg)

#### **Profit Simulator** 🤖
AI-powered ROI calculator with ARIMA forecasting
![Profit Simulator](documents/screenshots/profit%20simulator%20page%20farmer.jpeg)

#### **Crop Economics Analysis**
Detailed crop comparison and profitability trends
![Crop Economics](documents/screenshots/crop%20economics%20page%20farmer.jpeg)

#### **12-Month Profitability Trends**
Extended analysis with historical and projected data
![Crop Economics Trends](documents/screenshots/detailed%20crop%20economics%20page%20with%2012%20months%20trend%20farmer.jpeg)

#### **Government Subsidies & Schemes**
Browse and apply for government benefits
![Subsidies Page](documents/screenshots/schemes%20and%20subsides%20page%20farmer.jpeg)

#### **Redemption Store** 🎁
Earn and redeem coins for products/services
![Redemption Store](documents/screenshots/redeemption%20store%20page%20farmer.jpeg)

#### **Chat with Farmers** 💬
Direct communication with buyers
![Chat with Farmer](documents/screenshots/chat%20with%20farmer%20page%20buyer.jpeg)

---

### Buyer Interface

#### **Buyer Dashboard**
Main interface with active bids and purchase history
![Buyer Dashboard](documents/screenshots/bidding%20dashboard%20buyer.jpeg)

#### **Browse & Place Bids**
Search, filter, and bid on available auctions
![View Auction Details](documents/screenshots/view%20auction%20details%20modal%20buyer.jpeg)

#### **My Bids Tracking**
Monitor active bids and negotiations
![My Bids Page](documents/screenshots/mybids%20page%20buyer.jpeg)

#### **Chat with Farmers** 💬
Real-time messaging with sellers
![Chat with Farmer Buyer](documents/screenshots/chat%20with%20farmer%20page%20buyer.jpeg)

---

## 🚀 Key Features Deep Dive

### **Real-time Auction System (NILAMI)**
- ✅ Create auctions with reserve pricing
- ✅ Live bidding with real-time updates
- ✅ Counter-offer negotiations
- ✅ Automated bid notifications
- ✅ Transaction history

### **AI-Powered Profit Simulator**
- ✅ ARIMA time-series forecasting
- ✅ 12-month price predictions
- ✅ ROI comparison (Oilseeds vs. Paddy)
- ✅ Break-even analysis
- ✅ Cost tracking and projections

### **Crop Economics Module**
- ✅ Multi-crop comparison matrices
- ✅ Profitability analysis by crop
- ✅ Market demand visualization
- ✅ Historical price data
- ✅ Yield projections

### **IoT Field Monitoring**
- ✅ Real-time sensor data (temperature, humidity, soil moisture)
- ✅ Weather integration and alerts
- ✅ Disease risk indicators
- ✅ Automated recommendations
- ✅ Data visualization dashboard

### **Subsidies & Government Schemes**
- ✅ Comprehensive schemes database
- ✅ Eligibility checker
- ✅ Application workflow
- ✅ Status tracking
- ✅ Document management

### **Redemption Store (Gamification)**
- ✅ Earn coins per successful auction
- ✅ Coin-based rewards system
- ✅ Product/service catalog
- ✅ Transaction history
- ✅ Loyalty tier system

---

## 🔄 User Workflows

### **Farmer Workflow**
```
1. Register/Login → 2. Complete Onboarding → 3. Dashboard Access
4. Create Auction → 5. Receive Bids → 6. Accept Best Offer
7. Chat with Buyer → 8. Earn Coins → 9. Redeem Rewards
```

### **Buyer Workflow**
```
1. Register/Login → 2. Browse Auctions → 3. Filter & Search
4. View Details → 5. Place Bid → 6. Negotiate Offer
7. Win Auction → 8. Chat with Farmer → 9. Complete Transaction
```

### **Profit Planning Workflow**
```
1. Select Crop → 2. View Historical Data → 3. Run AI Forecasting
4. Compare ROI (Oilseeds vs. Paddy) → 5. Analyze Crop Economics
6. Check Subsidies → 7. Plan Next Season
```

---

## 🔐 Security Features

- ✅ Password hashing and salting
- ✅ OTP-based verification
- ✅ Session management with secure cookies
- ✅ CSRF protection
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS protection in templates

---

## 📊 Database Schema Overview

**Key Models:**
- `User` - Farmer/Buyer accounts with roles
- `Auction` - Marketplace listings with timestamps
- `Bid` - Bidding records with buyer-farmer links
- `Chat` - Real-time messaging between users
- `Crop` - Crop data for economics and forecasting
- `IoTSensor` - Field monitoring sensor readings
- `Subsidy` - Government scheme listings
- `Coin` - Gamification currency and transactions

---

## 🚨 Current Status & Roadmap

### ✅ Completed
- Core auction management system
- Real-time bidding engine
- AI profit simulator with ARIMA
- Crop economics analytics
- Chat system with Socket.IO
- Government subsidies database
- Redemption store backend
- IoT sensor integration
- Multi-language support

### 🔄 In Progress
- Mobile app (React Native)
- Enhanced analytics dashboard
- Blockchain integration for buy-back guarantees
- Voice-first interface (Boli-Se-Kheti)

### 📋 Planned
- Machine learning disease detection (Edge AI)
- Equipment rental marketplace (Yantra Sathi)
- Blockchain smart contracts
- API documentation (Swagger)
- Advanced data analytics

---

## 👥 The Team - Algo Sapiens

| Role | Member | Responsibility |
|------|--------|-----------------|
| **Backend Lead** | Dhiraj Durgade | Django/Flask architecture, database design, API development |
| **Blockchain Dev** | Harsh | Smart contracts, Web3 integration |
| **AI/ML Engineer** | Ujjwal | ARIMA models, profit calculations, forecasting |
| **Frontend Dev** | Vishal | UI/UX, dashboard design |
| **Frontend Dev** | Janhvi | Component development, responsive design |
| **IoT Engineer** | Naman | ESP32 configuration, sensor integration |
| **Mentor** | Nisarg Wath | Project guidance and support |

---

## 📞 Contact & Support

- **GitHub**: [TelhanSathi-SIH2025](https://github.com/dhirajdurgade7758/TelhanSathi-SIH2025)
- **Owner**: Dhiraj Durgade
- **Issue Reporting**: Use GitHub Issues for bugs and feature requests

---

## 📄 License

This project is developed for **Smart India Hackathon 2025** under Problem Statement 1604.

---

## 🙏 Acknowledgments

- **Smart India Hackathon** - Platform and support
- **Indian Agricultural Ministry** - Problem statement and insights
- **Agricultural Data Partners** - Historical crop price data
- **Google Cloud** - APIs for translation and AI services
- **Open Source Community** - Flask, SQLAlchemy, Scikit-Learn, and other libraries

---

Built with ❤️ for Indian Farmers at **Smart India Hackathon 2025**
**Telhan Sathi (तेलहन साथी) - Empowering Farmers, Enabling Prosperity** 🌾
│   │   └── api/               # API Integration Service
│   └── package.json
│
├── iot_firmware/              # NAMAN'S DOMAIN
│   ├── src/                   # Arduino/ESP32 C++ Code
│   ├── libraries/             # Sensor libraries
│   └── schematic.png          # Circuit Diagram (for Judges to see)
│
├── blockchain/                # HARSH'S DOMAIN
│   ├── contracts/             # Smart Contract (.sol)
│   ├── tests/                 # Test scripts
│   └── deploy.js              # Deployment scripts
│
├── docs/                      # DOCUMENTATION
│   ├── screenshots/           # App Screenshots
│   ├── diagrams/              # Architecture Diagrams
│   └── user_manual.pdf
│
├── .gitignore
└── README.md
```
