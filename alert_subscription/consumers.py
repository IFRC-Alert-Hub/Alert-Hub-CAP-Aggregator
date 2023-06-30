import json

from channels.generic.websocket import WebsocketConsumer
from .models import Channel

class AlertConsumer(WebsocketConsumer):
    def connect(self):
        Channel.objects.create(channel_name=self.channel_name).save()
        self.accept()

    def disconnect(self, close_code):
        Channel.objects.get(channel_name=self.channel_name).delete()
        pass
    #TO DO: When the server receives ACK message, it deletes un-sent alert records
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        message = text_data_json

        self.send(text_data=json.dumps({"message": message}))

    def alert_transfer(self, event):
        alert = event['text']
        print(f'Received alert: {alert}')

        self.send(text_data=json.dumps({"message": alert}))



