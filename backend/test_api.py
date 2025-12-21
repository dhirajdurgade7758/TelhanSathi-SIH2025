from app import app
from models import Farmer
import json

with app.test_client() as client:
    # First check what happens without session
    response = client.get('/notifications/api/list')
    print(f'Without session - Status: {response.status_code}')
    print(f'Response: {response.get_json()}')
    print()
    
    # Now simulate a logged-in user
    with app.app_context():
        farmer = Farmer.query.first()
        with client.session_transaction() as sess:
            sess['farmer_id_verified'] = farmer.id
    
    response = client.get('/notifications/api/list')
    print(f'With session - Status: {response.status_code}')
    data = response.get_json()
    print(f'Response keys: {list(data.keys())}')
    if 'notifications' in data:
        print(f'Number of notifications: {len(data["notifications"])}')
        if len(data['notifications']) > 0:
            print(f'First notification title: {data["notifications"][0]["title"]}')
