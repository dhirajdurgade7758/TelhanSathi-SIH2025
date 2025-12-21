#!/usr/bin/env python
"""Test that credentials are needed for session handling"""

from app import app

def test_fetch_credentials():
    """Test fetch credentials behavior"""
    
    client = app.test_client()
    
    # Step 1: Simulate farmer accessing the create auction page
    print("=" * 60)
    print("Step 1: Farmer accesses /bidding/create-auction (GET)")
    print("=" * 60)
    
    response = client.get('/bidding/create-auction')
    
    if response.status_code == 302:
        print(f"❌ Redirected (401): Farmer not authenticated")
        print(f"   Redirect location: {response.location}")
    elif response.status_code == 200:
        print(f"❌ Page loaded without authentication?")
    else:
        print(f"Unexpected status: {response.status_code}")
    
    # Step 2: Authenticate and then try to create auction
    print("\n" + "=" * 60)
    print("Step 2: Authenticate farmer and create auction")
    print("=" * 60)
    
    with app.app_context():
        from models import Farmer
        farmer = Farmer.query.first()
        farmer_id = farmer.id
    
    with client.session_transaction() as sess:
        sess['farmer_id_verified'] = farmer_id
        print(f"Session set: farmer_id_verified = {farmer_id}")
    
    # Now try with proper headers for fetch (credentials: 'include')
    form_data = {
        'crop_name': 'Mustard',
        'quantity': '60',
        'min_bid_price': '6000',
        'duration_hours': '24',
        'location': 'Rajasthan',
        'description': 'Test auction from test script'
    }
    
    response = client.post(
        '/bidding/farmer/create-auction',
        data=form_data
    )
    
    print(f"Status: {response.status_code}")
    json_data = response.get_json()
    
    if json_data.get('success'):
        print(f"✅ Auction created successfully!")
        print(f"   Auction ID: {json_data.get('auction_id')}")
    else:
        print(f"❌ Failed: {json_data.get('error')}")

if __name__ == '__main__':
    test_fetch_credentials()
