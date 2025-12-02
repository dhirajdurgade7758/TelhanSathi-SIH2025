import sys
from datetime import datetime, timezone
from app import app, db
from models import Farmer

with app.app_context():

    print("🚀 Running setup_db.py ...")

    # DO NOT use db.create_all() when using migrations.
    # db.create_all()

    # Sample seed data
    seed_aadhaar = "241632683724"
    seed_farmer_id = "567894251673"
    seed_phone = "+919405363574"
    seed_email = "ramesh@7785.com"

    # ---------- CHECK ALL UNIQUE FIELDS ----------
    existing = Farmer.query.filter(
        (Farmer.aadhaar_number == seed_aadhaar) |
        (Farmer.farmer_id == seed_farmer_id) |
        (Farmer.phone_number == seed_phone) |
        (Farmer.email == seed_email)
    ).first()

    if existing:
        print("⚠️ Seed farmer already exists. Skipping insertion.")
        print(f"   → Farmer ID: {existing.farmer_id}")
        print(f"   → Phone: {existing.phone_number}")
        print(f"   → Aadhaar: {existing.aadhaar_number}")
        exit(0)

    # ---------- INSERT NEW FARMER SAFELY ----------
    sample_farmer = Farmer(
        farmer_id=seed_farmer_id,
        name="Tanaji Durgade",
        aadhaar_number=seed_aadhaar,
        date_of_birth=datetime.strptime("1980-05-15", "%Y-%m-%d").date(),
        gender="M",
        phone_number=seed_phone,
        email=seed_email,
        caste_category="OBC",
        is_physically_handicapped=False,
        is_maharashtra_resident=True,
        permanent_address="Gauri Shankar park, Miraj",
        district="Sangli",
        taluka="Miraj",
        village="Miraj",
        state="Maharashtra",
        pincode="416410",
        latitude=27.2232,
        longitude=77.4470,
        land_survey_numbers="12/A, 13/B",
        total_land_area_hectares=2.5,
        land_area_gunthas=100,
        land_holder_type="Owner",
        soil_type="Loamy",
        current_crops="Paddy, Wheat",

        # Financial details
        bank_name="Bank of Baroda",
        bank_branch="Miraj Branch",
        account_number="1234567890",
        account_holder_name="Dhiraj Durgade",
        ifsc_code="SBIN0001234",

        # PM-KISAN
        is_pm_kisan_beneficiary=True,
        pm_kisan_reference_id="PM-KISAN-12345",

        # Verification
        is_verified=True,
        verification_timestamp=datetime.now(timezone.utc),
        documents_verified=True,

        # Default onboarding new fields
        irrigation_type=None,
        harvest_date=None,
        land_unit="acre",
        onboarding_completed=False
    )

    db.session.add(sample_farmer)
    db.session.commit()

    print("✅ Sample farmer inserted successfully!")
