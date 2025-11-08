import re

def normalize_query(query):
    """Простая нормализация"""
    if not query:
        return query, {}
    
    # Просто приводим к нижнему регистру
    normalized = query.lower().strip()
    
    print(f"🔧 Нормализованный запрос: '{normalized}'")
    
    return normalized, {}

# Пустые функции для совместимости
def extract_numeric_features(text):
    return {}

def fix_keyboard_layout(text):
    return text