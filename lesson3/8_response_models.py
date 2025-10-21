"""
Шаг 4: Response Models и HTTP статус коды

Цель: Научиться правильно формировать ответы API

Ключевые концепции:
- response_model для определения структуры ответа
- Исключение полей из ответа (пароли, внутренние данные)
- Различные модели для запроса и ответа
- HTTP статус коды
- Response model validation
- Множественные response models
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, Response, status
from pydantic import BaseModel, EmailStr, Field, SecretStr

app = FastAPI(
    title="Response Models API",
    description="API с правильными моделями ответов",
    version="1.0.0",
)


# ========================================
# 1. Базовые Response Models
# ========================================


class UserCreate(BaseModel):
    """Модель для создания пользователя (с паролем)"""

    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """Модель для ответа (БЕЗ пароля)"""

    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool = True

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "created_at": "2025-10-15T10:00:00",
                "is_active": True,
            }
        }


# Простое хранилище
users_db = {}
user_id_counter = 0


@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """
    Создать пользователя

    Принимает UserCreate (с паролем)
    Возвращает UserResponse (без пароля)
    Статус код: 201 Created
    """
    global user_id_counter
    user_id_counter += 1

    # Создаем пользователя (в реальности пароль нужно хешировать)
    user_data = {
        "id": user_id_counter,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "password_hash": f"hashed_{user.password}",  # НЕ возвращается
        "created_at": datetime.now(),
        "is_active": True,
    }

    users_db[user_id_counter] = user_data

    # response_model автоматически исключит password_hash
    return user_data


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """
    Получить пользователя

    Возвращает UserResponse (без пароля)
    """
    if user_id not in users_db:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return users_db[user_id]


# ========================================
# 2. Response Model с исключением полей
# ========================================


class ProductFull(BaseModel):
    """Полная модель товара (с внутренними данными)"""

    id: int
    name: str
    price: float
    cost: float  # Себестоимость - внутренние данные
    quantity: int
    supplier_id: int  # Внутренние данные
    is_active: bool


class ProductPublic(BaseModel):
    """Публичная модель товара (для клиентов)"""

    id: int
    name: str
    price: float
    in_stock: bool

    class Config:
        schema_extra = {
            "example": {"id": 1, "name": "Ноутбук", "price": 50000.0, "in_stock": True}
        }


products_db = {
    1: ProductFull(
        id=1,
        name="Ноутбук",
        price=50000,
        cost=35000,
        quantity=5,
        supplier_id=101,
        is_active=True,
    )
}


@app.get("/products/{product_id}", response_model=ProductPublic)
def get_product_public(product_id: int):
    """
    Получить товар (публичная информация)

    Скрывает cost, supplier_id, quantity
    Показывает только то, что нужно клиенту
    """
    if product_id not in products_db:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Товар не найден")

    product = products_db[product_id]

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "in_stock": product.quantity > 0,
    }


@app.get("/admin/products/{product_id}", response_model=ProductFull)
def get_product_admin(product_id: int):
    """
    Получить товар (полная информация для админа)

    Показывает все данные включая себестоимость
    """
    if product_id not in products_db:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Товар не найден")

    return products_db[product_id]


# ========================================
# 3. Списки в Response Models
# ========================================


@app.get("/users/", response_model=List[UserResponse])
def get_all_users():
    """
    Получить всех пользователей

    Возвращает список UserResponse
    """
    return list(users_db.values())


@app.get("/products/", response_model=List[ProductPublic])
def get_all_products():
    """
    Получить все товары

    Возвращает публичную информацию
    """
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "in_stock": p.quantity > 0,
        }
        for p in products_db.values()
    ]


# ========================================
# 4. Различные статус коды
# ========================================


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """
    Удалить пользователя

    Статус код: 204 No Content (без тела ответа)
    """
    if user_id not in users_db:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Пользователь не найден")

    users_db.pop(user_id)
    # Для 204 не возвращаем ничего
    return Response(status_code=status.HTTP_204_NO_CONTENT)


class ItemUpdate(BaseModel):
    """Модель для обновления товара"""

    name: Optional[str] = None
    price: Optional[float] = None


@app.patch("/products/{product_id}", response_model=ProductPublic)
def update_product(product_id: int, update: ItemUpdate):
    """
    Частично обновить товар

    Метод: PATCH (частичное обновление)
    Статус: 200 OK
    """
    if product_id not in products_db:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Товар не найден")

    product = products_db[product_id]

    if update.name is not None:
        product.name = update.name
    if update.price is not None:
        product.price = update.price

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "in_stock": product.quantity > 0,
    }


# ========================================
# 5. Обёрнутые ответы (Wrapper Responses)
# ========================================


class ResponseWrapper(BaseModel):
    """Обёртка для стандартизированных ответов"""

    success: bool
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)


@app.post("/users/{user_id}/activate", response_model=ResponseWrapper)
def activate_user(user_id: int):
    """
    Активировать пользователя

    Возвращает обёрнутый ответ
    """
    if user_id not in users_db:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user = users_db[user_id]
    user["is_active"] = True

    return {
        "success": True,
        "message": "Пользователь активирован",
        "data": {"user_id": user_id, "username": user["username"]},
    }


# ========================================
# 6. Условные Response Models
# ========================================


class OrderStatus(str, Enum):
    """Статусы заказа"""

    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"


class OrderBase(BaseModel):
    """Базовая информация о заказе"""

    id: int
    status: OrderStatus
    total: float
    created_at: datetime


class OrderWithDetails(OrderBase):
    """Заказ с деталями (для владельца)"""

    items: List[dict]
    customer_email: EmailStr
    shipping_address: str


orders_db = {
    1: {
        "id": 1,
        "status": OrderStatus.paid,
        "total": 5000,
        "created_at": datetime.now(),
        "items": [{"product_id": 1, "quantity": 1}],
        "customer_email": "customer@example.com",
        "shipping_address": "ул. Примерная, 123",
    }
}


@app.get(
    "/orders/{order_id}",
    response_model=OrderBase,
    responses={
        200: {
            "description": "Базовая информация о заказе",
            "model": OrderBase,
        }
    },
)
def get_order_basic(order_id: int):
    """
    Получить заказ (базовая информация)

    Для посторонних - только основная информация
    """
    if order_id not in orders_db:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Заказ не найден")

    return orders_db[order_id]


@app.get(
    "/my-orders/{order_id}",
    response_model=OrderWithDetails,
    responses={
        200: {
            "description": "Полная информация о заказе",
            "model": OrderWithDetails,
        }
    },
)
def get_my_order(order_id: int):
    """
    Получить свой заказ (полная информация)

    Для владельца - вся информация
    """
    if order_id not in orders_db:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Заказ не найден")

    return orders_db[order_id]


# ========================================
# 7. Response с вычисляемыми полями
# ========================================


class Statistics(BaseModel):
    """Статистика с вычисляемыми полями"""

    total_users: int
    active_users: int
    total_products: int
    available_products: int
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "total_users": 100,
                "active_users": 85,
                "total_products": 50,
                "available_products": 45,
                "timestamp": "2025-10-15T10:00:00",
            }
        }


@app.get("/statistics/", response_model=Statistics)
def get_statistics():
    """
    Получить статистику

    Вычисляет данные на лету
    """
    total_users = len(users_db)
    active_users = sum(1 for u in users_db.values() if u.get("is_active", False))

    total_products = len(products_db)
    available_products = sum(1 for p in products_db.values() if p.quantity > 0)

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_products": total_products,
        "available_products": available_products,
    }


# ========================================
# Примеры использования
# ========================================

# Для запуска:
# uvicorn 8_response_models:app --reload
#
# Swagger UI: http://127.0.0.1:8000/docs
#
# Примеры:
#
# 1. Создать пользователя (с паролем):
#    POST /users/
#    {
#      "username": "john_doe",
#      "email": "john@example.com",
#      "password": "SecurePass123",
#      "full_name": "John Doe"
#    }
#    Ответ НЕ содержит password!
#
# 2. Получить товар (публичный vs админ):
#    GET /products/1 - только публичная информация
#    GET /admin/products/1 - вся информация
#
# 3. Удалить пользователя:
#    DELETE /users/1 - возвращает 204 без тела
#
# 4. Получить статистику:
#    GET /statistics/ - вычисляемые поля
#
# Обратите внимание на:
# - Различные модели для запроса и ответа
# - Автоматическое исключение полей
# - Правильные статус коды
# - Структурированные ответы
