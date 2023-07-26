from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .models import Alert, AlertInfo, Feed
from django.utils import timezone
import cap_feed.formats.format_handler as fh



@shared_task(bind=True)
def poll_new_alerts(self, feeds):
    polled_alerts_count = 0
    for url in feeds:
        feed = Feed.objects.get(url=url)
        # additional persisting alerts to not be deleted
        alert_urls = set()
        polled_alerts_count += fh.get_alerts(feed, alert_urls)
    return f"polled {polled_alerts_count} alerts"

@shared_task(bind=True)
def remove_expired_alerts(self):
    AlertInfo.objects.filter(expires__lt=timezone.now()).delete()
    expired_alerts = Alert.objects.filter(info__isnull=True)
    expired_alerts_count = expired_alerts.count()
    expired_alerts.delete()
    return f"removed {expired_alerts_count} alerts"