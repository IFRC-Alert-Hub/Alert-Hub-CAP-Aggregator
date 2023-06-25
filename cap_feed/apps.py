from django.apps import AppConfig
from django.dispatch import receiver
from django.db.models.signals import post_save





class CapFeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cap_feed'
    #Listen to the new registration event of Feed
    def ready(self):
        Feed = self.get_model("Feed")
        post_save.connect(new_feed_registration, sender=Feed)


def new_feed_registration(sender, instance, created, update_fields, *args, **kwargs):
    if created:
        from . import views
        views.polling_alerts_from_new_feeds(instance)
    elif len(update_fields) != 0 and "polling_rate" in update_fields:
        from . import views
        views.polling_alerts_from_updated_feeds()
