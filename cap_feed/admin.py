from django.contrib import admin

from .models import Alert, Region, Country, Source
from django_celery_beat.models import CrontabSchedule, ClockedSchedule, SolarSchedule, IntervalSchedule
from django_celery_results.models import GroupResult
# Register your models here.

admin.site.register(Alert)
admin.site.register(Region)
admin.site.register(Country)
admin.site.register(Source)
#admin.site.register(Channel)

admin.site.unregister(GroupResult)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(IntervalSchedule)
