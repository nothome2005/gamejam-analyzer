FROM python:3.12-slim

WORKDIR /app

# Оптимізація роботи Python у контейнері та негайне виведення логів
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Встановлення залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання модулів системи, тестів та специфікацій
COPY src/ ./src/
COPY tests/ ./tests/
COPY docs/ ./docs/
COPY spec/ ./spec/
COPY logs/ ./logs/

# Створення папки логів у разі відсутності
RUN mkdir -p /app/logs

EXPOSE 8000

# Запуск REST API сервера FastAPI через Uvicorn
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
