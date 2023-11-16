import paho.mqtt.client as mqtt
import time
import threading
from datetime import datetime, timezone
import socket
import aiocoap

messages=[]
# receiver will open threads to listen to both protocols at the same time
# when it receives a message it will add it to a shared list

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    global messages
    messages.append([msg.topic,round(datetime.now(timezone.utc).timestamp(),6)])
    print("received")

def on_publish(client, userdata, mid):
    print("Message "+str(mid)+" published.")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe

client.connect("localhost", 1883)

qos=1
client.subscribe("test",qos)

mqttlistener=threading.Thread(target=client.loop_forever)


def coaplistener(received):
    pass



def main(received):
    pass