import paho.mqtt.client as mqtt
import time
import threading
from datetime import datetime, timezone
times=[]

def process(times):
    avg=[]
    min=100
    max=0
    couple=[]
    for i in range(len(times)):
        avg.append(times[i][1]-times[i][0])
        if times[i][1]-times[i][0]>max:
            max=times[i][1]-times[i][0]
            couple=times[i]
        if times[i][1]-times[i][0]<min:
            min=times[i][1]-times[i][0]
    # print(times)
    print(sum(avg)/len(times))
    if times!=sorted(times):
        print('arrived out of order')
    print(times[-1][1]-times[0][0])
    print((times[-1][1]-times[0][0])-sum(avg)/len(times))
    print('min',min)
    print('max',max)
    print('max couple',couple)
    for i in range(len(times)-1):
        if times[i+1][0]==times[i][0]:
            print('same time')

    times.clear()
    raise SystemExit

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_publish(client, userdata, mid):
    print("Message "+str(mid)+" published.")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    try:
        times.append([float(msg.payload.decode('utf-8')),round(datetime.now(timezone.utc).timestamp(),6)])
        # print(len(times))
    except:
        print(msg.payload.decode('utf-8'))
    if(len(times)>=100):
        process(times)




# Set up clients
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message

# Connect to broker
client.connect("192.168.0.101", 1883)

# Subscribe to topic
client.subscribe("python/mqtt",1)

# Publish message to topic
# client.publish("python/mqtt", "Listener listening")

# Loop to process callbacks
client.loop_forever()
