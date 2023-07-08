from django.contrib import admin
from .models import Alert, Continent, Region, Country, Source
from django_celery_beat.models import CrontabSchedule, ClockedSchedule, SolarSchedule, IntervalSchedule
from django_celery_results.models import GroupResult



class AlertAdmin(admin.ModelAdmin):
    #list_display = ["id", "source", "urgency", "severity", "certainty", "sent", "effective", "expires"]
    #list_filter = ["source", "urgency", "severity", "certainty", "sent", "effective", "expires"]
    pass

class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "iso3", "region", "continent"]
    list_filter = ["region", "continent"]
    search_fields = ["name", "iso3"]

class SourceAdmin(admin.ModelAdmin):
    list_display = ["url", "country", "format", "polling_interval"]
    list_filter = ["format", "polling_interval"]
    search_fields = ["url", "country"]



admin.site.register(Alert, AlertAdmin)
admin.site.register(Continent)
admin.site.register(Region)
admin.site.register(Country, CountryAdmin)
admin.site.register(Source, SourceAdmin)

admin.site.unregister(GroupResult)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(IntervalSchedule)
