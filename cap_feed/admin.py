from django.contrib import admin
from .models import Alert, AlertInfo, AlertInfoParameter, AlertInfoArea, AlertInfoAreaGeocode, AlertInfoAreaPolygon, AlertInfoAreaCircle, Continent, Region, Country, Feed
from django_celery_beat.models import CrontabSchedule, ClockedSchedule, SolarSchedule, IntervalSchedule
from django_celery_results.models import GroupResult

class AlertInfoAreaGeocodeAdmin(admin.ModelAdmin):
    list_display = ["alert_info_area", "value_name", "value"]

class AlertInfoAreaPolygonAdmin(admin.ModelAdmin):
    list_display = ["alert_info_area", "value"]

class AlertInfoAreaCircleAdmin(admin.ModelAdmin):
    list_display = ["alert_info_area", "value"]

class AlertInfoParameterAdmin(admin.ModelAdmin):
    list_display = ["alert_info", "value_name", "value"]

class AlertInfoAreaAdmin(admin.ModelAdmin):
    list_display = ["alert_info", "area_desc"]

class AlertInfoAdmin(admin.ModelAdmin):
    list_display = ["alert", "language"]
    list_filter = ["alert__feed", "alert__country"]
    search_fields = ["alert__id"]
    fieldsets = [
        ("Administration", {"fields": ["alert"]}),
        ("Alert Info" , {"fields": ["language", "category", "event", "response_type", "urgency", "severity", "certainty", "audience", "event_code", "effective", "onset", "expires", "sender_name", "headline", "description", "instruction", "web", "contact"]}),
    ]

class AlertInfoInline(admin.StackedInline):
    model = AlertInfo
    extra = 0

class AlertAdmin(admin.ModelAdmin):
    list_display = ["id", "feed", "sent", "status", "msg_type", "scope"]
    list_filter = ["feed", "country"]
    search_fields = ["id"]
    fieldsets = [
        ("Administration", {"fields": ["country", "feed"]}),
        ("Alert Header" , {"fields": ["identifier", "sender", "sent", "status", "msg_type", "source", "scope", "restriction", "addresses", "code", "note", "references", "incidents"]}),
    ]
    inlines = [AlertInfoInline]

class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "iso3", "region", "continent"]
    list_filter = ["region", "continent"]
    search_fields = ["name", "iso3"]

class FeedAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "url", "format", "polling_interval"]
    list_filter = ["format", "polling_interval"]
    search_fields = ["url", "country"]



admin.site.register(Alert, AlertAdmin)
#admin.site.register(AlertInfo, AlertInfoAdmin)
#admin.site.register(AlertInfoArea, AlertInfoAreaAdmin)
#admin.site.register(AlertInfoParameter, AlertInfoParameterAdmin)
#admin.site.register(AlertInfoAreaGeocode, AlertInfoAreaGeocodeAdmin)
#admin.site.register(AlertInfoAreaPolygon, AlertInfoAreaPolygonAdmin)
#admin.site.register(AlertInfoAreaCircle, AlertInfoAreaCircleAdmin)
admin.site.register(Continent)
admin.site.register(Region)
admin.site.register(Country, CountryAdmin)
admin.site.register(Feed, FeedAdmin)

admin.site.unregister(GroupResult)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(IntervalSchedule)
