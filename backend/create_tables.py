#!/usr/bin/env python
"""Create auction tables in database"""

from app import app
from extensions import db
from models_marketplace_keep import Auction, Bid, CounterOffer, AuctionNotification

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("✅ All tables created successfully!")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
