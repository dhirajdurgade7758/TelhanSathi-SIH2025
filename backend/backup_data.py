#!/usr/bin/env python3
"""Backup critical data before database reset"""

from app import app
from extensions import db
from models import Scheme, RedemptionOffer, FarmerRedemption
import json
from datetime import datetime

with app.app_context():
    try:
        # Backup Schemes
        schemes = Scheme.query.all()
        schemes_data = []
        for s in schemes:
            schemes_data.append({
                'scheme_code': s.scheme_code,
                'name': s.name,
                'description': s.description,
                'scheme_type': s.scheme_type,
                'focus_area': s.focus_area,
                'benefit_amount': s.benefit_amount,
                'eligibility_criteria': s.eligibility_criteria,
                'is_recommended': s.is_recommended,
                'is_active': s.is_active
            })
        
        with open('backup_schemes.json', 'w', encoding='utf-8') as f:
            json.dump(schemes_data, f, indent=2, ensure_ascii=False)
        print(f'✅ Schemes backed up: {len(schemes_data)} records')
        
        # Backup Redemption Offers
        redemption_items = RedemptionOffer.query.all()
        redemption_data = []
        for r in redemption_items:
            redemption_data.append({
                'title': r.title,
                'description': r.description,
                'category': r.category,
                'coin_cost': r.coin_cost,
                'icon': r.icon,
                'color': r.color,
                'offer_type': r.offer_type,
                'actual_value': r.actual_value,
                'validity_days': r.validity_days,
                'is_active': r.is_active,
                'stock_limit': r.stock_limit
            })
        
        with open('backup_redemption_offers.json', 'w', encoding='utf-8') as f:
            json.dump(redemption_data, f, indent=2, ensure_ascii=False)
        print(f'✅ Redemption offers backed up: {len(redemption_data)} records')
        
        print('✅ All backups created successfully!')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
