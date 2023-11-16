import paho.mqtt.client as mqtt
import time
import threading
from datetime import datetime, timezone
import socket
import aiocoap


payload="Hello World"

# we do three functions
# one function to send over mqtt
# one function to send over coap
# one function that will take the payload and call which protocol to send over

# MQTT
def on_connect(client, userdata, flags, rc):
    # print("Connected with result code "+str(rc))
    client.subscribe("test")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def mqtt_send(payload):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.publish("test", payload)
    client.loop_forever()


# COAP



# Sender
def sender(payload):
    #divide payload
    payload=payload.split()
    pointer=[0]

    # beggining of the payload we add
    


    pass



# we still need a way to tell the sender to switch between protocols

