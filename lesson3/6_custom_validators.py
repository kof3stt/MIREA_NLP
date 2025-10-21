"""
Шаг 2: Кастомные валидаторы

Цель: Научиться создавать собственную логику валидации

Ключевые концепции:
- @validator декоратор
- Валидация с доступом к другим полям
- @root_validator для проверки всей модели
- pre и post валидаторы
- Модификация значений в валидаторах
"""

import re
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field, root_validator, validator

app = FastAPI(
    title="Custom Validators API",
    description="API с кастомными валидаторами",
    version="1.0.0",
)


# ========================================
# 1. Простые кастомные валидаторы
# ========================================


class Username(BaseModel):
    """Валидация username с кастомными правилами"""

    username: str = Field(..., min_length=3, max_length=20)

    @validator("username")
    def username_valid(cls, v):
        """
        Правила для username:
        - Только буквы, цифры и подчеркивание
        - Не может начинаться с цифры
        - Не может содержать два подчеркивания подряд
        """
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError("Username должен начинаться с буквы")

        if "__" in v:
            raise ValueError("Username не может содержать двойное подчеркивание")

        # Можно модифицировать значение - приведем к нижнему регистру
        return v.lower()


@app.post("/validate-username/")
def validate_username(data: Username):
    """Проверка username"""
    return {
        "username": data.username,
        "message": "Username валиден и преобразован к нижнему регистру",
    }


# ========================================
# 2. Валидация с доступом к другим полям
# ========================================


class PasswordReset(BaseModel):
    """Сброс пароля с проверкой совпадения"""

    email: EmailStr
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str

    @validator("new_password")
    def password_strength(cls, v):
        """
        Проверка сложности пароля:
        - Минимум одна заглавная буква
        - Минимум одна строчная буква
        - Минимум одна цифра
        - Минимум один спецсимвол
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")

        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")

        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Пароль должен содержать хотя бы один спецсимвол")

        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Проверка совпадения паролей"""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("Пароли не совпадают")
        return v


@app.post("/reset-password/")
def reset_password(data: PasswordReset):
    """Сброс пароля с валидацией"""
    return {
        "email": data.email,
        "message": "Пароль успешно сброшен",
    }


# ========================================
# 3. Root validator - валидация всей модели
# ========================================


class DateRange(BaseModel):
    """Диапазон дат с комплексной валидацией"""

    start_date: date
    end_date: date
    include_weekends: bool = True

    @root_validator
    def validate_date_range(cls, values):
        """Валидация диапазона дат"""
        start = values.get("start_date")
        end = values.get("end_date")

        if not start or not end:
            return values

        # Проверка, что начало раньше конца
        if start > end:
            raise ValueError("Дата начала должна быть раньше даты окончания")

        # Проверка, что диапазон не более 365 дней
        delta = end - start
        if delta.days > 365:
            raise ValueError("Диапазон не может превышать 365 дней")

        # Проверка, что даты не в прошлом
        today = date.today()
        if start < today:
            raise ValueError("Дата начала не может быть в прошлом")

        return values

    @validator("start_date", "end_date")
    def no_far_future(cls, v):
        """Не более 2 лет в будущем"""
        max_date = date.today() + timedelta(days=730)
        if v > max_date:
            raise ValueError("Дата не может быть более чем через 2 года")
        return v


@app.post("/bookings/date-range/")
def create_booking(data: DateRange):
    """Создать бронирование с валидацией дат"""
    days = (data.end_date - data.start_date).days + 1
    return {
        "start_date": data.start_date,
        "end_date": data.end_date,
        "total_days": days,
        "include_weekends": data.include_weekends,
    }


# ========================================
# 4. Pre и Post валидаторы
# ========================================


class PhoneNumber(BaseModel):
    """Телефон с нормализацией"""

    phone: str

    @validator("phone", pre=True)
    def normalize_phone(cls, v):
        """
        Pre-validator: выполняется ДО проверки типа
        Нормализуем телефон - удаляем все кроме цифр и +
        """
        if isinstance(v, str):
            # Удаляем пробелы, дефисы, скобки
            v = re.sub(r"[\s\-\(\)]", "", v)
        return v

    @validator("phone")
    def validate_phone(cls, v):
        """
        Post-validator: выполняется ПОСЛЕ проверки типа
        Проверяем формат телефона
        """
        # Российский номер: +7 и 10 цифр
        if not re.match(r"^\+7\d{10}$", v):
            raise ValueError(
                "Телефон должен быть в формате +7XXXXXXXXXX (российский номер)"
            )
        return v


@app.post("/contacts/")
def add_contact(data: PhoneNumber):
    """Добавить контакт с нормализацией телефона"""
    return {
        "phone": data.phone,
        "message": "Контакт добавлен",
    }


# ========================================
# 5. Валидация списков и вложенных структур
# ========================================


class CourseModule(BaseModel):
    """Модуль курса"""

    title: str = Field(..., min_length=3, max_length=100)
    duration_minutes: int = Field(..., gt=0, le=480)  # Максимум 8 часов
    order: int = Field(..., ge=1)

    @validator("title")
    def title_capitalized(cls, v):
        """Заголовок с заглавной буквы"""
        return v.strip().capitalize()


class Course(BaseModel):
    """Курс с валидацией модулей"""

    name: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=1000)
    modules: List[CourseModule] = Field(..., min_items=1, max_items=50)
    price: float = Field(..., gt=0)

    @validator("modules")
    def validate_modules(cls, v):
        """Валидация списка модулей"""
        if not v:
            raise ValueError("Курс должен содержать хотя бы один модуль")

        # Проверка уникальности порядковых номеров
        orders = [m.order for m in v]
        if len(orders) != len(set(orders)):
            raise ValueError("Порядковые номера модулей должны быть уникальными")

        # Проверка непрерывности нумерации
        orders_sorted = sorted(orders)
        expected = list(range(1, len(orders) + 1))
        if orders_sorted != expected:
            raise ValueError("Порядковые номера должны идти последовательно от 1")

        return v

    @root_validator
    def validate_course(cls, values):
        """Валидация всего курса"""
        modules = values.get("modules", [])
        price = values.get("price", 0)

        if modules:
            total_duration = sum(m.duration_minutes for m in modules)

            # Минимальная длительность курса - 1 час
            if total_duration < 60:
                raise ValueError("Общая длительность курса минимум 60 минут")

            # Проверка адекватности цены
            # Примерно: 100 руб за минуту
            suggested_price = total_duration * 100
            if price < suggested_price * 0.5:
                raise ValueError(
                    f"Цена слишком низкая для курса длительностью {total_duration} минут. "
                    f"Рекомендуемая минимальная цена: {suggested_price * 0.5} руб"
                )

        return values


@app.post("/courses/")
def create_course(course: Course):
    """
    Создать курс с валидацией модулей

    Проверки:
    - Минимум 1 модуль
    - Уникальные порядковые номера
    - Последовательная нумерация
    - Общая длительность минимум 60 минут
    - Адекватная цена
    """
    total_duration = sum(m.duration_minutes for m in course.modules)

    return {
        "course": course,
        "summary": {
            "total_modules": len(course.modules),
            "total_duration_minutes": total_duration,
            "total_duration_hours": round(total_duration / 60, 2),
            "price_per_minute": round(course.price / total_duration, 2),
        },
    }


# ========================================
# 6. Условная валидация
# ========================================


class ShippingMethod(str, Enum):
    """Методы доставки"""

    pickup = "pickup"  # Самовывоз
    courier = "courier"  # Курьер
    post = "post"  # Почта


class ShippingDetails(BaseModel):
    """Детали доставки с условной валидацией"""

    method: ShippingMethod

    # Обязательно для courier и post
    address: Optional[str] = Field(None, min_length=10, max_length=200)
    city: Optional[str] = Field(None, min_length=2, max_length=50)
    postal_code: Optional[str] = None

    # Обязательно для всех
    recipient_name: str = Field(..., min_length=2, max_length=100)
    recipient_phone: str

    @root_validator
    def validate_shipping(cls, values):
        """Условная валидация в зависимости от метода доставки"""
        method = values.get("method")
        address = values.get("address")
        city = values.get("city")
        postal_code = values.get("postal_code")

        # Для курьера и почты нужен адрес
        if method in [ShippingMethod.courier, ShippingMethod.post]:
            if not address:
                raise ValueError(f"Для метода {method} необходимо указать адрес")
            if not city:
                raise ValueError(f"Для метода {method} необходимо указать город")

        # Для почты обязателен индекс
        if method == ShippingMethod.post:
            if not postal_code:
                raise ValueError("Для почтовой доставки необходимо указать индекс")

            # Российский индекс - 6 цифр
            if not re.match(r"^\d{6}$", postal_code):
                raise ValueError("Индекс должен состоять из 6 цифр")

        return values

    @validator("recipient_phone")
    def validate_phone_format(cls, v):
        """Валидация телефона"""
        # Нормализуем
        phone = re.sub(r"[\s\-\(\)]", "", v)

        if not re.match(r"^\+7\d{10}$", phone):
            raise ValueError("Телефон в формате +7XXXXXXXXXX")

        return phone


@app.post("/shipping/")
def create_shipping(shipping: ShippingDetails):
    """
    Создать заявку на доставку

    Условная валидация:
    - Самовывоз: только имя и телефон
    - Курьер: + адрес и город
    - Почта: + индекс
    """
    return {
        "shipping": shipping,
        "message": f"Заявка на доставку методом {shipping.method} создана",
    }


# ========================================
# Примеры использования
# ========================================

# Для запуска:
# uvicorn 6_custom_validators:app --reload
#
# Примеры запросов через Swagger UI: http://127.0.0.1:8000/docs
#
# Попробуйте:
# 1. Username с цифрой в начале (ошибка)
# 2. Пароли не совпадают (ошибка)
# 3. Даты в неправильном порядке (ошибка)
# 4. Телефон в разных форматах (нормализация)
# 5. Курс с неправильной нумерацией модулей (ошибка)
# 6. Доставку курьером без адреса (ошибка)
