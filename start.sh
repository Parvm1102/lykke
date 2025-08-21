#!/bin/bash

# Production startup script for Lykke Travel Application

# Exit on any error
set -e

echo "Starting Lykke Travel application..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional, for first deployment)
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
import os
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username=os.environ.get('ADMIN_USERNAME', 'admin'),
        email=os.environ.get('ADMIN_EMAIL', 'admin@lykke.com'),
        password=os.environ.get('ADMIN_PASSWORD', 'admin123')
    )
    print('Superuser created')
else:
    print('Superuser already exists')
"

# Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn --config gunicorn.conf.py lykke.wsgi:application
