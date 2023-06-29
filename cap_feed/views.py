import json

from django.http import HttpResponse
from django.template import loader
from .models import Alert, Region, Country
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import cap_feed.alert_processing as ap



def index(request):
    ap.inject_geographical_data()
    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))

def polling_alerts(request):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=60,
        period=IntervalSchedule.SECONDS,
    )
    PeriodicTask.objects.create(
        interval=schedule,  # we created this above.
        name='Polls CAP alerts periodically',  # simply describes this periodic task.
        task='cap_feed.tasks.get_alerts',  # name of task.
        args=json.dumps(['arg1', 'arg2']),
        kwargs=json.dumps({
            'be_careful': True,
       }),
    )
    return HttpResponse("DONE")

def removing_alerts(request):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=60,
        period=IntervalSchedule.SECONDS,
    )
    PeriodicTask.objects.create(
        interval=schedule,  # we created this above.
        name='Removes expired CAP alerts periodically',  # simply describes this periodic task.
        task='cap_feed.tasks.remove_expired_alerts',  # name of task.
        args=json.dumps(['arg1', 'arg2']),
        kwargs=json.dumps({
            'be_careful': True,
       }),
    )
    return HttpResponse("DONE")
