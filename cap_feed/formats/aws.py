import requests
import xml.etree.ElementTree as ET

from cap_feed.models import Alert
from cap_feed.formats.cap_xml import get_alert



# processing for aws format, example: https://cap-sources.s3.amazonaws.com/mg-meteo-en/rss.xml
def get_alerts_aws(source):
    identifiers = set()
    polled_alerts_count = 0

    # navigate list of alerts
    try:
        response = requests.get(source.url)
    except requests.exceptions.RequestException as e:
        print(f"Exception from source: {source.url}")
        print("It is likely that the connection to this source is unstable.")
        print(e)
        return identifiers, polled_alerts_count
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
            identifier, polled_alert_count = get_alert(id, alert_root, source, ns)
            identifiers.add(identifier)
            polled_alerts_count += polled_alert_count
        
        except Exception as e:
            print(f"Exception from source: {source.url}")
            print(f"Alert id: {id}")
            print(e)

    return identifiers, polled_alerts_count