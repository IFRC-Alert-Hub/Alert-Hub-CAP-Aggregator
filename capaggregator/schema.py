import graphene
from graphene_django import DjangoObjectType #used to change Django object into a format that is readable by GraphQL
from django.utils import timezone
from cap_feed.models import Alert, Continent, Region, Country

class AlertType(DjangoObjectType):
    class Meta:
        model = Alert
        field = ("id", "identifier", "sender", "sent", "status", "msg_type", "scope", "urgency", "severity", "certainty", "effective", "expires", "area_desc", "event", "geocode_name", "geocode_value")

class ContinentType(DjangoObjectType):
    class Meta:
        model = Continent
        field = ("id", "name")

class RegionType(DjangoObjectType):
    class Meta:
        model = Region
        field = ("id", "name", "polygon", "centroid")

class CountryType(DjangoObjectType):
    class Meta:
        model = Country
        field = ("id", "name", "iso3", "polygon", "multipolygon")


class Query(graphene.ObjectType):
    list_alert=graphene.List(AlertType)
    list_continents=graphene.List(ContinentType)
    list_country=graphene.List(CountryType)
    list_region=graphene.List(RegionType)

    def resolve_list_alert(root, info):
        return Alert.objects.order_by("-id")
    
    def resolve_list_continent(root, info):
        return Continent.objects.order_by("-id")
    
    def resolve_list_country(root, info):
        return Country.objects.order_by("-id")
    
    def resolve_list_region(root, info):
        return Region.objects.order_by("-id")

schema = graphene.Schema(query=Query)