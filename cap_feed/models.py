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
    expires = models.DateTimeField()

    area_desc = models.CharField(max_length=255)
    event = models.CharField(max_length=255)
    geocode_name = models.CharField(max_length=255, blank=True, default='')
    geocode_value = models.CharField(max_length=255, blank=True, default='')
    polygon = models.TextField(max_length=16383, blank=True, default='')
    country = models.ForeignKey(Country, on_delete=models.SET_DEFAULT, default='-1')

    def __str__(self):
        return self.id

'''
class Processing_Format(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    entry = models.CharField(max_length=255, default='atom:entry')
    id =  models.CharField(max_length=255)
    identifier = models.CharField(max_length=255)
    sent = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    msg_type = models.CharField(max_length=255)
    scope = models.CharField(max_length=255)
    urgency = models.CharField(max_length=255)
    severity = models.CharField(max_length=255)
    certainty = models.CharField(max_length=255)
    expires = models.CharField(max_length=255)
    area_desc = models.CharField(max_length=255)
    event = models.CharField(max_length=255)
    geocode = models.CharField(max_length=255, blank=True, null=True)
    geocode_name = models.CharField(max_length=255,blank=True, null=True)
    geocode_value = models.CharField(max_length=255,blank=True, null=True)
    polygon = models.CharField(max_length=255, blank=True, null=True)
'''

class Feed(models.Model):
    #Create a field that has interval of 1 second starting from 0:01 to 0:59 and a interval of 15 from 1:00 to 59:45
    INTERVAL_CHOICES = []
    for sec in range(30,135, 15):
        filled_min = str(sec//60).zfill(2)
        filled_second = str(sec%60).zfill(2)
        INTERVAL_CHOICES.append((sec, f"{filled_min}:{filled_second}"))

        '''
        if min == 0:
            for sec in range(60):
                filled_min = str(min).zfill(2)
                filled_second = str(sec).zfill(2)
                if min != 0 or sec != 0:
                    INTERVAL_CHOICES.append((min * 60 + sec, f"{filled_min}:{filled_second}"))
        else:
            for sec in range(0,60,15):
                filled_min = str(min).zfill(2)
                filled_second = str(sec).zfill(2)
                if min != 0 or sec != 0:
                    INTERVAL_CHOICES.append((min * 60 + sec, f"{filled_min}:{filled_second}"))
        '''
    url = models.CharField(primary_key=True, max_length=255)
    polling_rate = models.IntegerField(null=False, choices=INTERVAL_CHOICES)
    verification_keys = models.CharField(blank=True,null=True, max_length=255)
    iso3 = models.CharField(null=False, max_length=255)
    format = models.CharField(null=False, max_length=255)
    atom = models.CharField(null=False,max_length=255)
    cap = models.CharField(null=False, max_length=255)
    #This function is to be used for serialisation
    def to_dict(self):
        dictionary = dict()
        dictionary['url'] = self.url
        dictionary['polling_rate'] = self.polling_rate
        if self.verification_keys != None:
            dictionary['verification_keys'] = self.verification_keys
        dictionary['iso3'] = self.iso3
        dictionary['format'] = self.format
        dictionary['atom'] = self.atom
        dictionary['cap'] = self.cap
        return dictionary
def serialise_feed_list(feed_list):
    serialised_list = []
    for feed in feed_list:
        serialised_list.append(feed.to_dict())
    return serialised_list
class FeedEncoder(json.JSONEncoder):
    def default(self, obj):
        #This method converts the list of feed into a list of serialised dictionary
        #if isinstance(obj, list):
        #    feed_list = []
        #    for feed in obj:
        #        if isinstance(feed, Feed):
        #            feed_list.append(feed.to_dict())
        #    return feed_list
        if isinstance(obj, Feed):
            return obj.to_dict()

        return super().default(obj)