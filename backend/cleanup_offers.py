#!/usr/bin/env python3
"""
Clean up old English redemption offers and keep only Hindi offers
"""

import sys
from app import app, db
from models import RedemptionOffer

def cleanup_english_offers():
    """Remove old English offers, keep only Hindi offers."""
    print("\n" + "="*60)
    print("🧹 CLEANING UP OLD ENGLISH OFFERS")
    print("="*60)
    
    with app.app_context():
        # Find English offers (those without Hindi characters)
        all_offers = RedemptionOffer.query.all()
        
        english_offers = []
        hindi_offers = []
        
        for offer in all_offers:
            # Check if title contains Hindi characters
            has_hindi = any('\u0900' <= c <= '\u097F' for c in offer.title)
            
            if has_hindi:
                hindi_offers.append(offer)
            else:
                english_offers.append(offer)
        
        print(f"\n📊 Analysis:")
        print(f"   📦 Total offers: {len(all_offers)}")
        print(f"   🇬🇧 English offers: {len(english_offers)}")
        print(f"   🇮🇳 Hindi offers: {len(hindi_offers)}")
        
        if english_offers:
            print(f"\n🗑️  Deleting {len(english_offers)} old English offers...")
            for offer in english_offers:
                print(f"   ❌ Removing: {offer.title}")
                db.session.delete(offer)
            
            db.session.commit()
            print(f"\n✅ Cleanup complete!")
            
            # Verify
            remaining = RedemptionOffer.query.count()
            print(f"\n📊 Final count: {remaining} offers (all Hindi)")
            
            # Show sample Hindi offers
            print(f"\n📋 Sample Hindi offers in DB:")
            samples = RedemptionOffer.query.limit(5).all()
            for i, offer in enumerate(samples, 1):
                print(f"   {i}. {offer.title} - {offer.coin_cost} coins")
        else:
            print(f"\n✅ No English offers found. Database already clean!")
            print(f"📊 Database has {len(hindi_offers)} Hindi offers")

if __name__ == '__main__':
    cleanup_english_offers()
