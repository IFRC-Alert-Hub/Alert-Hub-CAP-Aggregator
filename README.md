# IFRC/UCL Alert Hub - CAP Aggregator

The CAP Aggregator is a performant public alert aggregation service built for IFRC's Alert Hub. Alerts use the Common Alerting Protocol (CAP) international standard.

This is a Python web app using the Django framework and the Azure Database for PostgreSQL relational database service. The Django app is hosted in a fully managed Azure App Service. Requests to hundreds of publicly available alert sources are managed by Celery, RabbitMQ and Redis. Finally, aggregated alerts are made available to the Alert Hub via a GRAPHQL API.

## Features

- Easily add/remove/update alert sources
- Configure how each source is processed: polling interval, xml format etc.