#!/usr/bin/env python
"""
Script to add coins to a farmer for testing
"""
from app import app, db
from models import Farmer, CoinBalance
from datetime import datetime

def add_coins_to_farmer(farmer_id, coins_amount):
    """Add coins to a farmer's balance"""
    with app.app_context():
        # Find farmer by farmer_id (the 12-digit number)
        farmer = Farmer.query.filter_by(farmer_id=farmer_id).first()
        
        if not farmer:
            print(f"❌ Farmer with ID {farmer_id} not found")
            return
        
        print(f"✓ Found farmer: {farmer.name} (ID: {farmer.farmer_id})")
        
        # Get or create coin balance
        coin_balance = farmer.coin_balance
        if not coin_balance:
            coin_balance = CoinBalance(farmer_id=farmer.id)
            db.session.add(coin_balance)
            print(f"✓ Created new CoinBalance record")
        
        # Add coins
        old_available = coin_balance.available_coins
        coin_balance.total_coins += coins_amount
        coin_balance.available_coins += coins_amount
        coin_balance.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        print(f"✅ Successfully added {coins_amount} coins")
        print(f"   Old balance: {old_available}")
        print(f"   New balance: {coin_balance.available_coins}")
        print(f"   Total coins: {coin_balance.total_coins}")

if __name__ == '__main__':
    import sys
    
    # Get farmer_id and coin amount from command line
    if len(sys.argv) != 3:
        print("Usage: python add_coins.py <farmer_id> <amount>")
        print("Example: python add_coins.py 567894251673 100")
        sys.exit(1)
    
    farmer_id = int(sys.argv[1])
    coins_amount = int(sys.argv[2])
    
    print(f"Adding {coins_amount} coins to farmer {farmer_id}...\n")
    add_coins_to_farmer(farmer_id, coins_amount)
