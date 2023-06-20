import graphene
from graphene_django import DjangoObjectType #used to change Django object into a format that is readable by GraphQL
from cap_feed.models import Alert

class AlertType(DjangoObjectType):
    # Describe the data that is to be formatted into GraphQL fields
    class Meta:
        model = Alert
        field = ("id", "identifier", "sender", "sent", "status", "msg_type", "scope", "urgency", "severity", "certainty", "expires", "area_desc", "event", "geocode_name", "geocode_value")

class Query(graphene.ObjectType):
    #query ContactType to get list of contacts
    list_alert=graphene.List(AlertType)

    def resolve_list_alert(root, info):
        # We can easily optimize query count in the resolve method
        return Alert.objects.order_by("-sent")[:20]

schema = graphene.Schema(query=Query)