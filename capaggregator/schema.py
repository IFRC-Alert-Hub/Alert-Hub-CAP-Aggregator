import graphene
from graphene_django import DjangoObjectType
from cap_feed.models import Continent, Region, Country, Alert



class AlertType(DjangoObjectType):
    class Meta:
        model = Alert

class ContinentType(DjangoObjectType):
    class Meta:
        model = Continent

class RegionType(DjangoObjectType):
    class Meta:
        model = Region

class CountryType(DjangoObjectType):
    class Meta:
        model = Country


class Query(graphene.ObjectType):
    list_alert=graphene.List(AlertType, iso3=graphene.String(), region_id=graphene.String(), continent_id=graphene.String())
    list_continent=graphene.List(ContinentType)
    list_country=graphene.List(CountryType, region_id=graphene.String(), continent_id=graphene.String())
    list_region=graphene.List(RegionType)

    def resolve_list_alert(root, info, iso3=None, region_id=None, continent_id=None, **kwargs):
        filter = dict()
        if iso3:
            filter['country__iso3'] = iso3
        if region_id:
            filter['country__region'] = region_id
        if continent_id:
            filter['country__continent'] = continent_id
        if len(filter) > 0:
            return Alert.objects.filter(**filter).all()

        return Alert.objects.all()
    
    def resolve_list_continent(root, info):
        return Continent.objects.all()
    
    def resolve_list_country(root, info, region_id=None, continent_id=None, **kwargs):
        filter = dict()
        if region_id:
            filter['region__id'] = region_id
        if continent_id:
            filter['continent__id'] = continent_id
        if len(filter) > 0:
            return Country.objects.filter(**filter).all()
        
        return Country.objects.all()
    
    def resolve_list_region(root, info):
        return Region.objects.all()

schema = graphene.Schema(query=Query)