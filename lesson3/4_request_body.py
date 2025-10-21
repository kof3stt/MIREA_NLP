"""
Шаг 4: Request Body и Pydantic модели

Цель: Научиться принимать и валидировать JSON данные

Ключевые концепции:
- Pydantic модели для структурирования данных
- POST запросы с телом
- Автоматическая валидация
- Вложенные модели
- Дополнительная валидация полей
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from fastapi import Body, FastAPI
from pydantic import BaseModel, EmailStr, Field, validator

app = FastAPI(
    title="Request Body API",
    description="API для изучения Request Body и Pydantic",
    version="1.0.0"
)


# ========================================
# 1. Простая Pydantic модель
# ========================================

class User(BaseModel):
    """Модель пользователя"""
    name: str
    email: str
    age: int


@app.post("/users/")
def create_user(user: User):
    """
    Создать нового пользователя
    
    Args:
        user: Данные пользователя в теле запроса
    
    Body:
    {
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "age": 25
    }
    """
    return {
        "message": "Пользователь создан",
        "user": user,
        "created_at": datetime.now()
    }


# ========================================
# 2. Модель с валидацией и значениями по умолчанию
# ========================================

class Product(BaseModel):
    """Модель товара с валидацией"""
    name: str = Field(..., min_length=3, max_length=50, description="Название товара")
    description: Optional[str] = Field(None, max_length=500, description="Описание товара")
    price: float = Field(..., gt=0, description="Цена должна быть больше 0")
    tax: Optional[float] = Field(None, ge=0, le=100, description="Налог от 0 до 100%")
    in_stock: bool = Field(True, description="Наличие на складе")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Ноутбук",
                "description": "Игровой ноутбук",
                "price": 50000.0,
                "tax": 20.0,
                "in_stock": True
            }
        }


@app.post("/products/")
def create_product(product: Product):
    """
    Создать новый товар
    
    Поля с валидацией:
    - name: 3-50 символов
    - price: больше 0
    - tax: от 0 до 100
    """
    total_price = product.price
    if product.tax:
        total_price += product.price * (product.tax / 100)
    
    return {
        "product": product,
        "total_price": total_price,
        "message": "Товар создан"
    }


# ========================================
# 3. Вложенные модели
# ========================================

class Address(BaseModel):
    """Модель адреса"""
    street: str
    city: str
    country: str
    postal_code: str


class Customer(BaseModel):
    """Модель клиента с адресом"""
    name: str
    email: EmailStr  # Требует установки: pip install pydantic[email]
    phone: Optional[str] = None
    address: Address
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Петр Петров",
                "email": "petr@example.com",
                "phone": "+7 999 123-45-67",
                "address": {
                    "street": "ул. Ленина, 10",
                    "city": "Москва",
                    "country": "Россия",
                    "postal_code": "123456"
                }
            }
        }


@app.post("/customers/")
def create_customer(customer: Customer):
    """
    Создать клиента с адресом
    
    Вложенная модель Address включена в Customer
    """
    return {
        "customer": customer,
        "message": f"Клиент {customer.name} из {customer.address.city} создан"
    }


# ========================================
# 4. Списки и перечисления
# ========================================

class OrderStatus(str, Enum):
    """Статусы заказа"""
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderItem(BaseModel):
    """Элемент заказа"""
    product_id: int
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)


class Order(BaseModel):
    """Модель заказа"""
    customer_id: int
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.pending
    notes: Optional[str] = None
    
    @validator('items')
    def items_not_empty(cls, v):
        """Проверка, что список товаров не пустой"""
        if not v:
            raise ValueError('Заказ должен содержать хотя бы один товар')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "customer_id": 1,
                "items": [
                    {"product_id": 1, "quantity": 2, "price": 100.0},
                    {"product_id": 2, "quantity": 1, "price": 250.0}
                ],
                "status": "pending",
                "notes": "Доставка до двери"
            }
        }


@app.post("/orders/")
def create_order(order: Order):
    """
    Создать новый заказ
    
    Заказ содержит список товаров и статус
    """
    total = sum(item.quantity * item.price for item in order.items)
    
    return {
        "order": order,
        "total_amount": total,
        "items_count": len(order.items),
        "message": "Заказ создан"
    }


# ========================================
# 5. Комбинация Path, Query и Body
# ========================================

class Review(BaseModel):
    """Модель отзыва"""
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: str = Field(..., min_length=10, max_length=500)
    recommend: bool = True


@app.post("/products/{product_id}/reviews")
def create_review(
    product_id: int,
    review: Review,
    user_id: int = Body(..., embed=True)
):
    """
    Создать отзыв на товар
    
    Комбинирует:
    - Path параметр: product_id
    - Body: review (модель Review)
    - Body: user_id (встроенное поле)
    
    Body:
    {
        "review": {
            "rating": 5,
            "comment": "Отличный товар!",
            "recommend": true
        },
        "user_id": 123
    }
    """
    return {
        "product_id": product_id,
        "user_id": user_id,
        "review": review,
        "message": "Отзыв добавлен"
    }


# ========================================
# 6. Кастомная валидация
# ========================================

class Registration(BaseModel):
    """Модель регистрации с кастомной валидацией"""
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8)
    password_confirm: str
    email: EmailStr
    age: int = Field(..., ge=18, le=120)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Имя пользователя должно быть буквенно-цифровым"""
        if not v.isalnum():
            raise ValueError('Username должен содержать только буквы и цифры')
        return v
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        """Проверка совпадения паролей"""
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        """Проверка сложности пароля"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(char.isupper() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        return v


@app.post("/register/")
def register_user(registration: Registration):
    """
    Регистрация пользователя с валидацией
    
    Валидируются:
    - Формат username (только буквы и цифры)
    - Сложность пароля (цифры, заглавные буквы)
    - Совпадение паролей
    - Формат email
    - Возраст >= 18
    """
    return {
        "message": "Регистрация успешна",
        "username": registration.username,
        "email": registration.email
    }


# ========================================
# Примеры использования
# ========================================

# Для запуска:
# uvicorn 4_request_body:app --reload
#
# Установка дополнительных зависимостей для email валидации:
# pip install pydantic[email]
#
# Примеры запросов с curl:
#
# 1. Создать пользователя:
# curl -X POST "http://127.0.0.1:8000/users/" \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Иван", "email": "ivan@test.com", "age": 25}'
#
# 2. Создать товар:
# curl -X POST "http://127.0.0.1:8000/products/" \
#   -H "Content-Type: application/json" \
#   -d '{"name": "Ноутбук", "price": 50000, "tax": 20, "in_stock": true}'
#
# 3. Создать заказ:
# curl -X POST "http://127.0.0.1:8000/orders/" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "customer_id": 1,
#     "items": [
#       {"product_id": 1, "quantity": 2, "price": 100},
#       {"product_id": 2, "quantity": 1, "price": 250}
#     ],
#     "status": "pending"
#   }'
#
# Лучше использовать Swagger UI: http://127.0.0.1:8000/docs
