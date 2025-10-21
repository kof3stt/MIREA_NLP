"""
Шаблон для проекта: Имитация OpenAI API

ИНСТРУКЦИЯ:
1. Найдите все комментарии "TODO" в коде
2. Реализуйте необходимую функциональность
3. Тестируйте в Swagger UI (http://127.0.0.1:8000/docs)
4. Проверьте все эндпоинты с помощью test_api.http

ПОДСКАЗКИ:
- Читайте комментарии внимательно
- Используйте примеры из предыдущих модулей
- Проверяйте TASK.md для деталей
- Запускайте код после каждого TODO
"""

import random
import string
import time
from typing import List, Optional, Union

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator

app = FastAPI(
    title="OpenAI API Imitation",
    description="Упрощенная имитация OpenAI API для обучения",
    version="1.0.0",
)


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================


def generate_id(prefix: str) -> str:
    """
    Генерация уникального ID
    
    Args:
        prefix: Префикс для ID (например, "chatcmpl", "cmpl")
    
    Returns:
        Строка вида "prefix-randomstring"
    """
    # TODO: Реализуйте генерацию случайной строки из 20 символов
    # Подсказка: используйте random.choices() и string.ascii_letters + string.digits
    # suffix = "РЕАЛИЗУЙТЕ_МЕНЯ"  # Замените это
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k = 20))
    return f"{prefix}-{suffix}"


def get_current_timestamp() -> int:
    """
    Получить текущий Unix timestamp
    
    Returns:
        Текущее время в секундах с 1970-01-01
    """
    # TODO: Верните текущий timestamp
    # Подсказка: используйте time.time() и int()
    # return 0  # Замените это
    return int(time.time())


def count_tokens(text: str) -> int:
    """
    Приблизительный подсчет токенов
    
    Примерно 4 символа = 1 токен
    
    Args:
        text: Текст для подсчета
        
    Returns:
        Количество токенов
    """
    # TODO: Реализуйте подсчет токенов
    # Подсказка: len(text) // 4, но минимум 1
    # return 1  # Замените это
    return min(1, len(text) // 4)


def generate_response(prompt: str, max_tokens: Optional[int] = 100) -> str:
    """
    Генерация случайного ответа
    
    Args:
        prompt: Промпт пользователя (можно использовать для контекста)
        max_tokens: Максимальное количество токенов
        
    Returns:
        Сгенерированный текст
    """
    # TODO: Реализуйте генерацию ответа
    # Подсказки:
    # 1. Создайте список из 5-10 вариантов ответов
    # 2. Выберите случайный: random.choice(responses)
    # 3. Ограничьте длину: max_tokens * 4 символов
    
    responses = [
        # TODO: Добавьте свои варианты ответов (минимум 5)
        # "Ответ 1",
        # "Ответ 2",
        # ... добавьте ещё
        "Интересная мысль! Расскажи подробнее.",
        "Это звучит логично, но можно рассмотреть и другой вариант.",
        "Хороший вопрос. Думаю, ответ кроется в деталях.",
        "Вот что я думаю: всё зависит от контекста.",
        "Отличное наблюдение! Возможно, стоит уточнить некоторые моменты.",
        "Не уверен, но можно попробовать так.",
        "Да, это действительно важно. Попробуем разобраться глубже.",
        "Пожалуй, с этим трудно не согласиться.",
        "Хм, интересно. Никогда не думал об этом под таким углом.",
        "Кажется, это можно объяснить довольно просто."
    ]
    
    response = random.choice(responses)

    if max_tokens is None:
        max_tokens = 100

    max_chars = max_tokens * 4
    return response[:max_chars]


def generate_embedding(text: str, dimensions: int = 1536) -> List[float]:
    """
    Генерация случайных эмбеддингов
    
    Args:
        text: Текст для эмбеддинга
        dimensions: Размерность вектора (обычно 1536)
        
    Returns:
        Список из dimensions случайных чисел от -1 до 1
    """
    # TODO: Реализуйте генерацию эмбеддингов
    # Подсказки:
    # 1. Используйте random.seed(hash(text)) для повторяемости
    # 2. Генерируйте dimensions случайных чисел
    # 3. Используйте random.uniform(-1, 1) для каждого числа
    
    random.seed(hash(text))
    # TODO: Замените это на правильную генерацию
    # return [0.0] * dimensions
    return [random.uniform(-1, 1) for _ in range(dimensions)]


# ============================================================
# КОНСТАНТЫ
# ============================================================

# TODO: Создайте список доступных моделей
# Должны быть: gpt-4, gpt-3.5-turbo, text-davinci-003, text-embedding-ada-002
# AVAILABLE_MODELS = [
#     # TODO: Добавьте модели здесь
# ]
AVAILABLE_MODELS = [
    "gpt-4",
    "gpt-3.5-turbo",
    "text-davinci-003",
    "text-embedding-ada-002"
]


# ============================================================
# МОДЕЛИ ДАННЫХ
# ============================================================

# ---------- Общие модели ----------

class Usage(BaseModel):
    """Информация об использовании токенов"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class EmbeddingUsage(BaseModel):
    """Использование токенов для embeddings"""
    prompt_tokens: int
    total_tokens: int


# ---------- Эндпоинт 1: Models ----------

class Model(BaseModel):
    """Информация о модели"""
    # TODO: Реализуйте поля:
    # - id: str (название модели)
    # - object: str (всегда "model")
    # - created: int (Unix timestamp)
    # - owned_by: str (владелец, например "openai")
    
    # pass  # Удалите pass после реализации
    id: str
    object: str
    created: int
    owned_by: str


class ModelList(BaseModel):
    """Список моделей"""
    # TODO: Реализуйте поля:
    # - object: str (всегда "list")
    # - data: List[Model]
    
    # pass  # Удалите pass после реализации
    object: str = "list"
    data: List[Model]


# ---------- Эндпоинт 2: Chat Completions ----------

class Message(BaseModel):
    """Сообщение в чате"""
    # TODO: Реализуйте поля:
    # - role: str
    # - content: str
    
    # TODO: Добавьте валидатор для role
    # role должен быть одним из: "system", "user", "assistant"
    # Используйте @validator
    
    # pass  # Удалите pass после реализации
    role: str
    content: str

    @validator("role")
    def validate_role(cls, v):
        allowed_roles = ["system", "user", "assistant"]
        if v not in allowed_roles:
            raise ValueError(f"Недопустимая роль: {v}. Разрешены: {allowed_roles}")
        return v




class ChatCompletionRequest(BaseModel):
    """Запрос на генерацию ответа в чате"""
    # TODO: Реализуйте поля:
    # - model: str
    # - messages: List[Message] (минимум 1, используйте Field)
    # - temperature: float = 1.0 (от 0.0 до 2.0, используйте Field)
    # - max_tokens: Optional[int] = None (если задано - больше 0)
    # - stream: bool = False
    
    # pass  # Удалите pass после реализации
    model: str
    messages: List[Message] = Field(..., min_items = 1)
    temperature: float = Field(1.0, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    stream: bool = False


class Choice(BaseModel):
    """Вариант ответа в чате"""
    # TODO: Реализуйте поля:
    # - index: int
    # - message: Message
    # - finish_reason: str ("stop", "length", или "content_filter")
    
    # pass  # Удалите pass после реализации
    index: int
    message: Message
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    """Ответ на запрос chat completion"""
    # TODO: Реализуйте поля:
    # - id: str
    # - object: str = "chat.completion"
    # - created: int
    # - model: str
    # - choices: List[Choice]
    # - usage: Usage
    
    # pass  # Удалите pass после реализации
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    


# ---------- Эндпоинт 3: Completions ----------

class CompletionRequest(BaseModel):
    """Запрос на генерацию текста"""
    # TODO: Реализуйте поля:
    # - model: str
    # - prompt: Union[str, List[str]]
    # - max_tokens: int = 16 (от 1 до 4096)
    # - temperature: float = 1.0 (от 0.0 до 2.0)
    # - n: int = 1 (от 1 до 10, количество вариантов)
    
    # pass  # Удалите pass после реализации
    model: str
    prompt: Union[str, List[str]]
    max_tokens: int = Field(16, ge=1, le=4096)
    temperature: float = Field(1.0, ge=0.0, le=2.0)
    n: int = Field(1, ge=1, le=10)



class CompletionChoice(BaseModel):
    """Вариант завершения текста"""
    # TODO: Реализуйте поля:
    # - text: str
    # - index: int
    # - finish_reason: str
    
    # pass  # Удалите pass после реализации
    text: str
    index: int
    finish_reason: str
    


class CompletionResponse(BaseModel):
    """Ответ на запрос completion"""
    # TODO: Реализуйте поля:
    # - id: str
    # - object: str = "text_completion"
    # - created: int
    # - model: str
    # - choices: List[CompletionChoice]
    # - usage: Usage
    
    # pass  # Удалите pass после реализации
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Usage



# ---------- Эндпоинт 4: Embeddings ----------

class EmbeddingRequest(BaseModel):
    """Запрос на генерацию эмбеддингов"""
    # TODO: Реализуйте поля:
    # - model: str
    # - input: Union[str, List[str]]
    # - encoding_format: str = "float"
    
    # TODO: Добавьте валидатор для encoding_format
    # Должен быть "float" или "base64"
    
    # pass  # Удалите pass после реализации
    model: str
    input: Union[str, List[str]]
    encoding_format: str = "float"

    @validator("encoding_format")
    def validate_encoding_format(cls, v):
        allowed =["float", "base64"]
        if v not in allowed:
            raise ValueError(f"encoding_format должен быть одним из {allowed}")
        return v



class Embedding(BaseModel):
    """Один эмбеддинг"""
    # TODO: Реализуйте поля:
    # - object: str = "embedding"
    # - embedding: List[float]
    # - index: int
    
    # pass  # Удалите pass после реализации
    object: str = "embedding"
    embedding: List[float]
    index: int



class EmbeddingResponse(BaseModel):
    """Ответ с эмбеддингами"""
    # TODO: Реализуйте поля:
    # - object: str = "list"
    # - data: List[Embedding]
    # - model: str
    # - usage: EmbeddingUsage
    
    # pass  # Удалите pass после реализации
    object: str = "list"
    data: List[Embedding]
    model: str
    usage: EmbeddingUsage


# ============================================================
# ЭНДПОИНТЫ
# ============================================================

# ---------- Эндпоинт 1: GET /v1/models ----------

@app.get("/v1/models", response_model=ModelList)
def list_models():
    """
    Получить список доступных моделей
    
    Returns:
        ModelList со всеми доступными моделями
    """
    # TODO: Реализуйте эндпоинт
    # Подсказки:
    # 1. Создайте список моделей (минимум 3)
    # 2. Для каждой модели создайте объект Model
    # 3. Используйте get_current_timestamp() для created
    # 4. owned_by = "openai"
    # 5. Верните ModelList с этими моделями
    
    models = [
        # TODO: Создайте модели
        # Пример:
        # Model(
        #     id="gpt-4",
        #     object="model",
        #     created=get_current_timestamp(),
        #     owned_by="openai"
        # ),
        Model(
            id=model_name,
            object="model",
            created=get_current_timestamp(),
            owned_by="openai"
        )
        for model_name in AVAILABLE_MODELS
    ]
    
    # TODO: Верните ModelList
    # pass
    return ModelList(object="list", data=models)


# ---------- Эндпоинт 2: POST /v1/chat/completions ----------

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def create_chat_completion(request: ChatCompletionRequest):
    """
    Генерация ответа в формате чата
    
    Args:
        request: Запрос с моделью и сообщениями
        
    Returns:
        ChatCompletionResponse с сгенерированным ответом
        
    Raises:
        HTTPException: Если модель не найдена или данные невалидны
    """
    # TODO: Реализуйте эндпоинт
    # Шаги:
    # 1. Проверьте, что модель существует (используйте AVAILABLE_MODELS)
    #    Если нет - raise HTTPException(404, "")
    
    # 2. Проверьте, что есть хотя бы одно сообщение
    #    Если нет - raise 
    
    # 3. Получите последнее сообщение пользователя
    #    user_message = 
    
    # 4. Сгенерируйте ответ
    #    response_text = 
    
    # 5. Подсчитайте токены
    #    prompt_tokens = 
    #    completion_tokens = 
    
    # 6. Создайте ответное сообщение
    #    assistant_message = Message()
    
    # 7. Создайте Choice
    #    choice = 
    
    # 8. Создайте Usage
    #    usage = Usage(
    #    )
    
    # 9. Верните ChatCompletionResponse
    #    return ChatCompletionResponse(
    #    )
    
    # pass  # Удалите после реализации
    if request.model not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модель '{request.model}' не найдена."
        )

    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Список сообщений не может быть пустым."
        )

    user_message = next(
        (msg.content for msg in reversed(request.messages) if msg.role == "user"),
        None
    )
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не найдено сообщение пользователя (role='user')."
        )
    
    response_text = generate_response(user_message, request.max_tokens)

    prompt_tokens = count_tokens(user_message)
    completion_tokens = count_tokens(response_text)

    assistant_message = Message(role="assistant", content=response_text)

    choice = Choice(
        index=0,
        message=assistant_message,
        finish_reason="stop"
    )

    usage = Usage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens
    )

    return ChatCompletionResponse(
        id=generate_id("chatcmpl"),
        created=get_current_timestamp(),
        model=request.model,
        choices=[choice],
        usage=usage
    )


# ---------- Эндпоинт 3: POST /v1/completions ----------

@app.post("/v1/completions", response_model=CompletionResponse)
def create_completion(request: CompletionRequest):
    """
    Генерация продолжения текста
    
    Args:
        request: Запрос с моделью и промптом
        
    Returns:
        CompletionResponse с сгенерированным текстом
        
    Raises:
        HTTPException: Если модель не найдена
    """
    # TODO: Реализуйте эндпоинт
    # Шаги:
    # 1. Проверьте модель (как в chat/completions)
    
    # 2. Преобразуйте prompt в строку (если это список)
    
    # 3. Сгенерируйте request.n вариантов ответа
    #    choices = []
    #    for i in range(request.n):
    #        text = generate_response(prompt_text, request.max_tokens)
    #        choice = CompletionChoice(
    #        )
    #        choices.append(choice)
    
    # 4. Подсчитайте токены
    
    # 5. Верните CompletionResponse
    
    # pass  # Удалите после реализации
    if request.model not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модель '{request.model}' не найдена."
        )
    
    if isinstance(request.prompt, list):
        prompt_text = " ".join(request.prompt)
    else:
        prompt_text = request.prompt

    choices = []
    for i in range(request.n):
        text = generate_response(prompt_text, request.max_tokens)
        choice = CompletionChoice(
            text=text,
            index=i,
            finish_reason="stop"
        )
        choices.append(choice)
    
    prompt_tokens = count_tokens(prompt_text)
    completion_tokens = sum(count_tokens(c.text) for c in choices)

    usage = Usage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens
    )

    return CompletionResponse(
        id=generate_id("cmpl"),
        created=get_current_timestamp(),
        model=request.model,
        choices=choices,
        usage=usage
    )
    



# ---------- Эндпоинт 4: POST /v1/embeddings ----------

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
def create_embeddings(request: EmbeddingRequest):
    """
    Генерация векторных представлений текста
    
    Args:
        request: Запрос с моделью и текстом
        
    Returns:
        EmbeddingResponse с эмбеддингами
        
    Raises:
        HTTPException: Если модель не найдена
    """
    # TODO: Реализуйте эндпоинт
    # Шаги:
    # 1. Проверьте модель
    #    Для embeddings используйте "text-embedding-ada-002"
    
    # 2. Преобразуйте input в список (если это строка)
    
    # 3. Сгенерируйте эмбеддинги для каждого текста
    #    embeddings = []
    #    for i, text in enumerate(inputs):
    #        embedding_vector = 
    #        emb = Embedding(
    #        )
    #        embeddings.append(emb)
    
    # 4. Подсчитайте токены
    #    total_tokens = 
    
    # 5. Верните EmbeddingResponse
    #    return EmbeddingResponse(
    #    )
    
    # pass  # Удалите после реализации
    if request.model != "text-embedding-ada-002":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Модель '{request.model}' не поддерживается для embeddings."
        )
    
    if isinstance(request.input, str):
        inputs = [request.input]
    else:
        inputs = request.input
    
    embeddings_list = []
    for i, text in enumerate(inputs):
        embedding_vector = generate_embedding(text)
        emb = Embedding(
            embedding=embedding_vector,
            index=i
        )
        embeddings_list.append(emb)

    total_tokens = sum(count_tokens(text) for text in inputs)
    usage = EmbeddingUsage(
        prompt_tokens=total_tokens,
        total_tokens=total_tokens
    )

    return EmbeddingResponse(
        data=embeddings_list,
        model=request.model,
        usage=usage
    )


# ============================================================
# ДОПОЛНИТЕЛЬНЫЕ ЭНДПОИНТЫ (ОПЦИОНАЛЬНО)
# ============================================================

@app.get("/")
def root():
    """Корневой эндпоинт"""
    return {
        "message": "OpenAI API Imitation",
        "endpoints": {
            "models": "GET /v1/models",
            "chat": "POST /v1/chat/completions",
            "completions": "POST /v1/completions",
            "embeddings": "POST /v1/embeddings",
        },
        "docs": "/docs",
    }


# TODO (ОПЦИОНАЛЬНО): Добавьте обработчик ошибок
# Создайте красивые ответы при ошибках

# TODO (ОПЦИОНАЛЬНО): Добавьте логирование
# Логируйте все запросы с timestamp

# TODO (ОПЦИОНАЛЬНО): Реализуйте streaming для chat/completions
# Когда stream=True, возвращайте Server-Sent Events


# ============================================================
# Для запуска:
# uvicorn template_students:app --reload
#
# После запуска откройте:
# - Swagger UI: http://127.0.0.1:8000/docs
# - ReDoc: http://127.0.0.1:8000/redoc
#
# Тестируйте каждый TODO по очереди!
# ============================================================
