from cap_feed.models import Alert, AlertInfo, AlertInfoParameter, AlertInfoArea, AlertInfoAreaPolygon, AlertInfoAreaCircle, AlertInfoAreaGeocode, FeedLog
from django.utils import timezone
from django.db import IntegrityError
from cap_feed.formats.utils import convert_datetime, log_attributeerror, log_integrityerror



def get_alert(url, alert_root, feed, ns):
    try:
        # register alert
        alert = Alert()
        alert.feed = feed
        alert.country = feed.country
        alert.url = url
        alert.identifier = alert_root.find('cap:identifier', ns).text
        alert.sender = alert_root.find('cap:sender', ns).text
        alert.sent = convert_datetime(alert_root.find('cap:sent', ns).text)
        alert.status = alert_root.find('cap:status', ns).text
        if alert.status != 'Actual':
            return alert.url, False
        alert.msg_type = alert_root.find('cap:msgType', ns).text
        alert.scope = alert_root.find('cap:scope', ns).text
        if (x := alert_root.find('cap:restriction', ns)) is not None: alert.restriction = x.text
        if (x := alert_root.find('cap:addresses', ns)) is not None: alert.addresses = x.text
        if (x := alert_root.find('cap:references', ns)) is not None: alert.references = x.text
        if (x := alert_root.find('cap:code', ns)) is not None: alert.code = x.text
        if (x := alert_root.find('cap:note', ns)) is not None: alert.note = x.text
        if (x := alert_root.find('cap:references', ns)) is not None: alert.references = x.text
        if (x := alert_root.find('cap:incidents', ns)) is not None: alert.incidents = x.text

        alert_has_valid_info = False
        # navigate alert info
        for alert_info_entry in alert_root.findall('cap:info', ns):
            alert_info = AlertInfo()
            alert_info.alert = alert
            if (x := alert_info_entry.find('cap:language', ns)) is not None: alert_info.language = x.text
            alert_info.category = alert_info_entry.find('cap:category', ns).text
            alert_info.event = alert_info_entry.find('cap:event', ns).text
            if (x := alert_info_entry.find('cap:responseType', ns)) is not None: alert_info.response_type = x.text
            alert_info.urgency = alert_info_entry.find('cap:urgency', ns).text
            alert_info.severity = alert_info_entry.find('cap:severity', ns).text
            alert_info.certainty = alert_info_entry.find('cap:certainty', ns).text
            if (x := alert_info_entry.find('cap:audience', ns)) is not None: alert_info.audience = x.text
            alert_info.effective = alert.sent if (x := alert_info_entry.find('cap:effective', ns)) is None else x.text
            if (x := alert_info_entry.find('cap:onset', ns)) is not None: alert_info.onset = convert_datetime(x.text)
            if (x := alert_info_entry.find('cap:expires', ns)) is not None: alert_info.expires = convert_datetime(x.text)
            if alert_info.expires < timezone.now():
                continue
            if (x := alert_info_entry.find('cap:senderName', ns)) is not None: alert_info.sender_name = x.text
            if (x := alert_info_entry.find('cap:headline', ns)) is not None: alert_info.headline = x.text
            if (x := alert_info_entry.find('cap:description', ns)) is not None: alert_info.description = x.text
            if (x := alert_info_entry.find('cap:instruction', ns)) is not None: alert_info.instruction = x.text
            if (x := alert_info_entry.find('cap:web', ns)) is not None: alert_info.web = x.text
            if (x := alert_info_entry.find('cap:contact', ns)) is not None: alert_info.contact = x.text
            alert.save()
            alert_info.save()
            alert_has_valid_info = True

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

        if (alert_has_valid_info):
            alert.info_has_been_added()
            alert.save()
            return alert.url, True
    
    except AttributeError as e:
        log_attributeerror(feed, e, url)
    except IntegrityError as e:
        log_integrityerror(feed, e, url)

    return alert.url, False