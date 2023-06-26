import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import json

# Create your models here.

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
    #Create a field that has interval of 1 second starting from 0:01 to 0:59 and a interval of 15 from 1:00 to 59:45
    INTERVAL_CHOICES = []
    for sec in range(30, 135, 15):
        filled_min = str(sec//60).zfill(2)
        filled_second = str(sec%60).zfill(2)
        INTERVAL_CHOICES.append((sec, f"{filled_min}:{filled_second}"))

    url = models.CharField(primary_key=True, max_length=255)
    polling_interval = models.IntegerField(null=False, choices=INTERVAL_CHOICES)
    verification_keys = models.CharField(blank=True, null=True, max_length=255)
    iso3 = models.CharField(null=False, max_length=255)
    format = models.CharField(null=False, max_length=255)
    atom = models.CharField(null=False,max_length=255)
    cap = models.CharField(null=False, max_length=255)
    
    __previous_polling_interval = None

    def __init__(self, *args, **kwargs):
        super(Source, self).__init__(*args, **kwargs)
        self.__previous_polling_interval = self.polling_interval

    def __str__(self):
        return self.url

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        #If the Source is created, then add the Source info into corresponding task.
        if self._state.adding:
            from . import views
            views.polling_alerts_from_new_sources(self)

        # When a Source is updated, the program will check if the polling rate is changed:
        # 1) If the polling rate is not changed, update the corresponding task
        # 2) If changed, remove the task that includes the previous info of the Source and append to the new task
        elif self.polling_interval == self.__previous_polling_interval:
            from . import views
            views.polling_alerts_from_updated_sources(self)
            print("Updated_1")
        elif self.polling_interval != self.__previous_polling_interval:
            from . import views
            views.update_sources_polling_interval(self, self.__previous_polling_interval)
            print("Updated_2")
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

def serialise_Source_list(Source_list):
    serialised_list = []
    for Source in Source_list:
        serialised_list.append(Source.to_dict())
    return serialised_list

class SourceEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Source):
            return obj.to_dict()

        return super().default(obj)