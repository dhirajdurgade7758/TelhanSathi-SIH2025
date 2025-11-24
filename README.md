# 🌾 Telhan Sathi - SIH 2025

**Problem Statement ID:** 1604 | **Theme:** Agriculture, FoodTech & Rural Development

> **Making Oilseeds More Profitable Than Paddy.**
> A comprehensive ecosystem combining AI, IoT, and Blockchain to de-risk oilseed farming and boost India's edible oil independence.

---

## 🚀 Features

* **🔮 Virtual Profit Simulator:** Splitscreen calculator showing "Paddy vs. Oilseed" ROI using real-time data.
* **🗣️ Voice-First Interface:** "Boli-Se-Kheti" enables illiterate farmers to navigate the app using voice commands.
* **🦠 Rog Mukti (AI Doctor):** Offline disease detection for crops using on-device Edge AI.
* **🚜 Yantra Sathi:** Peer-to-peer equipment rental (Uber for Tractors).
* **🔗 Blockchain Assurance:** "Digital Samjhauta" ensures guaranteed buy-back of harvests.

---

## 🏗️ Tech Stack

| Component      | Technology                                                       |
| -------------- | ---------------------------------------------------------------- |
| **Backend**    | Django REST Framework, PostgreSQL, PostGIS, Celery               |
| **Frontend**   | React Native (Mobile), React.js (Admin Dashboard)                |
| **AI / ML**    | Scikit-Learn (Yield), Prophet (Price), TensorFlow Lite (Disease) |
| **IoT**        | ESP32, DHT11, Soil Moisture Sensors, MQTT                        |
| **Blockchain** | Hyperledger Fabric / Ethereum (Testnet)                          |

---

## 🛠️ Installation & Setup

### 1. Backend (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Mobile App

```bash
cd mobile_app
npm install
npm start
```

### 3. AI Engine

```bash
cd ai_engine
pip install -r requirements.txt
python inference_service.py
```

---

## 👥 The Team - Algo Sapiens

* **Dhiraj:** Backend Lead & System Architect
* **Harsh:** Blockchain Developer & Full Stack Support
* **Ujjwal:** AI/ML Engineer
* **Vishal & Janhvi:** Frontend & UI/UX Developers
* **Naman:** IoT & Hardware Engineer
* **Mentor:** Nisarg Wath

Built with ❤️ for Indian Farmers at Smart India Hackathon 2025

---

## 📁 Project Structure (TelhanSathi-SIH2025/)

```
TelhanSathi-SIH2025/
│
├── backend/                   # DHIRAJ'S DOMAIN (Django)
│   ├── config/                # Main Settings (urls.py, settings.py)
│   ├── users/                 # Custom Farmer Login App
│   ├── analysis/              # Profit Simulator & Logic
│   ├── market/                # Market Linkage & Smart Contract Logic
│   ├── support/               # Subsidies & Gamification
│   ├── requirements.txt       # Python dependencies
│   └── manage.py
│
├── ai_engine/                 # UJJWAL'S DOMAIN
│   ├── datasets/              # CSVs for Yield/Price data
│   ├── models/                # Saved .pkl / .h5 files
│   ├── training_scripts/      # Jupyter Notebooks or Python scripts
│   └── inference_service.py   # The script Dhiraj imports to get predictions
│
├── mobile_app/                # VISHAL & JANHVI'S DOMAIN
│   ├── assets/                # Images, Fonts, TFLite models
│   ├── src/
│   │   ├── screens/           # Login, Dashboard, Market
│   │   ├── components/        # Buttons, Cards
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
