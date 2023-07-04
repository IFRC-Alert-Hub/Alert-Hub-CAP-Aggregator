import os
module_dir = os.path.dirname(__file__)  # get current directory
import json
import requests

import xml.etree.ElementTree as ET
import pytz
from .models import Alert, Continent, Region, Country, Source
from datetime import datetime
from django.utils import timezone

# inject source configurations if not already present
def inject_sources():
    source_data = [
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france", "FRA", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-belgium", "BEL", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-austria", "AUT", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-slovakia", "SVK", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-slovenia", "SVN", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-bosnia-herzegovina", "BIH", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-bulgaria", "BGR", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-croatia", "HRV", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-cyprus", "CYP", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-czechia", "CZE", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-denmark", "DNK", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-estonia", "EST", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-finland", "FIN", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-greece", "GRC", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-hungary", "HUN", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://alert.metservice.gov.jm/capfeed.php", "JAM", "capfeedphp", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
    ]

    if Source.objects.count() == 0:
        for source_entry in source_data:
            source = Source()
            source.url = source_entry[0]
            source.polling_interval = 60
            source.iso3 = source_entry[1]
            source.format = source_entry[2]
            source.atom = source_entry[3]['atom']
            source.cap = source_entry[3]['cap']
            source.save()

# inject region and country data if not already present
def inject_geographical_data():
    if Continent.objects.count() == 0:
        inject_continents()
        # inject unknown continent for alerts without a defined continent
        unknown_continent = Continent()
        unknown_continent.id = -1
        unknown_continent.name = 'Unknown'
        unknown_continent.save()
    if Region.objects.count() == 0:
        inject_regions()
        # inject unknown region for alerts without a defined region
        unknown_region = Region()
        unknown_region.id = -1
        unknown_region.name = 'Unknown'
        unknown_region.save()
    if Country.objects.count() == 0:
        inject_countries()
        # inject unknown country for alerts without a defined country
        unknown_country = Country()
        unknown_country.id = -1
        unknown_country.name = 'Unknown'
        unknown_country.save()

# inject continent data
def inject_continents():
    file_path = os.path.join(module_dir, 'geographical/continents.json')
    with open(file_path) as file:
        continent_data = json.load(file)
        for continent_entry in continent_data:
            continent = Continent()
            continent.id = continent_entry["id"]
            continent.name = continent_entry["name"]
            continent.save()

# inject region data
def inject_regions():
    file_path = os.path.join(module_dir, 'geographical/ifrc-regions.json')
    with open(file_path) as file:
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
    ifrc_countries = {}
    file_path = os.path.join(module_dir, 'geographical/ifrc-countries-and-territories.json')
    with open(file_path) as file:
        country_data = json.load(file)
        for index, feature in enumerate(country_data):
            name = feature["name"]
            region_id = feature["region"]
            iso3 = feature["iso3"]
            if ("Region" in name) or ("Cluster" in name) or (region_id is None) or (iso3 is None):
                continue
            ifrc_countries[iso3] = region_id
    processed_iso3 = set()
    file_path = os.path.join(module_dir, 'geographical/opendatasoft-countries-and-territories.geojson')
    with open(file_path) as file:
        country_data = json.load(file)
        for index, feature in enumerate(country_data['features']):
            country = Country()
            country.id = index
            country.name = feature['properties']['name']
            country.iso3 = feature['properties']['iso3']
            status = feature['properties']['status']
            if status == 'Occupied Territory (under review)' or status == 'PT Territory':
                    continue
            if (country.iso3 in ifrc_countries):
                country.region = Region.objects.filter(id = ifrc_countries[country.iso3]).first()
                country.continent = Continent.objects.filter(name = feature['properties']['continent']).first()
                coordinates = feature['geometry']['coordinates']
                if len(coordinates) == 1:
                    country.polygon = coordinates
                else:
                    country.multipolygon = coordinates
                
                latitude = feature['properties']['geo_point_2d']['lat']
                longitude = feature['properties']['geo_point_2d']['lon']
                country.centroid = f'[{longitude}, {latitude}]'

                #"properties":{"geo_point_2d":{"lon":31.49752845618843,"lat":-26.562642190929807},

                country.save()
            processed_iso3.add(country.iso3)

# converts CAP1.2 iso format datetime string to datetime object in UTC timezone
def convert_datetime(original_datetime):
    return datetime.fromisoformat(original_datetime).astimezone(pytz.timezone('UTC'))

# gets alerts from sources and processes them different for each source format
def poll_new_alerts(sources):
    # list of sources and configurations
    for source in sources:
        url = source["url"]
        iso3 = source["iso3"]
        format = source["format"]
        ns = {"atom":source["atom"], "cap": source["cap"]}
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
            alert.source = Source.objects.get(url=url)

            alert.id = entry.find('atom:id', ns).text
            alert.identifier = entry.find('cap:identifier', ns).text
            
            #sender needs to be fixed
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
            if geocode is not None:
                alert.geocode_name = geocode.find('atom:valueName', ns).text
                alert.geocode_value = geocode.find('atom:value', ns).text
            alert.country = Country.objects.get(iso3=iso3)
            alert.save()
        except Exception as e:
            print("get_alert_meteoalarm", e)

# processing for capfeedphp format, example: https://alert.metservice.gov.jm/capfeed.php
def get_alert_capfeedphp(url, iso3, ns):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for entry in root.findall('atom:entry', ns):
        try:
            alert = Alert()
            alert.source = Source.objects.get(url=url)

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
            alert.country = Country.objects.get(iso3=iso3)
            alert.save()
        except Exception as e:
            print("get_alert_capfeedphp", e)

def remove_expired_alerts():
    Alert.objects.filter(expires__lt=timezone.now()).delete()