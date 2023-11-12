import paho.mqtt.client as mqtt
import time
import threading
from datetime import datetime, timezone
import socket

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_publish(client, userdata, mid):
    print("Message "+str(mid)+" published.")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

# Set up client
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message

# Connect to broker
client.connect("192.168.0.101", 1883)
client.socket().setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
# Subscribe to topic
# client.subscribe("python/mqtt")

# Publish message to topic
# client.publish("python/mqtt", "sender connected")

#sent_time=str(round(datetime.now(timezone.utc).timestamp(),6)).ljust(17,'0')

thread1=threading.Thread(target=client.loop_forever)
thread1.start()
qos=1
for i in range(1000):
    client.publish("python/mqtt", str(round(datetime.now(timezone.utc).timestamp(),6)).ljust(17,'0'),qos)
    time.sleep(0.1)

print('done')
