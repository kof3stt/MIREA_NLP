"""
Шаг 3: Обработка ошибок

Цель: Научиться правильно обрабатывать и возвращать ошибки

Ключевые концепции:
- HTTPException для стандартных HTTP ошибок
- Кастомные exception handlers
- Structured error responses
- Validation errors customization
- Error logging
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Error Handling API",
    description="API с правильной обработкой ошибок",
    version="1.0.0",
)


# ========================================
# Модели данных
# ========================================


class Item(BaseModel):
    """Модель товара"""

    id: Optional[int] = None
    name: str = Field(..., min_length=3, max_length=100)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)


# Простое хранилище
items_db: Dict[int, Item] = {
    1: Item(id=1, name="Ноутбук", price=50000, quantity=5),
    2: Item(id=2, name="Мышь", price=500, quantity=10),
    3: Item(id=3, name="Клавиатура", price=2000, quantity=0),
}
next_id = 4


# ========================================
# 1. Базовые HTTPException
# ========================================


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """
    Получить товар по ID

    Возвращает 404 если товар не найден
    """
    if item_id not in items_db:
        # Стандартная HTTP ошибка
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Товар с ID {item_id} не найден",
        )

    return items_db[item_id]


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """
    Удалить товар

    Возвращает 404 если товар не найден
    """
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден"
        )

    deleted_item = items_db.pop(item_id)
    logger.info(f"Товар {item_id} удален: {deleted_item.name}")

    return {"message": "Товар удален", "item": deleted_item}


# ========================================
# 2. HTTPException с дополнительными данными
# ========================================


@app.post("/items/{item_id}/purchase")
def purchase_item(item_id: int, quantity: int = Query(..., gt=0)):
    """
    Купить товар

    Проверяет наличие на складе
    """
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден"
        )

    item = items_db[item_id]

    if item.quantity == 0:
        # Ошибка с дополнительными данными
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Товар отсутствует на складе",
            headers={"X-Error-Code": "OUT_OF_STOCK"},
        )

    if item.quantity < quantity:
        # Ошибка с информацией о доступном количестве
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Недостаточное количество товара",
                "requested": quantity,
                "available": item.quantity,
                "item_name": item.name,
            },
        )

    # Выполняем покупку
    item.quantity -= quantity
    total = item.price * quantity

    logger.info(f"Продано {quantity} шт. товара {item.name}")

    return {
        "message": "Покупка совершена",
        "item": item.name,
        "quantity": quantity,
        "total_price": total,
        "remaining": item.quantity,
    }


# ========================================
# 3. Кастомные исключения
# ========================================


class ItemNotFoundError(Exception):
    """Товар не найден"""

    def __init__(self, item_id: int):
        self.item_id = item_id
        self.message = f"Товар с ID {item_id} не найден"


class InsufficientStockError(Exception):
    """Недостаточно товара на складе"""

    def __init__(self, item_name: str, requested: int, available: int):
        self.item_name = item_name
        self.requested = requested
        self.available = available
        self.message = f"Недостаточно товара '{item_name}': запрошено {requested}, доступно {available}"


class InvalidPriceError(Exception):
    """Некорректная цена"""

    def __init__(self, price: float, reason: str):
        self.price = price
        self.reason = reason
        self.message = f"Некорректная цена {price}: {reason}"


# ========================================
# 4. Exception Handlers
# ========================================


@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    """Обработчик для ItemNotFoundError"""
    logger.warning(f"ItemNotFoundError: {exc.message}")

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "ITEM_NOT_FOUND",
            "message": exc.message,
            "item_id": exc.item_id,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(InsufficientStockError)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockError):
    """Обработчик для InsufficientStockError"""
    logger.warning(f"InsufficientStockError: {exc.message}")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "INSUFFICIENT_STOCK",
            "message": exc.message,
            "details": {
                "item_name": exc.item_name,
                "requested": exc.requested,
                "available": exc.available,
            },
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(InvalidPriceError)
async def invalid_price_handler(request: Request, exc: InvalidPriceError):
    """Обработчик для InvalidPriceError"""
    logger.error(f"InvalidPriceError: {exc.message}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "INVALID_PRICE",
            "message": exc.message,
            "price": exc.price,
            "reason": exc.reason,
            "timestamp": datetime.now().isoformat(),
        },
    )


# ========================================
# 5. Использование кастомных исключений
# ========================================


@app.post("/items/")
def create_item(item: Item):
    """
    Создать новый товар

    Использует кастомные исключения
    """
    global next_id

    # Валидация цены
    if item.price > 1000000:
        raise InvalidPriceError(item.price, "Цена превышает максимально допустимую")

    if item.price < 10:
        raise InvalidPriceError(item.price, "Цена слишком низкая")

    # Создаем товар
    item.id = next_id
    items_db[next_id] = item
    next_id += 1

    logger.info(f"Создан товар {item.id}: {item.name}")

    return {"message": "Товар создан", "item": item}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    """
    Обновить товар

    Использует кастомные исключения
    """
    if item_id not in items_db:
        raise ItemNotFoundError(item_id)

    # Валидация цены
    if item.price > 1000000:
        raise InvalidPriceError(item.price, "Цена превышает максимально допустимую")

    item.id = item_id
    items_db[item_id] = item

    logger.info(f"Обновлен товар {item_id}: {item.name}")

    return {"message": "Товар обновлен", "item": item}


@app.post("/items/{item_id}/reserve")
def reserve_item(item_id: int, quantity: int):
    """
    Зарезервировать товар

    Использует кастомные исключения
    """
    if item_id not in items_db:
        raise ItemNotFoundError(item_id)

    item = items_db[item_id]

    if item.quantity < quantity:
        raise InsufficientStockError(item.name, quantity, item.quantity)

    # Резервируем
    item.quantity -= quantity

    logger.info(f"Зарезервировано {quantity} шт. товара {item.name}")

    return {
        "message": "Товар зарезервирован",
        "item": item.name,
        "reserved": quantity,
        "remaining": item.quantity,
    }


# ========================================
# 6. Кастомизация Validation Errors
# ========================================


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Кастомный обработчик ошибок валидации

    Форматирует ошибки валидации в более удобный вид
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": " -> ".join(str(x) for x in error["loc"][1:]),  # Путь к полю
                "message": error["msg"],
                "type": error["type"],
                "value": error.get("input"),
            }
        )

    logger.warning(f"Validation error: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Ошибка валидации данных",
            "details": errors,
            "timestamp": datetime.now().isoformat(),
        },
    )


# ========================================
# 7. Общий exception handler
# ========================================


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Обработчик для всех необработанных исключений

    Логирует ошибку и возвращает общее сообщение
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Произошла внутренняя ошибка сервера",
            "timestamp": datetime.now().isoformat(),
            # В продакшене не показываем детали ошибки
            # "details": str(exc)
        },
    )


# ========================================
# 8. Эндпоинт для тестирования ошибок
# ========================================


@app.get("/errors/test/{error_type}")
def test_error(error_type: str):
    """
    Тестирование различных типов ошибок

    Параметры:
    - 404: Not Found
    - 400: Bad Request
    - 500: Internal Server Error
    - validation: Validation Error
    - custom: Custom Exception
    """
    if error_type == "404":
        raise HTTPException(status_code=404, detail="Тестовая ошибка 404")

    elif error_type == "400":
        raise HTTPException(status_code=400, detail="Тестовая ошибка 400")

    elif error_type == "500":
        raise HTTPException(status_code=500, detail="Тестовая ошибка 500")

    elif error_type == "custom":
        raise ItemNotFoundError(999)

    elif error_type == "exception":
        # Вызовет общий exception handler
        raise RuntimeError("Неожиданная ошибка!")

    return {"message": f"Тип ошибки '{error_type}' не распознан"}


# ========================================
# 9. Health Check с обработкой ошибок
# ========================================


@app.get("/health")
def health_check():
    """
    Проверка состояния API

    Возвращает информацию о работоспособности
    """
    try:
        # Проверяем доступность БД (в нашем случае - словаря)
        db_status = "ok" if items_db is not None else "error"

        # Проверяем количество товаров
        items_count = len(items_db)

        return {
            "status": "healthy",
            "database": db_status,
            "items_count": items_count,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис временно недоступен",
        )


# ========================================
# Примеры использования
# ========================================

# Для запуска:
# uvicorn 7_error_handling:app --reload
#
# Swagger UI: http://127.0.0.1:8000/docs
#
# Примеры запросов:
#
# 1. Получить несуществующий товар:
#    GET /items/999 -> 404 с кастомным сообщением
#
# 2. Купить больше чем есть:
#    POST /items/3/purchase?quantity=100 -> 400 с деталями
#
# 3. Создать товар с невалидной ценой:
#    POST /items/ с price=-100 -> 422 validation error
#
# 4. Зарезервировать несуществующий товар:
#    POST /items/999/reserve?quantity=1 -> кастомная ошибка
#
# 5. Тесты ошибок:
#    GET /errors/test/404
#    GET /errors/test/custom
#    GET /errors/test/exception
#
# Обратите внимание на:
# - Структурированные ответы об ошибках
# - Логирование ошибок
# - Различные HTTP статус коды
# - Дополнительные данные в ошибках
