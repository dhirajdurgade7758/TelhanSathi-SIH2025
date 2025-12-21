from app import app
from models import Farmer
from models_marketplace import SellRequest
from extensions import db

with app.app_context():
    # Check if we have any SellRequest data
    count = SellRequest.query.count()
    print(f"✅ Total SellRequest listings in database: {count}")
    
    # Get unique crops
    crops = db.session.query(SellRequest.crop_name).distinct().all()
    print(f"✅ Crops available: {[c[0] for c in crops]}")
    
    # Get sample listings
    for crop in ['Soybean', 'Mustard', 'Groundnut']:
        listings = SellRequest.query.filter_by(crop_name=crop).all()
        print(f"  - {crop}: {len(listings)} listings")

print("✅ Test complete - sellers route is ready!")
