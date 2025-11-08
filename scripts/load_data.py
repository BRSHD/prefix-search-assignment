import xml.etree.ElementTree as ET
import json
from elasticsearch import Elasticsearch
import time
import os

def parse_xml_to_json(xml_file_path):
    """Парсим XML в JSON формат"""
    print(f"📁 Читаем файл: {xml_file_path}")
    
    # Проверяем что файл существует
    if not os.path.exists(xml_file_path):
        print(f"❌ Файл не найден: {xml_file_path}")
        # Пробуем альтернативные пути
        alternative_paths = [
            "./data/catalog_products.xml",
            "catalog_products.xml",
            "/app/data/catalog_products.xml"
        ]
        for path in alternative_paths:
            if os.path.exists(path):
                xml_file_path = path
                print(f"✅ Найден файл по пути: {path}")
                break
        else:
            raise FileNotFoundError("Не удалось найти catalog_products.xml")
    
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    products = []
    
    for product in root.findall('product'):
        product_data = {
            'id': product.find('id').text if product.find('id') is not None else '',
            'name': product.find('name').text if product.find('name') is not None else '',
            'category': product.find('category').text if product.find('category') is not None else '',
            'brand': product.find('brand').text if product.find('brand') is not None else '',
            'weight': product.find('weight').text if product.find('weight') is not None else '',
            'package_size': product.find('package_size').text if product.find('package_size') is not None else '',
            'keywords': product.find('keywords').text if product.find('keywords') is not None else '',
            'description': product.find('description').text if product.find('description') is not None else '',
            'price': product.find('price').text if product.find('price') is not None else '',
            'image_url': product.find('image_url').text if product.find('image_url') is not None else ''
        }
        products.append(product_data)
    
    print(f"📊 Прочитано {len(products)} товаров")
    return products

def create_index(es_client, index_name="products"):
    """Создаем простой индекс"""
    
    # Удаляем индекс если существует
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
        print(f"🗑️ Удален старый индекс {index_name}")
    
    # ПРОСТАЯ схема - главное чтобы работало
    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "name": {"type": "text"},
                "category": {"type": "text"},
                "brand": {"type": "text"},
                "weight": {"type": "text"},
                "package_size": {"type": "text"},
                "keywords": {"type": "text"},
                "description": {"type": "text"},
                "price": {"type": "float"},
                "image_url": {"type": "keyword"}
            }
        }
    }
    
    es_client.indices.create(index=index_name, body=mapping)
    print(f"✅ Индекс {index_name} создан успешно!")

def load_data_to_elasticsearch(products, es_client, index_name="products"):
    """Загружаем данные в Elasticsearch"""
    print(f"📤 Загружаем {len(products)} товаров в Elasticsearch...")
    
    success_count = 0
    for i, product in enumerate(products):
        try:
            # Конвертируем price в float
            try:
                product['price'] = float(product['price']) if product['price'] else 0.0
            except (ValueError, TypeError):
                product['price'] = 0.0
                
            es_client.index(index=index_name, id=product['id'], document=product)
            success_count += 1
            
            if (i + 1) % 100 == 0:
                print(f"📦 Загружено {i + 1} продуктов...")
                
        except Exception as e:
            print(f"⚠️ Ошибка при загрузке продукта {product['id']}: {e}")
    
    # Обновляем индекс
    es_client.indices.refresh(index=index_name)
    print(f"🎉 Успешно загружено {success_count}/{len(products)} продуктов")

def main():
    print("🚀 НАЧИНАЕМ ЗАГРУЗКУ ДАННЫХ")
    print("=" * 50)
    
    # Ждем пока Elasticsearch запустится
    print("⏳ Ожидаем запуск Elasticsearch...")
    time.sleep(30)
    
    # Подключаемся к Elasticsearch
    print("🔗 Подключаемся к Elasticsearch...")
    es = Elasticsearch(
        ["http://elasticsearch:9200"],
        request_timeout=30,
        max_retries=5,
        retry_on_timeout=True
    )
    
    try:
        # Проверяем подключение
        if not es.ping():
            raise ValueError("Не удалось подключиться к Elasticsearch")
        
        print("✅ Подключение к Elasticsearch установлено!")
        
        # Парсим XML
        products = parse_xml_to_json("/app/data/catalog_products.xml")
        
        # Создаем индекс
        create_index(es)
        
        # Загружаем данные
        load_data_to_elasticsearch(products, es)
        
        print("🎉 ЗАГРУЗКА ДАННЫХ ЗАВЕРШЕНА УСПЕШНО!")
        
        # Проверяем что данные загрузились
        count = es.count(index="products")['count']
        print(f"🔍 В индексе сейчас: {count} товаров")
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()