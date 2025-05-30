#!/bin/bash
set -e

DUMP_FILE="logs/flows.dump"

# Проверяем, что python3-venv установлен
if ! dpkg -s python3-venv &>/dev/null; then
  echo "python3-venv не установлен. Устанавливаю..."
  sudo apt update && sudo apt install -y python3-venv
fi

# Создаём виртуальное окружение (если ещё нет)
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем pip и устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt

if [ -f logs/flows.dump ]; then
  mv logs/flows.dump logs/flows_$(date +%Y%m%d_%H%M%S).dump
fi

# Проверка и создание файла дампа, если он не существует
if [ ! -f "$DUMP_FILE" ]; then
  echo "Создаю файлы лога: $DUMP_FILE"
  sudo mkdir -p "$(dirname "$DUMP_FILE")"
  sudo touch "$DUMP_FILE"
  sudo chmod 666 "$DUMP_FILE"
else
  echo "Файл дампа уже существует: $DUMP_FILE"
fi

# Запускаем mitmweb с твоими параметрами
mitmweb --mode reverse:http://127.0.0.1:8000 \
  --web-host 0.0.0.0 --listen-port 8080 \
  --certs "*=certs/discorre.ru/full.pem" \
  -s main.py --set block_global=false \
  --save-stream-file=logs/flows.dump
