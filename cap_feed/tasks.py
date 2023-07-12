from __future__ import absolute_import, unicode_literals
from celery import shared_task

import cap_feed.alert_processor as ap

@shared_task(bind=True)
def poll_new_alerts(self, sources):
    ap.poll_new_alerts(sources)
    return "poll_new_alerts DONE"

@shared_task(bind=True)
def remove_expired_alerts(self):
    removed_alerts_count = ap.remove_expired_alerts()
    return f"removed {removed_alerts_count} alerts"