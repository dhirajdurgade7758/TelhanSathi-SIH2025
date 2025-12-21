import sys
from datetime import datetime, timezone
from app import app, db
from models import Farmer

with app.app_context():

    print("🚀 Running setup_db.py ...")

    # DO NOT use db.create_all() when using migrations.
    # db.create_all()

    # Sample seed data
    seed_farmer_id = "567894251673"
    seed_phone = "+919405363574"

    # ---------- CHECK ALL UNIQUE FIELDS ----------
    existing = Farmer.query.filter(
        (Farmer.farmer_id == seed_farmer_id) |
        (Farmer.phone_number == seed_phone)
    ).first()

    if existing:
        print("⚠️ Seed farmer already exists. Skipping insertion.")
        print(f"   → Farmer ID: {existing.farmer_id}")
        print(f"   → Phone: {existing.phone_number}")
        exit(0)

    # ---------- INSERT NEW FARMER SAFELY ----------
    sample_farmer = Farmer(
        farmer_id=seed_farmer_id,
        name="Tanaji Durgade",
        date_of_birth=datetime.strptime("1980-05-15", "%Y-%m-%d").date(),
        gender="M",
        phone_number=seed_phone,
        caste_category="OBC",
        is_physically_handicapped=False,
        permanent_address="Gauri Shankar park, Miraj",
        district="Sangli",
        taluka="Miraj",
        village="Miraj",
        state="Maharashtra",
        pincode="416410",
        total_land_area_hectares=2.5,
        land_area_gunthas=100,
        land_holder_type="Owner",
        soil_type="Loamy",
        current_crops="Paddy, Wheat",
        is_pm_kisan_beneficiary=True,
        pm_kisan_reference_id="PM-KISAN-12345",
        is_verified=True,
        verification_timestamp=datetime.now(timezone.utc),
        harvest_date=None,
        land_unit="acre",
        onboarding_completed=False
    )

    db.session.add(sample_farmer)
    db.session.commit()

    print("✅ Sample farmer inserted successfully!")
