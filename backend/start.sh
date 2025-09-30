#!/bin/bash
set -e

echo "Making migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Creating superuser..."
python manage.py create_su

echo "Collecting static files..."
python manage.py collectstatic --noinput