python manage.py migrate
python manage.py collectstatic --noinput
daphne -b 0.0.0.0 -p 8000 capaggregator.asgi:application & celery -A capaggregator worker -l info -c 4 & celery -A capaggregator beat -l info