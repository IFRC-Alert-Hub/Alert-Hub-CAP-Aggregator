from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .models import Alert, AlertInfo, Feed, Country
from django.utils import timezone
import cap_feed.data_injector as di
import cap_feed.formats.format_handler as fh



@shared_task(bind=True)
def poll_feed(self, url):
    polled_alerts_count = 0
    try:
        feed = Feed.objects.get(url=url)
        if not feed.enable_polling:
            return f"Feed with url {url} is disabled for polling"
        # additional persisting alerts to not be deleted, mainly for testing
        alert_urls = set()
        polled_alerts_count += fh.get_alerts(feed, alert_urls)
    except Feed.DoesNotExist:
        print(f"Feed with url {url} does not exist")
    return f"polled {polled_alerts_count} alerts"

@shared_task(bind=True)
def remove_expired_alerts(self):
    AlertInfo.objects.filter(expires__lt=timezone.now()).delete()
    expired_alerts = Alert.objects.filter(infos__isnull=True)
    expired_alerts_count = expired_alerts.count()
    expired_alerts.delete()
    return f"removed {expired_alerts_count} alerts"

@shared_task(bind=True)
def delete_data(self):
    Country.objects.all().delete()
    return f"deleted data"

@shared_task(bind=True)
def inject_data(self):
    di.inject_geographical_data()
    di.inject_feeds()
    return f"injected data"
