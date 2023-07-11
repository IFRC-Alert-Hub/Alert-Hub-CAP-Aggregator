from django.contrib import admin
from .models import Alert, AlertInfo, Continent, Region, Country, Source
from django_celery_beat.models import CrontabSchedule, ClockedSchedule, SolarSchedule, IntervalSchedule
from django_celery_results.models import GroupResult



class AlertInfoAdmin(admin.ModelAdmin):
    list_display = ["alert", "language"]
    list_filter = ["alert__source_feed"]
    fieldsets = [
        ("Administration", {"fields": ["alert"]}),
        ("Alert Info" , {"fields": ["language", "category", "event", "response_type", "urgency", "severity", "certainty", "audience", "event_code", "effective", "onset", "expires", "sender_name", "headline", "description", "instruction", "web", "contact", "parameter"]}),
    ]

class AlertInfoInline(admin.StackedInline):
    model = AlertInfo
    extra = 0

class AlertAdmin(admin.ModelAdmin):
    list_display = ["id", "source_feed", "sent"]
    list_filter = ["source_feed", "country"]
    fieldsets = [
        ("Administration", {"fields": ["country", "source_feed"]}),
        ("Alert Header" , {"fields": ["identifier", "sender", "sent", "status", "msg_type", "source", "scope", "restriction", "addresses", "code", "note", "references", "incidents"]}),
    ]
    inlines = [AlertInfoInline]

class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "iso3", "region", "continent"]
    list_filter = ["region", "continent"]
    search_fields = ["name", "iso3"]

class SourceAdmin(admin.ModelAdmin):
    list_display = ["url", "country", "format", "polling_interval"]
    list_filter = ["format", "polling_interval"]
    search_fields = ["url", "country"]



admin.site.register(Alert, AlertAdmin)
admin.site.register(AlertInfo, AlertInfoAdmin)
admin.site.register(Continent)
admin.site.register(Region)
admin.site.register(Country, CountryAdmin)
admin.site.register(Source, SourceAdmin)

admin.site.unregister(GroupResult)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(IntervalSchedule)
