"""
Шаг 1: Продвинутая валидация Pydantic

Цель: Изучить встроенные возможности валидации Pydantic

Ключевые концепции:
- Field с различными ограничениями
- Специальные типы данных (EmailStr, HttpUrl, UUID4)
- Constrained типы (conint, constr, confloat)
- Regex валидация
- Множественные ограничения
"""

import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI
from pydantic import (
    UUID4,
    BaseModel,
    EmailStr,
    Field,
    HttpUrl,
    confloat,
    conint,
    constr,
    validator,
)

app = FastAPI(
    title="Advanced Validation API",
    description="API с продвинутой валидацией данных",
    version="1.0.0",
)


# ========================================
# 1. Валидация строк
# ========================================


class Article(BaseModel):
    """Статья с валидацией строковых полей"""

    title: str = Field(
        ..., min_length=5, max_length=200, description="Заголовок статьи"
    )

    slug: constr(
        regex=r"^[a-z0-9-]+$", min_length=3, max_length=100
    ) = Field(  # type: ignore
        ..., description="URL-friendly идентификатор (только строчные буквы, цифры, дефисы)"
    )

    content: str = Field(..., min_length=50, max_length=10000)

    tags: List[constr(min_length=2, max_length=20)] = Field(  # type: ignore
        default_factory=list, max_items=10, description="Максимум 10 тегов"
    )

    author_email: EmailStr = Field(..., description="Email автора")

    source_url: Optional[HttpUrl] = Field(None, description="Ссылка на источник")

    class Config:
        schema_extra = {
            "example": {
                "title": "Введение в FastAPI",
                "slug": "intro-to-fastapi",
                "content": "FastAPI - это современный фреймворк для создания API..." * 5,
                "tags": ["python", "fastapi", "api"],
                "author_email": "author@example.com",
                "source_url": "https://fastapi.tiangolo.com",
            }
        }


@app.post("/articles/", summary="Создать статью")
def create_article(article: Article):
    """
    Создать новую статью с валидацией всех полей

    Валидация:
    - title: 5-200 символов
    - slug: только a-z, 0-9, дефисы
    - content: минимум 50 символов
    - tags: максимум 10, каждый 2-20 символов
    - author_email: валидный email
    - source_url: валидный URL
    """
    return {"message": "Статья создана", "article": article}


# ========================================
# 2. Валидация чисел
# ========================================


class Product(BaseModel):
    """Товар с числовой валидацией"""

    name: str = Field(..., min_length=3, max_length=100)

    # Цена: положительное число, максимум 2 знака после запятой
    price: confloat(gt=0, le=1000000) = Field(  # type: ignore
        ..., description="Цена в рублях"
    )

    # Количество: целое неотрицательное число
    quantity: conint(ge=0) = Field(  # type: ignore
        0, description="Количество на складе"
    )

    # Скидка: от 0 до 100 процентов
    discount: confloat(ge=0, le=100) = Field(  # type: ignore
        0, description="Процент скидки"
    )

    # Вес: положительное число
    weight_kg: Optional[confloat(gt=0)] = Field(  # type: ignore
        None, description="Вес в килограммах"
    )

    # Рейтинг: от 1 до 5
    rating: Optional[confloat(ge=1, le=5)] = Field(  # type: ignore
        None, description="Средний рейтинг"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Ноутбук Gaming Pro",
                "price": 75999.99,
                "quantity": 5,
                "discount": 10.5,
                "weight_kg": 2.5,
                "rating": 4.7,
            }
        }


@app.post("/products/")
def create_product(product: Product):
    """
    Создать товар с числовой валидацией

    Вычисляем цену со скидкой
    """
    final_price = product.price * (1 - product.discount / 100)

    return {
        "product": product,
        "final_price": round(final_price, 2),
        "in_stock": product.quantity > 0,
    }


# ========================================
# 3. Валидация дат и времени
# ========================================


class Event(BaseModel):
    """Событие с валидацией дат"""

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)

    start_date: datetime = Field(..., description="Дата и время начала")
    end_date: datetime = Field(..., description="Дата и время окончания")

    registration_deadline: Optional[datetime] = Field(
        None, description="Крайний срок регистрации"
    )

    max_participants: conint(gt=0, le=10000) = Field(  # type: ignore
        ..., description="Максимальное количество участников"
    )

    @validator("end_date")
    def end_after_start(cls, v, values):
        """Проверка, что событие заканчивается после начала"""
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("Дата окончания должна быть позже даты начала")
        return v

    @validator("registration_deadline")
    def deadline_before_start(cls, v, values):
        """Проверка, что регистрация заканчивается до начала события"""
        if v and "start_date" in values and v >= values["start_date"]:
            raise ValueError("Регистрация должна закончиться до начала события")
        return v

    class Config:
        schema_extra = {
            "example": {
                "title": "Python Workshop",
                "description": "Практический воркшоп по Python и FastAPI",
                "start_date": "2025-10-20T10:00:00",
                "end_date": "2025-10-20T18:00:00",
                "registration_deadline": "2025-10-19T23:59:59",
                "max_participants": 50,
            }
        }


@app.post("/events/")
def create_event(event: Event):
    """
    Создать событие с валидацией дат

    Проверки:
    - Событие заканчивается после начала
    - Регистрация до начала события
    """
    duration = event.end_date - event.start_date
    hours = duration.total_seconds() / 3600

    return {
        "event": event,
        "duration_hours": round(hours, 2),
        "message": "Событие создано",
    }


# ========================================
# 4. UUID и специальные форматы
# ========================================


class User(BaseModel):
    """Пользователь с UUID и специальными типами"""

    id: UUID4 = Field(..., description="Уникальный идентификатор")

    username: constr(  # type: ignore
        regex=r"^[a-zA-Z0-9_]{3,20}$", to_lower=True
    ) = Field(..., description="Имя пользователя")

    email: EmailStr

    website: Optional[HttpUrl] = None

    phone: Optional[constr(regex=r"^\+?[1-9]\d{10,14}$")] = Field(  # type: ignore
        None, description="Телефон в международном формате"
    )

    age: conint(ge=13, le=120) = Field(  # type: ignore
        ..., description="Возраст (от 13 до 120)"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "john_doe",
                "email": "john@example.com",
                "website": "https://johndoe.com",
                "phone": "+79991234567",
                "age": 25,
            }
        }


@app.post("/users/")
def create_user(user: User):
    """
    Создать пользователя с UUID и форматированием

    Валидация:
    - UUID4 формат для ID
    - Username: буквы, цифры, подчеркивание, 3-20 символов
    - Email: валидный формат
    - Website: валидный URL
    - Phone: международный формат
    """
    return {"message": "Пользователь создан", "user": user}


# ========================================
# 5. Комплексная валидация с вычислениями
# ========================================


class OrderItem(BaseModel):
    """Позиция в заказе"""

    product_id: int = Field(..., gt=0)
    quantity: conint(gt=0, le=1000) = Field(  # type: ignore
        ..., description="Количество (1-1000)"
    )
    price_per_unit: confloat(gt=0) = Field(  # type: ignore
        ..., description="Цена за единицу"
    )


class Order(BaseModel):
    """Заказ с комплексной валидацией"""

    order_id: UUID4
    customer_email: EmailStr

    items: List[OrderItem] = Field(..., min_items=1, max_items=100)

    promo_code: Optional[constr(regex=r"^[A-Z0-9]{4,10}$")] = Field(  # type: ignore
        None, description="Промокод (4-10 символов, заглавные буквы и цифры)"
    )

    shipping_cost: confloat(ge=0) = Field(  # type: ignore
        0, description="Стоимость доставки"
    )

    @validator("items")
    def validate_total_amount(cls, v):
        """Проверка общей суммы заказа"""
        total = sum(item.quantity * item.price_per_unit for item in v)
        if total > 1000000:
            raise ValueError("Общая сумма заказа не может превышать 1,000,000 руб")
        if total < 100:
            raise ValueError("Минимальная сумма заказа 100 руб")
        return v

    class Config:
        schema_extra = {
            "example": {
                "order_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer_email": "customer@example.com",
                "items": [
                    {"product_id": 1, "quantity": 2, "price_per_unit": 500.0},
                    {"product_id": 2, "quantity": 1, "price_per_unit": 1500.0},
                ],
                "promo_code": "SALE2025",
                "shipping_cost": 300.0,
            }
        }


@app.post("/orders/")
def create_order(order: Order):
    """
    Создать заказ с комплексной валидацией

    Вычисления:
    - Сумма товаров
    - Скидка по промокоду
    - Итоговая сумма
    """
    items_total = sum(item.quantity * item.price_per_unit for item in order.items)

    # Симуляция скидки по промокоду
    discount = 0.1 if order.promo_code else 0
    discount_amount = items_total * discount

    total = items_total - discount_amount + order.shipping_cost

    return {
        "order": order,
        "summary": {
            "items_total": round(items_total, 2),
            "discount": round(discount_amount, 2),
            "shipping": order.shipping_cost,
            "total": round(total, 2),
        },
    }


# ========================================
# Примеры использования
# ========================================

# Для запуска:
# uvicorn 5_advanced_validation:app --reload
#
# После запуска откройте: http://127.0.0.1:8000/docs
#
# Попробуйте отправить невалидные данные:
# - Слишком короткие/длинные строки
# - Отрицательные числа где нужны положительные
# - Неправильный формат email/URL
# - Неверные даты
# - Невалидный UUID
#
# Обратите внимание на подробные сообщения об ошибках валидации!
