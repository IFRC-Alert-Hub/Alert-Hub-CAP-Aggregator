import requests
import xml.etree.ElementTree as ET
from django.utils import timezone
from cap_feed.models import Alert, Source
from cap_feed.formats.utils import convert_datetime



# processing for capusphp format, example: https://alerts.weather.gov/cap/us.php?x=0
def get_alerts_capusphp(url, country, ns):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for entry in root.findall('atom:entry', ns):
        try:
            alert = Alert()
            alert.source = Source.objects.get(url=url)
            alert.country = country

            alert.id = entry.find('atom:id', ns).text
            
            author = entry.find('atom:author', ns)
            if author is not None:
                alert.sender = author.find('atom:name', ns).text
            alert.event = entry.find('cap:event', ns).text
            alert.effective = convert_datetime(entry.find('cap:effective', ns).text)
            alert.expires = convert_datetime(entry.find('cap:expires', ns).text)
            if alert.expires < timezone.now():
                continue
            alert.status = entry.find('cap:status', ns).text
            alert.msg_type = entry.find('cap:msgType', ns).text
            alert.urgency = entry.find('cap:urgency', ns).text
            alert.severity = entry.find('cap:severity', ns).text
            alert.certainty = entry.find('cap:certainty', ns).text
            alert.area_desc = entry.find('cap:areaDesc', ns).text
            #alert.polygon = entry_content_alert_info_area.find('cap:polygon', ns).text
            geocode = entry.find('cap:geocode', ns)
            if geocode is not None:
                alert.geocode_name = geocode.find('atom:valueName', ns).text
                alert.geocode_value = geocode.find('atom:value', ns).text
            try:
                alert.save()
            except ValueError as e:
                print("type error LMAOOO", e)
        except ValueError as e:
            print("get_alert_capusphp", e)
