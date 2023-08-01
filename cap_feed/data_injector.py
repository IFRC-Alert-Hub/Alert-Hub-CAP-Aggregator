import os
import json
from shapely.geometry import Polygon, MultiPolygon
module_dir = os.path.dirname(__file__)  # get current directory
from .models import Alert, Continent, Region, Country, District, Feed
from cap_feed.formats import format_handler as fh



# inject region and country data if not already present
def inject_geographical_data():
    if Continent.objects.count() == 0:
        print('Injecting continents...')
        inject_continents()
    if Region.objects.count() == 0:
        print('Injecting regions...')
        inject_regions()
    if Country.objects.count() == 0:
        print('Injecting countries...')
        inject_countries()
    if District.objects.count() == 0:
        print('Injecting districts...')
        inject_districts()

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
            if not country.iso3 in ifrc_countries:
                continue
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

            country.save()
            processed_iso3.add(country.iso3)

# inject district data
def inject_districts():
    file_path = os.path.join(module_dir, 'geographical/geoBoundariesCGAZ_ADM1.geojson')
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)
        for feature in data['features']:
            district = District()
            if not 'shapeName' in feature['properties']:
                continue
            district.name = feature['properties']['shapeName']
            iso3 = feature['properties']['shapeGroup']
            country = Country.objects.filter(iso3 = iso3).first()
            if not country:
                continue
            district.country = country
            coordinates = feature['geometry']['coordinates']
            type = feature['geometry']['type']
            if type == 'Polygon':
                district.polygon = json.dumps({'coordinates' : coordinates})
            elif type == 'MultiPolygon':
                district.multipolygon = json.dumps({'coordinates' : coordinates})
            district.save()

# inject feed configurations if not already present
def inject_feeds():
    if Feed.objects.count() == 0:
        print('Injecting districts...')
        # this could be converted to a fixture
        feed_data = [
            ("Meteo France", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france", "FRA", "meteoalarm"),
            ("Zentralanstalt für Meteorologie and Geodynamik", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-austria", "AUT", "meteoalarm"),
            ("Agencije Republike Slovenije za okolje", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-slovenia", "SVN", "meteoalarm"),
            ("Slovenský hydrometeorologický ústav", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-slovakia", "SVK", "meteoalarm"),
            ("Israel Meteorological Service", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-israel", "ISR", "meteoalarm"),
            ("Tanzania Meteorological Authority", "https://cap-sources.s3.amazonaws.com/tz-tma-en/rss.xml", "TZA", "aws"),
            ("Meteo Madagascar", "https://cap-sources.s3.amazonaws.com/mg-meteo-en/rss.xml", "MDG", "aws"),
            ("India Meteorological Department", "https://cap-sources.s3.amazonaws.com/in-imd-en/rss.xml", "IND", "aws"),
            ("Ghana Meteorological Agency", "https://cap-sources.s3.amazonaws.com/gh-gmet-en/rss.xml", "GHA", "aws"),
            ("Cameroon Directorate of National Meteorology", "https://cap-sources.s3.amazonaws.com/cm-meteo-en/rss.xml", "CMR", "aws"),
            ("United States National Weather Service", "https://api.weather.gov/alerts/active", "USA", "nws_us"),
            ("Hydrometcenter of Russia", "https://meteoinfo.ru/hmc-output/cap/cap-feed/en/atom.xml", "RUS", "meteo_ru"),
            ("Uruguayan Institute of Meteorology", "https://www.inumet.gub.uy/reportes/riesgo/rss.xml", "URY", "aws"),
        ]

        for feed_entry in feed_data:
            feed = Feed()
            feed.name = feed_entry[0]
            feed.url = feed_entry[1]
            feed.polling_interval = 60
            feed.country = Country.objects.get(iso3 = feed_entry[2])
            feed.format = feed_entry[3]
            feed.save()