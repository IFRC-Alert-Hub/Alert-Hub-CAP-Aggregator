import datetime
import json

from django.http import HttpResponse
from django.template import loader
from .models import Alert, Source, SourceEncoder
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import cap_feed.alert_processing as ap
from django_celery_beat.models import PeriodicTask



def index(request):
    ap.inject_unknown_regions()
    ap.inject_sources()
    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))


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
            interval=schedule,  # we created this above.
            name='Polling Every ' + key + ' Seconds',  # simply describes this periodic task.
            task='cap_feed.tasks.get_alerts',  # name of task.
            start_time=datetime.datetime.now(),
            kwargs=json.dumps({"sources": value}, cls=SourceEncoder),
        )
        task.save()
    return HttpResponse("Done")

def create_new_source_task(source, task_name, polling_interval):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=polling_interval,
        period=IntervalSchedule.SECONDS,
    )
    task = PeriodicTask.objects.create(
        interval=schedule,
        name=task_name,
        task='cap_feed.tasks.get_alerts',
        start_time=datetime.datetime.now(),
        kwargs=json.dumps({"sources": [source]}, cls=SourceEncoder),
    )
    task.save()

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

def append_source_info(source,task_name):
    periodic_task = PeriodicTask.objects.get(name=task_name)
    kwargs = json.loads(periodic_task.kwargs)
    kwargs["sources"].append(source)
    periodic_task.kwargs = json.dumps(kwargs, cls=SourceEncoder)
    periodic_task.save()

def delete_source_info(task_name, url):
    periodic_task = PeriodicTask.objects.get(name=task_name)
    kwargs = json.loads(periodic_task.kwargs)
    updated_source = {}
    # Find and Remove the pervious information about the source, Append new one
    for source_info in kwargs["sources"]:
        if source_info["url"] == url:
            updated_source = source_info
    if updated_source != {}:
        kwargs["sources"].remove(updated_source)
        #If there is no source to poll in this task, then remove it.
        if len(kwargs["sources"]) == 0:
            periodic_task.delete()
            print("Delete Successfully!")
        else:
            periodic_task.kwargs = json.dumps(kwargs, cls=SourceEncoder)
            periodic_task.save()
            print("Delete Successfully!")
    else:
        print("The source info is not found in the task.")

def polling_alerts_from_new_sources(source):
    polling_interval = str(source.polling_interval)
    task_name = 'Polling Every ' + polling_interval + ' Seconds'
    # Finding the task that has the same polling rate with the source
    # If there is one task, append the source information for polling
    try:
        append_source_info(source, task_name)
    # If there is no such task, create one
    except PeriodicTask.DoesNotExist:
        create_new_source_task(source,task_name,polling_interval)

#This function is used whenever a existing source is updated and the polling rate is not changed
def polling_alerts_from_updated_sources(source):
    polling_interval = str(source.polling_interval)
    url = str(source.url)
    task_name = 'Polling Every ' + polling_interval + ' Seconds'
    try:
        periodic_task = PeriodicTask.objects.get(name=task_name)
        kwargs = json.loads(periodic_task.kwargs)
        updated_source = {}
        # Find and Remove the pervious information about the source, Append new one
        for source_info in kwargs["sources"]:
            if source_info["url"] == url:
                updated_source = source_info
        if updated_source != {}:
            kwargs["sources"].remove(updated_source)
            kwargs["sources"].append(source)
            periodic_task.kwargs = json.dumps(kwargs, cls=SourceEncoder)
            periodic_task.save()
            print("Update Successfully")
    # Logically, an updated source should have a corresponding tasks, but if not, the program will create new one
    except:
        print("The existing sources do not have an associated task! The program will create new one!")
        create_new_source_task(source, task_name, polling_interval)

#This function is used whenever a existing source is updated and the polling rate is changed
def update_sources_polling_interval(source, original_polling_interval):
    # Finding the previous task that polls from these source, and Delete the source info from the task
    polling_interval = str(source.polling_interval)
    original_polling_interval = str(original_polling_interval)
    url = str(source.url)
    task_name = 'Polling Every ' + original_polling_interval + ' Seconds'
    new_task_name = 'Polling Every ' + polling_interval + ' Seconds'
    try:
        delete_source_info(task_name,url)
    except:
        print("The existing sources do not have an associated task! Please delete it and re-create one!")

    # Append the updated source info into new task
    try:
        # 1) Find if there is a task with the new polling rate
        #    If so, append the task info
        append_source_info(source, new_task_name)
    except PeriodicTask.DoesNotExist:
        # 2) If not existed, create new task
        create_new_source_task(source, new_task_name, polling_interval)

#This function is used whenever a existing source is deleted
def deleting_source_info_in_task(source):
    polling_interval = str(source.polling_interval)
    url = str(source.url)
    task_name = 'Polling Every ' + polling_interval + ' Seconds'
    try:
        delete_source_info(task_name,url)
    # Logically, an updated source should have a corresponding tasks, but if not, the program will create new one
    except:
        print("The sources to be deleted do not have an associated task!")
