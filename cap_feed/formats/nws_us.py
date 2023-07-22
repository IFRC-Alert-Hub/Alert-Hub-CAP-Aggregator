import requests
import xml.etree.ElementTree as ET

from cap_feed.models import Alert
from django.utils import timezone
from cap_feed.formats.cap_xml import get_alert
from cap_feed.formats.utils import convert_datetime



# processing for nws_us format, example: https://api.weather.gov/alerts/active
def get_alerts_nws_us(source):
    polled_alerts_count = 0

    # navigate list of alerts
    try:
        response = requests.get(source.url, headers={'Accept': 'application/atom+xml'})
    except requests.exceptions.RequestException as e:
        print("Exception: ", source.format, source.url, e)
        print("It is likely that the connection to this source is unstable.")
        return polled_alerts_count
    root = ET.fromstring(response.content)
    ns = {'atom': source.atom, 'cap': source.cap}
    for alert_entry in root.findall('atom:entry', ns):
        try:
            # skip if alert is expired or already exists
            expires = convert_datetime(alert_entry.find('cap:expires', ns).text)
            id = alert_entry.find('atom:id', ns).text
            if expires < timezone.now() or Alert.objects.filter(id=id).exists():
                continue

            # navigate alert
            cap_link = alert_entry.find('atom:link', ns).attrib['href']
            alert_response = requests.get(cap_link)
            alert_root = ET.fromstring(alert_response.content)
            polled_alerts_count += get_alert(id, alert_root, source, ns)

        except Exception as e:
            print("Exception: ", source.format, source.url, e)
            print("id:", id)

    return polled_alerts_count