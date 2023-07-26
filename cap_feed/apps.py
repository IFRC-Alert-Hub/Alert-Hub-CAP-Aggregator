from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save



class CapFeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cap_feed'
    # Listen to the new registration event of feed
    def ready(self):
        Feed = self.get_model("Feed")
        Alert = self.get_model("Alert")
        post_delete.connect(delete_feed, sender=Feed)
        post_save.connect(cache_incoming_alert, sender=Alert)
        post_delete.connect(cache_removed_alert,sender=Alert)
    
def delete_feed(sender, instance, *args, **kwargs):
    from .models import remove_feed
    remove_feed(instance)

def cache_incoming_alert(sender, instance, *args, **kwargs):
    from django.core.cache import cache
    incoming_alerts = cache.get("incoming_alerts")
    if instance.all_info_are_added() and incoming_alerts != None:
        incoming_alerts[instance.id] = instance.to_dict()
        # Get the two dictionary corresponding to cache keys
        cache.set("incoming_alerts", incoming_alerts)

def cache_removed_alert(sender, instance, *args, **kwargs):
    from django.core.cache import cache
    removed_alerts = cache.get("removed_alerts")
    if removed_alerts != None:
        print(instance.id)
        removed_alerts.append(instance.id)
        # Get the two dictionary corresponding to cache keys
        cache.set("removed_alerts", removed_alerts)