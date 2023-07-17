import graphene
from graphene_django import DjangoObjectType
from cap_feed.models import Continent, Region, Country, Alert, AlertInfo, AlertInfoArea, AlertInfoAreaCircle, AlertInfoAreaPolygon, AlertInfoAreaGeocode, Source



class AlertInfoAreaGeocodeType(DjangoObjectType):
    class Meta:
        model = AlertInfoAreaGeocode

class AlertInfoAreaPolygonType(DjangoObjectType):
    class Meta:
        model = AlertInfoAreaPolygon

class AlertInfoAreaCircleType(DjangoObjectType):
    class Meta:
        model = AlertInfoAreaCircle

class AlertInfoAreaType(DjangoObjectType):
    class Meta:
        model = AlertInfoArea

class AlertInfoType(DjangoObjectType):
    class Meta:
        model = AlertInfo

class AlertType(DjangoObjectType):
    alertinfoSet = graphene.List(AlertInfoType)
    class Meta:
        model = Alert
        fields = ('id', 'source_feed', 'sent', 'status', 'msg_type', 'scope', 'country', 'info')

    def resolve_alertinfoSet(self, info):
        return self.info.all()

class ContinentType(DjangoObjectType):
    class Meta:
        model = Continent

class RegionType(DjangoObjectType):
    class Meta:
        model = Region

class CountryType(DjangoObjectType):
    class Meta:
        model = Country

class SourceType(DjangoObjectType):
    class Meta:
        model = Source
        fields = ('name', 'country', 'url')


class Query(graphene.ObjectType):
    list_alert=graphene.List(AlertType, iso3=graphene.String(), region_id=graphene.String(), continent_id=graphene.String())
    list_alert_info=graphene.List(AlertInfoType, iso3=graphene.String(), region_id=graphene.String(), continent_id=graphene.String())
    list_continent=graphene.List(ContinentType)
    list_country=graphene.List(CountryType, region_id=graphene.String(), continent_id=graphene.String())
    list_region=graphene.List(RegionType)
    list_source=graphene.List(SourceType)

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
    
    def resolve_list_alert_info(root, info, iso3=None, region_id=None, continent_id=None, **kwargs):
        filter = dict()
        if iso3:
            filter['alert__country__iso3'] = iso3
        if region_id:
            filter['alert__country__region'] = region_id
        if continent_id:
            filter['alert__country__continent'] = continent_id
        if len(filter) > 0:
            return AlertInfo.objects.filter(**filter).all()

        return AlertInfo.objects.all()
    
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
    
    def resolve_list_source(root, info):
        return Source.objects.all()

schema = graphene.Schema(query=Query)