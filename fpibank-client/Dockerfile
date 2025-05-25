# Stage 1: Сборка проекта
FROM node:latest as build

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходники
COPY . .

# Собираем проект (Vite, React, Vue и т.д.)
RUN npm run build

# Stage 2: Запуск Nginx для раздачи статики
FROM nginx:latest

# Удаляем стандартные файлы Nginx
RUN rm -rf /usr/share/nginx/html/*

# Копируем собранные файлы из первого этапа
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем пользовательский конфиг Nginx
COPY default.conf /etc/nginx/conf.d/default.conf

# Для Let's Encrypt нам нужна возможность отдавать .well-known/acme-challenge
# Эти пути будут смонтированы через docker-compose
# Сертификаты будут взяты из /etc/letsencrypt/live/ваш_домен/

EXPOSE 80 443

# Запуск Nginx в foreground режиме
CMD ["nginx", "-g", "daemon off;"]