from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import json
import time
from datetime import timedelta


from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_celery_beat.models import PeriodicTask

# Create your models here.

class Continent(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=255)
    polygon = models.TextField(blank=True, default='')
    centroid = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=255)
    iso3 = models.CharField(unique=True, validators=[MinValueValidator(3), MaxValueValidator(3)])
    polygon = models.TextField(blank=True, default='')
    multipolygon = models.TextField(blank=True, default='')
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE)
    centroid = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.iso3 + ' ' + self.name

class Source(models.Model):
    INTERVAL_CHOICES = []
    # [10, 45, 60, 75, 90, 105, 120]
    for interval in range(10, 130, 10):
        INTERVAL_CHOICES.append((interval, f"{interval} seconds"))

    FORMAT_CHOICES = [
        ('meteoalarm', 'meteoalarm'),
        ('aws', 'aws'),
        ('nws_us', 'nws_us'),
        ('meteo_ru', 'meteo_ru')
    ]
    name = models.CharField(max_length=255)
    url = models.CharField(primary_key=True, max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    format = models.CharField(choices=FORMAT_CHOICES)
    polling_interval = models.IntegerField(choices=INTERVAL_CHOICES)
    atom = models.CharField(editable=False, default='http://www.w3.org/2005/Atom')
    cap = models.CharField(editable=False, default='urn:oasis:names:tc:emergency:cap:1.2')
    
    __previous_polling_interval = None
    __previous_url = None

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        self.__previous_polling_interval = self.polling_interval
        self.__previous_url = self.url

    def __str__(self):
        name = self.format + ' ' + str(self.country)
        return name

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self._state.adding:
            add_source(self)
        else:
            update_source(self, self.__previous_url, self.__previous_polling_interval)
        super(Source, self).save(force_insert, force_update, *args, **kwargs)
    
class Alert(models.Model):
    STATUS_CHOICES = [
        ('Actual', 'Actual'),
        ('Exercise', 'Exercise'),
        ('System', 'System'),
        ('Test', 'Test'),
        ('Draft', 'Draft')
    ]

    MSG_TYPE_CHOICES = [
        ('Alert', 'Alert'),
        ('Update', 'Update'),
        ('Cancel', 'Cancel'),
        ('Ack', 'Ack'),
        ('Error', 'Error')
    ]

    SCOPE_CHOICES = [
        ('Public', 'Public'),
        ('Restricted', 'Restricted'),
        ('Private', 'Private')
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    source_feed = models.ForeignKey(Source, on_delete=models.CASCADE)
    id = models.CharField(primary_key=True, max_length=255)

    identifier = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    sent = models.DateTimeField()
    status = models.CharField(choices = STATUS_CHOICES)
    msg_type = models.CharField(choices = MSG_TYPE_CHOICES)
    source = models.CharField(max_length=255, blank=True, default='')
    scope = models.CharField(choices = SCOPE_CHOICES)
    restriction = models.CharField(max_length=255, blank=True, default='')
    addresses = models.TextField(blank=True, default='')
    code = models.CharField(max_length=255, blank=True, default='')
    note = models.TextField(blank=True, default='')
    references = models.TextField(blank=True, default='')
    incidents = models.TextField(blank=True, default='')

    __all_info_added = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__all_info_added = False

    def __str__(self):
        return self.id

    def info_has_been_added(self):
        self.__all_info_added = True

    def all_info_are_added(self):
        return self.__all_info_added
    
# This method will be used for serialization of alert object to be cached into Redis.
    def to_dict(self):
        alert_dict = dict()
        alert_dict['id'] = self.id
        alert_dict['identifier'] = self.identifier
        alert_dict['sender'] = self.sender
        alert_dict['sent'] = self.sent
        alert_dict['status'] = self.status
        alert_dict['msg_type'] = self.msg_type
        alert_dict['source'] = self.source
        alert_dict['scope'] = self.scope
        alert_dict['restriction'] = self.restriction
        alert_dict['addresses'] = self.addresses
        alert_dict['code'] = self.code
        alert_dict['note'] = self.note
        alert_dict['references'] = self.references
        alert_dict['incidents'] = self.incidents
        alert_dict['source_url'] = self.source_feed.url
        alert_dict['source_format'] = self.source_feed.format
        alert_dict['country'] = self.country.name
        alert_dict['iso3'] = self.country.iso3

        info_list = []
        for info in self.info.all():
            info_list.append(info.to_dict())
        alert_dict['info'] = info_list
        return alert_dict

    # This method will be used for serialization of alert object to be transferred by websocket.
    def alert_to_be_transferred_to_dict(self):
        alert_dict = dict()
        #What is the difference between id and identifier?
        alert_dict['id'] = self.id
        alert_dict['country_name'] = self.country.name
        alert_dict['country_id'] = self.country.id
        alert_dict['source_feed'] = self.source_feed.url
        alert_dict['scope'] = self.scope

        first_info = self.info.first()
        if first_info != None:
            alert_dict['urgency'] = first_info.urgency
            alert_dict['severity'] = first_info.severity
            alert_dict['certainty'] = first_info.certainty

        info_list = []
        for info in self.info.all():
            info_list.append(info.alert_info_to_be_transferred_to_dict())
        alert_dict['info'] = info_list

        return alert_dict
    
class AlertCacheEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Alert):
            return obj.to_dict()

        return super().default(obj)

class AlertTransferEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Alert):
            return obj.alert_to_be_transferred_to_dict()

        return super().default(obj)
    
class AlertInfo(models.Model):
    # To dynamically set default expire time
    def default_expire():
        return timezone.now() + timedelta(days=1)

    CATEGORY_CHOICES = [
        ('Geo', 'Geo'),
        ('Met', 'Met'),
        ('Safety', 'Safety'),
        ('Security', 'Security'),
        ('Rescue', 'Rescue'),
        ('Fire', 'Fire'),
        ('Health', 'Health'),
        ('Env', 'Env'),
        ('Transport', 'Transport'),
        ('Infra', 'Infra'),
        ('CBRNE', 'CBRNE'),
        ('Other', 'Other')
    ]

    RESPONSE_TYPE_CHOICES = [
        ('Shelter', 'Shelter'),
        ('Evacuate', 'Evacuate'),
        ('Prepare', 'Prepare'),
        ('Execute', 'Execute'),
        ('Avoid', 'Avoid'),
        ('Monitor', 'Monitor'),
        ('Assess', 'Assess'),
        ('AllClear', 'AllClear'),
        ('None', 'None')
    ]

    URGENCY_CHOICES = [
        ('Immediate', 'Immediate'),
        ('Expected', 'Expected'),
        ('Future', 'Future'),
        ('Past', 'Past'),
        ('Unknown', 'Unknown')
    ]

    SEVERITY_CHOICES = [
        ('Extreme', 'Extreme'),
        ('Severe', 'Severe'),
        ('Moderate', 'Moderate'),
        ('Minor', 'Minor'),
        ('Unknown', 'Unknown')
    ]

    CERTAINTY_CHOICES = [
        ('Observed', 'Observed'),
        ('Likely', 'Likely'),
        ('Possible', 'Possible'),
        ('Unlikely', 'Unlikely'),
        ('Unknown', 'Unknown')
    ]

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="info")
    
    language = models.CharField(max_length=255, blank=True, default='en-US')
    category = models.CharField(choices = CATEGORY_CHOICES)
    event = models.CharField(max_length=255)
    response_type = models.CharField(choices = RESPONSE_TYPE_CHOICES, blank=True, default='')
    urgency = models.CharField(choices = URGENCY_CHOICES)
    severity = models.CharField(choices = SEVERITY_CHOICES)
    certainty = models.CharField(choices = CERTAINTY_CHOICES)
    audience = models.CharField(blank=True, default='')
    event_code = models.CharField(max_length=255, blank=True, default='')
    #effective = models.DateTimeField(default=Alert.objects.get(pk=alert).sent)
    effective = models.DateTimeField(blank=True, default=timezone.now)
    onset = models.DateTimeField(blank=True, null=True)
    expires = models.DateTimeField(blank=True, default=default_expire)
    sender_name = models.CharField(max_length=255, blank=True, default='')
    headline = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, null=True, default=None)
    instruction = models.TextField(blank=True, null=True, default=None)
    web = models.URLField(blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, default='')
    parameter = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return str(self.alert) + ' ' + self.language

    def to_dict(self):
        alert_info_dict = dict()
        alert_info_dict['language'] = self.language
        alert_info_dict['category'] = self.category
        alert_info_dict['event'] = self.event
        alert_info_dict['response_type'] = self.response_type
        alert_info_dict['urgency'] = self.urgency
        alert_info_dict['severity'] = self.severity
        alert_info_dict['certainty'] = self.certainty
        alert_info_dict['audience'] = self.audience
        alert_info_dict['event_code'] = self.event_code
        alert_info_dict['effective'] = self.effective
        alert_info_dict['onset'] = self.onset
        alert_info_dict['expires'] = self.expires
        alert_info_dict['sender_name'] = self.sender_name
        alert_info_dict['headline'] = self.headline
        alert_info_dict['description'] = self.description
        alert_info_dict['instruction'] = self.instruction
        alert_info_dict['web'] = self.web
        alert_info_dict['contact'] = self.contact

        parameter_set = self.alertinfoparameter_set.all()
        parameter_list = []
        for parameter in parameter_set:
            parameter_list.append(parameter.to_dict())
        if len(parameter_list) != 0:
            alert_info_dict['parameter'] = parameter_list

        area_set = self.alertinfoarea_set.all()
        area_list = []
        for area in area_set:
            area_list.append(area.to_dict())
        if len(area_list) != 0:
            alert_info_dict['area'] = area_list

        return alert_info_dict
    
    def alert_info_to_be_transferred_to_dict(self):
        alert_info_dict = dict()
        alert_info_dict['language'] = self.language
        alert_info_dict['category'] = self.category
        alert_info_dict['headline'] = self.headline
        alert_info_dict['description'] = self.description
        alert_info_dict['instruction'] = self.instruction
        return alert_info_dict

class AlertInfoParameter(models.Model):
    alert_info = models.ForeignKey(AlertInfo, on_delete=models.CASCADE)

    value_name = models.CharField(max_length=255)
    value = models.TextField()

    def to_dict(self):
        alert_info_parameter_dict = dict()
        alert_info_parameter_dict['value_name'] = self.value_name
        alert_info_parameter_dict['value'] = self.value
        return alert_info_parameter_dict

class AlertInfoArea(models.Model):
    alert_info = models.ForeignKey(AlertInfo, on_delete=models.CASCADE)

    area_desc = models.TextField()
    altitude = models.CharField(blank=True, default='')
    ceiling = models.CharField(blank=True, default='')

    def __str__(self):
        return str(self.alert_info) + ' ' + self.area_desc
    
    def to_dict(self):
        alert_info_area_dict = dict()
        alert_info_area_dict['area_desc'] = self.area_desc
        alert_info_area_dict['altitude'] = self.altitude
        alert_info_area_dict['ceiling'] = self.ceiling

        area_polygon_set = self.alertinfoareapolygon_set.all()
        area_polygon_list = []
        for area_polygon in area_polygon_set:
            area_polygon_list.append(area_polygon.to_dict())
        if len(area_polygon_list) != 0:
            alert_info_area_dict['polygon'] = area_polygon_list

        area_circle_set = self.alertinfoareacircle_set.all()
        area_circle_list = []
        for area_circle in area_circle_set:
            area_circle_list.append(area_circle.to_dict())
        if len(area_circle_list) != 0:
            alert_info_area_dict['circle'] = area_circle_list

        area_geocode_set = self.alertinfoareageocode_set.all()
        area_geocode_list = []
        for area_geocode in area_geocode_set:
            area_geocode_list.append(area_geocode.to_dict())
        if len(area_geocode_list) != 0:
            alert_info_area_dict['geocode'] = area_geocode_list

        return alert_info_area_dict

class AlertInfoAreaPolygon(models.Model):
    alert_info_area = models.ForeignKey(AlertInfoArea, on_delete=models.CASCADE)

    value = models.TextField()

    def to_dict(self):
        alert_info_area_ploygon_dict = dict()
        alert_info_area_ploygon_dict['value'] = self.value
        return alert_info_area_ploygon_dict

class AlertInfoAreaCircle(models.Model):
    alert_info_area = models.ForeignKey(AlertInfoArea, on_delete=models.CASCADE)

    value = models.TextField()

    def to_dict(self):
        alert_info_area_circle_dict = dict()
        alert_info_area_circle_dict['value'] = self.value
        return alert_info_area_circle_dict


class AlertInfoAreaGeocode(models.Model):
    alert_info_area = models.ForeignKey(AlertInfoArea, on_delete=models.CASCADE)

    value_name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def to_dict(self):
        alert_info_area_geocode_dict = dict()
        alert_info_area_geocode_dict['value_name'] = self.value_name
        alert_info_area_geocode_dict['value'] = self.value
        return alert_info_area_geocode_dict


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
        try:
            new_task = PeriodicTask.objects.create(
                interval = interval_schedule,
                name = 'poll_new_alerts_' + str(interval) + '_seconds',
                task = 'cap_feed.tasks.poll_new_alerts',
                start_time = timezone.now(),
                kwargs = json.dumps({"sources": [source.url]}),
            )
            new_task.save()
        except Exception as e:
            print('Error adding new periodic task', e)
    # If there is a task with the same interval, add the source to the task
    else:
        kwargs = json.loads(existing_task.kwargs)
        kwargs["sources"].append(source.url)
        existing_task.kwargs = json.dumps(kwargs)
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
        if source.url in kwargs["sources"]:
            kwargs["sources"].remove(source.url)
        existing_task.kwargs = json.dumps(kwargs)
        existing_task.save()
        if not kwargs["sources"]:
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