# processing for capfeedphp format, example: https://alert.metservice.gov.jm/capfeed.php
def get_alerts_capfeedphp(url, iso3, ns):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for entry in root.findall('atom:entry', ns):
        try:
            alert = Alert()
            alert.source = Source.objects.get(url=url)
            alert.country = Country.objects.get(iso3=iso3)

            alert.id = entry.find('atom:id', ns).text
            entry_content = entry.find('atom:content', ns)
            entry_content_alert = entry_content.find('cap:alert', ns)
            alert.identifier = entry_content_alert.find('cap:identifier', ns).text
            alert.sender = entry_content_alert.find('cap:sender', ns).text
            alert.sent = convert_datetime(entry_content_alert.find('cap:sent', ns).text)
            alert.status = entry_content_alert.find('cap:status', ns).text
            alert.msg_type = entry_content_alert.find('cap:msgType', ns).text
            alert.scope = entry_content_alert.find('cap:scope', ns).text

            entry_content_alert_info = entry_content_alert.find('cap:info', ns)
            alert.event = entry_content_alert_info.find('cap:event', ns).text
            alert.urgency = entry_content_alert_info.find('cap:urgency', ns).text
            alert.severity = entry_content_alert_info.find('cap:severity', ns).text
            alert.certainty = entry_content_alert_info.find('cap:certainty', ns).text
            alert.effective = convert_datetime(entry_content_alert_info.find('cap:effective', ns).text)
            alert.expires = convert_datetime(entry_content_alert_info.find('cap:expires', ns).text)
            if alert.expires < timezone.now():
                continue
            alert.senderName = entry_content_alert_info.find('cap:senderName', ns).text
            alert.description = entry_content_alert_info.find('cap:description', ns).text

            entry_content_alert_info_area = entry_content_alert_info.find('cap:area', ns)
            alert.area_desc = entry_content_alert_info_area.find('cap:areaDesc', ns).text
            #alert.polygon = entry_content_alert_info_area.find('cap:polygon', ns).text
            alert.save()
        except Exception as e:
            print("get_alert_capfeedphp", e)