import requests
import xml.etree.ElementTree as ET
from django.utils import timezone
from cap_feed.models import Alert, Source
from cap_feed.formats.utils import convert_datetime



# processing for meteoalarm format, example: https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france
def get_alerts_meteoalarm(url, country, ns):
    # navigate list of alerts
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for entry in root.findall('atom:entry', ns):
        try:
            alert = Alert()
            alert.source = Source.objects.get(url=url)
            alert.country = country
            alert.id = entry.find('atom:id', ns).text
            alert.expires = convert_datetime(entry.find('cap:expires', ns).text)
            if alert.expires < timezone.now():
                continue
            
            # navigate alert details
            alert_response = requests.get(alert.id)
            alert_root = ET.fromstring(alert_response.content)
            alert.identifier = alert_root.find('cap:identifier', ns).text
            alert.sender = alert_root.find('cap:sender', ns).text
            alert.sent = convert_datetime(alert_root.find('cap:sent', ns).text)
            alert.status = alert_root.find('cap:status', ns).text
            alert.msg_type = alert_root.find('cap:msgType', ns).text
            alert.scope = alert_root.find('cap:scope', ns).text

            alert_root_info = alert_root.find('cap:info', ns)
            alert.category = alert_root_info.find('cap:category', ns).text
            
            alert.save()
        except Exception as e:
            print("get_alert_meteoalarm", e)