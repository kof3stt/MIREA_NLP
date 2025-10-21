"""
Шаг 3: Query параметры

Цель: Научиться работать с параметрами запроса (query parameters)

Ключевые концепции:
- Query параметры после ? в URL
- Значения по умолчанию
- Опциональные параметры
- Валидация query параметров
- Множественные значения
"""

from typing import List, Optional

from fastapi import FastAPI, Query

app = FastAPI(
    title="Query Parameters API",
    description="API для изучения query параметров",
    version="1.0.0"
)


# ========================================
# 1. Простые query параметры
# ========================================

@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    """
    Получить список товаров с пагинацией
    
    Args:
        skip: Сколько элементов пропустить (по умолчанию 0)
        limit: Максимальное количество элементов (по умолчанию 10)
    
    Example: /items/?skip=5&limit=20
    """
    return {
        "skip": skip,
        "limit": limit,
        "message": f"Показать {limit} товаров, начиная с {skip}"
    }


# ========================================
# 2. Опциональные параметры
# ========================================

@app.get("/search/")
def search(q: Optional[str] = None, category: Optional[str] = None):
    """
    Поиск товаров
    
    Args:
        q: Поисковый запрос (опционально)
        category: Фильтр по категории (опционально)
    
    Example: /search/?q=laptop&category=electronics
    """
    result = {"message": "Поиск"}
    
    if q:
        result["query"] = q
    if category:
        result["category"] = category
    
    if not q and not category:
        result["message"] = "Укажите параметры поиска"
    
    return result


# ========================================
# 3. Query параметры с валидацией
# ========================================

@app.get("/products/")
def get_products(
    price_min: float = Query(0, ge=0, description="Минимальная цена"),
    price_max: float = Query(100000, le=1000000, description="Максимальная цена"),
    name: str = Query(
        ...,  # ... означает обязательный параметр
        min_length=2,
        max_length=50,
        description="Название товара"
    )
):
    """
    Фильтр товаров по цене и названию
    
    Args:
        price_min: Минимальная цена (>= 0)
        price_max: Максимальная цена (<= 1000000)
        name: Название товара (обязательно, 2-50 символов)
    
    Example: /products/?name=laptop&price_min=500&price_max=2000
    """
    return {
        "name": name,
        "price_range": {
            "min": price_min,
            "max": price_max
        }
    }


# ========================================
# 4. Boolean параметры
# ========================================

@app.get("/users/")
def get_users(active: bool = True, verified: Optional[bool] = None):
    """
    Получить пользователей с фильтрами
    
    Args:
        active: Показать активных пользователей (по умолчанию True)
        verified: Фильтр по верификации (опционально)
    
    Boolean значения могут быть:
    - true, True, 1, yes, on
    - false, False, 0, no, off
    
    Example: /users/?active=true&verified=false
    """
    filters = {"active": active}
    if verified is not None:
        filters["verified"] = verified
    
    return {
        "filters": filters,
        "message": f"Пользователи с фильтрами: {filters}"
    }


# ========================================
# 5. Список значений (Multiple values)
# ========================================

@app.get("/filter/")
def filter_items(tags: Optional[List[str]] = Query(None)):
    """
    Фильтр по нескольким тегам
    
    Args:
        tags: Список тегов для фильтрации
    
    Example: /filter/?tags=electronics&tags=sale&tags=new
    """
    if tags is None:
        return {"message": "Теги не указаны"}
    
    return {
        "tags": tags,
        "count": len(tags),
        "message": f"Фильтр по тегам: {', '.join(tags)}"
    }


# ========================================
# 6. Комбинация path и query параметров
# ========================================

@app.get("/categories/{category_id}/products")
def get_category_products(
    category_id: int,
    skip: int = 0,
    limit: int = 10,
    sort: str = Query("name", regex="^(name|price|date)$")
):
    """
    Получить товары категории с пагинацией и сортировкой
    
    Args:
        category_id: ID категории (path параметр)
        skip: Пропустить элементов
        limit: Максимум элементов
        sort: Сортировка (name, price, или date)
    
    Example: /categories/5/products?skip=0&limit=20&sort=price
    """
    return {
        "category_id": category_id,
        "pagination": {
            "skip": skip,
            "limit": limit
        },
        "sort_by": sort
    }


# ========================================
# 7. Строковая валидация с regex
# ========================================

@app.get("/validate/")
def validate_query(
    email: str = Query(
        ...,
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Email адрес"
    )
):
    """
    Валидация email через regex
    
    Example: /validate/?email=user@example.com
    """
    return {
        "email": email,
        "message": "Email валиден"
    }


# ========================================
# Примеры использования
# ========================================

# Для запуска:
# uvicorn 3_query_params:app --reload
#
# Примеры запросов:
#
# 1. Пагинация:
#    curl "http://127.0.0.1:8000/items/"
#    curl "http://127.0.0.1:8000/items/?skip=10&limit=5"
#
# 2. Опциональные параметры:
#    curl "http://127.0.0.1:8000/search/"
#    curl "http://127.0.0.1:8000/search/?q=laptop"
#    curl "http://127.0.0.1:8000/search/?q=laptop&category=electronics"
#
# 3. С валидацией:
#    curl "http://127.0.0.1:8000/products/?name=laptop&price_min=500&price_max=2000"
#
# 4. Boolean:
#    curl "http://127.0.0.1:8000/users/?active=true&verified=false"
#
# 5. Множественные значения:
#    curl "http://127.0.0.1:8000/filter/?tags=new&tags=sale&tags=featured"
#
# 6. Комбинация path и query:
#    curl "http://127.0.0.1:8000/categories/5/products?skip=0&limit=20&sort=price"
#
# 7. Email валидация:
#    curl "http://127.0.0.1:8000/validate/?email=user@example.com"
