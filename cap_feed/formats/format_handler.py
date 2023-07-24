from cap_feed.models import Alert
from .meteoalarm import get_alerts_meteoalarm
from .aws import get_alerts_aws
from .nws_us import get_alerts_nws_us
from .meteo_ru import get_alerts_meteo_ru



def get_alerts(source):
    # track existing alerts
    existing_alerts = set()
    existing_alerts.update(Alert.objects.filter(source=source).values_list('identifier', flat=True))
    # track number of new alerts
    polled_alerts_count = 0
    # track new alerts
    identifiers = set()
    
    match source.format:
        case "meteoalarm":
            identifiers, polled_alerts_count = get_alerts_meteoalarm(source)
        case "aws":
            identifiers, polled_alerts_count = get_alerts_aws(source)
        case "nws_us":
            identifiers, polled_alerts_count = get_alerts_nws_us(source)
        case "meteo_ru":
            identifiers, polled_alerts_count = get_alerts_meteo_ru(source)
        case _:
            print("Format not supported")

    # delete alerts that are no longer active
    Alert.objects.filter(source=source).exclude(identifier__in=identifiers).delete()

    return polled_alerts_count
