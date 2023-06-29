from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import json


from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_celery_beat.models import PeriodicTask

# Create your models here.

class Continent(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Region(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    polygon = models.TextField(max_length=16383, blank=True, default='')
    centroid = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.name

class Country(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    iso3 = models.CharField(max_length=255, blank=True, default='')
    polygon = models.TextField(max_length=16383, blank=True, default='')
    region = models.ForeignKey(Region, on_delete=models.SET_DEFAULT, default='-1')
    continent = models.ForeignKey(Continent, on_delete=models.SET_DEFAULT, default='-1')

    def __str__(self):
        return self.name
    

class Region(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    polygon = models.TextField(max_length=16383, blank=True, default='')
    centroid = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.name

class Country(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    iso = models.CharField(max_length=255, blank=True, default='')
    iso3 = models.CharField(max_length=255, blank=True, default='')
    polygon = models.TextField(max_length=16383, blank=True, default='')
    centroid = models.CharField(max_length=255, blank=True, default='')
    region = models.ForeignKey(Region, on_delete=models.SET_DEFAULT, default='-1')

    def __str__(self):
        return self.name
    
class Alert(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    identifier = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    sent = models.DateTimeField()
    status = models.CharField(max_length=255)
    msg_type = models.CharField(max_length=255)
    scope = models.CharField(max_length=255)
    urgency = models.CharField(max_length=255)
    severity = models.CharField(max_length=255)
    certainty = models.CharField(max_length=255)
    effective = models.DateTimeField()
    effective = models.DateTimeField()
    expires = models.DateTimeField()

    area_desc = models.CharField(max_length=255)
    event = models.CharField(max_length=255)
    geocode_name = models.CharField(max_length=255, blank=True, default='')
    geocode_value = models.CharField(max_length=255, blank=True, default='')
    polygon = models.TextField(max_length=16383, blank=True, default='')
    country = models.ForeignKey(Country, on_delete=models.SET_DEFAULT, default='-1')

    def __str__(self):
        return self.id

class Source(models.Model):
    INTERVAL_CHOICES = []
    # [30, 45, 60, 75, 90, 105, 120]
    for interval in range(30, 135, 15):
        INTERVAL_CHOICES.append((interval, f"{interval} seconds"))

    url = models.CharField(primary_key=True, max_length=255)
    polling_interval = models.IntegerField(null=False, choices=INTERVAL_CHOICES)
    verification_keys = models.CharField(blank=True, null=True, max_length=255)
    iso3 = models.CharField(null=False, max_length=255)
    format = models.CharField(null=False, max_length=255)
    atom = models.CharField(null=False,max_length=255)
    cap = models.CharField(null=False, max_length=255)
    
    __previous_polling_interval = None
    __previous_url = None

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        self.__previous_polling_interval = self.polling_interval
        self.__previous_url = self.url

    def __str__(self):
        return self.url

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self._state.adding:
            add_source(self)
        else:
            update_source(self, self.__previous_url, self.__previous_polling_interval)
        super(Source, self).save(force_insert, force_update, *args, **kwargs)

    #This function is to be used for serialisation
    def to_dict(self):
        dictionary = dict()
        dictionary['url'] = self.url
        dictionary['polling_interval'] = self.polling_interval
        if self.verification_keys != None:
            dictionary['verification_keys'] = self.verification_keys
        dictionary['iso3'] = self.iso3
        dictionary['format'] = self.format
        dictionary['atom'] = self.atom
        dictionary['cap'] = self.cap
        return dictionary

class SourceEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Source):
            return obj.to_dict()

        return super().default(obj)
    


# Adds source to a periodic task
def add_source(source):
    interval = source.polling_interval
    interval_schedule = IntervalSchedule.objects.filter(every=interval, period='seconds').first()
    if interval_schedule is None:
        interval_schedule = IntervalSchedule.objects.create(every=interval, period='seconds')
        interval_schedule.save()
    alert_tasks = PeriodicTask.objects.filter(task='cap_feed.tasks.poll_new_alerts')
    existing_task = None
    for alert_task in alert_tasks:
        if alert_task.interval.every == interval and alert_task.interval.period == 'seconds':
            existing_task = alert_task
            break
    # If there is no task with the same interval, create a new one
    if existing_task is None:
        new_task = PeriodicTask.objects.create(
            interval = interval_schedule,
            name = 'poll_new_alerts',
            task = 'cap_feed.tasks.poll_new_alerts',
            start_time = timezone.now(),
            kwargs = json.dumps({"sources": [source]}, cls=SourceEncoder),
        )
        new_task.save()
    # If there is a task with the same interval, add the source to the task
    else:
        kwargs = json.loads(existing_task.kwargs)
        # for kwarg_source in kwargs["sources"]:
        #     print('hello', kwarg_source['url'], source.url)
        #     if kwarg_source['url'] == source.url:
        #         source_to_add = kwarg_source
        #         break
        kwargs["sources"].append(source)
        existing_task.kwargs = json.dumps(kwargs, cls=SourceEncoder)
        existing_task.save()

# Removes source from a periodic task
def remove_source(source):
    interval = source.polling_interval
    interval_schedule = IntervalSchedule.objects.filter(every=interval, period='seconds').first()
    existing_task = PeriodicTask.objects.filter(interval=interval_schedule, task="cap_feed.tasks.poll_new_alerts").first()
    # If there is no task with the same interval, thats a problem
    if existing_task is None:
        print("There is no periodic task with the same interval")
    # If there is a task with the same interval, remove the source from the task
    else:
        kwargs = json.loads(existing_task.kwargs)
        for kwarg_source in kwargs["sources"]:
            if kwarg_source['url'] == source.url:
                source_to_remove = kwarg_source
                break
        kwargs["sources"].remove(source_to_remove)
        existing_task.kwargs = json.dumps(kwargs, cls=SourceEncoder)
        existing_task.save()
        if kwargs == {"sources": []}:
            existing_task.delete()

def update_source(source, previous_url, previous_interval):
    # Remove the source with old configurations
    new_url = source.url
    new_interval = source.polling_interval
    source.url = previous_url
    source.polling_interval = previous_interval
    # Remove entry from database
    source.delete()
    # Add the updated source again
    source.url = new_url
    source.polling_interval = new_interval
    add_source(source)