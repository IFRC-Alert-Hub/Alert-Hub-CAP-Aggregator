import requests
import xml.etree.ElementTree as ET
from django.utils import timezone
from cap_feed.models import Alert, AlertInfo, AlertInfoParameter, AlertInfoArea, AlertInfoAreaPolygon, AlertInfoAreaCircle, AlertInfoAreaGeocode, Source
from cap_feed.formats.utils import convert_datetime



# processing for nws_us format, example: https://api.weather.gov/alerts/active
def get_alerts_nws_us(url, country, ns):
    # navigate list of alerts
    response = requests.get(url, headers={'Accept': 'application/atom+xml'})
    root = ET.fromstring(response.content)

    for alert_entry in root.findall('atom:entry', ns):
        try:
            # skip if alert is expired or already exists
            expires = convert_datetime(alert_entry.find('cap:expires', ns).text)
            id = alert_entry.find('atom:id', ns).text
            if expires < timezone.now() or Alert.objects.filter(id=id).exists():
                continue

            # register intial alert details
            alert = Alert()
            alert.source_feed = Source.objects.get(url=url)
            alert.country = country
            alert.id = id

            # navigate alert
            cap_link = alert_entry.find('atom:link', ns).attrib['href']
            alert_response = requests.get(cap_link)
            alert_root = ET.fromstring(alert_response.content)
            alert.identifier = alert_root.find('cap:identifier', ns).text
            alert.sender = alert_root.find('cap:sender', ns).text
            alert.sent = convert_datetime(alert_root.find('cap:sent', ns).text)
            alert.status = alert_root.find('cap:status', ns).text
            alert.msg_type = alert_root.find('cap:msgType', ns).text
            alert.scope = alert_root.find('cap:scope', ns).text
            alert.code = alert_root.find('cap:code', ns).text
            if (x := root.find('cap:references', ns)) is not None: alert.references = x.text
            alert.save()

            # navigate alert info
            for alert_info_entry in alert_root.findall('cap:info', ns):
                alert_info = AlertInfo()
                alert_info.alert = alert
                alert_info.language = alert_info_entry.find('cap:language', ns).text
                alert_info.category = alert_info_entry.find('cap:category', ns).text
                alert_info.event = alert_info_entry.find('cap:event', ns).text
                alert_info.response_type = alert_info_entry.find('cap:responseType', ns).text
                alert_info.urgency = alert_info_entry.find('cap:urgency', ns).text
                alert_info.severity = alert_info_entry.find('cap:severity', ns).text
                alert_info.certainty = alert_info_entry.find('cap:certainty', ns).text
                #alert_info.event_code
                alert_info.effective = alert.sent if (x := alert_info_entry.find('cap:effective', ns)) is None else x.text
                if (x := alert_info_entry.find('cap:onset', ns)) is not None: alert_info.onset = convert_datetime(x.text)
                alert_info.expires = convert_datetime(alert_info_entry.find('cap:expires', ns).text)
                if (x := alert_info_entry.find('cap:senderName', ns)) is not None: alert_info.sender_name = x.text
                if (x := alert_info_entry.find('cap:headline', ns)) is not None: alert_info.headline = x.text
                if (x := alert_info_entry.find('cap:description', ns)) is not None: alert_info.description = x.text
                if (x := alert_info_entry.find('cap:instruction', ns)) is not None: alert_info.instruction = x.text
                if (x := alert_info_entry.find('cap:web', ns)) is not None: alert_info.web = x.text
                alert_info.save()

                # navigate alert info parameter
                for alert_info_parameter_entry in alert_info_entry.findall('cap:parameter', ns):
                    alert_info_parameter = AlertInfoParameter()
                    alert_info_parameter.alert_info = alert_info
                    alert_info_parameter.value_name = alert_info_parameter_entry.find('cap:valueName', ns).text
                    alert_info_parameter.value = alert_info_parameter_entry.find('cap:value', ns).text
                    alert_info_parameter.save()

                # navigate alert info area
                for alert_info_area_entry in alert_info_entry.findall('cap:area', ns):
                    alert_info_area = AlertInfoArea()
                    alert_info_area.alert_info = alert_info
                    alert_info_area.area_desc = alert_info_area_entry.find('cap:areaDesc', ns).text
                    if (x := alert_info_area_entry.find('cap:altitude', ns)) is not None: alert_info_area.altitude = x.text
                    if (x := alert_info_area_entry.find('cap:ceiling', ns)) is not None: alert_info_area.ceiling = x.text
                    alert_info_area.save()

                    # navigate alert info area polygon
                    for alert_info_area_polygon_entry in alert_info_area_entry.findall('cap:polygon', ns):
                        alert_info_area_polygon = AlertInfoAreaPolygon()
                        alert_info_area_polygon.alert_info_area = alert_info_area
                        alert_info_area_polygon.value = alert_info_area_polygon_entry.text
                        alert_info_area_polygon.save()

                    # navigate alert info area circle
                    for alert_info_area_circle_entry in alert_info_area_entry.findall('cap:circle', ns):
                        alert_info_area_circle = AlertInfoAreaCircle()
                        alert_info_area_circle.alert_info_area = alert_info_area
                        alert_info_area_circle.value = alert_info_area_circle_entry.text
                        alert_info_area_circle.save()

                    # navigate info area geocode
                    for alert_info_area_geocode_entry in alert_info_area_entry.findall('cap:geocode', ns):
                        alert_info_area_geocode = AlertInfoAreaGeocode()
                        alert_info_area_geocode.alert_info_area = alert_info_area
                        alert_info_area_geocode.value_name = alert_info_area_geocode_entry.find('cap:valueName', ns).text
                        alert_info_area_geocode.value = alert_info_area_geocode_entry.find('cap:value', ns).text
                        alert_info_area_geocode.save()

        except Exception as e:
            print("get_alerts_nws_us:", e)
            print("id:", id)