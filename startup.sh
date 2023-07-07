python manage.py migrate
gunicorn --workers 2 --threads 4 --timeout 60 --access-logfile \
    '-' --error-logfile '-' --bind=0.0.0.0:8000 \
     --chdir=/home/site/wwwroot capaggregator.wsgi & daphne -b 0.0.0.0 -p 8001 capaggregator.asgi:application & python manage.py runworker -v2 & celery -A capaggregator worker -l info --pool=solo & celery -A capaggregator beat -l info