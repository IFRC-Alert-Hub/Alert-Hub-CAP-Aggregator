from django.core.cache import cache
from .models import Alert
import json

def cache_all_alerts():
    # Fetch all instances of the Alert model
    alerts = Alert.objects.all()

    # Convert each alert instance to a dictionary representation
    alert_dicts = [alert.to_dict() for alert in alerts]

    # Store the alert_dicts in the cache using a unique key
    cache_key = 'all_alerts'
    cache.set(cache_key, alert_dicts)

