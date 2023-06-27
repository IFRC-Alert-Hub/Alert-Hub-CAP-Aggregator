from __future__ import absolute_import, unicode_literals
from celery import shared_task

import cap_feed.alert_processing as ap

@shared_task(bind=True)
def poll_new_alerts(self, sources):
    ap.get_alerts(sources)
    return "get_alerts DONE"

@shared_task(bind=True)
def remove_expired_alerts(self):
    ap.remove_expired_alerts()
    return "remove_expired_alerts DONE"