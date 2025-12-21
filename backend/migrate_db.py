import os
import sqlite3
from app import app, db
from models import Farmer, OTPRecord, SubsidyApplication, PriceAlert, FarmerReward

db_path = 'telhan_sathi.db'

# Drop all tables and recreate
with app.app_context():
    # Drop all tables
    db.drop_all()
    print("✅ All tables dropped!")
    
    # Create all tables fresh
    db.create_all()
    print("✅ Database tables created successfully!")
    
    # Seed sample farmer data for testing
    from datetime import datetime
    
    sample_farmer = Farmer(
        farmer_id="123456789012",
        name="Ramesh Kumar",
        date_of_birth=datetime.strptime("1980-05-15", "%Y-%m-%d").date(),
        gender="M",
        phone_number="9876543210",
        caste_category="OBC",
        is_physically_handicapped=False,
        permanent_address="Village Bayana, Bharatpur",
        district="Bharatpur",
        taluka="Bayana",
        village="Bayana",
        state="Rajasthan",
        pincode="321401",
        total_land_area_hectares=2.5,
        land_area_gunthas=100,
        land_holder_type="Owner",
        soil_type="Loamy",
        current_crops="Paddy, Wheat",
        is_pm_kisan_beneficiary=True,
        pm_kisan_reference_id="PM-KISAN-12345",
        is_verified=True,
        verification_timestamp=datetime.utcnow()
    )
    
    db.session.add(sample_farmer)
    db.session.commit()
    print("✅ Sample farmer seeded with complete AgriStack data!")
    print("\n📊 Database Ready!")
    print("Farmer ID: 123456789012")
    print("Name: Ramesh Kumar")
