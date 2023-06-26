from django.apps import AppConfig
from django.dispatch import receiver
from django.db.models.signals import post_delete





class CapFeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cap_feed'
    #Listen to the new registration event of Source
    def ready(self):
        Source = self.get_model("Source")
        post_delete.connect(existing_source_deletion, sender=Source)


def existing_source_deletion(sender, instance, *args, **kwargs):
    from . import views
    views.deleting_source_info_in_task(instance)