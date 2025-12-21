"""
Script to clear old schemes and seed new genuine government schemes
"""
from extensions import db
from models import Scheme, SubsidyApplication
from app import app

def update_schemes():
    """Clear old schemes and seed new ones"""
    
    with app.app_context():
        # Delete all existing schemes and their applications
        print("🗑️  Clearing old schemes...")
        SubsidyApplication.query.delete()
        Scheme.query.delete()
        db.session.commit()
        print("✓ Old schemes cleared")
        
        # Now seed new schemes
        print("\n📚 Seeding new genuine government schemes...")
        from seed_schemes import seed_schemes
        seed_schemes()

if __name__ == '__main__':
    update_schemes()
    print("\n✅ All schemes updated successfully!")
