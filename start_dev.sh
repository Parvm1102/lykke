#!/bin/bash

# Development startup script for Lykke Travel Application

# Exit on any error
set -e

echo "Starting Lykke Travel application in development mode..."

# Set development environment
export DEBUG=True
export ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0"

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

# Start development server with Gunicorn
echo "Starting Gunicorn development server on 0.0.0.0:8000..."
exec gunicorn --bind 0.0.0.0:8000 --workers 1 --reload --log-level debug lykke.wsgi:application
