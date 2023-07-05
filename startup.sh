python manage.py migrate
daphne capaggregator.asgi:application -p 8000 & celery -A capaggregator worker -l info --pool=solo & celery -A capaggregator beat -l info