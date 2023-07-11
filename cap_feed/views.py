import cap_feed.data_injector as dl
from django.http import HttpResponse
from django.template import loader
from .models import Alert, Source

import cap_feed.alert_processor as ap



def index(request):
    try:
        dl.inject_geographical_data()
        if Source.objects.count() == 0:
            dl.inject_sources()
        #ap.remove_expired_alerts()
        #ap.poll_new_alerts([])
    except Exception as e:
        print(e)
        return HttpResponse(f"Error while injecting data {e}")

    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))
  