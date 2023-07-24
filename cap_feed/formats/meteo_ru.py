import requests
import xml.etree.ElementTree as ET

from cap_feed.models import Alert
from cap_feed.formats.cap_xml import get_alert



# processing for meteo_ru format, example: https://meteoinfo.ru/hmc-output/cap/cap-feed/en/atom.xml
def get_alerts_meteo_ru(source):
    identifiers = set()
    polled_alerts_count = 0

    # navigate list of alerts
    try:
        response = requests.get(source.url)
    except requests.exceptions.RequestException as e:
        print(f"RequestException from source: {source.url}")
        print("It is likely that the connection to this source is unstable.")
        print(e)
        return identifiers, polled_alerts_count
    root = ET.fromstring(response.content)
    ns = {'atom': source.atom, 'cap': source.cap}
    for alert_entry in root.findall('atom:entry', ns):
        try:
            # skip if alert is expired or already exists
            id = alert_entry.find('atom:id', ns).text
            if Alert.objects.filter(id=id).exists():
                continue
            alert_response = requests.get(id)
        except requests.exceptions.RequestException as e:
            print(f"RequestException from source: {source.url}")
            print("It is likely that the connection to this source is unstable.")
            print(e)
        except AttributeError as e:
            print(f"AttributeError from source: {source.url}")
            print(f"Alert id: {id}")
            print("It is likely that the source format has changed and needs to be updated.")
            print(e)
        else:
            # navigate alert
            alert_root = ET.fromstring(alert_response.content)
            identifier, polled_alert_count = get_alert(id, alert_root, source, ns)
            identifiers.add(identifier)
            polled_alerts_count += polled_alert_count

    return identifiers, polled_alerts_count