"""
Simple multilingual translation system using predefined dictionaries
Supports: Hindi (hi), Marathi (mr), English (en), Gujarati (gu)
"""

# Translation dictionary for common UI strings
TRANSLATIONS = {
    # Header
    'Telhan Sathi': {
        'hi': 'तेल्हण साथी',
        'mr': 'तेलहण साथी',
        'gu': 'તેલહણ સાથી'
    },
    'Go to Redemption Store': {
        'hi': 'पुरस्कार स्टोर पर जाएं',
        'mr': 'पुरस्कार स्टोर वर जा',
        'gu': 'પુરસ્કાર સ્ટોર પર જાઓ'
    },
    'Change Language': {
        'hi': 'भाषा बदलें',
        'mr': 'भाषा बदलें',
        'gu': 'ભાષા બદલો'
    },
    'English': {
        'hi': 'अंग्रेजी',
        'mr': 'इंग्रजी',
        'gu': 'અંગ્રેજી'
    },
    'हिंदी': {
        'hi': 'हिंदी',
        'mr': 'हिंदी',
        'gu': 'હિન્દી'
    },
    'मराठी': {
        'hi': 'मराठी',
        'mr': 'मराठी',
        'gu': 'મરાઠી'
    },
    'ગુજરાતી': {
        'hi': 'ગુજરાતી',
        'mr': 'ગુજરાતી',
        'gu': 'ગુજરાતી'
    },

    # Footer Navigation
    'Home': {
        'hi': 'होम',
        'mr': 'होम',
        'gu': 'હોમ'
    },
    'Weather': {
        'hi': 'मौसम',
        'mr': 'हवामान',
        'gu': 'હવામાન'
    },
    'My Deals': {
        'hi': 'मेरे डील',
        'mr': 'माझे डील',
        'gu': 'મારા ડીલ્સ'
    },
    'My Profile': {
        'hi': 'मेरी प्रोफाइल',
        'mr': 'माझी प्रोफाइल',
        'gu': 'મારી પ્રોફાઇલ'
    },

    # Dashboard
    'उपकरण': {
        'hi': 'उपकरण',
        'mr': 'साधने',
        'gu': 'સાધનો'
    },
    'मार्केट प्लेस': {
        'hi': 'मार्केट प्लेस',
        'mr': 'मार्केट प्लेस',
        'gu': 'માર્કેટ પ્લેસ'
    },
    'मौसम पूर्वानुमान': {
        'hi': 'मौसम पूर्वानुमान',
        'mr': 'हवामान अंदाज',
        'gu': 'હવામાન આગાહી'
    },
    'लाभ सिम्युलेटर': {
        'hi': 'लाभ सिम्युलेटर',
        'mr': 'नफा सिम्युलेटर',
        'gu': 'લાભ સિમ્યુલેટર'
    },
    'सरकारी योजनाएँ': {
        'hi': 'सरकारी योजनाएँ',
        'mr': 'सरकारी योजना',
        'gu': 'સરકારી યોજના'
    },
    'फसल अर्थशास्त्र': {
        'hi': 'फसल अर्थशास्त्र',
        'mr': 'पीक अर्थशास्त्र',
        'gu': 'પાક અર્થશાસ્ત્ર'
    },
    'रिडेम्पशन': {
        'hi': 'रिडेम्पशन',
        'mr': 'रिडेम्पशन',
        'gu': 'વધુશાહી'
    },
    'लीडरबोर्ड': {
        'hi': 'लीडरबोर्ड',
        'mr': 'लीडरबोर्ड',
        'gu': 'લીડરબોર્ડ'
    },
    'स्टोर': {
        'hi': 'स्टोर',
        'mr': 'स्टोर',
        'gu': 'સ્ટોર'
    },

    # Special sections
    'विशेष: खेत मॉनिटरिंग सिस्टम': {
        'hi': 'विशेष: खेत मॉनिटरिंग सिस्टम',
        'mr': 'विशेष: शेत निरीक्षण प्रणाली',
        'gu': 'વિશેષ: ખેતી મોનિટરિંગ સિસ્ટમ'
    },
    'रीयल-टाइम फसल स्वास्थ्य, मिट्टी की स्थिति और सैटेलाइट अपडेट।': {
        'hi': 'रीयल-टाइम फसल स्वास्थ्य, मिट्टी की स्थिति और सैटेलाइट अपडेट।',
        'mr': 'रीयल-टाइम पीक आरोग्य, मातीची स्थिती आणि उपग्रह अपडेट।',
        'gu': 'રીયલ-ટાઇમ પાક આરોગ્ય, માટીની સ્થિતિ અને ઉપગ્રહ અપડેટ્સ।'
    },

    # Auth related
    'Login': {
        'hi': 'लॉगिन',
        'mr': 'लॉगिन',
        'gu': 'લૉગિન'
    },
    'Register': {
        'hi': 'रजिस्टर',
        'mr': 'नोंदणी',
        'gu': 'નોંધણી'
    },
    'Logout': {
        'hi': 'लॉग आउट',
        'mr': 'लॉग आउट',
        'gu': 'લૉગ આઉટ'
    },
    'Loading...': {
        'hi': 'लोड हो रहा है...',
        'mr': 'लोड होत आहे...',
        'gu': 'લોડ થઇ રહ્યું છે...'
    },

    # Common buttons and actions
    'OK': {
        'hi': 'ठीक है',
        'mr': 'ठीक आहे',
        'gu': 'ઠીક છે'
    },
    'Cancel': {
        'hi': 'रद्द करें',
        'mr': 'रद्द करा',
        'gu': 'રદ્દ કરો'
    },
    'Submit': {
        'hi': 'जमा करें',
        'mr': 'सबमिट करा',
        'gu': 'સબમિટ કરો'
    },
    'Save': {
        'hi': 'सहेजें',
        'mr': 'जतन करा',
        'gu': 'સંરક્ષણ કરો'
    },
    'Delete': {
        'hi': 'हटाएं',
        'mr': 'हटवा',
        'gu': 'કાઢી નાખો'
    },
    'Edit': {
        'hi': 'संपादित करें',
        'mr': 'संपादित करा',
        'gu': 'સંપાદિત કરો'
    },
    'Back': {
        'hi': 'वापस',
        'mr': 'परत',
        'gu': 'પાછળ'
    },

    # Messages
    'Success': {
        'hi': 'सफलता',
        'mr': 'यशस्वी',
        'gu': 'સાફલ્ય'
    },
    'Error': {
        'hi': 'त्रुटि',
        'mr': 'त्रुटी',
        'gu': 'ભૂલ'
    },
    'Warning': {
        'hi': 'चेतावनी',
        'mr': 'चेतावणी',
        'gu': 'ચેતવણી'
    },
    'No data available': {
        'hi': 'कोई डेटा उपलब्ध नहीं है',
        'mr': 'कोई डेटा उपलब्ध नाही',
        'gu': 'કોઈ ડેટા ઉપલબ્ધ નથી'
    },
}


def get_translation(text, language='en'):
    """
    Get translation for text in specified language
    
    Args:
        text (str): Original text to translate
        language (str): Target language code (en, hi, mr, gu)
    
    Returns:
        str: Translated text or original if not found
    """
    if language == 'en' or not text:
        return text
    
    if text in TRANSLATIONS:
        return TRANSLATIONS[text].get(language, text)
    
    return text


def get_all_translations():
    """Return all translation dictionaries"""
    return TRANSLATIONS
