from cap_feed.models import Alert
from .meteoalarm import get_alerts_meteoalarm
from .aws import get_alerts_aws
from .nws_us import get_alerts_nws_us
from .meteo_ru import get_alerts_meteo_ru



def get_alerts(source, identifiers):
    # track existing alerts
    existing_alerts = set()
    existing_alerts.update(Alert.objects.filter(source=source).values_list('identifier', flat=True))
    
    match source.format:
        case "meteoalarm":
            new_identifiers, polled_alerts_count, valid_poll = get_alerts_meteoalarm(source)
        case "aws":
            new_identifiers, polled_alerts_count, valid_poll = get_alerts_aws(source)
        case "nws_us":
            new_identifiers, polled_alerts_count, valid_poll = get_alerts_nws_us(source)
        case "meteo_ru":
            new_identifiers, polled_alerts_count, valid_poll = get_alerts_meteo_ru(source)
        case _:
            print("Format not supported")
            new_identifiers, polled_alerts_count, valid_poll = set(), 0, True
    
    if valid_poll:
        identifiers.update(new_identifiers)
        # delete alerts that are no longer active
        Alert.objects.filter(source_feed=source).exclude(identifier__in=identifiers).delete()

    return polled_alerts_count
