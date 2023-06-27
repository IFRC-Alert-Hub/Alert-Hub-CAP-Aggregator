# IFRC/UCL Alert Hub - CAP Aggregator

The CAP Aggregator is a public alert aggregation service built for IFRC's Alert Hub. Alerts use the Common Alerting Protocol (CAP) international standard.

This is a Python web app using the Django framework and the Azure Database for PostgreSQL relational database service. The Django app is hosted in a fully managed Azure App Service. Requests to hundreds of publicly available alert sources are managed by Celery, RabbitMQ and Redis. Aggregated alerts are then made available to the Alert Hub via a GraphQL API.

## Features

- Easily manage alert sources: configure urls, polling intervals, xml formats
- Get new alerts efficiently: filtered queries, remove expired alerts, retrieve location data