"""
Translation utility using Google Translate API
Supports: Hindi (hi), Marathi (mr), English (en), Gujarati (gu)
"""
from google.cloud import translate_v2
from functools import lru_cache
import os

# Initialize translation client
try:
    # Try to use service account if credentials are set
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        translate_client = translate_v2.Client()
    else:
        # Fallback to simple translation using requests (free tier)
        translate_client = None
except Exception as e:
    print(f"Warning: Google Cloud Translate not configured: {e}")
    translate_client = None

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
    'mr': 'मराठी',
    'gu': 'ગુજરાતી',
}

# Language codes for Google Translate
LANG_CODES = {
    'en': 'en',
    'hi': 'hi',
    'mr': 'mr',
    'gu': 'gu',
}


@lru_cache(maxsize=1000)
def translate_text(text, target_language='en'):
    """
    Translate text to target language using Google Translate
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (en, hi, mr, gu)
    
    Returns:
        str: Translated text or original if translation fails
    """
    if not text or target_language == 'en':
        return text
    
    if target_language not in LANG_CODES:
        return text
    
    try:
        if translate_client:
            # Use Google Cloud Translate API
            result = translate_client.translate_text(
                text,
                target_language=LANG_CODES[target_language]
            )
            return result['translatedText']
        else:
            # Fallback: return original text
            # In production, you should set up Google Cloud credentials
            return text
    except Exception as e:
        print(f"Translation error for '{text}' to {target_language}: {e}")
        return text


def get_supported_languages():
    """Return list of supported languages"""
    return SUPPORTED_LANGUAGES


def is_valid_language(lang_code):
    """Check if language code is supported"""
    return lang_code in LANG_CODES
