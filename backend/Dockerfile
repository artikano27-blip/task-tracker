FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. 🗄️ Системные зависимости для компиляции
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. 📦 Установка и настройка Poetry (до копирования файлов проекта)
RUN pip install --no-cache-dir "poetry>=2.0.0" \
    && poetry config virtualenvs.create false

# 3. 📄 Копирование манифестов зависимостей
# Звёздочка poetry.lock* не даст упасть сборке, если lock-файл ещё не создан
COPY pyproject.toml poetry.lock* ./

# 4. ⚙️ Установка библиотек без самого исходного кода (--no-root)
RUN poetry install --no-root --no-interaction --no-ansi

# 5. 🚀 Копирование исходного кода проекта (меняется чаще всего)
COPY . .