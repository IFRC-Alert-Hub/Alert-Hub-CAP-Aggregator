import requests
import xml.etree.ElementTree as ET

from cap_feed.models import Alert
from cap_feed.formats.cap_xml import get_alert



# processing for meteo_ru format, example: https://meteoinfo.ru/hmc-output/cap/cap-feed/en/atom.xml
def get_alerts_meteo_ru(source):
    polled_alerts_count = 0

    # navigate list of alerts
    response = requests.get(source.url)
    root = ET.fromstring(response.content)
    ns = {'atom': source.atom, 'cap': source.cap}
    for alert_entry in root.findall('atom:entry', ns):
        try:
            # skip if alert is expired or already exists
            id = alert_entry.find('atom:id', ns).text
            if Alert.objects.filter(id=id).exists():
                continue

            # navigate alert
            alert_response = requests.get(id)
            alert_root = ET.fromstring(alert_response.content)
            polled_alerts_count += get_alert(id, alert_root, source, ns)
            
        except Exception as e:
            print("Exception: ", source.format, source.url, e)
            print("id:", id)

import requests
import xml.etree.ElementTree as ET

url = 'https://meteoinfo.ru/hmc-output/cap/cap-feed/en/atom.xml'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}


# except requests.exceptions.RequestException as e: