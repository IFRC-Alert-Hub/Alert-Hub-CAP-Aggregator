import json
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
from .models import Alert
import time


#Cache alerts in a very intuitive way without any optimisation
def cache_all_alerts():
    alerts_list = []
    i = 0
    for alert in Alert.objects.all():
        if i > 2:
            continue
        alerts_list.append(alert.to_dict())
        i += 1
    static_alerts_dictionary = {"all_alerts:": alerts_list}
    # Convert the dictionary to a JSON-formatted string
    static_alerts_in_json = json.dumps(static_alerts_dictionary, indent=4)
    if len(alerts_list) >1:
        static_alerts_in_json = static_alerts_in_json[0:-2] + ","

    cache.set("static_alerts", static_alerts_in_json, timeout=20)
    cache.set("static_alerts_have_been_cached", False, timeout=20)

def get_all_cached_alerts():
    if cache.get("static_alerts_have_been_cached") == None:
        cache_all_alerts()
        return cache.get("static_alerts")
    else:
        return cache.get("static_alerts")

def reset_cached_fragment():
    key = make_template_fragment_key('static_alerts_key')
    cache.delete(key)



