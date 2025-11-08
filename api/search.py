from fastapi import APIRouter, Query, HTTPException
from elasticsearch import Elasticsearch
import json

router = APIRouter()

# Подключаемся к Elasticsearch
es = Elasticsearch(["http://elasticsearch:9200"])

@router.get("/search")
async def search_products(
    q: str = Query(..., description="Поисковый запрос"),
    size: int = Query(10, description="Количество результатов")
):
    """
    Простой поиск товаров - сначала сделаем рабочую версию
    """
    try:
        print(f"🔍 Получен запрос: '{q}'")
        
        # Простая нормализация
        normalized_query = q.lower().strip()
        
        # Простой поисковый запрос
        search_body = {
            "query": {
                "multi_match": {
                    "query": normalized_query,
                    "fields": ["name", "brand", "category", "keywords"],
                    "type": "best_fields"
                }
            },
            "size": size
        }
        
        print(f"🔍 Выполняем поиск: '{normalized_query}'")
        
        # Выполняем поиск
        response = es.search(index="products", body=search_body)
        
        # Форматируем результаты
        results = []
        for hit in response['hits']['hits']:
            product = hit['_source']
            product['score'] = hit['_score']
            results.append(product)
        
        print(f"🔍 Найдено результатов: {len(results)}")
        
        return {
            "query": q,
            "normalized_query": normalized_query,
            "numeric_filters": {},
            "total": response['hits']['total']['value'],
            "results": results
        }
        
    except Exception as e:
        print(f"❌ Ошибка поиска: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")