#!/bin/sh
set -e
echo "Ожидаем запуска Postgres..."
while ! nc -z -v db 5432; do
  sleep 1
done

echo "Выполняем миграции..."
python manage.py migrate --noinput

echo "Собираем статику..."
python manage.py collectstatic --noinput

echo "Запускаем Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
