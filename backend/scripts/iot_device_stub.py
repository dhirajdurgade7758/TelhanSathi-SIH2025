"""
Simple IoT device stub to POST fake sensor readings to the app's `/field-monitoring/api/push` endpoint.
Usage (PowerShell):
& ".venv\Scripts\python.exe" "scripts\iot_device_stub.py" --serial DEMO-DEVICE-01 --count 5 --interval 1

The script uses the `requests` package.
"""
import os
import sys
import time
import json
import random
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import requests
from datetime import datetime

DEFAULT_URL = 'http://localhost:5000/field-monitoring/api/push'

parser = argparse.ArgumentParser()
parser.add_argument('--serial', default='DEMO-DEVICE-01')
parser.add_argument('--url', default=DEFAULT_URL)
parser.add_argument('--count', type=int, default=10)
parser.add_argument('--interval', type=float, default=2.0)
args = parser.parse_args()

print(f'Starting IoT stub: serial={args.serial}, url={args.url}, count={args.count}, interval={args.interval}s')

for i in range(args.count):
    temp = round(24 + random.random() * 6, 1)
    hum = round(50 + random.random() * 30, 1)
    soil = round(30 + random.random() * 40, 1)
    light = round(100 + random.random() * 900, 1)
    probe_temp = round(temp + random.uniform(-0.5, 0.5), 1)

    payload = {
        'device_serial': args.serial,
        'temperature': temp,
        'humidity': hum,
        'soil_moisture': soil,
        'light': light,
        'probe_temp': probe_temp,
        'timestamp': datetime.utcnow().isoformat()
    }

    try:
        r = requests.post(args.url, json=payload, timeout=5)
        print(f'[{i+1}/{args.count}] Sent: {payload} -> status {r.status_code} {r.text}')
    except Exception as e:
        print('Error sending payload:', e)

    time.sleep(args.interval)

print('IoT stub finished.')
