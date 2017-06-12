release: python manage.py makemigrations && python manage.py migrate --noinput --fake
web: gunicorn djangobackend.wsgi --log-file -