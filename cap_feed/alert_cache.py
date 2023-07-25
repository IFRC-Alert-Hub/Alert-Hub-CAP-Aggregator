import json
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
from .models import Alert
import time


#Cache alerts in a very intuitive way without any optimisation
def cache_static_alerts():
    alerts_list = []
    i = 0
    for alert in Alert.objects.all():
        if i > 1:
            continue
        alerts_list.append(alert.to_dict())
        i += 1
    static_alerts_dictionary = {"static_alerts:": alerts_list}
    # Convert the dictionary to a JSON-formatted string
    static_alerts_in_json = json.dumps(static_alerts_dictionary, indent=4)
    if len(alerts_list) > 0:
        static_alerts_in_json = static_alerts_in_json[0:-2] + ","
    cache.set("static_alerts", static_alerts_in_json, timeout=200)
    cache.set("static_alerts_have_been_cached", True, timeout=200)

def get_static_alerts():
    if cache.get("static_alerts_have_been_cached") == None:
        cache_static_alerts()
        return cache.get("static_alerts")
    else:
        return cache.get("static_alerts")

def reset_template():
    key = make_template_fragment_key('static_alerts_key')
    cache.delete(key)
    cache.delete("dynamic_alerts")
    cache.delete("incoming_alerts")
    cache.delete("removed_alerts")


def cache_dynamic_alerts():
    #Get current dynamic alert parts.
    dynamic_alerts_dictionary = cache.get("dynamic_alerts")

    #Fetch all new incoming alerts
    new_incoming_alerts = cache.get("incoming_alerts")
    #Extending the previous incoming alerts with new one
    if dynamic_alerts_dictionary != None:
        incoming_alerts = dynamic_alerts_dictionary["dynamic_alerts"]["incoming_alerts"]
        incoming_alerts.extend(new_incoming_alerts)
        updated_alerts_dictionary = {"incoming_alerts" : incoming_alerts}
    else:
        incoming_alerts = []
        updated_alerts_dictionary = {"incoming_alerts": incoming_alerts}
    #Fetch all new removed alerts
    new_removed_alerts = cache.get("removed_alerts")
    # Extending the previous expired alerts with new one
    if dynamic_alerts_dictionary != None:
        removed_alerts = dynamic_alerts_dictionary["dynamic_alerts"]["removed_alerts"]
        removed_alerts.extend(new_removed_alerts)
        removed_alerts_dictionary = {"removed_alerts": removed_alerts}
    else:
        removed_alerts = []
        removed_alerts_dictionary = {"removed_alerts": removed_alerts}

    #Update the dynamic alerts
    updated_alerts_dictionary.update(removed_alerts_dictionary)
    if dynamic_alerts_dictionary == None:
        dynamic_alerts_dictionary = {}
    dynamic_alerts_dictionary["dynamic_alerts"] = updated_alerts_dictionary

    #Convert dictionary into json format
    current_dynamic_alerts_in_json= json.dumps(dynamic_alerts_dictionary, indent=4)
    current_dynamic_alerts_in_json = current_dynamic_alerts_in_json[2:]

    #Clear two dynamic sets
    cache.set("incoming_alerts", [], timeout=None)
    cache.set("removed_alerts", [], timeout=None)

    #Update the cache
    cache.set("dynamic_alerts", dynamic_alerts_dictionary, timeout=None)

    return current_dynamic_alerts_in_json

def get_dynamic_alerts():
    current_dynamic_alerts_in_json = cache_dynamic_alerts()
    return current_dynamic_alerts_in_json

