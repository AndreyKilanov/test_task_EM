#!/bin/bash
set -e

if [ "$DEBUG" = "False" ]; then
    echo "Waiting for PostgreSQL..."

    until pg_isready -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME"; do
      echo "PostgreSQL is unavailable - sleeping"
      sleep 1
    done

    echo "PostgreSQL is ready!"
fi

echo "Making migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Creating superuser..."
python manage.py create_su

echo "Creating access control..."
python manage.py init_access_control

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
if [ "$DEBUG" = "True" ]; then
    python manage.py runserver 0.0.0.0:8000
else
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
fi