import json

from django.shortcuts import render
import ssl
from django.http import HttpResponse


from channels.layers import get_channel_layer
from asgiref.sync import AsyncToSync
from cap_feed.models import AlertEncoder
from .models import Channel
def send_alert_to_channel(alert):
    channel_layer = get_channel_layer()
    # Check if the connection exists
    AsyncToSync(channel_layer.send)(
        Channel.objects.all().first().channel_name,
        {"type": "alert.transfer",
         "text": json.dumps(alert, cls=AlertEncoder)
        }
    )
    print(Channel.objects.all().first().channel_name)