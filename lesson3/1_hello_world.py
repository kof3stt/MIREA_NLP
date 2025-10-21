"""
Шаг 1: Hello World - Первое FastAPI приложение

Цель: Создать простейшее API приложение и понять базовую структуру

Ключевые концепции:
- Создание FastAPI приложения
- Декораторы для определения эндпоинтов
- Возврат JSON ответов
- Автоматическая документация
"""

from fastapi import FastAPI

# Создание экземпляра приложения FastAPI
app = FastAPI(
    title="Hello World API",
    description="Первое FastAPI приложение",
    version="1.0.0"
)


# Корневой эндпоинт
@app.get("/")
def read_root():
    """
    Главная страница API
    
    Возвращает приветственное сообщение
    """
    return {"message": "Hello World"}


@app.get("/hello/{name}")
def greet_user(name: str):
    """
    Персональное приветствие
    
    Args:
        name: Имя пользователя из пути URL
        
    Returns:
        Персонализированное приветствие
    """
    return {"message": f"Привет, {name}!"}


@app.get("/info")
def get_info():
    """
    Информация о приложении
    
    Возвращает метаинформацию о API
    """
    return {
        "app_name": "Hello World API",
        "version": "1.0.0",
        "framework": "FastAPI",
        "python_version": "3.7+"
    }


# Для запуска:
# uvicorn 1_hello_world:app --reload
#
# После запуска:
# - API доступен по адресу: http://127.0.0.1:8000
# - Swagger UI документация: http://127.0.0.1:8000/docs
# - ReDoc документация: http://127.0.0.1:8000/redoc
# - OpenAPI схема (JSON): http://127.0.0.1:8000/openapi.json
#
# Примеры запросов:
# curl http://127.0.0.1:8000/
# curl http://127.0.0.1:8000/hello/Иван
# curl http://127.0.0.1:8000/info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")