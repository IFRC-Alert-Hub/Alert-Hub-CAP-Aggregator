import requests
import xml.etree.ElementTree as ET

from cap_feed.models import Alert, ExpiredAlert
from django.utils import timezone
from cap_feed.formats.cap_xml import get_alert
from cap_feed.formats.utils import convert_datetime, log_requestexception, log_attributeerror, log_valueerror



# processing for atom format, example: https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france
def get_alerts_atom(feed, ns):
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
    for alert_entry in root.findall('atom:entry', ns):
        try:
            url = alert_entry.find('atom:id', ns).text
            # skip if alert has already been identified as expired
            if ExpiredAlert.objects.filter(url=url).exists():
                continue
            # skip if alert already exists
            if Alert.objects.filter(url=url).exists():
                alert_urls.add(url)
                continue
            # skip if alert is expired
            x = alert_entry.find('cap:expires', ns)
            if not x is None:
                expires = convert_datetime(x.text)
                if expires < timezone.now():
                    expired_alert = ExpiredAlert()
                    expired_alert.url = url
                    expired_alert.feed = feed
                    continue
            alert_response = requests.get(url)
        except requests.exceptions.RequestException as e:
            log_requestexception(feed, e, url)
            valid_poll = False
        except AttributeError as e:
            log_attributeerror(feed, e, url)
            valid_poll = False
        except ValueError as e:
            log_valueerror(feed, e, url)
            valid_poll = False
        else:
            # navigate alert
            alert_root = ET.fromstring(alert_response.content)
            alert_url, polled_alert_count = get_alert(url, alert_root, feed, ns)
            polled_alerts_count += polled_alert_count
            if polled_alert_count:
                alert_urls.add(alert_url)
                

    return alert_urls, polled_alerts_count, valid_poll