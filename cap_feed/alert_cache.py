from django.core.cache import cache
from .models import Alert
import time


#Cache alerts in a very intuitive way without any optimisation
def cache_all_alerts():
    # Fetch all instances of the Alert model
    alerts = Alert.objects.all()

    # Convert each alert instance to a dictionary representation
    alert_dicts = [alert.to_dict() for alert in alerts]

    # Store the alert_dicts in the cache using a unique key
    cache_key = 'all_alerts'
    cache.set(cache_key, alert_dicts, timeout=None)

def return_all_cached_alerts():
    #Set the alert keys
    all_alerts_cache_key = 'all_alerts'
    new_alerts_cache_key = 'new'

    #Get the two dictionary corresponding to cache keys
    start_time1 = time.time()

    #Alert Cache
    all_alerts = cache.get(all_alerts_cache_key)
    # Record the end time
    end_time1 = time.time()

    print(len(all_alerts))

    # Calculate the time spent (in seconds)
    time_spent_seconds1 = end_time1 - start_time1

    # Convert to milliseconds
    time_spent_milliseconds1 = time_spent_seconds1 * 1000

    # Get the two dictionary corresponding to cache keys
    start_time2 = time.time()
    # Fetch all instances of the Alert model
    alerts = list(Alert.objects.all())
    # Record the end time
    end_time2 = time.time()

    # Calculate the time spent (in seconds)
    time_spent_seconds2 = end_time2 - start_time2

    # Convert to milliseconds
    time_spent_milliseconds2 = time_spent_seconds2 * 1000

    # Print the result
    print(f"Time spent (milliseconds), Redis Cache: {time_spent_milliseconds1}, "
          f"Django Model: {time_spent_milliseconds2}")

    #keys = cache.keys('*')
    #print(keys)
    #new_alerts = cache.get(new_alerts_cache_key)
    #Update the alerts with new one
    #all_alerts.update(new_alerts)
    #Set the new cache key
   # cache.set(all_alerts_cache_key, all_alerts)

    #Remove the old alerts
    #cache.delete(new_alerts)
    #return new_alerts