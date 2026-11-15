# Game Jam Analyzer — REST API Service

Інформаційна система для обліку, криптографічного аудиту доброчесності (SHA-256), контролю Soft Deadline та аналітики ігрових джемів (FastAPI, OpenAPI 3.0.3, RFC 7807).

---

## Швидкий запуск через Docker 🐳

### 1. Запуск веб-сервера
```bash
docker compose up -d
```
Сервер буде доступний за адресою:
- **Swagger UI (Інтерактивна документація)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### 2. Запуск тестів у контейнері
```bash
docker compose run --rm test
```
*Запускає повний комплекс із 41 тесту (BDD, Unit, Integration, Addendum 02).*

### 3. Зупинка сервера
```bash
docker compose down
```

---

## Запуск локально без Docker (Python / uv) 🐍

### 1. Запуск сервера
```bash
uv run --with fastapi --with uvicorn --with pydantic uvicorn src.api.app:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Запуск тестів
```bash
uv run --with pytest --with fastapi --with httpx --with pydantic --with openapi-spec-validator python -m pytest -v
```

### 3. Валідація специфікації OpenAPI 3.0.3
```bash
uv run --with openapi-spec-validator openapi-spec-validator docs/openapi.yaml
```

---

## Логування (Audit Logs)
Усі HTTP-запити, бізнес-події та структуровані помилки RFC 7807 автоматично логуються у форматі JSONL у файл `logs/system_execution.log`.
