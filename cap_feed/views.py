import json

import requests
import xml.etree.ElementTree as ET

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from .models import Alert
from .tasks import add


def index(request):
    getAlerts()
    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))

def getAlerts():
    sources = [
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-croatia", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ]
    for source in sources:
        url, ns = source
        getAlert(url, ns)

def getAlert(url, ns):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for entry in root.findall('atom:entry', ns):
        alert = Alert()
        alert.id = entry.find('atom:id', ns).text
        alert.identifier = entry.find('cap:identifier', ns).text
        alert.sender = url
        alert.sent = entry.find('cap:sent', ns).text
        alert.status = entry.find('cap:status', ns).text
        alert.msg_type = entry.find('cap:message_type', ns).text
        alert.scope = entry.find('cap:scope', ns).text
        alert.urgency = entry.find('cap:urgency', ns).text
        alert.severity = entry.find('cap:severity', ns).text
        alert.certainty = entry.find('cap:certainty', ns).text
        alert.expires = entry.find('cap:expires', ns).text

        alert.area_desc = entry.find('cap:areaDesc', ns).text
        alert.event = entry.find('cap:event', ns).text
        geocode = entry.find('cap:geocode', ns)
        alert.geocode_name = geocode.find('atom:valueName', ns).text
        alert.geocode_value = geocode.find('atom:value', ns).text
        alert.save()

def polling_alerts(request):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=60,
        period=IntervalSchedule.SECONDS,
    )
    PeriodicTask.objects.create(
        interval=schedule,  # we created this above.
        name='Polling Every One Minutes',  # simply describes this periodic task.
        task='cap_feed.tasks.getAlerts',  # name of task.
        args=json.dumps(['arg1', 'arg2']),
        kwargs=json.dumps({
            'be_careful': True,
        }),
    )
    return HttpResponse("Done")
