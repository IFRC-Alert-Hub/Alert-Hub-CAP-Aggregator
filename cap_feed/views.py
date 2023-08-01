import json

from django.http import HttpResponse
from django.template import loader
from .models import Alert

from cap_feed.tasks import inject_data
import cap_feed.alert_cache as ac



def index(request):
    try:
        inject_data.delay()
    except:
        print('Celery not running')

    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))

def reset_template(request):
    ac.reset_template()
    return HttpResponse("Done")

def get_alerts(request):
    return HttpResponse(ac.get_all_alerts())