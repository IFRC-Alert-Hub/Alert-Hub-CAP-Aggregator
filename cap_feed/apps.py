import os
import sys

from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save, pre_delete
import json



class CapFeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cap_feed'
    # Listen to the new registration event of feed
    def ready(self):
        if ('WEBSITE_HOSTNAME' in os.environ and 'migrate' not in sys.argv and 'collectstatic'
         not in sys.argv) or ('WEBSITE_HOSTNAME' not in os.environ and 'runserver' in sys.argv):
            from django.core.cache import cache
            result = cache.add('locked', True, timeout=10)
            if result:
                Feed = self.get_model("Feed")
                Alert = self.get_model("Alert")
                post_save.connect(notify_incoming_alert_for_subscription, sender=Alert)
                post_delete.connect(notify_removed_alert_for_subscription, sender=Alert)
                post_delete.connect(delete_feed, sender=Feed)
                post_save.connect(cache_incoming_alert, sender=Alert)
                pre_delete.connect(cache_removed_alert, sender=Alert)

    
def delete_feed(sender, instance, *args, **kwargs):
    from .models import remove_task
    remove_task(instance)

def notify_incoming_alert_for_subscription(sender, instance, *args, **kwargs):
    from capaggregator.celery import app
    if instance.all_info_are_added():
        print("?????????????")
        app.send_task('subscription_manager_dir.tasks.get_incoming_alert', args=[],
                      kwargs={'alert_id': instance.id}, queue='subscription_manager',
                      routing_key='subscription_manager.#', exchange='subscription_manager')

def notify_removed_alert_for_subscription(sender, instance, *args, **kwargs):
    from capaggregator.celery import app
    app.send_task('subscription_manager_dir.tasks.get_removed_alert', args=[],
                  kwargs={'alert_id': instance.id}, queue='subscription_manager',
                  routing_key='subscription_manager.#', exchange='subscription_manager')

def cache_incoming_alert(sender, instance, *args, **kwargs):
    from capaggregator.celery import app
    if instance.all_info_are_added():
        alert_data = {
            'alert_id': instance.id,
            'country_id': instance.country.id,
            'admin1_ids': [alert_admin1.admin1.id for alert_admin1 in instance.alertadmin1_set.all()],
            'info_ids': [info.id for info in instance.infos.all()],
        }

        app.send_task('cache.tasks.cache_incoming_alert', args=[], kwargs=alert_data, queue='cache', routing_key='cache.#', exchange='cache')

def cache_removed_alert(sender, instance, *args, **kwargs):
    from capaggregator.celery import app
    alert_data = {
        'alert_id': instance.id,
        'country_id': instance.country.id,
        'admin1_ids': [alert_admin1.admin1.id for alert_admin1 in instance.alertadmin1_set.all()],
        'info_ids': [info.id for info in instance.infos.all()],
    }
    #print(alert_data)

    app.send_task('cache.tasks.remove_cached_alert', args=[], kwargs=alert_data, queue='cache', routing_key='cache.#', exchange='cache')