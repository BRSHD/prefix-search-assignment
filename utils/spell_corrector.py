import re

class SimpleSpellCorrector:
    def __init__(self):
        self.common_typos = {
            'масло раст': 'масло растительное',
            'кар тофель': 'картофель',
            'греч не': 'гречневая',
            'хозяйст мыло': 'хозяйственное мыло',
            'круп греч': 'крупа гречневая',
            'рыба фил': 'рыба филе',
            'джин то': 'джин тоник',
            'памперсы': 'подгузники',
            'диап': 'подгузники',
            'ночник': 'ночные',
            'холс': 'холост',
            'сан пелле': 'san pellegrino',
            'посуд моющ': 'посудомоечное',
            'кабель usb': 'кабель usb-c'
        }
        
        self.synonyms = {
            'подгузники': ['памперсы', 'diapers', 'диаперсы'],
            'памперсы': ['подгузники', 'diapers'],
            'diapers': ['подгузники', 'памперсы'],
            'ночные': ['night', 'ночник'],
            'night': ['ночные'],
            'adult': ['взрослый', 'для взрослых'],
            'hypo': ['гипоаллергенный'],
            'prosecco': ['просэкко'],
            'riesling': ['рислинг'],
            'cheddar': ['чеддер'],
            'gouda': ['гауда'],
            'моющее': ['моющее средство'],
            'посуд': ['посудомоечное']
        }
    
    def correct(self, query):
        query_lower = query.lower()
        
        # Исправление частых опечаток
        corrected_query = query
        for typo, correct in self.common_typos.items():
            if typo in query_lower:
                corrected_query = corrected_query.replace(typo, correct)
                print(f"🔧 Исправлена опечатка: '{typo}' -> '{correct}'")
        
        # Создаем список вариантов запросов
        query_variants = [corrected_query]
        
        # Добавляем синонимы для каждого слова
        words = corrected_query.split()
        for i, word in enumerate(words):
            if word.lower() in self.synonyms:
                for synonym in self.synonyms[word.lower()]:
                    new_words = words.copy()
                    new_words[i] = synonym
                    new_query = ' '.join(new_words)
                    if new_query not in query_variants:
                        query_variants.append(new_query)
                        print(f"🔧 Добавлен синоним: '{word}' -> '{synonym}'")
        
        return query_variants

# Глобальный экземпляр
spell_corrector = SimpleSpellCorrector()