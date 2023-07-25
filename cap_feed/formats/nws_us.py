import requests
import xml.etree.ElementTree as ET

from cap_feed.models import Alert
from django.utils import timezone
from cap_feed.formats.cap_xml import get_alert
from cap_feed.formats.utils import convert_datetime



# processing for nws_us format, example: https://api.weather.gov/alerts/active
def get_alerts_nws_us(feed):
    alert_urls = set()
    polled_alerts_count = 0
    valid_poll = True

    # navigate list of alerts
    try:
        response = requests.get(feed.url, headers={'Accept': 'application/atom+xml'})
    except requests.exceptions.RequestException as e:
        print(f"RequestException from feed: {feed.url}")
        print("It is likely that the connection to this feed is unstable.")
        print(e)
        valid_poll = False
        return alert_urls, polled_alerts_count, valid_poll
    root = ET.fromstring(response.content)
    ns = {'atom': feed.atom, 'cap': feed.cap}
    for alert_entry in root.findall('atom:entry', ns):
        try:
            # skip if alert is expired or already exists
            expires = convert_datetime(alert_entry.find('cap:expires', ns).text)
            id = alert_entry.find('atom:id', ns).text
            if expires < timezone.now():
                continue
            if Alert.objects.filter(id=id).exists():
                alert_urls.add(id)
                continue
            cap_link = alert_entry.find('atom:link', ns).attrib['href']
            alert_response = requests.get(cap_link)
        except requests.exceptions.RequestException as e:
            print(f"RequestException from feed: {feed.url}")
            print("It is likely that the connection to this feed is unstable.")
            print(e)
            valid_poll = False
        except AttributeError as e:
            print(f"AttributeError from feed: {feed.url}")
            print(f"Alert id: {id}")
            print("It is likely that the feed format has changed and needs to be updated.")
            print(e)
            valid_poll = False
        else:
            # navigate alert
            alert_root = ET.fromstring(alert_response.content)
            alert_url, polled_alert_count = get_alert(id, alert_root, feed, ns)
            polled_alerts_count += polled_alert_count
            if polled_alert_count:
                alert_urls.add(alert_url)

    return alert_urls, polled_alerts_count, valid_poll