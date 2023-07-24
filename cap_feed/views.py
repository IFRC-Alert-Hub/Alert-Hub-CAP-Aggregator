import json

import cap_feed.data_injector as dl
from django.http import HttpResponse
from django.template import loader
from .models import Alert, Source
from django.shortcuts import render

import cap_feed.alert_cache as ac



def index(request):
    try:
        dl.inject_geographical_data()
        if Source.objects.count() == 0:
            dl.inject_sources()
    except Exception as e:
        print(e)
        return HttpResponse(f"Error while injecting data {e}")

    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))

def reset_cached_fragment(request):
    ac.reset_cached_fragment()
    return HttpResponse("Done")

def dynamic_view(request):
    context = {"static_alerts" : ac.get_all_cached_alerts()}
    return HttpResponse(render(request, 'cap_feed/rebroadcaster.html', context))