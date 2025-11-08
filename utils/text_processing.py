import re
try:
    from transliterate import translit
    HAS_TRANSLITERATE = True
except ImportError:
    HAS_TRANSLITERATE = False

# Таблица для исправления раскладки (qwerty -> йцукен)
LAYOUT_MAP = {
    'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
    '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л',
    'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь',
    ',': 'б', '.': 'ю', '/': '.', '`': 'ё', 
    'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
    '{': 'Х', '}': 'Ъ', 'A': 'Ф', 'S': 'Ы', 'D': 'В', 'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л',
    'L': 'Д', ':': 'Ж', '"': 'Э', 'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И', 'N': 'Т', 'M': 'Ь',
    '<': 'Б', '>': 'Ю', '?': ',', '~': 'Ё'
}

# Обратная таблица (йцукен -> qwerty)
REVERSE_LAYOUT_MAP = {v: k for k, v in LAYOUT_MAP.items()}

def fix_keyboard_layout(text):
    """Исправляет неправильную раскладку клавиатуры"""
    # Если текст в основном состоит из латинских букв, но похож на русские слова
    # значит пользователь ввел русское слово в английской раскладке
    if any(char in LAYOUT_MAP for char in text.lower()):
        fixed = []
        for char in text:
            fixed.append(LAYOUT_MAP.get(char, char))
        return ''.join(fixed)
    return text

def transliterate_text(text):
    """Транслитерирует текст (латиница -> кириллица)"""
    if not HAS_TRANSLITERATE:
        return text
        
    try:
        # Если текст содержит в основном латинские буквы, пробуем транслитерировать
        latin_count = sum(1 for char in text if char.isalpha() and char.isascii())
        cyrillic_count = sum(1 for char in text if char.isalpha() and not char.isascii())
        
        if latin_count > cyrillic_count:
            # Пробуем транслитерировать с английского на русский
            transliterated = translit(text, 'ru')
            return transliterated
    except Exception as e:
        print(f"Ошибка транслитерации: {e}")
    
    return text

def extract_numeric_features(text):
    """Извлекает числовые признаки из запроса (вес, объем)"""
    numeric_filters = {}
    
    # Паттерны для веса: "5кг", "500г", "1.5 kg" и т.д.
    weight_patterns = [
        r'(\d+\.?\d*)\s*(кг|kg|кg|kг)',
        r'(\d+\.?\d*)\s*(г|g|гр|gr)'
    ]
    
    # Паттерны для объема: "1л", "500ml", "2.5 l" и т.д.
    volume_patterns = [
        r'(\d+\.?\d*)\s*(л|l|лtr|liter)',
        r'(\d+\.?\d*)\s*(мл|ml|мl|mл)'
    ]
    
    for pattern in weight_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            numeric_filters['weight'] = matches[0][0]
            break
            
    for pattern in volume_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            numeric_filters['volume'] = matches[0][0]
            break
            
    return numeric_filters

def normalize_query(query):
    """Простая нормализация - сначала сделаем рабочую версию"""
    if not query:
        return "", {}
    
    # Просто приводим к нижнему регистру и обрезаем пробелы
    normalized = query.strip().lower()
    
    print(f"🔧 Нормализованный запрос: '{normalized}'")
    
    return normalized, {}