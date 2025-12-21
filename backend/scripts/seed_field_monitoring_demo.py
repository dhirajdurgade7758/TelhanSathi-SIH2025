"""
Seed demo data for field monitoring: create an IoTDevice for farmer `567894251673`
and insert sample SensorReading rows.
Run from backend folder with virtualenv python.
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Ensure project root on path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from extensions import db
from models import Farmer, IoTDevice, SensorReading

FARMER_KP_ID = '567894251673'
DEVICE_SERIAL = 'DEMO-DEVICE-01'

with app.app_context():
    farmer = Farmer.query.filter_by(farmer_id=FARMER_KP_ID).first()
    if not farmer:
        print(f'Farmer with farmer_id={FARMER_KP_ID} not found. Creating a demo farmer record...')
        farmer = Farmer(
            farmer_id=FARMER_KP_ID,
            name='Demo Farmer',
            phone_number='9000000000',
            district='Demo District',
            is_verified=True,
            onboarding_completed=True
        )
        db.session.add(farmer)
        db.session.commit()
        print('Created demo farmer:', farmer)

    # Check existing device
    device = IoTDevice.query.filter_by(device_serial=DEVICE_SERIAL).first()
    if device:
        print('Demo device already exists:', device)
    else:
        device = IoTDevice(
            farmer_id=farmer.id,
            device_serial=DEVICE_SERIAL,
            installed=True,
            installed_at=datetime.utcnow() - timedelta(days=1),
            location_description='Demo field near village'
        )
        db.session.add(device)
        db.session.commit()
        print('Created demo IoTDevice:', device)

    # Create sample readings (12 readings, 15-minute interval)
    now = datetime.utcnow()
    readings = []
    for i in range(12):
        ts = now - timedelta(minutes=15 * (11 - i))  # oldest first
        temp = round(24 + random.random() * 6, 1)  # 24-30 C
        hum = round(50 + random.random() * 30, 1)  # 50-80 %
        soil = round(30 + random.random() * 40, 1)  # 30-70
        light = round(100 + random.random() * 900, 1)  # 100-1000 lux
        probe_temp = round(temp + random.uniform(-0.5, 0.5), 1)
        r = SensorReading(
            device_id=device.id,
            temperature=temp,
            humidity=hum,
            soil_moisture=soil,
            light=light,
            probe_temp=probe_temp,
            received_at=ts
        )
        db.session.add(r)
        readings.append(r)

    db.session.commit()
    print(f'Inserted {len(readings)} sensor readings for device {DEVICE_SERIAL} (farmer {FARMER_KP_ID}).')
    print('Done.')
