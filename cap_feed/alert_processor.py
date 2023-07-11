from .models import Alert, AlertInfo, Source
from django.utils import timezone
import cap_feed.formats.format_handler as fh



# gets alerts from sources and processes them different for each source format
def poll_new_alerts():
    # list of sources and configurations
    for source in Source.objects.all():
        format = source.format
        url = source.url
        country = source.country
        ns = {"atom": source.atom, "cap": source.cap}
        fh.get_alerts(format, url, country, ns)

def remove_expired_alerts():
    AlertInfo.objects.filter(expires__lt=timezone.now()).delete()
    Alert.objects.filter(alertinfo__isnull=True).delete()