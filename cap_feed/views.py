import json
import cap_feed.alert_processing as ap

from django.http import HttpResponse
from django.utils import timezone
from django.template import loader
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_celery_beat.models import PeriodicTask
from .models import Alert, Source, SourceEncoder



def index(request):
    try:
        ap.inject_unknown_regions()
        ap.inject_sources()
        latest_alert_list = Alert.objects.order_by("-sent")[:10]
        template = loader.get_template("cap_feed/index.html")
        context = {
            "latest_alert_list": latest_alert_list,
        }
    except Exception as e:
        print(f"Bug is {e}")
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

def polling_alerts(request):
    # To optimise the performance and decrease the number of tasks created with the same interval
    # I will record a dictionary where the key is polling rate of the sources and value is a list of sources
    polling_interval_map = dict()
    for source in Source.objects.all():
        if str(source.polling_interval) not in polling_interval_map.keys():
            polling_interval_map[str(source.polling_interval)] = [source]
        else:
            polling_interval_map[str(source.polling_interval)].append(source)

    # For tasks with the same polling rate, I will generate a task that runs them together.
    for key, value in polling_interval_map.items():
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=key,
            period=IntervalSchedule.SECONDS,
        )
        task = PeriodicTask.objects.create(
            interval = schedule,
            name = 'poll_new_alerts',
            task = 'cap_feed.tasks.poll_new_alerts',
            start_time = timezone.now(),
            kwargs = json.dumps({"sources": value}, cls=SourceEncoder),
        )
        task.save()
    return HttpResponse("Done")