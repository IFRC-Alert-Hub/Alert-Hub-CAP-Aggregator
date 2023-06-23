import json
import requests
import xml.etree.ElementTree as ET

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader
from .models import Alert, Region, Country


region_centroids = ["17.458740234362434 -2.677413176352464", "-80.83261851536723 -2.6920536197633442", "117.78896429869648 -3.1783208418475954", "30.64725652750233 45.572165430308736", "21.18749859869599 31.264366696701767"]





def index(request):
    getAlerts()
    saveRegions()
    saveCountries()
    latest_alert_list = Alert.objects.order_by("-sent")[:10]
    template = loader.get_template("cap_feed/index.html")
    context = {
        "latest_alert_list": latest_alert_list,
    }
    return HttpResponse(template.render(context, request))


def saveRegions():
    with open('cap_feed/region.json') as file:
        region_data = json.load(file)
        count = 0
        for region_entry in region_data:
            region = Region()
            region.id = region_entry["id"]
            region.name = region_entry["region_name"]
            coordinates = region_entry["bbox"]["coordinates"][0]
            for coordinate in coordinates:
                region.polygon += str(coordinate[0]) + "," + str(coordinate[1]) + " "
            region.centroid = region_centroids[count]
            count += 1
            region.save()


def saveCountries():
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

# sources = [
#     ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
#     ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-croatia", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
#     ]

sources = [
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://alert.metservice.gov.jm/capfeed.php", "capfeedphp", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
    ]


# ignore non-polygon sources for now
def getAlerts():
    for source in sources:
        url, format, ns = source
        match format:
            case "meteoalarm":
                #get_alert_meteoalarm(url, ns)
                pass
            case "capfeedphp":
                get_alert_capfeedphp(url, ns)

# Example: https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france

def get_alert_meteoalarm(url, ns):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for entry in root.findall('atom:entry', ns):
        alert = Alert()
        alert.id = entry.find('atom:id', ns).text
        alert.identifier = entry.find('cap:identifier', ns).text
        alert.sender = url
        alert.sent = entry.find('cap:sent', ns).text
        alert.status = entry.find('cap:status', ns).text
        alert.msg_type = entry.find('cap:message_type', ns).text
        alert.scope = entry.find('cap:scope', ns).text
        alert.urgency = entry.find('cap:urgency', ns).text
        alert.severity = entry.find('cap:severity', ns).text
        alert.certainty = entry.find('cap:certainty', ns).text
        alert.expires = entry.find('cap:expires', ns).text

        alert.area_desc = entry.find('cap:areaDesc', ns).text
        alert.event = entry.find('cap:event', ns).text

        geocode = entry.find('cap:geocode', ns)
        alert.geocode_name = geocode.find('atom:valueName', ns).text
        alert.geocode_value = geocode.find('atom:value', ns).text
        alert.save()

# Example: https://alert.metservice.gov.jm/capfeed.php
def get_alert_capfeedphp(url, ns):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    for entry in root.findall('atom:entry', ns):
        alert = Alert()
        alert.id = entry.find('atom:id', ns).text
        alert.expires = entry.find('cap:expires', ns).text

        entry_content = entry.find('atom:content', ns)
        entry_content_alert = entry_content.find('cap:alert', ns)
        alert.identifier = entry_content_alert.find('cap:identifier', ns).text
        alert.sender = entry_content_alert.find('cap:sender', ns).text
        alert.sent = entry_content_alert.find('cap:sent', ns).text
        alert.status = entry_content_alert.find('cap:status', ns).text
        alert.msg_type = entry_content_alert.find('cap:msgType', ns).text
        alert.scope = entry_content_alert.find('cap:scope', ns).text

        entry_content_alert_info = entry_content_alert.find('cap:info', ns)
        alert.urgency = entry_content_alert_info.find('cap:urgency', ns).text
        alert.severity = entry_content_alert_info.find('cap:severity', ns).text
        alert.certainty = entry_content_alert_info.find('cap:certainty', ns).text
        alert.expires = entry_content_alert_info.find('cap:expires', ns).text
        alert.event = entry_content_alert_info.find('cap:event', ns).text

        entry_content_alert_info_area = entry_content_alert_info.find('cap:area', ns)
        alert.area_desc = entry_content_alert_info_area.find('cap:areaDesc', ns).text
        alert.polygon = entry_content_alert_info_area.find('cap:polygon', ns).text
        alert.save()