import json
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
from .models import Alert
import time


#Cache alerts in a very intuitive way without any optimisation
def cache_static_alerts():
    alerts_dictionary = {}
    for alert in Alert.objects.all():
        alert_key = alert.id
        alerts_dictionary[alert_key] = alert.to_dict()

    cache.set("static_alerts", alerts_dictionary, timeout=None)
    cache.set("static_alerts_have_been_cached", True, timeout=None)

def get_static_alerts():
    if cache.get("static_alerts_have_been_cached") == None:
        cache_static_alerts()
        return cache.get("static_alerts")
    else:
        return cache.get("static_alerts")

def reset_template():
    cache.delete("static_alerts_have_been_cached")
    cache.delete("static_alerts")
    cache.delete("incoming_alerts")
    cache.delete("removed_alerts")

def cache_dynamic_alerts():
    #Fetch static alerts
    static_alerts = get_static_alerts()
    #Fetch all new incoming alerts
    incoming_alerts = cache.get("incoming_alerts")

    #Appending the incoming alerts
    if incoming_alerts != None:
        static_alerts.update(incoming_alerts)
    #Clear the incoming alerts list
    cache.set("incoming_alerts", {}, timeout=None)

    #Fetch all remored alerts
    removed_alerts = cache.get("removed_alerts")
    #Delete the alerts of removed list in cache
    if removed_alerts != None:
        for alert_id in removed_alerts:
            try:
                del static_alerts[alert_id]

            except Exception as e:
                print(f"Error : {e}")
    #Clear the incoming alerts list
    cache.set("removed_alerts", [], timeout=None)
    cache.set("static_alerts", static_alerts, timeout=None)

    #Convert dictionary into json format
    all_alerts_in_json= json.dumps(static_alerts, indent=None)
    return all_alerts_in_json

def get_all_alerts():
    return cache_dynamic_alerts()

