python manage.py migrate
celery -A capaggregator worker -l info --pool=solo & celery -A capaggregator beat -l info