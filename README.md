# IFRC/UCL Alert Hub - CAP Aggregator

The CAP Aggregator is an alert aggregation service built for IFRC's Alert Hub. Public alerts use the Common Alerting Protocol (CAP) Version 1.2 standard.

This is a Python web app using the Django framework and the Azure Database for PostgreSQL relational database service. The Django app is hosted in a fully managed Azure App Service. Requests to hundreds of publicly available alert sources are managed by Celery and Redis. Aggregated alerts are then made available to the Alert Hub via a GraphQL API.

## Features

**Easily manage alert sources**:
- Change urls/polling intervals/source countries
- Set up new sources quickly using templates to interpret xml formats
- Identify problematic sources with feedback (WIP)

**Get new alerts efficiently**:
- Filtered queries using GraphQL
- Automatic removal of expired and cancelled alerts
- Distributed alert retrieval from sources using Redis task queues
- Websocket communication using Django Channels (WIP)

## Table of Contents
* Documentation
    * <a href="#geographical-organisation">Geographical Organisation</a>
    * <a href="#alert-aggregation-process">Alert Aggregation Process</a>
    * <a href="#feed-facade">Feed Facade</a>
* Development
    * <a href="#installation-and-setup">Installation and Setup</a>

## Geographical Organisation
*The structure behind the handling of alerts and sources involves a clear distinction between different geographical areas.*

The fundamental unit of geographical area in our system is a country. Major alerting sources such as meteorological institutions are often national and therefore only report alerts under a particular country. For reference purposes, 'ISO 3166-1 alpha-3' country codes are used to distinguish between countries.

Each country belongs to both a region and continent. The five regions are defined according to the structure of IFRC's National Societies. Continents are defined according to the six continents system which refers to North and South America as the Americas. The primary reason for using this structure is due to organisation of countries and their metadata by the data source we used — [opendatasoft](https://public.opendatasoft.com/explore/dataset/world-administrative-boundaries/table/).

The allocation of countries into regions and continents is necessary for easier navigation and filtering on the IFRC Alert Hub website. The inclusion of specific countries (and territories) in our system was decided by ease of data entry and pre-processing from the opendatasoft data source. New countries can be added or removed easily by IFRC using the Feed Facade, and perhaps a new term could be used to replace 'countries' to account for the inclusion of territories and disputed states.

## Alert Aggregation Process
*Alerts are retrieved and processed before they are handed off to be displayed on the Alert Hub and alert subscription system.*

New alert sources are added by an admin from the Feed Facade and polling intervals are used to adjust the frequency of requests to the alerting source. Alert sources with the same polling interval are automatically grouped into the same periodic task used by the *Celery Beat* scheduler. These tasks are handed off to *Redis* and *Celery* workers for asynchronous background processing.

When processing the CAP feed of alerting sources, a processing template or format is used to interpret the different xml formats. For example, Meteoalarm represents a network of public weather services across Europe, and these European countries encode their cap alerts in the same xml format. The 'meteoalarm' format can therefore be selected when adding MeteoAlarm alerting sources in the feed facade, but a different format would need to be used to interpret alerts from the Algerian Meteorological Office.

Formats are very convenient for admin users and can guarantee alerts are processed correctly. But they inevitably have to be manually created by developers and updated if alerting sources make changes to their alert feed format.

The CAP-aggregator processes alerts according to the CAP-V1.2 specification which details alert elements and sub-elements such as *info*. Dates and times are standardised across the system using the UTC timezone. Some alerting sources keep outdated alerts on their alert feeds, so expired alerts are identified and are not saved.

Another periodic task for removing expired alerts also runs continously in the background. This task is responsible for identifying and removing alerts which have expired since being saved to the database. However, the alert expiry date and time is contained in the *info* element according to CAP V-1.2. Therefore it is theoretically possible for multiple *info* elements to have different expiry times. Expired *info* elements are automatically removed, and the *alert* element (the actual alert itself) will be removed if all *info* elements have expired or been removed.

Alerts are aggregated by countries, regions, and continents. Using filtered queries with GraphQL, the Alert Hub and other broadcasters can easily fetch only the relevant alerts, reducing unnecessary strain on the system.

## Feed Facade
*Admin users can manage countries, regions, continents, sources, and each individual alert using the Feed Facade.*

Each alerting source and their alerts belong to a country, and each country belongs to a particular region and continent. Therefore, it is necessary for regions and continents to exist first before countries can be added (although all regions and continents already exist in the system). Similarly, a new country needs be created by an admin user before a new alerting source can be added for that country.

Deleting a region or continent would delete all countries belonging to them. In a chain reaction, all alerts and sources belonging to the deleted countries would also be deleted. This current behaviour is possibly unsafe and undesirable but is convenient for development. Lastly, deleting an alerting source also deletes existing alerts from the same country.

Search functions, filters and sortable columns are available when they would be relevant. For example, an admin user could filter sources by format (e.g., meteoalarm) or search for sources belonging to a particular country using the search bar on the same page.

A page called 'Task results' is available under the 'Celery Results' section. This shows a historical record of all the tasks for retrieving new alerts and removing expired alerts. We intend to replace this section or amend existing sections with more informative feedback about the status of each source. This would indicating possible problems to the admin such as connection issues, alert retrieval failure, and format compatibility.

## Installation and Setup

WIP due to upcoming changes to Websockets and Django Channels. More detailed instructions will be added including our Azure deployment process (maybe useful?).

### Useful Celery Commands

Inspect active workers
```
celery -A capaggregator inspect active
```

Start celery worker and scheduler on deployment:
```
celery multi start w1 -A capaggregator -l info
celery -A capaggregator beat --detach -l info
```

Start celery worker and sceduler for local development:
```
celery -A capaggregator worker -l info --pool=solo
celery -A capaggregator beat -l info
```