import datetime
import json

from django.http import HttpResponse
from django.template import loader
from .models import Alert, Region, Country, Feed, FeedEncoder
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import cap_feed.alert_processing as ap



def index(request):
    ap.injectUnknownRegions()
    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))

def polling_alerts(request):
    #To optimise the performance and decrease the number of tasks created with the same interval
    #I will record a dictionary where the key is polling rate of the feeds and value is a list of feeds
    polling_rate_map = dict()
    for feed in Feed.objects.all():
        if str(feed.polling_rate) not in polling_rate_map.keys():
            polling_rate_map[str(feed.polling_rate)] = [feed]
        else:
            polling_rate_map[str(feed.polling_rate)].append(feed)

    #For tasks with the same polling rate, I will generate a task that runs them together.
    for key, value in polling_rate_map.items():
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=key,
            period=IntervalSchedule.SECONDS,
        )
        task = PeriodicTask.objects.create(
            interval=schedule,  # we created this above.
            name='Polling Every ' + key + ' Seconds',  # simply describes this periodic task.
            task='cap_feed.tasks.getAlerts',  # name of task.
            start_time=datetime.datetime.now(),
            kwargs=json.dumps({"feeds": value}, cls=FeedEncoder),
        )
        task.save()

    return HttpResponse("Done")
