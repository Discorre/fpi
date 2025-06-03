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

# Выбор брандмауэра
echo "Выберите брандмауэр для настройки:"
echo "1) UFW"
echo "2) iptables"
echo "3) Не использовать брандмауэр"
read -p "Введите номер (1-3): " FIREWALL_CHOICE

# Переменная для хранения решения очищать ли правила
CLEAR_RULES="yes"

case $FIREWALL_CHOICE in
  1|2)
    echo "Очистить текущие правила $([ "$FIREWALL_CHOICE" = "1" ] && echo "UFW" || echo "iptables")?"
    read -p "Очистить правила? (да/нет): " CLEAR_RULES_INPUT
    CLEAR_RULES=${CLEAR_RULES_INPUT,,}  # приводим к нижнему регистру
    ;;
  *)
    echo "Брандмауэр не будет настраиваться."
    ;;
esac

# Настройка брандмауэра
case $FIREWALL_CHOICE in
  1)
    echo "Настраиваем UFW..."

    if ! command -v ufw &>/dev/null; then
      echo "ufw не установлен. Устанавливаю..."
      sudo apt update && sudo apt install -y ufw
    fi

    if [[ "$CLEAR_RULES" == "да" || "$CLEAR_RULES" == "yes" || "$CLEAR_RULES" == "y" ]]; then
      echo "Сбрасываю текущие правила UFW..."
      sudo ufw --force reset

      # Настраиваем политики по умолчанию
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
    else
      echo "Правила UFW не изменены. Продолжаю без настройки."
    fi
    ;;
  2)
    echo "Настраиваем iptables..."

    if [[ "$CLEAR_RULES" == "да" || "$CLEAR_RULES" == "yes" || "$CLEAR_RULES" == "y" ]]; then
      echo "Очищаю текущие правила iptables..."
      sudo iptables -F
      sudo iptables -X
      sudo iptables -P INPUT ACCEPT
      sudo iptables -P FORWARD ACCEPT
      sudo iptables -P OUTPUT ACCEPT

      # Разрешаем входящее соединение только из подсети 10.8.0.0/24 на порты 8081 и 8082
      sudo iptables -A INPUT -s 10.8.0.0/24 -p tcp --dport 8081 -j ACCEPT
      sudo iptables -A INPUT -s 10.8.0.0/24 -p tcp --dport 8082 -j ACCEPT

      # Блокируем все остальные соединения на эти порты
      sudo iptables -A INPUT -p tcp --dport 8081 -j DROP
      sudo iptables -A INPUT -p tcp --dport 8082 -j DROP

      # Сохраняем правила
      if command -v iptables-save &>/dev/null; then
        sudo iptables-save > /etc/iptables/rules.v4
      else
        echo "Установите iptables-persistent, чтобы сохранить правила после перезагрузки."
      fi
    else
      echo "Правила iptables не изменены. Продолжаю без настройки."
    fi
    ;;
  3)
    echo "Брандмауэр не будет настроен."
    ;;
  *)
    echo "Неверный выбор. Брандмауэр не будет настроен."
    ;;
esac

# Проверка и создание файла дампа, если он не существует
if [ -f "$DUMP_FILE" ]; then
  mv "$DUMP_FILE" "logs/flows_$(date +%Y%m%d_%H%M%S).dump"
fi

sudo mkdir -p "$(dirname "$DUMP_FILE")"
sudo touch "$DUMP_FILE"
sudo chmod 666 "$DUMP_FILE"

# Конфигурация mitmweb
echo "Настройка запуска mitmweb..."

read -p "Режим reverse-proxy? (да/нет, по умолчанию да): " USE_REVERSE_PROXY
USE_REVERSE_PROXY=${USE_REVERSE_PROXY:-"да"}

REVERSE_URL=""
if [[ "$USE_REVERSE_PROXY" == "да" || "$USE_REVERSE_PROXY" == "yes" ]]; then
  read -p "Введите URL reverse-прокси (по умолчанию http://127.0.0.1:8000): " REVERSE_URL
  REVERSE_URL=${REVERSE_URL:-"http://127.0.0.1:8000"}
  REVERSE_FLAG="--mode reverse:${REVERSE_URL}"
else
  REVERSE_FLAG=""
fi

read -p "Порт для прослушивания (по умолчанию 8080): " LISTEN_PORT
LISTEN_PORT=${LISTEN_PORT:-"8080"}

read -p "Хост веб-интерфейса (по умолчанию 0.0.0.0): " WEB_HOST
WEB_HOST=${WEB_HOST:-"0.0.0.0"}

read -p "Использовать SSL-сертификат? (да/нет, по умолчанию да): " USE_CERT
USE_CERT=${USE_CERT:-"да"}

CERT_PATH=""
if [[ "$USE_CERT" == "да" || "$USE_CERT" == "yes" ]]; then
  read -p "Путь к сертификату (по умолчанию certs/discorre.ru/full.pem): " CERT_PATH
  CERT_PATH=${CERT_PATH:-"certs/discorre.ru/full.pem"}
  CERT_FLAG="--certs \"*=$CERT_PATH\""
else
  CERT_FLAG=""
fi

read -p "Запускать main.py? (да/нет, по умолчанию да): " USE_SCRIPT
USE_SCRIPT=${USE_SCRIPT:-"да"}

SCRIPT_FLAG=""
if [[ "$USE_SCRIPT" == "да" || "$USE_SCRIPT" == "yes" ]]; then
  SCRIPT_FLAG="-s main.py"
fi

read -p "Файл сохранения дампа (по умолчанию logs/flows.dump): " DUMP_FILE
DUMP_FILE=${DUMP_FILE:-"logs/flows.dump"}

BLOCK_GLOBAL="--set block_global=false"

# Формируем команду
MITMWEB_CMD="mitmweb \
  $REVERSE_FLAG \
  --web-host $WEB_HOST \
  --listen-port $LISTEN_PORT \
  $CERT_FLAG \
  $SCRIPT_FLAG \
  $BLOCK_GLOBAL \
  --save-stream-file=\"$DUMP_FILE\""

# Убираем лишние пробелы
MITMWEB_CMD=$(echo "$MITMWEB_CMD" | sed 's/  */ /g')

echo "Запускаю mitmweb с командой:"
echo "$MITMWEB_CMD"

# Выполняем команду
eval "$MITMWEB_CMD"