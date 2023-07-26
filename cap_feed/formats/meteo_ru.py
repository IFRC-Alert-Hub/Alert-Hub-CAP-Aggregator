import requests
import xml.etree.ElementTree as ET

from cap_feed.models import Alert
from cap_feed.formats.cap_xml import get_alert
from cap_feed.formats.utils import log_requestexception, log_attributeerror



# processing for meteo_ru format, example: https://meteoinfo.ru/hmc-output/cap/cap-feed/en/atom.xml
def get_alerts_meteo_ru(feed):
    alert_urls = set()
    polled_alerts_count = 0
    valid_poll = True

    # navigate list of alerts
    try:
        response = requests.get(feed.url)
    except requests.exceptions.RequestException as e:
        log_requestexception(feed, e, None)
        return alert_urls, polled_alerts_count, valid_poll
    root = ET.fromstring(response.content)
    ns = {'atom': feed.atom, 'cap': feed.cap}
    for alert_entry in root.findall('atom:entry', ns):
        try:
            # skip if alert already exists
            url = alert_entry.find('atom:id', ns).text
            if Alert.objects.filter(url=url).exists():
                alert_urls.add(url)
                continue
            alert_response = requests.get(url)
        except requests.exceptions.RequestException as e:
            log_requestexception(feed, e, url)
            valid_poll = False
        except AttributeError as e:
            log_attributeerror(feed, e, url)
            valid_poll = False
        else:
            # navigate alert
            alert_root = ET.fromstring(alert_response.content)
            alert_url, polled_alert_count = get_alert(url, alert_root, feed, ns)
            polled_alerts_count += polled_alert_count
            if polled_alert_count:
                alert_urls.add(alert_url)
                

    return alert_urls, polled_alerts_count, valid_poll