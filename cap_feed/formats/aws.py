import requests
import xml.etree.ElementTree as ET
from django.utils import timezone
from cap_feed.models import Alert, AlertInfo, Source
from cap_feed.formats.utils import convert_datetime



# processing for aws format, example: https://cap-sources.s3.amazonaws.com/mg-meteo-en/rss.xml
def get_alerts_aws(url, country, ns):
    # navigate list of alerts
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for alert_entry in root.find('channel').findall('item'):
        try:
            # skip if alert already exists
            id = alert_entry.find('link').text
            if Alert.objects.filter(id=id).exists():
                continue
            
            # register intial alert details
            alert = Alert()
            alert.source_feed = Source.objects.get(url=url)
            alert.country = country
            alert.id = id

            # navigate alert
            alert_response = requests.get(alert.id)
            alert_root = ET.fromstring(alert_response.content)
            alert.identifier = alert_root.find('cap:identifier', ns).text
            alert.sender = alert_root.find('cap:sender', ns).text
            alert.sent = convert_datetime(alert_root.find('cap:sent', ns).text)
            alert.status = alert_root.find('cap:status', ns).text
            alert.msg_type = alert_root.find('cap:msgType', ns).text
            alert.scope = alert_root.find('cap:scope', ns).text

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
                alert_info.effective = alert.sent if (x := alert_info_entry.find('cap:effective', ns)) is None else x.text
                alert_info.onset = convert_datetime(alert_info_entry.find('cap:onset', ns).text)
                alert_info.expires = convert_datetime(alert_info_entry.find('cap:expires', ns).text)
                if alert_info.expires < timezone.now():
                    continue
                alert_info.sender_name = alert_info_entry.find('cap:senderName', ns).text
                alert_info.headline = alert_info_entry.find('cap:headline', ns).text
                alert_info.description = alert_info_entry.find('cap:description', ns).text
                alert_info.instruction = alert_info_entry.find('cap:instruction', ns).text
                alert_info.web = alert_info_entry.find('cap:web', ns).text
                alert_info.contact = alert_info_entry.find('cap:contact', ns).text
                alert.save()
                alert_info.save()

        except Exception as e:
            print("get_alerts_aws", e)
            print("id:", id)