#!/usr/bin/env python
from app import app

with app.app_context():
    print("✅ Crop Economics Dashboard Routes:")
    for rule in app.url_map.iter_rules():
        if 'crop-economics' in rule.rule or 'crop_economics' in rule.endpoint:
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"  {methods:8} {rule.rule:50} -> {rule.endpoint}")
