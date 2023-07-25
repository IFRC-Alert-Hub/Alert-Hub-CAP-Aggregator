from django.apps import AppConfig
from django.db.models.signals import post_delete



class CapFeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cap_feed'
    # Listen to the new registration event of feed
    def ready(self):
        Feed = self.get_model("Feed")
        post_delete.connect(delete_feed, sender=Feed)

def delete_feed(sender, instance, *args, **kwargs):
    from .models import remove_feed
    remove_feed(instance)