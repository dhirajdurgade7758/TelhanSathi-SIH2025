"""
Seed script to populate the database with sample crop listings and sell requests
for crop economics dashboard testing
"""

import sys
from datetime import datetime
from app import app
from extensions import db
from models_marketplace import SellRequest, CropListing
from models import Farmer

def seed_crop_data():
    """Add sample crop listings and sell requests with various prices"""
    
    with app.app_context():
        # Get a sample farmer (or create one)
        sample_farmer = Farmer.query.first()
        if not sample_farmer:
            print("❌ No farmer found. Please create a farmer first.")
            return
        
        farmer_id = sample_farmer.id
        
        # Sample crop data with varying prices
        crops_data = [
            # Soybean listings
            {'name': 'Soybean', 'prices': [4500, 4650, 4700, 4550, 4800, 4600], 'quantity': 10},
            # Mustard listings
            {'name': 'Mustard', 'prices': [5200, 5300, 5100, 5400, 5250, 5150], 'quantity': 15},
            # Groundnut listings
            {'name': 'Groundnut', 'prices': [6000, 6100, 5950, 6200, 6050, 5900], 'quantity': 20},
            # Sunflower listings
            {'name': 'Sunflower', 'prices': [5800, 5900, 5750, 6000, 5850, 5700], 'quantity': 12},
            # Safflower listings
            {'name': 'Safflower', 'prices': [6500, 6600, 6400, 6700, 6550, 6450], 'quantity': 8},
            # Sesame listings
            {'name': 'Sesame', 'prices': [7200, 7300, 7100, 7400, 7250, 7150], 'quantity': 5},
        ]
        
        existing_count = SellRequest.query.filter(
            db.func.lower(SellRequest.crop_name).in_([c['name'].lower() for c in crops_data])
        ).count()
        
        if existing_count > 0:
            print(f"✓ Crop data already exists ({existing_count} listings). Skipping seed...")
            return
        
        # Create sell requests
        for crop_data in crops_data:
            for idx, price in enumerate(crop_data['prices']):
                sell_request = SellRequest(
                    farmer_id=farmer_id,
                    crop_name=crop_data['name'],
                    quantity_quintal=crop_data['quantity'] + idx,
                    expected_price=price,
                    farmer_name=sample_farmer.name,
                    farmer_phone=sample_farmer.phone_number,
                    status='pending'
                )
                db.session.add(sell_request)
        
        db.session.commit()
        
        total_listings = SellRequest.query.filter(
            db.func.lower(SellRequest.crop_name).in_([c['name'].lower() for c in crops_data])
        ).count()
        
        print(f"✅ Successfully seeded {total_listings} crop listings for crop economics dashboard")
        print(f"   - Soybean: 6 listings")
        print(f"   - Mustard: 6 listings")
        print(f"   - Groundnut: 6 listings")
        print(f"   - Sunflower: 6 listings")
        print(f"   - Safflower: 6 listings")
        print(f"   - Sesame: 6 listings")

if __name__ == '__main__':
    seed_crop_data()
