from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .models import Alert, AlertInfo, Source
from django.utils import timezone
import cap_feed.formats.format_handler as fh



@shared_task(bind=True)
def poll_new_alerts(self, sources):
    polled_alerts_count = 0
    for url in sources:
        source = Source.objects.get(url=url)
        # additional persisting alerts to not be deleted
        identifiers = set()
        polled_alerts_count += fh.get_alerts(source, identifiers)
    return f"polled {polled_alerts_count} alerts"

@shared_task(bind=True)
def remove_expired_alerts(self):
    AlertInfo.objects.filter(expires__lt=timezone.now()).delete()
    expired_alerts = Alert.objects.filter(info__isnull=True)
    expired_alerts_count = expired_alerts.count()
    expired_alerts.delete()
    return f"removed {expired_alerts_count} alerts"