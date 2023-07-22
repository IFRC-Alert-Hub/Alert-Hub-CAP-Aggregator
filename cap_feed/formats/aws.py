import requests
import xml.etree.ElementTree as ET

from cap_feed.models import Alert
from cap_feed.formats.cap_xml import get_alert



# processing for aws format, example: https://cap-sources.s3.amazonaws.com/mg-meteo-en/rss.xml
def get_alerts_aws(source):
    polled_alerts_count = 0

    # navigate list of alerts
    try:
        response = requests.get(source.url)
    except requests.exceptions.RequestException as e:
        print("Exception: ", source.format, source.url, e)
        print("It is likely that the connection to this source is unstable.")
        return polled_alerts_count
    root = ET.fromstring(response.content)
    ns = {'atom': source.atom, 'cap': source.cap}
    for alert_entry in root.find('channel').findall('item'):
        try:
            # skip if alert already exists
            id = alert_entry.find('link').text
            if Alert.objects.filter(id=id).exists():
                continue

            # navigate alert
            alert_response = requests.get(id)
            alert_root = ET.fromstring(alert_response.content)
            polled_alerts_count += get_alert(id, alert_root, source, ns)

        except Exception as e:
            print("Exception: ", source.format, source.url, e)
            print("id:", id)

    return polled_alerts_count