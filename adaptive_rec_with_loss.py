import paho.mqtt.client as mqtt
import threading
from datetime import datetime, timezone
import aiocoap
import logging

import detectloss

device_ip='192.168.0.140'
broker_ip='192.168.0.102'
packet_count=0

messages=[]
# receiver will open threads to listen to both protocols at the same time
# when it receives a message it will add it to a shared list

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    global messages
    global packet_count
    messages.append([msg.payload.decode('utf-8'),round(datetime.now(timezone.utc).timestamp(),6)])
    print("received mqtt", packet_count)

def on_publish(client, userdata, mid):
    print("Message "+str(mid)+" published.")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe

client.connect(broker_ip, 1883)

qos=1
client.subscribe("python/mqtt",qos)

mqttlistener=threading.Thread(target=client.loop_forever)

import aiocoap.resource as resource
import asyncio

class CoAPResource(resource.Resource):
    async def render_post(self, request):
        global messages
        global packet_count
        payload = request.payload.decode('utf-8')
        print(f"Received coap", packet_count)
        messages.append([payload, round(datetime.now(timezone.utc).timestamp(), 6)])
        # Return the response directly without using 'await'
        return aiocoap.Message(payload=payload.encode('utf-8'))


async def coap_server():
    logging.basicConfig(level=logging.INFO)

    # Create a CoAP context with the CoAPResource
    root = resource.Site()
    root.add_resource(('time',), CoAPResource())

    context = await aiocoap.Context.create_server_context(root, bind=(device_ip, 5683))

    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("Server terminated by user.")

coaplistener = threading.Thread(target=lambda: asyncio.run(coap_server()))

from scapy.all import *

def count_packet_loss(packet):
    global packet_count
    while True:
        print(packet)
        if IP in packet:

            if UDP in packet and packet[UDP].dport == 5683:
                # CoAP
                packet_count+=1
                # print(packet_count)

            elif TCP in packet and packet[TCP].dport == 1883:
                # MQTT
                packet_count+=1
                # print(packet_count)


def counter():
    # Adjust the filter as needed to capture the desired traffic
    sniff(filter="tcp or udp", prn=count_packet_loss, iface="lo0")

def main():
    global messages
    mqttlistener.start()
    coaplistener.start()
    compute=False
    while True:
        if len(messages)>=300:
            messages_copy=messages.copy()
            messages.clear()
            compute=True
        if compute:
            compute=False
            delays=[]
            for i in range(0,len(messages)):
                delay=messages_copy[i][1]-float(messages_copy[i][0])
                delays.append(delay)
            avgdelay=sum(delays)/len(delays)
            print(f"Average delay: {avgdelay}")

main()
