# Используем официальный Python-образ
FROM python:3.11-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && apk add curl

# Копируем весь проект
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска FastAPI (через Uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
