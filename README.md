# IFRC/UCL Alert Hub - CAP Aggregator

The CAP Aggregator is an alert aggregation service built for IFRC's Alert Hub. Public alerts use the Common Alerting Protocol (CAP) Version 1.2 standard.

This is a Python web app using the Django framework and the Azure Database for PostgreSQL relational database service. The Django app is hosted in a fully managed Azure App Service. Requests to hundreds of publicly available alert feeds are managed by Celery and Redis. Aggregated alerts are then made available to the Alert Hub via a GraphQL API.

## Features

**Easily manage alert feeds**:
- Customise different polling intervals for each feed.
- Add new alerting sources quickly using pre-existing *formats* to interpret alert feeds.
- Identify problematic feeds with helpful error logs

**Get new alerts efficiently**:
- Filtered queries using GraphQL
- Automatic removal of expired and cancelled alerts
- Distributed feed polling using Redis task queues and concurrent Celery workers
- Websocket communication using Django Channels

### Upcoming Features
- New alert manager for handling API requests and internal communication across components.  
--> Extremely fast API responses with Redis caching, more robust as a decoupled component.
- New geographical subdivisions (ISO 3166-2).  
--> Sub-national regions and polygons to better group and display alerts. Also used to allow alert subscriptions to individual sub-national regions.

## Table of Contents
* Documentation
    * <a href="#geographical-organisation">Geographical Organisation</a>
    * <a href="#alert-aggregation-process">Alert Aggregation Process</a>
    * <a href="#feed-facade">Feed Facade</a>
* Development
    * <a href="#installation-and-setup">Installation and Setup</a>

## Geographical Organisation
*The structure behind the handling of alerts and feeds involves a clear distinction between different geographical areas.*

The fundamental unit of geographical area in our system is a country. Major alerting feeds such as meteorological institutions are often national and therefore only report alerts under a particular country. For reference purposes, 'ISO 3166-1 alpha-3' country codes are used to distinguish between countries.

Each country belongs to both a region and continent. The five regions are defined according to the structure of IFRC's National Societies. Continents are defined according to the six continents system which refers to North and South America as the Americas. The primary reason for using this structure is due to organisation of countries and their metadata by the data source we used — [opendatasoft](https://public.opendatasoft.com/explore/dataset/world-administrative-boundaries/table/).

The allocation of countries into regions and continents is necessary for easier navigation and filtering on the IFRC Alert Hub website. The inclusion of specific countries (and territories) in our system was decided by ease of data entry and pre-processing from the opendatasoft data source. New countries can be added or removed easily by IFRC using the Feed Facade, and perhaps a new term could be used to replace 'countries' to account for the inclusion of territories and disputed states.

## Alert Aggregation Process
*Alerts are retrieved and processed before they are handed off to be displayed on the Alert Hub and alert subscription system.*

New alert feeds are added by an admin from the Feed Facade and polling intervals are used to adjust the frequency of requests to the alerting source. Each feed has its own periodic task that is managed by the *Celery Beat* scheduler. These tasks are handed off to *Redis* and multiple *Celery* workers for distributed processing.

When processing the CAP feed of alerting feeds, a processing format is used to interpret the layout of different feeds. For example, the 'meteoalarm' format can be selected when adding MeteoAlarm feeds in the feed facade, but a different format would need to be used to interpret alerts from the Algerian Meteorological Office.

Formats are very convenient for admin users and can guarantee alerts are processed correctly. But they inevitably have to be manually created by developers and updated if alerting feeds make changes to their feed format. However, the same format can be used for up to dozens of feeds, and each format only differs by about 5-10 lines of code.

The CAP-aggregator processes alerts according to the CAP-V1.2 specification which details alert elements and sub-elements such as *info*. Dates and times are standardised across the system using the UTC timezone. Some alerting feeds keep outdated alerts on their alert feeds, so expired alerts are identified and are not saved.

Another periodic task for removing expired alerts also runs continously in the background. This task is responsible for identifying and removing alerts which have expired since being saved to the database. However, the alert expiry date and time is contained in the *info* element according to CAP V-1.2. Therefore it is theoretically possible for multiple *info* elements to have different expiry times. Expired *info* elements are automatically removed, and the *alert* element (the actual alert itself) will be removed if all *info* elements have expired or been removed.

Alerts are aggregated by countries, regions, and continents. Using filtered queries with GraphQL, the Alert Hub and other broadcasters can easily fetch only the relevant alerts, reducing unnecessary strain on the system.

## Feed Facade
*Admin users can manage countries, regions, continents, feeds, and each individual alert using the Feed Facade.*

Each alerting feed and their alerts belong to a country, and each country belongs to a particular region and continent. Therefore, it is necessary for regions and continents to exist first before countries can be added (although all regions and continents already exist in the system). Similarly, a new country needs be created by an admin user before a new alerting feed can be added for that country.

Deleting a region or continent would delete all countries belonging to them. In a chain reaction, all alerts and feeds belonging to the deleted countries would also be deleted. This current behaviour is possibly unsafe and undesirable but is convenient for development. Lastly, deleting an alerting feed also deletes existing alerts from the same country.

Search functions, filters and sortable columns are available when they would be relevant. For example, an admin user could filter feeds by format (e.g., meteoalarm) or search for feeds belonging to a particular country using the search bar on the same page.

The 'Feed logs' section displays any issues or exceptions encountered while polling from different feeds. This feature offers very powerful feedback for admins. It describes the context of the problem (which feed and alert), what the exception is, what the exception means, the exact system error message, and possible solutions for the problem. Logs are kept in the system for 2 weeks and can identify connection problems, format problems, and violations of the CAP-v1.2 specification by alerting sources.

## Installation and Setup

*It is possible to develop and run the Django app, Celery, and Redis using Docker on Windows. However, Celery and Redis are not officially supported and certain features such as concurrent Celery workers will not work.*

1. Clone the repository and checkout the main or develop branch.
    ```
    git clone https://github.com/IFRC-Alert-Hub/Alert-Hub-CAP-Aggregator.git
    git checkout develop
    ```
2. Set up and activate a virtual environment.  
    Windows:
    ```
    python -m venv venv
    venv\Scripts\activate
    ```
    Linux:
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install packages with pip.
    ```
    pip install -r requirements.txt
    ```
4. Setup a PostGreSQL database and check it works.  
    Linux:
    ```
    sudo apt install postgresql postgresql-contrib
    sudo passwd postgres
    sudo service postgresql start
    sudo -u postgres psql
    create database cap_aggregator;

    sudo service postgresql status
    ```
5. Create .env in the same directory as manage.py with your credentials. You can generate a secret key at https://djecrety.ir/.  
    Example:
    ```
    DBNAME=cap_aggregator
    DBHOST=localhost
    DBUSER=username
    DBPASS=1234
    SECRET_KEY=d3bt^98*kjp^f&e3+=(0m(vge)6ky+ox76q4gbudy#-2kqkz%c
    CELERY_BROKER_URL=redis://localhost:6379
    REDIS_URL=redis://localhost:6379
    ```
6. Verify the progress so far by running some tests successfully.
    ```
    python manage.py migrate
    python manage.py test
    ```
7. Setup a Redis server and check it works.  
    Linux:
    ```
    sudo apt install redis-server
    sudo service redis-server start

    redis-cli ping
    ```
8. Add admin credentials and start the Django server.
    ```
    python manage.py createsuperuser
    python manage.py runserver
    ```
9. Check the Django app works so far.  
    Initial geographical data and feeds should be loaded and visible in the feed facade after refreshing the index page.

    Index page: http://127.0.0.1:8000/  
    Feed facade: http://127.0.0.1:8000/admin/
10. Start Celery works and the scheduler.  
    Windows:
    ```
    celery -A capaggregator worker -l info --pool=solo
    celery -A capaggregator beat -l info
    ```
    Linux (-c [concurrent workers])
    ```
    celery -A capaggregator worker -l info -c 4
    celery -A capaggregator beat -l info
    ```
11. Alerts are now being aggregated!  
    Check the index page or feed facade for alert entries.

    

### Useful Commands

Inspect active workers
```
celery -A capaggregator inspect active
```

Start celery worker and scheduler on deployment:
```
celery multi start w1 -A capaggregator -l info
celery -A capaggregator beat --detach -l info
```