#!/usr/bin/env python3
"""
Seed Hindi Notifications for a specific farmer
"""

import sys
from datetime import datetime, timedelta
from app import app, db
from models import Farmer, Notification

def seed_notifications_for_farmer(phone_number):
    """Seed sample Hindi notifications for a farmer."""
    print("\n" + "="*60)
    print("📬 SEEDING HINDI NOTIFICATIONS")
    print("="*60)
    
    with app.app_context():
        # Find farmer by phone number
        farmer = Farmer.query.filter_by(phone_number=phone_number).first()
        
        if not farmer:
            print(f"\n❌ Error: Farmer with phone {phone_number} not found!")
            return False
        
        print(f"\n✅ Found Farmer: {farmer.name}")
        print(f"   ID: {farmer.id}")
        print(f"   Phone: {farmer.phone_number}")
        
        # Create sample Hindi notifications
        notifications = [
            {
                'title': '🌾 नई योजना: प्रधानमंत्री कृषि सिंचाई योजना',
                'description': 'आपके जिले में नई सिंचाई योजना शुरू हुई है। 40-50% अनुदान प्राप्त करें। अधिक जानकारी के लिए क्लिक करें।',
                'notification_type': 'scheme_update',
                'related_type': 'scheme',
                'related_id': 'pmksy',
                'is_important': True,
            },
            {
                'title': '💰 विशेष सौदा: हाइब्रिड बीज पर 20% छूट',
                'description': 'यह सप्ताह हाइब्रिड सरसों के बीजों पर विशेष छूट उपलब्ध है। सीमित समय के लिए।',
                'notification_type': 'deal_alert',
                'related_type': 'deal',
                'related_id': None,
                'is_important': False,
            },
            {
                'title': '📊 मंडी मूल्य अपडेट: सरसों ₹5,200/क्विंटल',
                'description': 'आपके क्षेत्र में सरसों की कीमत ₹5,200 प्रति क्विंटल है। अच्छी कीमत मिल रही है।',
                'notification_type': 'price_alert',
                'related_type': 'price',
                'related_id': None,
                'is_important': False,
            },
            {
                'title': '⚙️ सिस्टम अपडेट: नई सुविधाएं जोड़ी गईं',
                'description': 'तेलहन साथी ऐप में अब फसल डॉक्टर रिपोर्ट और उन्नत मौसम पूर्वानुमान उपलब्ध है।',
                'notification_type': 'system_update',
                'related_type': None,
                'related_id': None,
                'is_important': False,
            },
            {
                'title': '🎯 आपकी योजना आवेदन स्वीकृत',
                'description': 'प्रधानमंत्री किसान सम्मान निधि योजना के लिए आपका आवेदन स्वीकृत हो गया है।',
                'notification_type': 'scheme_update',
                'related_type': 'scheme',
                'related_id': 'pmkisan',
                'is_important': True,
            },
            {
                'title': '🌱 फसल स्वास्थ्य सलाह: बीज दर समायोजन',
                'description': 'सरसों की फसल के लिए बीज दर 4-5 किग्रा/हेक्टेयर होनी चाहिए। अच्छी उपज के लिए सही दर बनाए रखें।',
                'notification_type': 'general_alert',
                'related_type': 'crop',
                'related_id': None,
                'is_important': False,
            },
            {
                'title': '💧 सिंचाई सलाह: बेहतर पानी प्रबंधन',
                'description': 'मौजूदा मौसम में सरसों को 2-3 सिंचाई की आवश्यकता है। ड्रिप सिंचाई 30% पानी बचाती है।',
                'notification_type': 'general_alert',
                'related_type': None,
                'related_id': None,
                'is_important': False,
            },
            {
                'title': '🏆 आपके पुरस्कार तैयार हैं',
                'description': 'आपने 5,000 सिक्के अर्जित किए हैं! मोचन स्टोर में विशेष ऑफर के लिए उपयोग करें।',
                'notification_type': 'general_alert',
                'related_type': None,
                'related_id': None,
                'is_important': True,
            },
            {
                'title': '📡 आईओटी सेंसर किट पर 10% छूट',
                'description': 'स्मार्ट खेती के लिए आईओटी सेंसर किट पर विशेष मूल्य। आज ही ऑर्डर करें।',
                'notification_type': 'deal_alert',
                'related_type': 'deal',
                'related_id': None,
                'is_important': False,
            },
            {
                'title': '🌤️ मौसम सतर्कता: तेज हवाएं',
                'description': 'आने वाले 2 दिन में तेज हवाएं चलने की संभावना है। बुवाई कार्य स्थगित करें।',
                'notification_type': 'general_alert',
                'related_type': None,
                'related_id': None,
                'is_important': True,
            },
        ]
        
        # Create notifications with different timestamps
        now = datetime.utcnow()
        created_count = 0
        
        for i, notif_data in enumerate(notifications):
            # Create notifications spread over the past week
            created_at = now - timedelta(hours=i*8)
            
            notification = Notification(
                farmer_id=farmer.id,
                title=notif_data['title'],
                description=notif_data['description'],
                notification_type=notif_data['notification_type'],
                related_type=notif_data.get('related_type'),
                related_id=notif_data.get('related_id'),
                is_important=notif_data.get('is_important', False),
                is_read=False,
                created_at=created_at
            )
            db.session.add(notification)
            created_count += 1
        
        try:
            db.session.commit()
            print(f"\n✨ Notifications Seeding Complete!")
            print(f"   ✅ Created {created_count} Hindi notifications")
            
            # Display sample notifications
            print(f"\n📋 Sample Notifications:")
            sample_notifs = Notification.query.filter_by(farmer_id=farmer.id).order_by(
                Notification.created_at.desc()
            ).limit(3).all()
            
            for i, notif in enumerate(sample_notifs, 1):
                print(f"\n   {i}. {notif.title}")
                print(f"      Type: {notif.notification_type}")
                print(f"      Created: {notif.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            total = Notification.query.filter_by(farmer_id=farmer.id).count()
            print(f"\n   📊 Total notifications for farmer: {total}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error seeding notifications: {str(e)}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    phone_number = '8805937758'
    
    if len(sys.argv) > 1:
        phone_number = sys.argv[1]
    
    success = seed_notifications_for_farmer(phone_number)
    sys.exit(0 if success else 1)
