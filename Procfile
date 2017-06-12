release: python manage.py makemigrations && python manage.py migrate --noinput --fake default
web: gunicorn djangobackend.wsgi --log-file -