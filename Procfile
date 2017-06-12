release: python manage.py makemigrations && python manage.py migrate --noinput
web: gunicorn djangobackend.wsgi --log-file -