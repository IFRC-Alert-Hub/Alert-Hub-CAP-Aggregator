import datetime
import json

from django.http import HttpResponse
from django.template import loader
from .models import Alert, Region, Country, Feed, FeedEncoder
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import cap_feed.alert_processing as ap
from django_celery_beat.models import PeriodicTask




def index(request):
    ap.injectUnknownRegions()
    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))


def polling_alerts(request):
    # To optimise the performance and decrease the number of tasks created with the same interval
    # I will record a dictionary where the key is polling rate of the feeds and value is a list of feeds
    polling_rate_map = dict()
    for feed in Feed.objects.all():
        if str(feed.polling_rate) not in polling_rate_map.keys():
            polling_rate_map[str(feed.polling_rate)] = [feed]
        else:
            polling_rate_map[str(feed.polling_rate)].append(feed)

    # For tasks with the same polling rate, I will generate a task that runs them together.
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

def create_new_feed_task(feed, task_name, polling_rate):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=polling_rate,
        period=IntervalSchedule.SECONDS,
    )
    task = PeriodicTask.objects.create(
        interval=schedule,
        name=task_name,
        task='cap_feed.tasks.getAlerts',
        start_time=datetime.datetime.now(),
        kwargs=json.dumps({"feeds": [feed]}, cls=FeedEncoder),
    )
    task.save()

def append_feed_info(feed,task_name):
    periodic_task = PeriodicTask.objects.get(name=task_name)
    kwargs = json.loads(periodic_task.kwargs)
    kwargs["feeds"].append(feed)
    periodic_task.kwargs = json.dumps(kwargs, cls=FeedEncoder)
    periodic_task.save()

def delete_feed_info(task_name, url):
    periodic_task = PeriodicTask.objects.get(name=task_name)
    kwargs = json.loads(periodic_task.kwargs)
    updated_feed = {}
    # Find and Remove the pervious information about the feed, Append new one
    for feed_info in kwargs["feeds"]:
        if feed_info["url"] == url:
            updated_feed = feed_info
    if updated_feed != {}:
        kwargs["feeds"].remove(updated_feed)
        #If there is no feed to poll in this task, then remove it.
        if len(kwargs["feeds"]) == 0:
            periodic_task.delete()
            print("Delete Successfully!")
        else:
            periodic_task.kwargs = json.dumps(kwargs, cls=FeedEncoder)
            periodic_task.save()
            print("Delete Successfully!")
    else:
        print("The feed info is not found in the task.")
def polling_alerts_from_new_feeds(feed):
    polling_rate = str(feed.polling_rate)
    task_name = 'Polling Every ' + polling_rate + ' Seconds'
    # Finding the task that has the same polling rate with the feed
    # If there is one task, append the feed information for polling
    try:
        append_feed_info(feed, task_name)
    # If there is no such task, create one
    except PeriodicTask.DoesNotExist:
        create_new_feed_task(feed,task_name,polling_rate)


#This function is used whenever a existing feed is updated and the polling rate is not changed
def polling_alerts_from_updated_feeds(feed):
    polling_rate = str(feed.polling_rate)
    url = str(feed.url)
    task_name = 'Polling Every ' + polling_rate + ' Seconds'
    try:
        periodic_task = PeriodicTask.objects.get(name=task_name)
        kwargs = json.loads(periodic_task.kwargs)
        updated_feed = {}
        # Find and Remove the pervious information about the feed, Append new one
        for feed_info in kwargs["feeds"]:
            if feed_info["url"] == url:
                updated_feed = feed_info
        if updated_feed != {}:
            kwargs["feeds"].remove(updated_feed)
            kwargs["feeds"].append(feed)
            periodic_task.kwargs = json.dumps(kwargs, cls=FeedEncoder)
            periodic_task.save()
            print("Update Successfully")
    # Logically, an updated feed should have a corresponding tasks, but if not, the program will create new one
    except:
        print("The existing feeds do not have an associated task! The program will create new one!")
        create_new_feed_task(feed, task_name, polling_rate)

#This function is used whenever a existing feed is updated and the polling rate is changed
def update_feeds_polling_rate(feed, original_polling_rate):
    # Finding the previous task that polls from these feed, and Delete the feed info from the task
    polling_rate = str(feed.polling_rate)
    original_polling_rate = str(original_polling_rate)
    url = str(feed.url)
    task_name = 'Polling Every ' + original_polling_rate + ' Seconds'
    new_task_name = 'Polling Every ' + polling_rate + ' Seconds'
    try:
        delete_feed_info(task_name,url)
    except:
        print("The existing feeds do not have an associated task! Please delete it and re-create one!")

    # Append the updated feed info into new task
    try:
        # 1) Find if there is a task with the new polling rate
        #    If so, append the task info
        append_feed_info(feed, new_task_name)
    except PeriodicTask.DoesNotExist:
        # 2) If not existed, create new task
        create_new_feed_task(feed, new_task_name, polling_rate)

#This function is used whenever a existing feed is deleted
def deleting_feed_info_in_task(feed):
    polling_rate = str(feed.polling_rate)
    url = str(feed.url)
    task_name = 'Polling Every ' + polling_rate + ' Seconds'
    try:
        delete_feed_info(task_name,url)
    # Logically, an updated feed should have a corresponding tasks, but if not, the program will create new one
    except:
        print("The feeds to be deleted do not have an associated task!")
