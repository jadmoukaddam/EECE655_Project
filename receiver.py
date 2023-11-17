import paho.mqtt.client as mqtt
import threading
from datetime import datetime, timezone
import aiocoap
import logging

messages=[]
# receiver will open threads to listen to both protocols at the same time
# when it receives a message it will add it to a shared list

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    global messages
    messages.append([msg.payload.decode('utf-8'),round(datetime.now(timezone.utc).timestamp(),6)])
    print("received mqtt")

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



class CoAPResource(aiocoap.Resource):
    def render_post(self, request):
        global messages
        payload = request.payload.decode('utf-8')
        print(f"Received coap")
        messages.append([payload,round(datetime.now(timezone.utc).timestamp(),6)])
        return aiocoap.Message(payload=payload.encode('utf-8'))

def coap_server():
    logging.basicConfig(level=logging.INFO)

    context = aiocoap.Context()
    resource = CoAPResource()
    context.add_resource(('localhost', 5683), resource)

    try:
        context.run()
    except KeyboardInterrupt:
        print("Server terminated by user.")

coaplistener=threading.Thread(target=coap_server)



def main():
    global messages
    mqttlistener.start()
    coaplistener.start()
    while True:
        if len(messages)>1000:
            break
    
    #compute the average delay
    delays=[]
    for i in range(0,len(messages)):
        delay=messages[i][1]-float(messages[i][0])
        delays.append(delay)
    avgdelay=sum(delays)/len(delays)
    print(f"Average delay: {avgdelay}")