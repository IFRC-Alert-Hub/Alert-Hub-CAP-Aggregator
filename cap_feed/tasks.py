from __future__ import absolute_import, unicode_literals
from celery import shared_task

import cap_feed.alert_processing as ap

@shared_task(bind=True)
def getAlerts(self):
    ap.getAlerts()
    return "Done"