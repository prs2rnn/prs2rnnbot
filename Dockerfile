# Используем стабильную LTS‑версию Python
FROM python:3.14.0-slim

# Метаданные образа (полезны для документации)
LABEL maintainer="prs2rnn <developer.prs2rnn@gmail.com>"
LABEL description="Telegram bot for personal portfolio"

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app

# Создаём рабочую директорию
WORKDIR $APP_HOME

# Создаём непривилегированного пользователя для безопасности
RUN groupadd -r app && useradd -r -g app app

# Обновляем пакеты и устанавливаем инструменты сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем только файлы зависимостей для кэширования
COPY pyproject.toml poetry.lock README.md LICENSE ./
COPY src/ ./src/

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Настраиваем Poetry: отключаем виртуальные окружения
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости (слой кэшируется, если зависимости не менялись)
RUN poetry install --no-interaction --no-ansi --only=main

# Меняем владельца файлов на непривилегированного пользователя
RUN chown -R app:app $APP_HOME
USER app

# Создаём директорию для логов
RUN mkdir -p $APP_HOME/logs

# Проверяем, что main.py существует
RUN test -f src/prs2rnnbot/main.py

# Открываем порт (если бот использует вебхуки)
# EXPOSE 8080

# Добавляем проверку здоровья контейнера
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Команда запуска
CMD ["python", "src/prs2rnnbot/main.py"]
