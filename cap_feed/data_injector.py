import os
import json
import requests
module_dir = os.path.dirname(__file__)  # get current directory
from .models import Continent, Region, Country, District, Feed, LanguageInfo



# inject region and country data if not already present
def inject_geographical_data():
    azure_path = None
    if 'WEBSITE_HOSTNAME' in os.environ:
        from capaggregator.production import MEDIA_URL
        azure_path = MEDIA_URL

    if Continent.objects.count() == 0:
        print('Injecting continents...')
        inject_continents(azure_path)
    if Region.objects.count() == 0:
        print('Injecting regions...')
        inject_regions(azure_path)
    if Country.objects.count() == 0:
        print('Injecting countries...')
        inject_countries(azure_path)
    if District.objects.count() == 0:
        print('Injecting districts...')
        inject_districts(azure_path)

# inject continent data
def inject_continents(azure_path):
    def process_continents():
        for continent_entry in continent_data:
            continent = Continent()
            continent.name = continent_entry["name"]
            continent.save()

    if azure_path:
        file_path = os.path.join(azure_path, 'geographical/continents.json')
        response = requests.get(file_path)
        continent_data = json.loads(response.content)
        process_continents()
    else:
        file_path = os.path.join(module_dir, 'geographical/continents.json')
        with open(file_path) as file:
            continent_data = json.load(file)
            process_continents()

# inject region data
def inject_regions(azure_path):
    def process_regions():
        for region_entry in region_data:
            region = Region()
            region.name = region_entry["region_name"]
            region.centroid = region_entry["centroid"]
            coordinates = region_entry["bbox"]["coordinates"][0]
            for coordinate in coordinates:
                region.polygon += str(coordinate[0]) + "," + str(coordinate[1]) + " "
            region.save()

    if azure_path:
        file_path = os.path.join(azure_path, 'geographical/ifrc-regions.json')
        response = requests.get(file_path)
        region_data = json.loads(response.content)
        process_regions()
    else:
        file_path = os.path.join(module_dir, 'geographical/ifrc-regions.json')
        with open(file_path) as file:
            region_data = json.load(file)
            process_regions()

# inject country data
def inject_countries(azure_path):
    def process_regions():
        for region_entry in region_data:
            name = region_entry["region_name"]
            region_id = region_entry["id"]
            region_names[region_id] = name
        
    def process_countries_ifrc():
        for feature in country_data:
            name = feature["name"]
            region_id = feature["region"]
            iso3 = feature["iso3"]
            if ("Region" in name) or ("Cluster" in name) or (region_id is None) or (iso3 is None):
                continue
            ifrc_countries[iso3] = region_names[region_id]

    def process_countries_opendatasoft():
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
            type = feature['geometry']['type']
            if type == 'Polygon':
                country.polygon = coordinates
            elif type == 'MultiPolygon':
                country.multipolygon = coordinates
            
            latitude = feature['properties']['geo_point_2d']['lat']
            longitude = feature['properties']['geo_point_2d']['lon']
            country.centroid = f'[{longitude}, {latitude}]'

            country.save()
            processed_iso3.add(country.iso3)

    region_names = {}
    if azure_path:
        file_path = os.path.join(azure_path, 'geographical/ifrc-regions.json')
        response = requests.get(file_path)
        region_data = json.loads(response.content)
        process_regions()
    else:
        file_path = os.path.join(module_dir, 'geographical/ifrc-regions.json')
        with open(file_path) as file:
            region_data = json.load(file)
            process_regions()

    ifrc_countries = {}
    if azure_path:
        file_path = os.path.join(azure_path, 'geographical/ifrc-countries-and-territories.json')
        response = requests.get(file_path)
        country_data = json.loads(response.content)
        process_countries_ifrc()
    else:
        file_path = os.path.join(module_dir, 'geographical/ifrc-countries-and-territories.json')
        with open(file_path) as file:
            country_data = json.load(file)
            process_countries_ifrc()
    
    processed_iso3 = set()
    if azure_path:
        file_path = os.path.join(azure_path, 'geographical/opendatasoft-countries-and-territories.geojson')
        response = requests.get(file_path)
        country_data = json.loads(response.content)
        process_countries_opendatasoft()
    else:
        file_path = os.path.join(module_dir, 'geographical/opendatasoft-countries-and-territories.geojson')
        with open(file_path) as file:
            country_data = json.load(file)
            process_countries_opendatasoft()

# inject district data
def inject_districts(azure_path):
    def process_districts():
        for feature in district_data['features']:
            district = District()
            # Skip unparsable features
            if not 'shapeName' in feature['properties']:
                continue
            district.name = feature['properties']['shapeName']
            iso3 = feature['properties']['shapeGroup']
            country = Country.objects.filter(iso3 = iso3).first()
            # Skip ISO3 codes that do not match existing countries
            if not country:
                continue
            district.country = country
            coordinates = feature['geometry']['coordinates']
            type = feature['geometry']['type']
            if type == 'Polygon':
                district.polygon = coordinates
            elif type == 'MultiPolygon':
                district.multipolygon = coordinates
            district.save()
    if azure_path:
        file_path = os.path.join(azure_path, 'geographical/geoBoundariesCGAZ_ADM1.geojson')
        response = requests.get(file_path)
        district_data = json.loads(response.content)
        process_districts()
    else:
        file_path = os.path.join(module_dir, 'geographical/geoBoundariesCGAZ_ADM1.geojson')
        with open(file_path, encoding='utf-8') as f:
            district_data = json.load(f)
            process_districts()
            

# inject feed configurations if not already present
def inject_feeds():
    if Feed.objects.count() == 0:
        print('Injecting feeds...')
        # this could be converted to a fixture
        feed_data = [
            ("Meteo France", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-france", "FRA", "atom"),
            ("Zentralanstalt für Meteorologie and Geodynamik", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-austria", "AUT", "atom"),
            ("Agencije Republike Slovenije za okolje", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-slovenia", "SVN", "atom"),
            ("Slovenský hydrometeorologický ústav", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-slovakia", "SVK", "atom"),
            ("Israel Meteorological Service", "https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-israel", "ISR", "atom"),
            ("Tanzania Meteorological Authority", "https://cap-sources.s3.amazonaws.com/tz-tma-en/rss.xml", "TZA", "rss"),
            ("Meteo Madagascar", "https://cap-sources.s3.amazonaws.com/mg-meteo-en/rss.xml", "MDG", "rss"),
            ("India Meteorological Department", "https://cap-sources.s3.amazonaws.com/in-imd-en/rss.xml", "IND", "rss"),
            ("Ghana Meteorological Agency", "https://cap-sources.s3.amazonaws.com/gh-gmet-en/rss.xml", "GHA", "rss"),
            ("Cameroon Directorate of National Meteorology", "https://cap-sources.s3.amazonaws.com/cm-meteo-en/rss.xml", "CMR", "rss"),
            ("United States National Weather Service", "https://api.weather.gov/alerts/active", "USA", "nws_us"),
            ("Hydrometcenter of Russia", "https://meteoinfo.ru/hmc-output/cap/cap-feed/en/atom.xml", "RUS", "atom"),
            ("Uruguayan Institute of Meteorology", "https://www.inumet.gub.uy/reportes/riesgo/rss.xml", "URY", "rss"),
        ]

        for feed_entry in feed_data:
            try:
                feed = Feed()
                feed.url = feed_entry[1]
                feed.country = Country.objects.get(iso3 = feed_entry[2])
                feed.format = feed_entry[3]
                feed.polling_interval = 60
                feed.status = 'operating'
                feed.author_name = 'Unknown'
                feed.author_email = 'Unknown'
                feed.official = True
                feed.save()

                language_info = LanguageInfo()
                language_info.feed = feed
                language_info.name = feed_entry[0]
                language_info.language = 'en'
                language_info.save()
                
            except Exception as e:
                print(f'Error injecting feed {feed.id}: {e}')