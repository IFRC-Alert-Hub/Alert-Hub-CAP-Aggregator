import os
import json
module_dir = os.path.dirname(__file__)  # get current directory
from .models import Alert, Continent, Region, Country, Source
from cap_feed.formats import format_handler as fh



# inject region and country data if not already present
def inject_geographical_data():
    if Continent.objects.count() == 0:
        inject_continents()
    if Region.objects.count() == 0:
        inject_regions()
    if Country.objects.count() == 0:
        inject_countries()

# inject continent data
def inject_continents():
    file_path = os.path.join(module_dir, 'geographical/continents.json')
    with open(file_path) as file:
        continent_data = json.load(file)
        for continent_entry in continent_data:
            continent = Continent()
            continent.name = continent_entry["name"]
            continent.save()

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
            region.name = region_entry["region_name"]
            region.centroid = region_entry["centroid"]
            coordinates = region_entry["bbox"]["coordinates"][0]
            for coordinate in coordinates:
                region.polygon += str(coordinate[0]) + "," + str(coordinate[1]) + " "
            region.save()

# inject country data
def inject_countries():
    region_names = {}
    file_path = os.path.join(module_dir, 'geographical/ifrc-regions.json')
    with open(file_path) as file:
        region_data = json.load(file)
        for region_entry in region_data:
            name = region_entry["region_name"]
            region_id = region_entry["id"]
            region_names[region_id] = name

    ifrc_countries = {}
    file_path = os.path.join(module_dir, 'geographical/ifrc-countries-and-territories.json')
    with open(file_path) as file:
        country_data = json.load(file)
        for feature in country_data:
            name = feature["name"]
            region_id = feature["region"]
            iso3 = feature["iso3"]
            if ("Region" in name) or ("Cluster" in name) or (region_id is None) or (iso3 is None):
                continue
            ifrc_countries[iso3] = region_names[region_id]
    
    processed_iso3 = set()
    file_path = os.path.join(module_dir, 'geographical/opendatasoft-countries-and-territories.geojson')
    with open(file_path) as file:
        country_data = json.load(file)
        for feature in country_data['features']:
            country = Country()
            country.name = feature['properties']['name']
            country.iso3 = feature['properties']['iso3']
            status = feature['properties']['status']
            if status == 'Occupied Territory (under review)' or status == 'PT Territory':
                    continue
            if (country.iso3 in ifrc_countries):
                country.region = Region.objects.filter(name = ifrc_countries[country.iso3]).first()
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

# inject source configurations if not already present
def inject_sources():
    # this could be converted to a fixture
    source_data = [
        ("https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france", "FRA", "meteoalarm", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://cap-sources.s3.amazonaws.com/mg-meteo-en/rss.xml", "MDG", "aws", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://cap-sources.s3.amazonaws.com/cm-meteo-en/rss.xml", "CMR", "aws", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
        ("https://api.weather.gov/alerts/active", "USA", "nws_us", {'atom': 'http://www.w3.org/2005/Atom', 'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}),
    ]

    for source_entry in source_data:
        source = Source()
        source.url = source_entry[0]
        source.polling_interval = 60
        source.country = Country.objects.get(iso3 = source_entry[1])
        source.format = source_entry[2]
        source.atom = source_entry[3]['atom']
        source.cap = source_entry[3]['cap']
        source.save()