python manage.py migrate
daphne -b 0.0.0.0 -p 8001 capaggregator.asgi:application & celery -A capaggregator worker -l info --pool=solo & celery -A capaggregator beat -l info