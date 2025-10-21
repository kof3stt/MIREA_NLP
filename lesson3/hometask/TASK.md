# Детальное описание задания

## Эндпоинт 1: GET /v1/models

### Описание
Возвращает список доступных моделей для генерации текста.

### Request
```http
GET /v1/models
```

Параметры: нет

### Response
```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-4",
      "object": "model",
      "created": 1687882411,
      "owned_by": "openai"
    },
    {
      "id": "gpt-3.5-turbo",
      "object": "model", 
      "created": 1677610602,
      "owned_by": "openai"
    }
  ]
}
```

### Что нужно реализовать
1. Модель `Model` с полями:
   - `id: str` - название модели
   - `object: str` - всегда "model"
   - `created: int` - Unix timestamp
   - `owned_by: str` - владелец модели

2. Модель `ModelList` для списка:
   - `object: str` - всегда "list"
   - `data: List[Model]` - список моделей

3. Эндпоинт возвращает минимум 3 модели:
   - gpt-4
   - gpt-3.5-turbo
   - text-embedding-ada-002

---

## Эндпоинт 2: POST /v1/chat/completions

### Описание
Генерирует ответ в формате чата (диалог с ассистентом).

### Request
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello!"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 100,
  "stream": false
}
```

### Параметры
- `model` (обязательно): название модели (gpt-4, gpt-3.5-turbo)
- `messages` (обязательно): список сообщений
  - `role`: "system", "user", или "assistant"
  - `content`: текст сообщения
- `temperature` (опционально): 0.0-2.0, по умолчанию 1.0
- `max_tokens` (опционально): максимум токенов в ответе
- `stream` (опционально): streaming ответа (для продвинутых)

### Response
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 9,
    "total_tokens": 19
  }
}
```

### Что нужно реализовать

1. **Модель Message**:
   ```python
   class Message(BaseModel):
       role: str  # "system", "user", "assistant"
       content: str
   ```
   - Валидация: role должен быть одним из ["system", "user", "assistant"]

2. **Модель ChatCompletionRequest**:
   - `model: str`
   - `messages: List[Message]` (минимум 1 сообщение)
   - `temperature: float = 1.0` (от 0.0 до 2.0)
   - `max_tokens: Optional[int] = None` (если указано - больше 0)
   - `stream: bool = False`

3. **Модель ChatCompletionResponse**:
   - `id: str` - уникальный ID (например, "chatcmpl-" + случайные цифры)
   - `object: str = "chat.completion"`
   - `created: int` - текущий Unix timestamp
   - `model: str`
   - `choices: List[Choice]`
   - `usage: Usage`

4. **Вспомогательные модели**:
   ```python
   class Choice(BaseModel):
       index: int
       message: Message
       finish_reason: str  # "stop", "length", "content_filter"
   
   class Usage(BaseModel):
       prompt_tokens: int
       completion_tokens: int
       total_tokens: int
   ```

5. **Логика генерации**:
   - Извлечь последнее сообщение пользователя
   - Сгенерировать случайный ответ
   - Подсчитать токены (приблизительно)
   - Вернуть ответ в правильном формате

6. **Обработка ошибок**:
   - Модель не найдена → 404
   - Пустой список сообщений → 400
   - Неверная роль в сообщении → 422

---

## Эндпоинт 3: POST /v1/completions

### Описание
Генерирует продолжение текста (старый формат, не чат).

### Request
```json
{
  "model": "text-davinci-003",
  "prompt": "Once upon a time",
  "max_tokens": 50,
  "temperature": 0.7,
  "n": 1
}
```

### Параметры
- `model` (обязательно): название модели
- `prompt` (обязательно): текст для продолжения (строка или список строк)
- `max_tokens` (опционально): максимум токенов, по умолчанию 16
- `temperature` (опционально): 0.0-2.0, по умолчанию 1.0
- `n` (опционально): количество вариантов ответа, по умолчанию 1

### Response
```json
{
  "id": "cmpl-123",
  "object": "text_completion",
  "created": 1677652288,
  "model": "text-davinci-003",
  "choices": [
    {
      "text": " in a land far away, there lived a brave knight.",
      "index": 0,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 12,
    "total_tokens": 17
  }
}
```

### Что нужно реализовать

1. **Модель CompletionRequest**:
   - `model: str`
   - `prompt: Union[str, List[str]]` - может быть строкой или списком
   - `max_tokens: int = 16` (1-4096)
   - `temperature: float = 1.0` (0.0-2.0)
   - `n: int = 1` (1-10)

2. **Модель CompletionResponse**:
   - `id: str`
   - `object: str = "text_completion"`
   - `created: int`
   - `model: str`
   - `choices: List[CompletionChoice]`
   - `usage: Usage`

3. **Модель CompletionChoice**:
   ```python
   class CompletionChoice(BaseModel):
       text: str
       index: int
       finish_reason: str
   ```

4. **Логика**:
   - Поддержать prompt как строку и как список
   - Сгенерировать n вариантов ответа
   - Ограничить длину по max_tokens
   - Подсчитать токены

---

## Эндпоинт 4: POST /v1/embeddings

### Описание
Генерирует векторные представления (embeddings) текста.

### Request
```json
{
  "model": "text-embedding-ada-002",
  "input": "The food was delicious and the waiter was friendly.",
  "encoding_format": "float"
}
```

### Параметры
- `model` (обязательно): модель для эмбеддингов
- `input` (обязательно): текст или список текстов
- `encoding_format` (опционально): "float" или "base64"

### Response
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.0023, -0.0091, 0.0014, ...],  // 1536 чисел
      "index": 0
    }
  ],
  "model": "text-embedding-ada-002",
  "usage": {
    "prompt_tokens": 8,
    "total_tokens": 8
  }
}
```

### Что нужно реализовать

1. **Модель EmbeddingRequest**:
   - `model: str`
   - `input: Union[str, List[str]]`
   - `encoding_format: str = "float"` (только "float" или "base64")

2. **Модель EmbeddingResponse**:
   - `object: str = "list"`
   - `data: List[Embedding]`
   - `model: str`
   - `usage: EmbeddingUsage`

3. **Вспомогательные модели**:
   ```python
   class Embedding(BaseModel):
       object: str = "embedding"
       embedding: List[float]  # Вектор размерностью 1536
       index: int
   
   class EmbeddingUsage(BaseModel):
       prompt_tokens: int
       total_tokens: int
   ```

4. **Логика**:
   - Генерировать вектор размерностью 1536 (стандарт для ada-002)
   - Для одинакового текста генерировать одинаковые эмбеддинги
   - Поддержать список текстов
   - Подсчитать токены

---

## Дополнительные требования

### Валидация

1. **Модель должна существовать**:
   ```python
   AVAILABLE_MODELS = ["gpt-4", "gpt-3.5-turbo", "text-davinci-003", "text-embedding-ada-002"]
   
   if request.model not in AVAILABLE_MODELS:
       raise HTTPException(404, f"Model {request.model} not found")
   ```

2. **Temperature в диапазоне**:
   ```python
   temperature: float = Field(1.0, ge=0.0, le=2.0)
   ```

3. **Max tokens положительный**:
   ```python
   max_tokens: int = Field(16, ge=1, le=4096)
   ```

### Обработка ошибок

Все эндпоинты должны обрабатывать:

1. **404 - Model not found**:
   ```json
   {
     "error": {
       "message": "The model 'gpt-5' does not exist",
       "type": "invalid_request_error",
       "code": "model_not_found"
     }
   }
   ```

2. **400 - Invalid request**:
   ```json
   {
     "error": {
       "message": "Invalid request: messages cannot be empty",
       "type": "invalid_request_error",
       "code": null
     }
   }
   ```

3. **422 - Validation error** (автоматически от Pydantic)

### Response Models

Всегда используйте `response_model` для правильной документации:

```python
@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(request: ChatCompletionRequest):
    ...
```

---

## Подсказки по реализации

### 1. Генерация ID

```python
import random
import string

def generate_id(prefix: str) -> str:
    """Генерация уникального ID"""
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    return f"{prefix}-{suffix}"

# Использование:
# generate_id("chatcmpl")  -> "chatcmpl-aB3dE5fG7hI9jK1lM2nO3"
```

### 2. Текущий timestamp

```python
import time

current_timestamp = int(time.time())
```

### 3. Генерация случайного ответа

```python
import random

SAMPLE_RESPONSES = [
    "Это интересный вопрос! Позвольте мне объяснить.",
    "Я рад помочь вам разобраться в этом вопросе.",
    "Давайте рассмотрим это более подробно.",
    "Вот что я думаю по этому поводу:",
]

def generate_response(prompt: str, max_tokens: int = 100) -> str:
    response = random.choice(SAMPLE_RESPONSES)
    # Ограничить по max_tokens (примерно)
    max_chars = max_tokens * 4  # ~4 символа = 1 токен
    return response[:max_chars]
```

### 4. Подсчет токенов

```python
def count_tokens(text: str) -> int:
    """Приблизительный подсчет токенов"""
    # Простая формула: ~4 символа = 1 токен
    return max(1, len(text) // 4)
```

### 5. Валидация роли сообщения

```python
from pydantic import validator

class Message(BaseModel):
    role: str
    content: str
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['system', 'user', 'assistant']
        if v not in allowed_roles:
            raise ValueError(f'role must be one of {allowed_roles}')
        return v
```

---

## Тестирование

После реализации проверьте:

1. Все эндпоинты возвращают правильный формат
2. Swagger UI (/docs) отображает документацию
3. Валидация работает (попробуйте невалидные данные)
4. Ошибки обрабатываются правильно
5. Response models исключают лишние поля

Используйте файл `test_api.http` для быстрого тестирования!
