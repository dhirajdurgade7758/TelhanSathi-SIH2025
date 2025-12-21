"""
Translation API routes for multilingual support
"""
from flask import Blueprint, request, session, jsonify
from translations import get_translation, get_all_translations, TRANSLATIONS

translation_bp = Blueprint('translation', __name__, url_prefix='/api/translate')

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
    'mr': 'मराठी',
    'gu': 'ગુજરાતી',
}


@translation_bp.route('/set-language', methods=['POST'])
def set_language():
    """Set the user's preferred language in session"""
    data = request.get_json()
    language = data.get('language', 'en')
    
    if language not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Invalid language code'}), 400
    
    session['language'] = language
    return jsonify({'success': True, 'language': language})


@translation_bp.route('/get-language', methods=['GET'])
def get_language():
    """Get the user's current language"""
    language = session.get('language', 'en')
    return jsonify({'language': language})


@translation_bp.route('/translate', methods=['POST'])
def translate():
    """
    Translate text to target language
    Request: {"text": "Hello", "target_language": "hi"}
    """
    data = request.get_json()
    text = data.get('text', '')
    target_language = data.get('target_language', 'en')
    
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    if target_language not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Invalid language code'}), 400
    
    translated = get_translation(text, target_language)
    return jsonify({
        'original': text,
        'translated': translated,
        'language': target_language
    })


@translation_bp.route('/languages', methods=['GET'])
def languages():
    """Get list of supported languages"""
    return jsonify(SUPPORTED_LANGUAGES)


@translation_bp.route('/all-translations', methods=['GET'])
def all_translations():
    """Get all translation dictionaries"""
    return jsonify(TRANSLATIONS)


@translation_bp.route('/translate-page', methods=['POST'])
def translate_page():
    """
    Translate entire page by replacing all known text strings
    Request: {"target_language": "hi"}
    """
    data = request.get_json()
    target_language = data.get('target_language', 'en')
    
    if target_language not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Invalid language code'}), 400
    
    # Get all translations for this language
    translations = {}
    for original_text, lang_translations in TRANSLATIONS.items():
        if target_language in lang_translations:
            translations[original_text] = lang_translations[target_language]
    
    return jsonify({
        'language': target_language,
        'translations': translations
    })
