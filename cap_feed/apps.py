from django.apps import AppConfig
from django.dispatch import receiver
from django.db.models.signals import post_delete





class CapFeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cap_feed'
    #Listen to the new registration event of Feed
    def ready(self):
        Feed = self.get_model("Feed")
        post_delete.connect(existing_feed_deletion, sender=Feed)


def existing_feed_deletion(sender, instance, *args, **kwargs):
    from . import views
    views.deleting_feed_info_in_task(instance)