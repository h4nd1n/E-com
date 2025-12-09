# syntax=docker/dockerfile:1.7

# Базовый образ с Python
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Установим зависимости системы для aiosqlite и Kafka SSL (если понадобится)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Скопируем только requirements для ускорения кеша
COPY orders_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходники сервиса
COPY orders_service /app/orders_service

# Точка входа
CMD ["python", "-m", "orders_service.main"]
