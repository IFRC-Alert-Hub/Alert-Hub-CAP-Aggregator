import json

from django.shortcuts import render
import websocket
import ssl
from django.http import HttpResponse

# Create your views here.
# Disable SSL certificate verification if needed
def send_packet(request):
    websocket.enableTrace(True)  # Optional: Enable trace for debugging
    ws = websocket.create_connection(
        "ws://127.0.0.1:8000/ws/fetch_new_alert/w5/"
    )

    packet = "Your packet data"  # Replace with your actual packet data
    ws.send(json.dumps(packet))

    result = ws.recv()
    print("Received response from server:", result)

    ws.close()

    return HttpResponse("Received response from server:", result)