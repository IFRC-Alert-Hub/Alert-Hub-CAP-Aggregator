from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.

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
    geocode_name = models.CharField(max_length=255)
    geocode_value = models.CharField(max_length=255)

    def __str__(self):
        return self.id