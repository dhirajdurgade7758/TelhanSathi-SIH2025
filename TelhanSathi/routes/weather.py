from flask import Blueprint, render_template, jsonify, session, request
from datetime import datetime, timedelta
import random
import requests
import os
import json
from models import Farmer, WeatherRecommendation
from extensions import db

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

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


# ======================== WEATHER AI RECOMMENDATION FUNCTIONS ========================

def _get_farmer_context(farmer):
    """Extract relevant farmer information for Gemini context"""
    return {
        'name': farmer.name,
        'state': farmer.state,
        'district': farmer.district,
        'taluka': farmer.taluka,
        'village': farmer.village,
        'land_area_hectares': farmer.total_land_area_hectares,
        'soil_type': farmer.soil_type,
        'current_crops': farmer.current_crops,
        'water_type': farmer.water_type,
        'is_oilseed_farmer': farmer.is_oilseed_farmer
    }


def _is_cache_valid(weather_rec):
    """Check if cached recommendation is still valid"""
    if not weather_rec:
        return False
    if not weather_rec.expires_at:
        return False
    return weather_rec.expires_at > datetime.utcnow()


def _get_gemini_weather_recommendations(farmer, forecast):
    """
    Get weather-based recommendations using Gemini API.
    Returns structured recommendations or None if API fails.
    """
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("[WEATHER] No GEMINI_API_KEY configured")
            return None
        
        # Build farmer and weather context
        farmer_context = _get_farmer_context(farmer)
        
        # Create detailed prompt for Gemini (English for clarity, translate output to Hindi)
        prompt = f"""आप एक कृषि विशेषज्ञ हैं जो भारतीय किसानों को मौसम-आधारित फसल प्रबंधन में विस्तृत सलाह देते हैं।

किसान की जानकारी:
- नाम: {farmer_context.get('name', 'Unknown')}
- स्थान: {farmer_context.get('taluka', '')}, {farmer_context.get('district', '')}, {farmer_context.get('state', '')}
- भूमि क्षेत्र: {farmer_context.get('land_area_hectares', 0)} हेक्टेयर
- मिट्टी का प्रकार: {farmer_context.get('soil_type', 'निर्दिष्ट नहीं')}
- वर्तमान फसलें: {farmer_context.get('current_crops', 'निर्दिष्ट नहीं')}
- पानी का स्रोत: {farmer_context.get('water_type', 'निर्दिष्ट नहीं')}
- तेलहन किसान: {farmer_context.get('is_oilseed_farmer', False)}

7 दिन का मौसम पूर्वानुमान:
{json.dumps(forecast, indent=2)}

कार्य: किसान के मौसम, फसलों और मिट्टी के आधार पर विस्तृत कृषि सिफारिशें दीजिए। प्रत्येक सिफारिश में:
1. संक्षिप्त सारांश (2-3 वाक्य)
2. विस्तृत व्याख्या (6-8 विस्तृत वाक्य)
3. विशिष्ट कार्रवाई के कदम
4. चेतावनियां व सावधानियां

केवल यह JSON वापस करें (कोई मार्कडाउन नहीं, कोई अतिरिक्त पाठ नहीं, कोई अंग्रेजी नहीं):

{{
    "critical_alerts": [
        {{
            "type": "अत्यधिक वर्षा|सूखा|पाला|ओले|अत्यधिक गर्मी|तूफान",
            "severity": "high|medium|low",
            "affected_days": [दिन संख्याएं],
            "hindi_emoji": "उपयुक्त emoji",
            "hindi_title": "खतरे का नाम हिंदी में",
            "hindi_summary": "यह चेतावनी क्या है (2-3 पूर्ण वाक्य हिंदी में)",
            "hindi_details": "विस्तृत व्याख्या (कम से कम 6-8 पूर्ण वाक्य हिंदी में)। समझाएं कि यह आपकी फसल को कैसे प्रभावित करेगा, क्या समस्याएं हो सकती हैं, और साधारण किसान क्या सोचेंगे।",
            "hindi_action": "विस्तृत कार्रवाई के कदम (कम से कम 3-4 स्पष्ट निर्देश हिंदी में)"
        }}
    ],
    "irrigation_advice": {{
        "hindi_emoji": "💧",
        "hindi_title": "सिंचाई की सलाह",
        "hindi_summary": "क्या सिंचाई की जरूरत है (2-3 वाक्य हिंदी में)",
        "hindi_details": "विस्तृत निर्देश (कम से कम 6-8 वाक्य हिंदी में)। कब सिंचाई करें, कितना पानी दें, किस तरीके से करें।",
        "needed": true|false,
        "timing": "तुरंत|अगले 3 दिन|अगले सप्ताह",
        "quantity_mm": संख्या,
        "hindi_method": "सिंचाई का तरीका हिंदी में (ड्रिप, बाढ़, आदि)"
    }},
    "pest_disease_alerts": [
        {{
            "hindi_emoji": "🐛",
            "pest_disease_hindi": "कीट/रोग का नाम हिंदी में",
            "hindi_summary": "यह कीट/रोग क्या है और क्या नुकसान करता है (2-3 वाक्य हिंदी में)",
            "hindi_details": "विस्तृत जानकारी (कम से कम 6-8 वाक्य हिंदी में)। यह कब आता है, कैसे दिखता है, क्या लक्षण हैं, क्या नुकसान करता है।",
            "risk_level": "high|medium|low",
            "hindi_prevention": "रोकथाम के विस्तृत उपाय (कम से कम 5-6 वाक्य हिंदी में)। कौन सी दवा लगाएं, कितनी बार, कब लगाएं।",
            "critical_window": "दिन X से दिन Y तक सबसे ज्यादा खतरा"
        }}
    ],
    "fertilizer_timing": {{
        "hindi_emoji": "🌾",
        "hindi_title": "खाद का समय और तरीका",
        "hindi_summary": "खाद के बारे में सारांश (2-3 वाक्य हिंदी में)",
        "hindi_details": "विस्तृत निर्देश (कम से कम 6-8 वाक्य हिंदी में)। कौन सी खाद लगाएं, कितनी मात्रा में, कब लगाएं, कैसे लगाएं।",
        "next_application_day": दिन संख्या,
        "type": "नाइट्रोजन|पोटेशियम|फॉस्फोरस|मिश्रित",
        "quantity_kg_per_hectare": संख्या,
        "hindi_precautions": "महत्वपूर्ण सावधानियां (3-4 वाक्य हिंदी में)"
    }},
    "weather_warnings": [
        {{
            "hindi_emoji": "⚠️",
            "condition_hindi": "मौसम की स्थिति का नाम हिंदी में",
            "hindi_summary": "मौसम की स्थिति का सारांश (2-3 वाक्य हिंदी में)",
            "hindi_details": "विस्तृत विश्लेषण (कम से कम 6-8 वाक्य हिंदी में)। क्या होगा, कब होगा, किस हद तक होगा, क्या नुकसान हो सकता है।",
            "timing": "मौसम कब आएगा (दिन X से दिन Y तक)",
            "hindi_preparedness": "तैयारी के कदम (कम से कम 4-5 वाक्य हिंदी में)"
        }}
    ],
    "soil_management": {{
        "hindi_emoji": "🌱",
        "hindi_title": "मिट्टी की देखभाल",
        "hindi_summary": "मिट्टी की देखभाल (2-3 वाक्य हिंदी में)",
        "hindi_details": "विस्तृत सलाह (कम से कम 6-8 वाक्य हिंदी में)। मिट्टी को स्वस्थ कैसे रखें, क्या करें, क्या न करें।",
        "mulching_required": true|false,
        "drainage_required": true|false,
        "hindi_specific_steps": "विशिष्ट कदम (3-4 वाक्य हिंदी में)"
    }},
    "seasonal_insights": {{
        "hindi_emoji": "📈",
        "hindi_title": "मौसमी सुझाव",
        "hindi_summary": "इस मौसम के लिए क्या करें (2-3 वाक्य हिंदी में)",
        "hindi_details": "व्यापक सलाह (कम से कम 8-10 वाक्य हिंदी में)। इस समय क्या अवसर हैं, क्या जोखिम हैं, कौन से काम प्राथमिकता दें।",
        "optimal_practices": "सर्वोत्तम तरीके (6-8 वाक्य हिंदी में)"
    }}
}}

अत्यंत महत्वपूर्ण निर्देश (MANDATORY):
1. प्रत्येक वर्ण, शब्द, वाक्य पूरी तरह हिंदी में होना चाहिए - कोई अंग्रेजी नहीं
2. "details" वाले सभी फील्ड में कम से कम 6-8 पूरे वाक्य हिंदी में लिखें
3. संख्याएं (1, 2, 3, आदि) ठीक है, लेकिन बाकी सब हिंदी में हो
4. असली किसानों की भाषा में लिखें - जटिल न हो, सरल और समझने में आसान हो
5. केवल JSON ही भेजें - कोई व्याख्या, कोई markdown, कोई अन्य पाठ नहीं"""
        
        # Call Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            recommendations = json.loads(json_str)
            return {
                'success': True,
                'recommendations': recommendations,
                'ai_method': 'gemini'
            }
        else:
            print(f"[WEATHER] Could not extract JSON from Gemini response: {response_text[:200]}")
            return None
    
    except json.JSONDecodeError as e:
        print(f"[WEATHER] JSON parse error from Gemini: {e}")
        return None
    except Exception as e:
        print(f"[WEATHER] Gemini API error: {str(e)}")
        return None


def _get_rule_based_weather_recommendations(farmer, forecast):
    """Rule-based fallback recommendations with Hindi translations"""
    try:
        recommendations = {
            'critical_alerts': [],
            'irrigation_advice': {},
            'pest_disease_alerts': [],
            'fertilizer_timing': {},
            'weather_warnings': [],
            'soil_management': {},
            'seasonal_insights': {},
            'ai_method': 'rule_based'
        }
        
        # Calculate weather statistics
        total_rainfall = sum(day.get('precip_mm', 0) for day in forecast)
        avg_temp = sum(day.get('temp_max', 25) for day in forecast) / len(forecast) if forecast else 25
        max_wind = max((day.get('wind_kmh', 0) for day in forecast), default=0)
        rainy_days = [i+1 for i, d in enumerate(forecast) if d.get('precip_mm', 0) > 2]
        
        # Check for excessive rainfall
        if total_rainfall > 50:
            recommendations['critical_alerts'].append({
                'type': 'अत्यधिक वर्षा',
                'severity': 'high',
                'affected_days': rainy_days,
                'hindi_summary': 'अगले 7 दिनों में अत्यधिक वर्षा की संभावना है। इससे खेत में जलभराव हो सकता है।',
                'hindi_details': f'कुल वर्षा {total_rainfall:.1f} मिमी की संभावना है जो आपकी फसल के लिए हानिकारक हो सकती है। इस अवधि में मिट्टी में अतिरिक्त पानी होगा जिससे पौधों की जड़ें सड़ सकती हैं। आपको तुरंत जल निकासी व्यवस्था सुनिश्चित करनी चाहिए। बाढ़ के पानी को खेत से बाहर निकालने के लिए नालियां बनाएं।',
                'hindi_action': 'खेत में तुरंत जल निकासी नालियां बनाएं। सिंचाई बिल्कुल न करें। ट्रैक्टर या अन्य यंत्रों से अतिरिक्त पानी निकालने में सहायता लें।',
                'crop_impact': 'फसल में पत्ती धब्बा रोग की संभावना'
            })
        
        # Check for drought conditions
        elif total_rainfall < 5 and avg_temp > 28:
            recommendations['critical_alerts'].append({
                'type': 'सूखा',
                'severity': 'high',
                'affected_days': list(range(1, 8)),
                'hindi_summary': 'सूखे की स्थिति बनने वाली है। कम वर्षा और उच्च तापमान पौधों के लिए दबाव बनाएंगे।',
                'hindi_details': f'अगले 7 दिनों में केवल {total_rainfall:.1f} मिमी वर्षा की संभावना है और तापमान {avg_temp:.1f}°C रहेगा। ये परिस्थितियां आपकी फसल को सूखा ग्रस्त कर सकती हैं। पौधों की पत्तियां पीली पड़ सकती हैं और विकास रुक सकता है। मिट्टी की नमी कम हो जाएगी।',
                'hindi_action': 'तुरंत गहरी सिंचाई करें। ड्रिप सिंचाई का उपयोग करें यदि संभव हो। पौधों के पास गीली घास (मल्च) लगाएं।',
                'crop_impact': 'फसल की पैदावार में कमी'
            })
        
        # Irrigation advice based on rainfall and temperature
        if total_rainfall < 15:
            recommendations['irrigation_advice'] = {
                'hindi_summary': f'आपको निश्चित रूप से सिंचाई की आवश्यकता है क्योंकि अगले 7 दिनों में केवल {total_rainfall:.1f} मिमी वर्षा की संभावना है।',
                'hindi_details': f'मौसम के आंकड़ों के अनुसार अगले सप्ताह में अपर्याप्त वर्षा होगी। आपको {25 - total_rainfall:.0f}mm से अधिक सिंचाई करनी चाहिए। सिंचाई सुबह 5-7 बजे या शाम 6-8 बजे करें जब तापमान कम हो। ड्रिप सिंचाई सर्वोत्तम है क्योंकि इससे पानी की बर्बादी कम होती है। मिट्टी की नमी जांचें - यदि मिट्टी सूखी है तो तुरंत सिंचाई करें।',
                'needed': True,
                'timing': 'immediate' if total_rainfall < 5 else 'next 3 days',
                'quantity_mm': max(20, 25 - total_rainfall),
                'frequency_days': 3 if avg_temp > 30 else 4
            }
        else:
            recommendations['irrigation_advice'] = {
                'hindi_summary': 'पर्याप्त वर्षा की संभावना है, इसलिए आपको अतिरिक्त सिंचाई की तत्काल आवश्यकता नहीं है।',
                'hindi_details': f'अगले 7 दिनों में {total_rainfall:.1f} मिमी वर्षा की संभावना है जो आपकी फसल के लिए काफी है। तुरंत सिंचाई न करें। हालांकि, यदि वर्षा 2-3 दिन में न हो तो सिंचाई के लिए तैयार रहें। मिट्टी की नमी नियमित रूप से जांचते रहें। अत्यधिक वर्षा के बाद तुरंत jल निकास की व्यवस्था सुनिश्चित करें।',
                'needed': False,
                'timing': 'as needed',
                'quantity_mm': 0,
                'frequency_days': 0
            }
        
        # Pest alerts based on temperature and humidity
        if avg_temp > 28 and total_rainfall > 30:
            recommendations['pest_disease_alerts'] = [
                {
                    'pest_disease_hindi': 'पत्ती धब्बा रोग (Leaf Spot)',
                    'hindi_summary': 'गर्म और आर्द्र मौसम में पत्ती धब्बा रोग के विकास के लिए अनुकूल परिस्थितियां हैं।',
                    'hindi_details': 'यह कवक रोग उच्च तापमान ({:.1f}°C) और अधिक वर्षा ({:.1f}mm) में तेजी से फैलता है। संक्रमित पत्तियों पर भूरे या काले धब्बे दिखाई देंगे। यह रोग पौधे की पत्तियों को नष्ट कर देता है जिससे प्रकाश संश्लेषण में कमी आती है। फसल की पैदावार में 20-30% तक कमी हो सकती है।'.format(avg_temp, total_rainfall),
                    'risk_level': 'high',
                    'hindi_prevention': 'ट्राइकोडर्मा या कॉपर आधारित कवकनाशी का छिड़काव करें। पौधों के बीच उचित दूरी बनाए रखें ताकि हवा का प्रवाह अच्छा हो। संक्रमित पत्तियों को तुरंत तोड़कर जला दें। गीली घास न लगाएं जो रोग को बढ़ावा दे।',
                    'critical_window': 'दिन 2-6'
                }
            ]
        elif avg_temp > 32:
            recommendations['pest_disease_alerts'] = [
                {
                    'pest_disease_hindi': 'थ्रिप्स और मकड़ियों की बहुलता',
                    'hindi_summary': 'बहुत गर्म मौसम में कीटों की गतिविधि तेजी से बढ़ जाती है।',
                    'hindi_details': f'तापमान {avg_temp:.1f}°C होने से थ्रिप्स, एफिड्स और मकड़ियां तेजी से प्रजनन करेंगे। ये कीट पौधे की कोमल पत्तियों को चूसते हैं जिससे पत्तियां पीली और मुड़ जाती हैं। नीम का तेल या कीटनाशक का छिड़काव करें। पौधों की निरंतर निगरानी रखें।',
                    'risk_level': 'medium',
                    'hindi_prevention': 'नीम का तेल 3% घोल का छिड़काव करें। स्ट्रिंग ट्रैप या पीले रंग के चिपचिपे ट्रैप लगाएं। पौधों के चारों ओर सहायक पौधे लगाएं जो कीटों को आकर्षित करें।',
                    'critical_window': 'दिन 1-7'
                }
            ]
        
        # Fertilizer timing
        recommendations['fertilizer_timing'] = {
            'hindi_summary': 'आने वाले मौसम के अनुसार उचित समय पर खाद का प्रयोग करें।',
            'hindi_details': 'यदि वर्षा की संभावना है तो खाद को बारिश की शुरुआत से 2-3 दिन पहले डालें ताकि बारिश में यह पौधों को अवशोषित हो सके। नाइट्रोजन खाद मौसम गर्म है तो इसका असर जल्दी होता है। जैव खाद (कोम्पोस्ट) का उपयोग मिट्टी की गुणवत्ता में सुधार के लिए करें। पोटेशियम की कमी होने पर पौधे कमजोर हो जाते हैं।',
            'next_application_day': 2 if total_rainfall > 10 else 1,
            'type': 'mixed' if total_rainfall > 30 else 'nitrogen',
            'quantity_kg_per_hectare': 40 if total_rainfall > 30 else 60,
            'precautions_hindi': 'वर्षा के दिन खाद न डालें। सूखी मिट्टी में खाद डालें। पत्ती जलन से बचने के लिए पत्तीय खाद सूर्यास्त के बाद ही डालें।'
        }
        
        # Soil management
        recommendations['soil_management'] = {
            'hindi_summary': 'मिट्टी की उचित देखभाल उच्च पैदावार के लिए आवश्यक है।',
            'hindi_details': 'आने वाले मौसम में मिट्टी की नमी बनाए रखना महत्वपूर्ण है। अत्यधिक वर्षा से बचने के लिए जल निकास व्यवस्था करें। गीली घास (मल्च) मिट्टी की नमी को बनाए रखने में मदद करता है और तापमान को नियंत्रित करता है। मिट्टी के स्वास्थ्य के लिए नियमित रूप से जैव खाद का प्रयोग करें। मिट्टी की जांच 6 महीने में एक बार करवाएं।',
            'mulching_required': total_rainfall < 20,
            'drainage_required': total_rainfall > 40
        }
        
        # Seasonal insights
        recommendations['seasonal_insights'] = {
            'hindi_summary': 'मौजूदा मौसम में फसल उत्पादन के लिए निम्नलिखित सुझाव महत्वपूर्ण हैं।',
            'hindi_details': 'आने वाले सप्ताह में मौसम परिवर्तनशील रहेगा। तापमान और वर्षा दोनों में उतार-चढ़ाव हो सकते हैं। आपको पौधों की स्वास्थ्य स्थिति पर नजर रखनी चाहिए। नियमित निरीक्षण से समस्याओं को जल्दी पहचाना जा सकता है। स्थानीय कृषि विशेषज्ञों से सलाह लें यदि कोई समस्या दिखाई दे। बीज उपचार करें बीमारियों से बचने के लिए।',
            'optimal_practices': 'नियमित निरीक्षण, समय पर सिंचाई, उचित खाद प्रबंधन, और कीट नियंत्रण।'
        }
        
        return {
            'success': True,
            'recommendations': recommendations,
            'ai_method': 'rule_based'
        }
    
    except Exception as e:
        print(f"[WEATHER] Rule-based recommendation error: {str(e)}")
        return None


def _get_weather_recommendations(farmer_id):
    """
    Main function to get weather recommendations with caching and fallback.
    Returns cached recommendations if valid, otherwise generates new ones via Gemini or rule-based.
    """
    try:
        farmer = Farmer.query.filter_by(id=farmer_id).first()
        if not farmer:
            return {'error': 'Farmer not found'}
        
        # Check for valid cached recommendation (less than 24 hours old)
        cached_rec = WeatherRecommendation.query.filter(
            WeatherRecommendation.farmer_id == farmer_id,
            WeatherRecommendation.expires_at > datetime.utcnow()
        ).order_by(WeatherRecommendation.created_at.desc()).first()
        
        if cached_rec and _is_cache_valid(cached_rec):
            return {
                'success': True,
                'recommendations': cached_rec.recommendations,
                'weather_data': cached_rec.weather_data,
                'ai_method': cached_rec.ai_method,
                'from_cache': True,
                'expires_at': cached_rec.expires_at.isoformat()
            }
        
        # Clear expired recommendations
        WeatherRecommendation.query.filter(
            WeatherRecommendation.farmer_id == farmer_id,
            WeatherRecommendation.expires_at <= datetime.utcnow()
        ).delete()
        db.session.commit()
        
        # Fetch current weather forecast
        location_name = farmer.district or 'India'
        
        # Get weather data (reuse existing api_forecast logic)
        try:
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
            
            lat, lon = 20.5937, 78.9629  # Default (India center)
            if farmer.district and farmer.district in district_coords:
                lat, lon = district_coords[farmer.district]
            
            url = f"https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max',
                'timezone': 'Asia/Kolkata',
                'forecast_days': 7
            }
            
            weather_response = requests.get(url, params=params, timeout=5)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            
            # Parse weather
            forecast = []
            daily = weather_data.get('daily', {})
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
                    'wind_kmh': round(wind[i] * 3.6, 1) if i < len(wind) else 10
                })
        except Exception as e:
            print(f"[WEATHER] Error fetching forecast: {e}")
            forecast = generate_forecast_for_location(district=location_name, days=7)
        
        # Try Gemini API first
        recommendations_result = None
        if GEMINI_AVAILABLE:
            recommendations_result = _get_gemini_weather_recommendations(farmer, forecast)
        
        # Fallback to rule-based if Gemini unavailable/failed
        if not recommendations_result:
            recommendations_result = _get_rule_based_weather_recommendations(farmer, forecast)
        
        if recommendations_result and recommendations_result.get('success'):
            # Cache the recommendations
            expiry_time = datetime.utcnow() + timedelta(hours=24)
            
            weather_rec = WeatherRecommendation(
                farmer_id=farmer_id,
                weather_data=forecast,
                recommendations=recommendations_result['recommendations'],
                ai_method=recommendations_result['ai_method'],
                expires_at=expiry_time
            )
            db.session.add(weather_rec)
            db.session.commit()
            
            return {
                'success': True,
                'recommendations': recommendations_result['recommendations'],
                'weather_data': forecast,
                'ai_method': recommendations_result['ai_method'],
                'from_cache': False,
                'expires_at': expiry_time.isoformat()
            }
        
        return {'error': 'Could not generate recommendations', 'success': False}
    
    except Exception as e:
        print(f"[WEATHER] Error in _get_weather_recommendations: {str(e)}")
        return {'error': str(e), 'success': False}


# ======================== API ENDPOINTS ========================

@weather_bp.route('/api/recommendations')
def api_weather_recommendations():
    """Get AI-powered weather-based recommendations with caching"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    farmer_id = session['farmer_id_verified']
    result = _get_weather_recommendations(farmer_id)
    
    if result.get('success'):
        # Store recommendations in session for detail page access
        session['recommendations'] = result['recommendations']
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@weather_bp.route('/api/refresh', methods=['POST'])
def api_refresh_recommendations():
    """Force refresh: clear cache and regenerate recommendations"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    farmer_id = session['farmer_id_verified']
    
    try:
        # Delete all existing recommendations for this farmer
        WeatherRecommendation.query.filter_by(farmer_id=farmer_id).delete()
        db.session.commit()
        
        # Generate fresh recommendations
        result = _get_weather_recommendations(farmer_id)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Recommendations refreshed successfully',
                'recommendations': result['recommendations'],
                'weather_data': result['weather_data'],
                'ai_method': result['ai_method'],
                'expires_at': result['expires_at']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate recommendations')
            }), 500
    
    except Exception as e:
        print(f"[WEATHER] Error in refresh: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/ask-followup', methods=['POST'])
def api_ask_followup():
    """Interactive chat: ask follow-up questions to Gemini about recommendations"""
    if 'farmer_id_verified' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        farmer_id = session['farmer_id_verified']
        data = request.get_json() or {}
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        if not GEMINI_AVAILABLE:
            return jsonify({
                'error': 'AI chat unavailable',
                'message': 'Gemini API is not configured'
            }), 503
        
        # Get the latest recommendation for context
        weather_rec = WeatherRecommendation.query.filter_by(
            farmer_id=farmer_id
        ).order_by(WeatherRecommendation.created_at.desc()).first()
        
        if not weather_rec or not weather_rec.recommendations:
            return jsonify({
                'error': 'No recommendations found',
                'message': 'Please generate recommendations first'
            }), 404
        
        farmer = Farmer.query.filter_by(id=farmer_id).first()
        
        # Build context for follow-up
        context_prompt = f"""
You are an agricultural advisor helping a farmer understand weather-based crop management.

FARMER CONTEXT:
- Name: {farmer.name if farmer else 'Unknown'}
- Location: {farmer.district if farmer else 'Unknown'}, {farmer.state if farmer else 'Unknown'}
- Crops: {farmer.current_crops if farmer else 'Unknown'}
- Soil: {farmer.soil_type if farmer else 'Unknown'}

PREVIOUS RECOMMENDATIONS:
{json.dumps(weather_rec.recommendations, indent=2)}

FARMER'S QUESTION: {question}

Provide a brief, helpful answer (2-3 sentences maximum) related to the above recommendations and the farmer's situation.
Be direct and actionable. Do not provide long explanations or multiple paragraphs.
"""
        
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            response = model.generate_content(context_prompt)
            answer = response.text.strip()
            
            # Store chat context for future reference (in this session)
            if not weather_rec.chat_context:
                weather_rec.chat_context = []
            
            weather_rec.chat_context.append({
                'role': 'user',
                'content': question
            })
            weather_rec.chat_context.append({
                'role': 'assistant',
                'content': answer
            })
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'question': question,
                'answer': answer,
                'context': 'Based on your current weather forecast and recommendations'
            }), 200
        
        except Exception as e:
            print(f"[WEATHER] Gemini chat error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to get response: {str(e)}'
            }), 500
    
    except Exception as e:
        print(f"[WEATHER] Follow-up error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ======================== DETAILS PAGE ROUTE ========================

@weather_bp.route('/details/<detail_type>')
def details_page(detail_type):
    """Display detailed information for a specific recommendation"""
    if 'farmer_id_verified' not in session:
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    farmer_id = session.get('farmer_id_verified')
    farmer = Farmer.query.filter_by(id=farmer_id).first()
    
    # Get recommendations from session or API
    if 'recommendations' not in session:
        result = _get_weather_recommendations(farmer_id)
        if not result.get('success'):
            return render_template('weather_details.html', 
                                   error='सिफारिशें लोड नहीं कर सकते',
                                   farmer_name=farmer.name if farmer else 'किसान')
        session['recommendations'] = result['recommendations']
    
    recommendations = session.get('recommendations', {})
    
    # Extract details based on type
    detail_data = None
    title = ''
    
    if detail_type == 'irrigation':
        detail_data = recommendations.get('irrigation_advice', {})
        title = '💧 सिंचाई सलाह'
    
    elif detail_type == 'pest':
        detail_data = recommendations.get('pest_alerts', [])
        if detail_data and isinstance(detail_data, list):
            detail_data = detail_data[0] if detail_data else {}
        title = '🐛 कीट नियंत्रण'
    
    elif detail_type == 'fertilizer':
        detail_data = recommendations.get('fertilizer_timing', {})
        title = '🌾 खाद का समय'
    
    elif detail_type == 'weather':
        detail_data = recommendations.get('weather_warnings', [])
        if detail_data and isinstance(detail_data, list):
            detail_data = detail_data[0] if detail_data else {}
        title = '⚠️ मौसम चेतावनी'
    
    elif detail_type == 'seasonal':
        detail_data = recommendations.get('seasonal_insights', {})
        title = '📈 मौसमी सुझाव'
    
    elif detail_type == 'alerts':
        detail_data = recommendations.get('critical_alerts', [])
        title = '🚨 गंभीर चेतावनियां'
    
    return render_template('weather_details.html',
                           detail_type=detail_type,
                           title=title,
                           detail_data=detail_data,
                           farmer_name=farmer.name if farmer else 'किसान')
