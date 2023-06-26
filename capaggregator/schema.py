import graphene
from graphene_django import DjangoObjectType #used to change Django object into a format that is readable by GraphQL
from django.utils import timezone
from cap_feed.models import Alert, Region, Country

class AlertType(DjangoObjectType):
    # Describe the data that is to be formatted into GraphQL fields
    class Meta:
        model = Alert
        field = ("id", "identifier", "sender", "sent", "status", "msg_type", "scope", "urgency", "severity", "certainty", "effective", "expires", "area_desc", "event", "geocode_name", "geocode_value")

class RegionType(DjangoObjectType):
    # Describe the data that is to be formatted into GraphQL fields
    class Meta:
        model = Region
        field = ("id", "name", "polygon", "centroid")

class CountryType(DjangoObjectType):
    # Describe the data that is to be formatted into GraphQL fields
    class Meta:
        model = Country
        field = ("id", "name", "iso", "iso3", "polygon", "centroid")


class Query(graphene.ObjectType):
    list_alert=graphene.List(AlertType)
    list_country=graphene.List(CountryType)
    list_region=graphene.List(RegionType)

    def resolve_list_alert(root, info):
        # We can easily optimize query count in the resolve method
        return Alert.objects.order_by("-id")
    
    def resolve_list_country(root, info):
        # We can easily optimize query count in the resolve method
        return Country.objects.order_by("-id")
    
    def resolve_list_region(root, info):
        # We can easily optimize query count in the resolve method
        return Region.objects.order_by("-id")

schema = graphene.Schema(query=Query)