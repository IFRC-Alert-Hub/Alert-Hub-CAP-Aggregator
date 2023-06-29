from django.contrib import admin

from .models import Alert, Continent, Region, Country

# Register your models here.

admin.site.register(Alert)
admin.site.register(Continent)
admin.site.register(Region)
admin.site.register(Country)
