from cap_feed.models import Alert
from .meteoalarm import get_alerts_meteoalarm
from .aws import get_alerts_aws
from .nws_us import get_alerts_nws_us
from .meteo_ru import get_alerts_meteo_ru



def get_alerts(feed, alert_urls):
    # track new alerts
    new_alert_urls = set()
    # track number of alerts polled
    polled_alerts_count = 0
    # track if poll was valid
    valid_poll = False

    
    print(f'Feed: {feed}')
    print(f'Alerts in system: {Alert.objects.filter(feed=feed).count()}')
    
    try:
        match feed.format:
            case "meteoalarm":
                new_alert_urls, polled_alerts_count, valid_poll = get_alerts_meteoalarm(feed)
            case "aws":
                new_alert_urls, polled_alerts_count, valid_poll = get_alerts_aws(feed)
            case "nws_us":
                new_alert_urls, polled_alerts_count, valid_poll = get_alerts_nws_us(feed)
            case "meteo_ru":
                new_alert_urls, polled_alerts_count, valid_poll = get_alerts_meteo_ru(feed)
            case _:
                print("Format not supported")
                new_alert_urls, polled_alerts_count, valid_poll = set(), 0, True
    except Exception as e:
        print(f"Error getting alerts from {feed.url}: {e}")

    if valid_poll:
        alert_urls.update(new_alert_urls)
        print(f'Valid alerts in feed: {len(alert_urls)}')
        # delete alerts that are no longer active
        deleted_alerts = Alert.objects.filter(feed=feed).exclude(id__in=alert_urls)
        print(f'Alerts deleted: {deleted_alerts.count()}')
        deleted_alerts.delete()

    return polled_alerts_count
