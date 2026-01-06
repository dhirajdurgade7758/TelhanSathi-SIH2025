#!/usr/bin/env python3
"""
Database Seeding Script
Populates the database with Schemes and Redemption Offers from JSON files
"""

import json
import sys
from datetime import datetime
from app import app, db
from models import Scheme, RedemptionOffer

def seed_schemes():
    """Load and seed schemes from backup_schemes.json"""
    print("\n" + "="*60)
    print("🌾 SEEDING SCHEMES & SUBSIDIES")
    print("="*60)
    
    try:
        with open('backup_schemes.json', 'r', encoding='utf-8') as f:
            schemes_data = json.load(f)
        
        print(f"\n📂 Found {len(schemes_data)} schemes in JSON file")
        
        seeded_count = 0
        updated_count = 0
        
        for scheme_data in schemes_data:
            # Check if scheme already exists
            existing_scheme = Scheme.query.filter_by(
                scheme_code=scheme_data.get('scheme_code')
            ).first()
            
            if existing_scheme:
                # Update existing scheme
                existing_scheme.name = scheme_data.get('name')
                existing_scheme.description = scheme_data.get('description')
                existing_scheme.scheme_type = scheme_data.get('scheme_type')
                existing_scheme.focus_area = scheme_data.get('focus_area')
                existing_scheme.benefit_amount = scheme_data.get('benefit_amount')
                existing_scheme.eligibility_criteria = scheme_data.get('eligibility_criteria')
                existing_scheme.is_recommended = scheme_data.get('is_recommended', False)
                existing_scheme.is_active = scheme_data.get('is_active', True)
                existing_scheme.updated_at = datetime.utcnow()
                
                updated_count += 1
                print(f"  ✏️  Updated: {scheme_data.get('name')} (Code: {scheme_data.get('scheme_code')})")
            else:
                # Create new scheme
                new_scheme = Scheme(
                    scheme_code=scheme_data.get('scheme_code'),
                    name=scheme_data.get('name'),
                    description=scheme_data.get('description'),
                    scheme_type=scheme_data.get('scheme_type'),
                    focus_area=scheme_data.get('focus_area'),
                    benefit_amount=scheme_data.get('benefit_amount'),
                    eligibility_criteria=scheme_data.get('eligibility_criteria'),
                    is_recommended=scheme_data.get('is_recommended', False),
                    is_active=scheme_data.get('is_active', True)
                )
                db.session.add(new_scheme)
                seeded_count += 1
                print(f"  ✅ Seeded: {scheme_data.get('name')} (Code: {scheme_data.get('scheme_code')})")
        
        db.session.commit()
        print(f"\n✨ Schemes Seeding Complete!")
        print(f"   ✅ New schemes added: {seeded_count}")
        print(f"   ✏️  Schemes updated: {updated_count}")
        print(f"   📊 Total schemes in DB: {Scheme.query.count()}")
        
    except FileNotFoundError:
        print("❌ Error: backup_schemes.json not found!")
        return False
    except Exception as e:
        print(f"❌ Error seeding schemes: {str(e)}")
        db.session.rollback()
        return False
    
    return True


def seed_redemption_offers():
    """Load and seed redemption offers from backup_redemption_offers_hindi.json"""
    print("\n" + "="*60)
    print("🎁 SEEDING REDEMPTION OFFERS")
    print("="*60)
    
    try:
        with open('backup_redemption_offers_hindi.json', 'r', encoding='utf-8') as f:
            offers_data = json.load(f)
        
        print(f"\n📂 Found {len(offers_data)} offers in JSON file")
        
        seeded_count = 0
        updated_count = 0
        
        for offer_data in offers_data:
            # Check if offer already exists by title (as it's unique)
            existing_offer = RedemptionOffer.query.filter_by(
                title=offer_data.get('title')
            ).first()
            
            if existing_offer:
                # Update existing offer
                existing_offer.description = offer_data.get('description')
                existing_offer.category = offer_data.get('category')
                existing_offer.coin_cost = offer_data.get('coin_cost')
                existing_offer.icon = offer_data.get('icon')
                existing_offer.color = offer_data.get('color')
                existing_offer.offer_type = offer_data.get('offer_type')
                existing_offer.actual_value = offer_data.get('actual_value')
                existing_offer.validity_days = offer_data.get('validity_days', 90)
                existing_offer.is_active = offer_data.get('is_active', True)
                existing_offer.updated_at = datetime.utcnow()
                
                updated_count += 1
                print(f"  ✏️  Updated: {offer_data.get('title')} ({offer_data.get('coin_cost')} coins)")
            else:
                # Create new offer
                new_offer = RedemptionOffer(
                    title=offer_data.get('title'),
                    description=offer_data.get('description'),
                    category=offer_data.get('category'),
                    coin_cost=offer_data.get('coin_cost'),
                    icon=offer_data.get('icon'),
                    color=offer_data.get('color'),
                    offer_type=offer_data.get('offer_type'),
                    actual_value=offer_data.get('actual_value'),
                    validity_days=offer_data.get('validity_days', 90),
                    is_active=offer_data.get('is_active', True)
                )
                db.session.add(new_offer)
                seeded_count += 1
                print(f"  ✅ Seeded: {offer_data.get('title')} ({offer_data.get('coin_cost')} coins)")
        
        db.session.commit()
        print(f"\n✨ Redemption Offers Seeding Complete!")
        print(f"   ✅ New offers added: {seeded_count}")
        print(f"   ✏️  Offers updated: {updated_count}")
        print(f"   📊 Total offers in DB: {RedemptionOffer.query.count()}")
        
    except FileNotFoundError:
        print("❌ Error: backup_redemption_offers_hindi.json not found!")
        return False
    except Exception as e:
        print(f"❌ Error seeding redemption offers: {str(e)}")
        db.session.rollback()
        return False
    
    return True


def main():
    """Main seeding function"""
    print("\n" + "🌾"*30)
    print("TELHAN SATHI - DATABASE SEEDING SCRIPT")
    print("🌾"*30)
    
    with app.app_context():
        try:
            # Seed schemes
            schemes_success = seed_schemes()
            
            # Seed redemption offers
            offers_success = seed_redemption_offers()
            
            # Summary
            print("\n" + "="*60)
            print("📊 SEEDING SUMMARY")
            print("="*60)
            
            total_schemes = Scheme.query.count()
            total_offers = RedemptionOffer.query.count()
            recommended_schemes = Scheme.query.filter_by(is_recommended=True).count()
            active_offers = RedemptionOffer.query.filter_by(is_active=True).count()
            
            print(f"\n📋 Schemes & Subsidies:")
            print(f"   📊 Total schemes: {total_schemes}")
            print(f"   ⭐ Recommended schemes: {recommended_schemes}")
            
            print(f"\n🎁 Redemption Offers:")
            print(f"   📊 Total offers: {total_offers}")
            print(f"   ✅ Active offers: {active_offers}")
            
            if schemes_success and offers_success:
                print("\n" + "="*60)
                print("✅ ALL DATA SEEDING COMPLETED SUCCESSFULLY!")
                print("="*60 + "\n")
                return 0
            else:
                print("\n" + "="*60)
                print("⚠️  SOME SEEDING OPERATIONS FAILED!")
                print("="*60 + "\n")
                return 1
        
        except Exception as e:
            print(f"\n❌ Critical Error: {str(e)}")
            print("="*60 + "\n")
            return 1


if __name__ == '__main__':
    sys.exit(main())
