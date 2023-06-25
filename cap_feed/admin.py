from django.contrib import admin

from .models import Alert, Region, Country, Feed

# Register your models here.

admin.site.register(Alert)
admin.site.register(Region)
admin.site.register(Country)
admin.site.register(Feed)

