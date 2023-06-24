import json
import requests

import xml.etree.ElementTree as ET
import pytz
from .models import Alert, Region, Country
from datetime import datetime
from django.utils import timezone



# inject region and country data if not already present
def inject_unknown_regions():
    if Region.objects.count() == 0:
        inject_regions()
        # inject unknown region for alerts without a defined region
        unknown_region = Region()
        unknown_region.id = -1
        unknown_region.name = "Unknown"
        unknown_region.save()
    if Country.objects.count() == 0:
        inject_countries()
        # inject unknown country for alerts without a defined country
        unknown_country = Country()
        unknown_country.id = -1
        unknown_country.name = "Unknown"
        unknown_country.save()

# inject region data
def inject_regions():
    with open('cap_feed/region.json') as file:
        region_data = json.load(file)
        for region_entry in region_data:
            region = Region()
            region.id = region_entry["id"]
            region.name = region_entry["region_name"]
            region.centroid = region_entry["centroid"]
            coordinates = region_entry["bbox"]["coordinates"][0]
            for coordinate in coordinates:
                region.polygon += str(coordinate[0]) + "," + str(coordinate[1]) + " "
            region.save()

# inject country data
def inject_countries():
    with open('cap_feed/country.json') as file:
        country_data = json.load(file)
        for country_entry in country_data:
            country = Country()
            country.id = country_entry["id"]
            country.name = country_entry["name"]
            region_id = country_entry["region"]
            if ("Region" in country.name) or ("Cluster" in country.name):
                continue
            if region_id is not None:
                country.region = Region.objects.get(id=country_entry["region"])
                if country_entry["iso"] is not None:
                    country.iso = country_entry["iso"]
                if country_entry["iso3"] is not None:
                    country.iso3 = country_entry["iso3"]
                if country_entry["bbox"] is not None:
                    coordinates = country_entry["bbox"]["coordinates"][0]
                    for coordinate in coordinates:
                        country.polygon += str(coordinate[0]) + "," + str(coordinate[1]) + " "
                if country_entry["centroid"] is not None:
                    coordinates = country_entry["centroid"]["coordinates"]
                    country.centroid = str(coordinates[0]) + "," + str(coordinates[1])
                country.save()

# converts CAP1.2 iso format datetime string to datetime object in UTC timezone
def convert_datetime(original_datetime):
    return datetime.fromisoformat(original_datetime).astimezone(pytz.timezone('UTC'))

# gets alerts from sources and processes them different for each source format
def get_alerts():
    # list of sources and configurations
    sources = [
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france", "FRA", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-belgium", "BEL", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-austria", "AUT", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-slovakia", "SVK", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-slovenia", "SVN", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://alert.metservice.gov.jm/capfeed.php", "JAM", "capfeedphp", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
    ]

    for source in sources:
        url, iso3, format, ns = source
        match format:
            case "meteoalarm":
                get_alert_meteoalarm(url, iso3, ns)
            case "capfeedphp":
                get_alert_capfeedphp(url, iso3, ns)

# processing for meteoalarm format, example: https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france
def get_alert_meteoalarm(url, iso3, ns):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for entry in root.findall('atom:entry', ns):
        try:
            alert = Alert()
            alert.id = entry.find('atom:id', ns).text
            alert.identifier = entry.find('cap:identifier', ns).text
            alert.sender = url
            alert.sent = convert_datetime(entry.find('cap:sent', ns).text)
            alert.status = entry.find('cap:status', ns).text
            alert.msg_type = entry.find('cap:message_type', ns).text
            alert.scope = entry.find('cap:scope', ns).text
            alert.urgency = entry.find('cap:urgency', ns).text
            alert.severity = entry.find('cap:severity', ns).text
            alert.certainty = entry.find('cap:certainty', ns).text
            alert.effective = convert_datetime(entry.find('cap:effective', ns).text)
            alert.expires = convert_datetime(entry.find('cap:expires', ns).text)
            if alert.expires < timezone.now():
                continue

            alert.area_desc = entry.find('cap:areaDesc', ns).text
            alert.event = entry.find('cap:event', ns).text

            geocode = entry.find('cap:geocode', ns)
            alert.geocode_name = geocode.find('atom:valueName', ns).text
            alert.geocode_value = geocode.find('atom:value', ns).text
            alert.country = Country.objects.get(iso3=iso3)
            alert.save()
        except:
            pass

# processing for capfeedphp format, example: https://alert.metservice.gov.jm/capfeed.php
def get_alert_capfeedphp(url, iso3, ns):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for entry in root.findall('atom:entry', ns):
        try:
            alert = Alert()
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
            alert.urgency = entry_content_alert_info.find('cap:urgency', ns).text
            alert.severity = entry_content_alert_info.find('cap:severity', ns).text
            alert.certainty = entry_content_alert_info.find('cap:certainty', ns).text
            alert.effective = convert_datetime(entry_content_alert_info.find('cap:effective', ns).text)
            alert.expires = convert_datetime(entry_content_alert_info.find('cap:expires', ns).text)
            if alert.expires < timezone.now():
                continue
            alert.event = entry_content_alert_info.find('cap:event', ns).text

            entry_content_alert_info_area = entry_content_alert_info.find('cap:area', ns)
            alert.area_desc = entry_content_alert_info_area.find('cap:areaDesc', ns).text
            alert.polygon = entry_content_alert_info_area.find('cap:polygon', ns).text
            alert.country = Country.objects.get(iso3=iso3)
            alert.save()
        except:
            pass

def remove_expired_alerts():
    Alert.objects.filter(expires__lt=timezone.now()).delete()