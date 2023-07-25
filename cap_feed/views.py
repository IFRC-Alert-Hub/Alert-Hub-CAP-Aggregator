import cap_feed.data_injector as dl
from django.http import HttpResponse
from django.template import loader
from .models import Alert, Feed

import cap_feed.alert_cache as ac



def index(request):
    try:
        dl.inject_geographical_data()
        if Feed.objects.count() == 0:
            dl.inject_feeds()
    except Exception as e:
        print(e)
        return HttpResponse(f"Error while injecting data {e}")

    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))


def cache_all_alert(request):
    ac.cache_all_alerts()
    return HttpResponse("Good Work!")


def get_cached_data(request):
    ac.return_all_cached_alerts()
    return HttpResponse("Good Work!")

def dynamic_view(request):
    context = {
        'static_alert': Alert.objects.all(),
        'dynamic_alert': ac.return_all_cached_alerts(),
    }
    template = loader.get_template("cap_feed/rebroadcaster.html")
    return HttpResponse(template.render(context, request))