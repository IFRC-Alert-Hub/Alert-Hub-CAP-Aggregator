import json
import cap_feed.alert_processing as ap

from django.http import HttpResponse
from django.utils import timezone
from django.template import loader
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_celery_beat.models import PeriodicTask
from .models import Alert, Source, SourceEncoder



def index(request):
    try:
        ap.inject_geographical_data()
    except Exception as e:
        print(e)
        return HttpResponse(f"Error while injecting geographical data {e}")
    try:
        ap.inject_sources()
    except Exception as e:
        print(e)
        return HttpResponse(f"Error while injecting source data {e}")

    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))
  