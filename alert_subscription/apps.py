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
    if created:
        send_alert_to_channel(instance)
