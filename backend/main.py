"""
Главный модуль ИИ-консультанта BBKinvest.
"""
import os
import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Добавляем путь к проекту для корректных импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем API endpoints
from backend.api.endpoints import router as chat_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BBKinvest AI Consultant API",
    description="API для ИИ-консультанта сайта BBKinvest",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем маршруты
app.include_router(chat_router)

@app.get("/")
async def root():
    """Проверка работоспособности API."""
    return {
        "status": "ok",
        "service": "BBKinvest AI Consultant",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/v1/chat (POST)",
            "quick_start": "/api/v1/chat/quick-start (POST)",
            "health": "/health (GET)"
        }
    }

@app.get("/health")
async def health_check():
    """Эндпоинт для проверки здоровья сервиса."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )