FROM python:3.10-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и ставим зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем сам скрипт бота
COPY . .

# Команда по умолчанию при запуске контейнера
CMD ["python", "weekly_report.py"]