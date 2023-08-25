import json
from cap_feed.models import Admin1, AlertAdmin1, Alert, AlertInfo, AlertInfoParameter, AlertInfoArea, AlertInfoAreaPolygon, AlertInfoAreaCircle, AlertInfoAreaGeocode, ExpiredAlert
from django.utils import timezone
from django.db import IntegrityError
from cap_feed.formats.utils import convert_datetime, log_attributeerror, log_integrityerror, log_valueerror
from shapely.geometry import Polygon, MultiPolygon



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
        alert_matched_admin1 = False
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
                expired_alert = ExpiredAlert()
                expired_alert.url = alert.url
                expired_alert.feed = alert.feed
                expired_alert.save()
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
                polygons = []
                for alert_info_area_polygon_entry in alert_info_area_entry.findall('cap:polygon', ns):
                    alert_info_area_polygon = AlertInfoAreaPolygon()
                    alert_info_area_polygon.alert_info_area = alert_info_area
                    alert_info_area_polygon.value = alert_info_area_polygon_entry.text
                    alert_info_area_polygon.save()
                    points = [point.split(',') for point in alert_info_area_polygon_entry.text.strip().split(' ')]
                    polygons.append(Polygon([[point[1],point[0]] for point in points]))

                # check polygon intersection with admin1s
                for polygon in polygons:
                    (min_longitude, min_latitude, max_longitude, max_latitude) = polygon.bounds
                    possible_admin1s = Admin1.objects.filter(country = alert.country, min_longitude__lte=max_longitude, max_longitude__gte=min_longitude, min_latitude__lte=max_latitude, max_latitude__gte=min_latitude)
                    for admin1 in possible_admin1s:
                        admin1_polygon = None
                        if admin1.polygon:
                            polygon_string = '{"coordinates": ' + admin1.polygon + '}'
                            polygon_dict = json.loads(polygon_string)['coordinates'][0]
                            admin1_polygon = Polygon(polygon_dict)
                        elif admin1.multipolygon:
                            multipolygon_string = '{"coordinates": ' + admin1.multipolygon + '}'
                            multipolygon_dict = json.loads(multipolygon_string)['coordinates']
                            polygons = [Polygon(x[0]) for x in multipolygon_dict]
                            admin1_polygon = MultiPolygon(polygons)
                        else:
                            continue
                        if admin1_polygon.intersects(polygon):
                            alert_admin1 = AlertAdmin1()
                            alert_admin1.alert = alert
                            alert_admin1.admin1 = admin1
                            alert_admin1.save()
                            alert_matched_admin1 = True

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

        if alert_has_valid_info:
            if not alert_matched_admin1:
                unknown_admin1 = Admin1.objects.filter(country = alert.country, name = 'Unknown').first()
                if unknown_admin1:
                    alert_admin1 = AlertAdmin1()
                    alert_admin1.alert = alert
                    alert_admin1.admin1 = unknown_admin1
                    alert_admin1.save()
                    alert_matched_admin1 = True

            alert.info_has_been_added()
            alert.save()
            return alert.url, True
    
    except AttributeError as e:
        log_attributeerror(feed, e, url)
    except IntegrityError as e:
        if not 'duplicate key value' in str(e):
            log_integrityerror(feed, e, url)
    except ValueError as e:
        log_valueerror(feed, e, url)

    return alert.url, False