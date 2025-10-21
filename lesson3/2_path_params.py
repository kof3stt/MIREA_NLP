"""
Шаг 2: Path параметры

Цель: Научиться работать с динамическими путями в URL

Ключевые концепции:
- Path параметры в фигурных скобках {param}
- Типизация параметров
- Автоматическая валидация
- Работа с разными типами данных
"""

from enum import Enum

from fastapi import FastAPI, Path

app = FastAPI(
    title="Path Parameters API",
    description="API для изучения path параметров",
    version="1.0.0"
)


# ========================================
# 1. Простые path параметры
# ========================================

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """
    Получить пользователя по ID
    
    Args:
        user_id: ID пользователя (автоматически преобразуется в int)
    """
    return {
        "user_id": user_id,
        "message": f"Информация о пользователе {user_id}"
    }


@app.get("/items/{item_name}")
def get_item(item_name: str):
    """
    Получить товар по названию
    
    Args:
        item_name: Название товара
    """
    return {
        "item_name": item_name,
        "message": f"Информация о товаре: {item_name}"
    }


# ========================================
# 2. Несколько path параметров
# ========================================

@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    """
    Получить конкретный пост пользователя
    
    Args:
        user_id: ID пользователя
        post_id: ID поста
    """
    return {
        "user_id": user_id,
        "post_id": post_id,
        "message": f"Пост {post_id} пользователя {user_id}"
    }


# ========================================
# 3. Path параметры с дополнительной валидацией
# ========================================

@app.get("/products/{product_id}")
def get_product(
    product_id: int = Path(
        ..., 
        title="Product ID",
        description="Уникальный идентификатор товара",
        ge=1,  # greater than or equal - больше или равно
        le=1000  # less than or equal - меньше или равно
    )
):
    """
    Получить товар с валидацией ID
    
    ID должен быть от 1 до 1000
    """
    return {
        "product_id": product_id,
        "message": f"Товар с ID {product_id}"
    }


# ========================================
# 4. Enum для ограниченного набора значений
# ========================================

class Category(str, Enum):
    """Доступные категории товаров"""
    electronics = "electronics"
    clothing = "clothing"
    food = "food"
    books = "books"


@app.get("/categories/{category_name}")
def get_category(category_name: Category):
    """
    Получить информацию о категории
    
    Принимает только предопределенные значения категорий
    """
    return {
        "category": category_name,
        "message": f"Категория: {category_name.value}"
    }


# ========================================
# 5. Float path параметры
# ========================================

@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    """
    Чтение файла с путем, содержащим слеши
    
    :path позволяет включать / в параметр
    
    Example: /files/home/user/document.txt
    """
    return {
        "file_path": file_path
    }


# ========================================
# Примеры использования
# ========================================

# Для запуска:
# uvicorn 2_path_params:app --reload
#
# Примеры запросов:
#
# 1. Простые параметры:
#    curl http://127.0.0.1:8000/users/42
#    curl http://127.0.0.1:8000/items/laptop
#
# 2. Несколько параметров:
#    curl http://127.0.0.1:8000/users/1/posts/5
#
# 3. С валидацией (попробуйте невалидные значения):
#    curl http://127.0.0.1:8000/products/100     # OK
#    curl http://127.0.0.1:8000/products/2000    # Ошибка: > 1000
#    curl http://127.0.0.1:8000/products/0       # Ошибка: < 1
#
# 4. Enum параметры:
#    curl http://127.0.0.1:8000/categories/electronics  # OK
#    curl http://127.0.0.1:8000/categories/invalid      # Ошибка
#
# 5. Path с слешами:
#    curl http://127.0.0.1:8000/files/home/user/doc.txt
