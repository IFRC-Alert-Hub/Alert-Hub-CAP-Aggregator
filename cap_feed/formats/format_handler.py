from cap_feed.models import Alert
from .atom import get_alerts_atom
from .rss import get_alerts_rss
from .nws_us import get_alerts_nws_us



def get_alerts(feed, alert_urls):
    # track new alerts
    new_alert_urls = set()
    # track number of alerts polled
    polled_alerts_count = 0
    # track if poll was valid
    valid_poll = False

    
    print(f'Processing feed: {feed}')
    #print(f'Alerts in system: {Alert.objects.filter(feed=feed).count()}')
    
    try:
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}
        match feed.format:
            case "atom":
                new_alert_urls, polled_alerts_count, valid_poll = get_alerts_atom(feed, ns)
            case "rss":
                new_alert_urls, polled_alerts_count, valid_poll = get_alerts_rss(feed, ns)
            case "nws_us":
                new_alert_urls, polled_alerts_count, valid_poll = get_alerts_nws_us(feed, ns)
            case _:
                print(f'Format not supported: {feed}')
                new_alert_urls, polled_alerts_count, valid_poll = set(), 0, True
    except Exception as e:
        print(f'Error getting alerts from {feed.url}: {e}')

    if valid_poll:
        alert_urls.update(new_alert_urls)
        #print(f'Valid alerts in feed: {len(alert_urls)}')
        # delete alerts that are no longer active
        deleted_alerts = Alert.objects.filter(feed=feed).exclude(url__in=alert_urls)
        #print(f'Alerts deleted: {deleted_alerts.count()}')
        deleted_alerts.delete()

    return polled_alerts_count
