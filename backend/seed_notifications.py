"""
Seed script to populate sample notifications
"""
from app import app, db
from models import Notification, Farmer
from datetime import datetime, timedelta
import uuid

def seed_notifications():
    """Add sample notifications for the first farmer"""
    with app.app_context():
        # Get first farmer (if exists)
        farmer = Farmer.query.filter_by(farmer_id=567894251673).first()
        if not farmer:
            print("❌ No farmers found in database. Please onboard a farmer first.")
            return
        
        # Check if notifications already exist
        existing_count = Notification.query.filter_by(farmer_id=farmer.id).count()
        if existing_count > 0:
            print(f"✓ Notifications already exist ({existing_count} records). Skipping seed...")
            return
        
        # Create sample notifications
        notifications_data = [
            {
                'title': 'New Government Scheme Available',
                'description': 'PM-KISAN scheme is now available in your district. You can apply for ₹6000 annual support.',
                'type': 'scheme_update',
                'icon': 'check_circle',
                'color': 'success',
                'related_type': 'scheme',
                'action_link': '/subsidies/list',
                'is_important': True,
            },
            {
                'title': 'Price Alert: Wheat prices rising',
                'description': 'Wheat prices have increased by 8% in your region. Best time to sell now!',
                'type': 'price_alert',
                'icon': 'trending_up',
                'color': 'warning',
                'related_type': 'price',
                'action_link': '/market/deals-list',
                'is_important': False,
            },
            {
                'title': 'New Buyer Interested in Your Crops',
                'description': 'A buyer from your area is interested in purchasing cotton. View the deal to negotiate.',
                'type': 'deal_alert',
                'icon': 'handshake',
                'color': 'info',
                'related_type': 'deal',
                'action_link': '/market/deals-list',
                'is_important': True,
            },
            {
                'title': 'PMFBY Crop Insurance Application Deadline',
                'description': 'Last date to apply for crop insurance under PMFBY is 31st December. Don\'t miss out!',
                'type': 'scheme_update',
                'icon': 'shield',
                'color': 'warning',
                'related_type': 'scheme',
                'is_important': True,
            },
            {
                'title': 'Soil Health Card Report Ready',
                'description': 'Your soil health card report is ready. View recommendations to improve soil fertility.',
                'type': 'general_alert',
                'icon': 'leaf',
                'color': 'success',
                'related_type': 'general',
            },
            {
                'title': 'Weather Alert: Heavy Rain Expected',
                'description': 'Weather forecast indicates 80mm rain in next 48 hours. Plan your farm activities accordingly.',
                'type': 'general_alert',
                'icon': 'cloud_rain',
                'color': 'warning',
                'related_type': 'general',
            },
            {
                'title': 'System Maintenance Notice',
                'description': 'The app will be under maintenance on Dec 5th from 2-4 AM. Plan your work accordingly.',
                'type': 'system_update',
                'icon': 'build',
                'color': 'info',
                'related_type': 'general',
            },
            {
                'title': 'Agri Infrastructure Fund Extended',
                'description': 'Good news! The Agri Infrastructure Fund scheme has been extended. New applications welcome.',
                'type': 'scheme_update',
                'icon': 'construction',
                'color': 'success',
                'related_type': 'scheme',
                'is_important': True,
            },
            {
                'title': 'Market Price Comparison Available',
                'description': 'Compare prices across 5 mandis in your region. Get best rates for your produce.',
                'type': 'price_alert',
                'icon': 'compare_arrows',
                'color': 'info',
                'related_type': 'price',
                'action_link': '/market/deals-list',
            },
            {
                'title': 'Achievement: 500 Points Unlocked!',
                'description': 'Congratulations! You earned 500 loyalty points. Redeem them for exclusive offers.',
                'type': 'general_alert',
                'icon': 'star',
                'color': 'success',
                'related_type': 'general',
            },
        ]
        
        # Create notifications with varied timestamps
        now = datetime.utcnow()
        for i, notif_data in enumerate(notifications_data):
            # Spread notifications over the last 7 days
            days_ago = i // 2
            created_at = now - timedelta(days=days_ago, hours=i%6)
            
            notification = Notification(
                id=str(uuid.uuid4()),
                farmer_id=farmer.id,
                title=notif_data['title'],
                description=notif_data['description'],
                notification_type=notif_data['type'],
                icon=notif_data.get('icon'),
                color=notif_data.get('color'),
                related_type=notif_data.get('related_type'),
                action_link=notif_data.get('action_link'),
                is_important=notif_data.get('is_important', False),
                is_read=i > 5,  # Mark older ones as read
                created_at=created_at,
                updated_at=created_at,
            )
            db.session.add(notification)
        
        db.session.commit()
        print(f"✅ Successfully seeded {len(notifications_data)} notifications for farmer {farmer.name}")

if __name__ == '__main__':
    seed_notifications()
