from deep_translator import GoogleTranslator
def translate_text(text, target_language='en'):
    return GoogleTranslator(source='auto', target=target_language).translate(text)



