import paho.mqtt.client as mqtt
import threading
from datetime import datetime, timezone
import aiocoap
import logging
packets=0
messages=[]
# receiver will open threads to listen to both protocols at the same time
# when it receives a message it will add it to a shared list

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    global messages
    global packets
    messages.append([msg.payload.decode('utf-8'),round(datetime.now(timezone.utc).timestamp(),6)])
    packets+=1
    print("received mqtt", packets)

def on_publish(client, userdata, mid):
    print("Message "+str(mid)+" published.")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe

client.connect("192.168.0.100", 1883)

qos=1
client.subscribe("python/mqtt",qos)

mqttlistener=threading.Thread(target=client.loop_forever)

import aiocoap.resource as resource
import asyncio

class CoAPResource(resource.Resource):
    async def render_post(self, request):
        global messages
        global packets
        payload = request.payload.decode('utf-8')
        packets+=1
        print(f"Received coap", packets)
        messages.append([payload, round(datetime.now(timezone.utc).timestamp(), 6)])
        # Return the response directly without using 'await'
        return aiocoap.Message(payload=payload.encode('utf-8'))


async def coap_server():
    logging.basicConfig(level=logging.INFO)

    # Create a CoAP context with the CoAPResource
    root = resource.Site()
    root.add_resource(('time',), CoAPResource())

    context = await aiocoap.Context.create_server_context(root, bind=('192.168.0.140', 5683))

    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("Server terminated by user.")

coaplistener = threading.Thread(target=lambda: asyncio.run(coap_server()))



def main():
    global messages
    mqttlistener.start()
    coaplistener.start()
    while True:
        if len(messages)>=300:
            break
    
    #compute the average delay
    delays=[]
    for i in range(0,len(messages)):
        delay=messages[i][1]-float(messages[i][0])
        delays.append(delay)
    avgdelay=sum(delays)/len(delays)
    print(f"Average delay: {avgdelay}")


main()
