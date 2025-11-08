
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from scripts.load_data import main as load_data_main
from api.search import router as search_router  
import threading
import time

app = FastAPI(
    title="Prefix Search API",
    description="API для префиксного поиска по каталогу товаров", 
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(search_router, prefix="/api/v1", tags=["search"])

@app.get("/")
async def root():
    return {"message": "Prefix Search API работает!", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def load_data_in_background():
    """Загружаем данные в фоновом режиме"""
    time.sleep(15)  
    try:
        load_data_main()
        print("✅ Данные успешно загружены в Elasticsearch!")
    except Exception as e:
        print(f"❌ Ошибка при загрузке данных: {e}")

@app.on_event("startup")
async def startup_event():
    """Запускаем загрузку данных при старте приложения"""
    print("🚀 Запускаем загрузку данных в фоновом режиме...")
    print("⏳ Ожидаем 10 секунд перед началом загрузки...")
    time.sleep(10)
    
    thread = threading.Thread(target=load_data_in_background)
    thread.daemon = True
    thread.start()
    
    # Проверяем статус через 30 секунд
    def check_status():
        time.sleep(30)
        try:
            es = Elasticsearch(["http://elasticsearch:9200"])
            if es.ping():
                count = es.count(index="products")['count']
                print(f"📊 Статус: Elasticsearch работает, товаров в индексе: {count}")
            else:
                print("❌ Elasticsearch не доступен")
        except Exception as e:
            print(f"❌ Ошибка проверки статуса: {e}")
    
    status_thread = threading.Thread(target=check_status)
    status_thread.daemon = True
    status_thread.start()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)