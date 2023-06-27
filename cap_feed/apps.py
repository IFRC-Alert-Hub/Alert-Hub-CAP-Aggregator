from django.apps import AppConfig
from django.db.models.signals import post_delete



class CapFeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cap_feed'
    # Listen to the new registration event of Source
    def ready(self):
        Source = self.get_model("Source")
        post_delete.connect(delete_source, sender=Source)

def delete_source(sender, instance, *args, **kwargs):
    from .models import remove_source
    remove_source(instance)