import json

from .models import SourceEncoder
from django.http import HttpResponse
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_celery_beat.models import PeriodicTask
    

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
    return HttpResponse("Done")

# Adds source to a periodic task
def add_source(source):
    interval = source.polling_interval
    existing_task = PeriodicTask.objects.filter(schedule=interval).first()
    # If there is no task with the same interval, create a new one
    if existing_task is None:
        task_name = 'Polling Every ' + str(interval) + ' Seconds'
        new_task = PeriodicTask.objects.create(
            schdule=interval,
            name=task_name,
            task='cap_feed.tasks.get_alerts',
            start_time=timezone.now(),
            kwargs=json.dumps({"sources": [source]}, cls=SourceEncoder),
        )
        new_task.save()
    # If there is a task with the same interval, add the source to the task
    else:
        kwargs = json.loads(existing_task.kwargs)
        kwargs["sources"].append(source)
        existing_task.kwargs = json.dumps(kwargs, cls=SourceEncoder)
        existing_task.save()

# Removes source from a periodic task
def remove_source(source):
    interval = source.polling_interval
    existing_task = PeriodicTask.objects.filter(schedule=interval).first()
    # If there is no task with the same interval, thats a problem
    if existing_task is None:
        print("There is no periodic task with the same interval")
    # If there is a task with the same interval, remove the source from the task
    else:
        kwargs = json.loads(existing_task.kwargs)
        kwargs["sources"].remove(source.url)
        existing_task.kwargs = json.dumps(kwargs, cls=SourceEncoder)
        existing_task.save()

def update_source(source, previous_url, previous_interval):
    # Remove the source with old configurations
    new_url = source.url
    new_interval = source.polling_interval
    source.url = previous_url
    source.polling_interval = previous_interval
    remove_source(source)

    # Add the updated source again
    source.url = new_url
    source.polling_interval = new_interval
    add_source(source)