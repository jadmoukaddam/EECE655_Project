import paho.mqtt.client as mqtt
import time
import threading
from datetime import datetime, timezone
import socket
import aiocoap


# receiver will open threads to listen to both protocols at the same time
# when it receives a message it will add it to a shared list

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("testtopic/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_publish(client, userdata, mid):
    print("Message "+str(mid)+" published.")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe

client.connect("localhost", 1883, 60)

def mqttlistener(received):
    pass


def coaplistener(received):
    pass



def main(received):
    processed=0
    while True:
        if len(received)>processed:
            print(received[processed])
            processed+=1