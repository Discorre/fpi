# Используем официальный образ Node.js
FROM node:latest as build

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем package.json и package-lock.json для установки зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все файлы проекта в рабочую директорию контейнера
COPY . .

# Собираем проект с помощью Vite
RUN npm run build

# Stage 2 - создаем Nginx-сервер для раздачи статики
FROM nginx:latest

# Копируем собранные файлы из stage 1 в Nginx-сервер
COPY --from=build /app/dist /usr/share/nginx/html

# Опционально: копируем конфигурацию Nginx, если требуется настройка
COPY default.conf /etc/nginx/conf.d/default.conf

# Команда запуска Nginx в контейнере
CMD ["nginx", "-g", "daemon off;"]
