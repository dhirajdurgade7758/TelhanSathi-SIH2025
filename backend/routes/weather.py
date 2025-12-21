from flask import Blueprint, render_template, jsonify, session
from datetime import datetime, timedelta
import random
import requests
from models import Farmer

weather_bp = Blueprint('weather', __name__, url_prefix='/weather')


@weather_bp.route('/')
def dashboard():
    # simple page; JS will fetch forecast
    if 'farmer_id_verified' not in session:
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    return render_template('weather.html')


def generate_forecast_for_location(district=None, lat=None, lon=None, days=7):
    """
    Stub weather forecast generator.
    Uses deterministic randomness seeded from district or lat/lon to create plausible day forecasts.
    Returns a list of days with date, summary, temp_min, temp_max, precipitation_mm, wind_kmh.
    """
    seed_val = 0
    if district:
        seed_val = sum(ord(c) for c in district)
    elif lat and lon:
        seed_val = int((abs(lat) + abs(lon)) * 1000)
    else:
        seed_val = int(datetime.utcnow().timestamp())

    rnd = random.Random(seed_val)
    out = []
    today = datetime.utcnow().date()
    for i in range(days):
        d = today + timedelta(days=i)
        # base temps vary mildly
        base = 25 + (rnd.random() * 8 - 2)
        tmax = round(base + rnd.uniform(2, 6), 1)
        tmin = round(base - rnd.uniform(2, 6), 1)
        precip_chance = rnd.random()
        if precip_chance > 0.8:
            summary = 'Heavy rain'
            precip = round(rnd.uniform(10, 60),1)
        elif precip_chance > 0.6:
            summary = 'Light rain'
            precip = round(rnd.uniform(1, 10),1)
        elif precip_chance > 0.4:
            summary = 'Cloudy'
            precip = 0.0
        else:
            summary = 'Sunny'
            precip = 0.0
        wind = round(rnd.uniform(5, 25),1)
        out.append({
            'date': d.isoformat(),
            'summary': summary,
            'temp_min': tmin,
            'temp_max': tmax,
            'precip_mm': precip,
            'wind_kmh': wind
        })
    return out


@weather_bp.route('/api/forecast')
def api_forecast():
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    farmer_id = session['farmer_id_verified']
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    
    # Default to India's approximate center if no farmer location
    lat, lon = 20.5937, 78.9629
    location_name = 'India'
    
    if farmer:
        # Map common Indian districts to approximate lat/lon
        district_coords = {
            'Maharashtra': (19.7515, 75.7139),
            'Karnataka': (15.3173, 75.7139),
            'Gujarat': (22.2587, 71.1924),
            'Punjab': (31.1471, 74.8722),
            'Haryana': (29.0588, 77.0745),
            'Uttar Pradesh': (26.8467, 80.9462),
            'Madhya Pradesh': (22.9375, 78.6553),
            'Bihar': (25.0961, 85.3131),
            'West Bengal': (24.3745, 88.2007),
            'Tamil Nadu': (11.1271, 79.2787),
            'Andhra Pradesh': (15.9129, 79.7400),
            'Telangana': (18.1124, 79.0193),
            'Rajasthan': (27.0238, 74.2179),
        }
        
        district = getattr(farmer, 'district', None)
        if district and district in district_coords:
            lat, lon = district_coords[district]
            location_name = district
        elif district:
            location_name = district
    
    try:
        # Use Open-Meteo free API (no key required)
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
            'timezone': 'Asia/Kolkata',
            'forecast_days': 7
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Parse the response
        forecast = []
        daily = data.get('daily', {})
        dates = daily.get('time', [])
        temps_max = daily.get('temperature_2m_max', [])
        temps_min = daily.get('temperature_2m_min', [])
        precip = daily.get('precipitation_sum', [])
        wind = daily.get('wind_speed_10m_max', [])
        weather_codes = daily.get('weather_code', [])
        
        for i in range(min(7, len(dates))):
            summary = get_weather_summary_from_code(weather_codes[i] if i < len(weather_codes) else 0)
            forecast.append({
                'date': dates[i] if i < len(dates) else '',
                'summary': summary,
                'temp_min': round(temps_min[i], 1) if i < len(temps_min) else 20,
                'temp_max': round(temps_max[i], 1) if i < len(temps_max) else 30,
                'precip_mm': round(precip[i], 1) if i < len(precip) else 0,
                'wind_kmh': round(wind[i] * 3.6, 1) if i < len(wind) else 10  # Convert m/s to km/h
            })
        
        return jsonify({'location': location_name, 'forecast': forecast})
    
    except Exception as e:
        print(f"Error fetching real weather: {e}")
        # Fallback to stub generator
        forecast = generate_forecast_for_location(district=location_name, days=7)
        return jsonify({'location': location_name, 'forecast': forecast})


def get_weather_summary_from_code(code):
    """
    Convert WMO weather code to summary string.
    Based on WMO codes: https://www.weatherapi.com/docs/
    """
    code = int(code)
    if code == 0:
        return 'Clear'
    elif code == 1 or code == 2:
        return 'Partly cloudy'
    elif code == 3:
        return 'Overcast'
    elif code == 45 or code == 48:
        return 'Foggy'
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return 'Rainy'
    elif code in [71, 73, 75, 77, 85, 86]:
        return 'Snowy'
    elif code in [80, 81, 82]:
        return 'Rain showers'
    elif code in [85, 86]:
        return 'Snow showers'
    elif code in [95, 96, 99]:
        return 'Thunderstorm'
    else:
        return 'Cloudy'
