import asyncio

from django.apps import AppConfig
from django.db.models.signals import post_save

class AlertSubscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alert_subscription'

    # Listen to the new registration event of alert
    def ready(self):
        from cap_feed.models import Alert
        post_save.connect(send_alert, sender=Alert)

def send_alert(sender, instance, created, *args, **kwargs):
    from .views import send_alert_to_channel
    if instance.all_info_are_added():
        #print(instance.info)
        send_alert_to_channel(instance)

def cache_alert(sender, instance, created, *args, **kwargs):
    from django.core.cache import cache
    if instance.all_info_are_added():
        new_alerts_cache_key = 'new ' + instance.id
        # Get the two dictionary corresponding to cache keys
        cache.set(new_alerts_cache_key, instance.to_dict())