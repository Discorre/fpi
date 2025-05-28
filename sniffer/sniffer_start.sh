#!/bin/bash
set -e

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

# Проверяем, что ufw установлен
if ! command -v ufw &>/dev/null; then
  echo "ufw не установлен. Устанавливаю..."
  sudo apt update && sudo apt install -y ufw
fi

# Настраиваем политики  по умолчанию, чтобы установка сниффера не влияла на остальные сервисы на сервере
sudo ufw default allow incoming
sudo ufw default allow outgoing

# Разрешаем доступ на порты только из подсети VPN
sudo ufw allow from 10.8.0.0/24 to any port 8082
sudo ufw allow from 10.8.0.0/24 to any port 8081

# Запрещаем доступ к этим портам для остальных
sudo ufw deny 8082
sudo ufw deny 8081

# Включаем ufw, если он ещё не включён
if ! sudo ufw status | grep -q "Status: active"; then
  echo "Включаю ufw..."
  sudo ufw --force enable
fi

# Запускаем mitmweb с твоими параметрами
mitmweb --mode reverse:http://127.0.0.1:8000 \
  --web-host 0.0.0.0 --listen-port 8080 \
  --certs "*=certs/discorre.ru/full.pem" \
  -s main.py --set block_global=false
