import os

print("Проверяем наличие данных...")
data_files = os.listdir('data')
print(f"Файлы в папке data: {data_files}")

if 'catalog_products.xml' in data_files:
    print("✅ catalog_products.xml найден")
else:
    print("❌ catalog_products.xml не найден!")
    
if 'prefix_queries.csv' in data_files:
    print("✅ prefix_queries.csv найден")  
else:
    print("❌ prefix_queries.csv не найден!")