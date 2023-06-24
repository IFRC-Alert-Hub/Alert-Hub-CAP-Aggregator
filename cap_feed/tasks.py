from __future__ import absolute_import, unicode_literals
from celery import shared_task

import cap_feed.alert_processing as ap

@shared_task(bind=True)
def get_alerts(self):
    ap.get_alerts()
    return "get_alerts DONE"

@shared_task(bind=True)
def remove_expired_alerts(self):
    ap.remove_expired_alerts()
    return "remove_expired_alerts DONE"