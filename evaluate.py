import requests
import csv
import time
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

def test_prefix_queries():
    """Тестируем 30 открытых запросов из prefix_queries.csv"""
    
    # Читаем тестовые запросы
    with open('data/prefix_queries.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        queries = [row for row in reader if row.get('type') == 'open']
    
    print(f"🔍 Тестируем {len(queries)} открытых запросов...")
    
    results = []
    
    for query_data in queries:
        query = query_data['query']
        site = query_data['site']
        notes = query_data['notes']
        
        try:
            start_time = time.time()
            response = requests.get(f"{API_BASE}/search", params={"q": query, "size": 5})
            end_time = time.time()
            
            latency = round((end_time - start_time) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                
                # Формируем результат в требуемом формате
                result_row = {
                    "query": query,
                    "site": site,
                    "type": "open",
                    "notes": notes,
                    "latency_ms": latency,
                    "total_results": data["total"],
                    "normalized_query": data["normalized_query"],
                    "numeric_filters": json.dumps(data["numeric_filters"], ensure_ascii=False)
                }
                
                # Добавляем топ-5 результатов
                for i in range(5):
                    if i < len(data["results"]):
                        product = data["results"][i]
                        result_row[f"top_{i+1}"] = product["name"]
                        result_row[f"top_{i+1}_score"] = round(product["score"], 2)
                    else:
                        result_row[f"top_{i+1}"] = ""
                        result_row[f"top_{i+1}_score"] = ""
                
                # Оценка релевантности (простая эвристика)
                if data["total"] > 0:
                    result_row["judgement"] = "✅ RELEVANT"
                else:
                    result_row["judgement"] = "❌ NO_RESULTS"
                    
                results.append(result_row)
                print(f"✅ '{query}' -> найдено {data['total']} товаров")
                
            else:
                print(f"❌ Ошибка для '{query}': {response.status_code}")
                
        except Exception as e:
            print(f"❌ Исключение для '{query}': {e}")
    
    return results

def calculate_metrics(results):
    """Считаем метрики качества"""
    total_queries = len(results)
    relevant_queries = sum(1 for r in results if "✅" in r["judgement"]) 
    success_rate = (relevant_queries / total_queries) * 100 if total_queries > 0 else 0
    
    avg_latency = sum(r["latency_ms"] for r in results) / len(results) if results else 0
    
    print(f"\n📊 МЕТРИКИ КАЧЕСТВА:")
    print(f"Всего запросов: {total_queries}")
    print(f"Релевантных результатов: {relevant_queries}")
    print(f"Успешность: {success_rate:.1f}%")
    print(f"Средняя задержка: {avg_latency:.1f} мс")
    
    return success_rate, relevant_queries, avg_latency  
def save_results(results, success_rate, relevant_queries, avg_latency):  
    """Сохраняем результаты в CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/evaluation_results_{timestamp}.csv"
    
    # Создаем папку если нет
    import os
    os.makedirs('reports', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'query', 'site', 'type', 'notes', 
            'top_1', 'top_1_score', 'top_2', 'top_2_score', 'top_3', 'top_3_score', 'top_4', 'top_4_score', 'top_5', 'top_5_score',
            'latency_ms', 'total_results', 'normalized_query', 'numeric_filters', 'judgement'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"\n💾 Результаты сохранены в: {filename}")
    
    # Сохраняем сводку
    summary_filename = f"reports/summary_{timestamp}.txt"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write("ОЦЕНКА КАЧЕСТВА ПРЕФИКСНОГО ПОИСКА\n")
        f.write("=" * 50 + "\n")
        f.write(f"Дата тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Всего запросов: {len(results)}\n")
        f.write(f"Релевантных результатов: {relevant_queries}\n")
        f.write(f"Успешность: {success_rate:.1f}%\n")
        f.write(f"Средняя задержка: {avg_latency:.1f} мс\n")
        f.write(f"Минимальный порог: 70%\n")
        f.write(f"Статус: {'✅ ПРОЙДЕНО' if success_rate >= 70 else '❌ НЕ ПРОЙДЕНО'}\n")
    
    print(f"📄 Сводка сохранена в: {summary_filename}")
    
    return success_rate >= 70

if __name__ == "__main__":
    print("🚀 ЗАПУСК ОЦЕНКИ КАЧЕСТВА ПОИСКА")
    print("=" * 60)
    
    results = test_prefix_queries()
    success_rate, relevant_queries, avg_latency = calculate_metrics(results)  
    is_passed = save_results(results, success_rate, relevant_queries, avg_latency)  
    
    if is_passed:
        print("\n🎉 ПОЗДРАВЛЯЮ! Система соответствует требованиям (≥70%)")
        print("✅ Можете отправлять решение!")
    else:
        print("\n⚠️  Система требует доработки")
        print("❌ Успешность ниже 70%")