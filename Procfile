web: gunicorn --config gunicorn.conf.py lykke.wsgi:application
release: python manage.py migrate && python manage.py collectstatic --noinput
