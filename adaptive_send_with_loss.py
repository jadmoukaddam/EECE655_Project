#!/usr/bin/env python3

# SPDX-FileCopyrightText: Christian AmsÃ¼ss and the aiocoap contributors
#
# SPDX-License-Identifier: MIT

"""This is a usage example of aiocoap that demonstrates how to implement a
simple client. See the "Usage Examples" section in the aiocoap documentation
for some more information."""

import logging
import asyncio
import threading
import subprocess
import time
from aiocoap import *
import paho.mqtt.client as mqtt
import socket
from datetime import datetime, timezone

import detectloss


IP_receiver="192.168.0.140"
IP_broker="192.168.0.102"
packets_sent = 0
packets_lost = 0
packet_loss = 0
packet_count=0
mode="Adaptive"
class TransportTuning2(TransportTuning):
    """Base parameters that guide CoAP transport behaviors

    The values in here are recommended values, often defaults from RFCs. They
    can be tuned in subclasses (and then passed into a message as
    ``transport_tuning``), although users should be aware that alteing some of
    these can cause the library to behave in ways violating the specification,
    especially with respect to congestion control.
    """

    #   +-------------------+---------------+
    #   | name              | default value |
    #   +-------------------+---------------+
    #   | ACK_TIMEOUT       | 2 seconds     |
    #   | ACK_RANDOM_FACTOR | 1.5           |
    #   | MAX_RETRANSMIT    | 4             |
    #   | NSTART            | 1             |
    #   | DEFAULT_LEISURE   | 5 seconds     |
    #   | PROBING_RATE      | 1 Byte/second |
    #   +-------------------+---------------+

    ACK_TIMEOUT = 2.0
    """The time, in seconds, to wait for an acknowledgement of a
    confirmable message. The inter-transmission time doubles
    for each retransmission."""

    ACK_RANDOM_FACTOR = 1.5
    """Timeout multiplier for anti-synchronization."""

    MAX_RETRANSMIT = 4
    """The number of retransmissions of confirmable messages to
    non-multicast endpoints before the infrastructure assumes no
    acknowledgement will be received."""

    NSTART = 1
    """Maximum number of simultaneous outstanding interactions
       that endpoint maintains to a given server (including proxies)"""

    #   +-------------------+---------------+
    #   | name              | default value |
    #   +-------------------+---------------+
    #   | MAX_TRANSMIT_SPAN |          45 s |
    #   | MAX_TRANSMIT_WAIT |          93 s |
    #   | MAX_LATENCY       |         100 s |
    #   | PROCESSING_DELAY  |           2 s |
    #   | MAX_RTT           |         202 s |
    #   | EXCHANGE_LIFETIME |         247 s |
    #   | NON_LIFETIME      |         145 s |
    #   +-------------------+---------------+

    @property
    def MAX_TRANSMIT_SPAN(self):
        """Maximum time from the first transmission
        of a confirmable message to its last retransmission."""
        return self.ACK_TIMEOUT * (2 ** self.MAX_RETRANSMIT - 1) * self.ACK_RANDOM_FACTOR

    @property
    def MAX_TRANSMIT_WAIT(self):
        """Maximum time from the first transmission
        of a confirmable message to the time when the sender gives up on
        receiving an acknowledgement or reset."""
        return self.ACK_TIMEOUT * (2 ** (self.MAX_RETRANSMIT + 1) - 1) * self.ACK_RANDOM_FACTOR

    MAX_LATENCY = 100.0
    """Maximum time a datagram is expected to take from the start
    of its transmission to the completion of its reception."""

    @property
    def PROCESSING_DELAY(self):
        """"Time a node takes to turn around a
        confirmable message into an acknowledgement."""
        return self.ACK_TIMEOUT

    @property
    def MAX_RTT(self):
        """Maximum round-trip time."""
        return 2 * self.MAX_LATENCY + self.PROCESSING_DELAY

    @property
    def EXCHANGE_LIFETIME(self):
        """time from starting to send a confirmable message to the time when an
        acknowledgement is no longer expected, i.e. message layer information about the
        message exchange can be purged"""
        return self.MAX_TRANSMIT_SPAN + self.MAX_RTT

    DEFAULT_BLOCK_SIZE_EXP = MAX_REGULAR_BLOCK_SIZE_EXP
    """Default size exponent for blockwise transfers."""

    EMPTY_ACK_DELAY = 0.1
    """After this time protocol sends empty ACK, and separate response"""

    REQUEST_TIMEOUT = MAX_TRANSMIT_WAIT
    """Time after which server assumes it won't receive any answer.
       It is not defined by IETF documents.
       For human-operated devices it might be preferable to set some small value
       (for example 10 seconds)
       For M2M it's application dependent."""

    DEFAULT_LEISURE = 5

    @property
    def MULTICAST_REQUEST_TIMEOUT(self):
        return self.REQUEST_TIMEOUT + self.DEFAULT_LEISURE

    OBSERVATION_RESET_TIME = 128
    """Time in seconds after which the value of the observe field are ignored.

    This number is not explicitly named in RFC7641.
    """

logging.basicConfig(level=logging.ERROR)
Times = [0]
Threads=[]
client=""
protocol=""
async def sendmsg_CoAP(payload):
    global packet_count
    #global protocol
    #protocol = await Context.create_client_context()
    #request = Message(code=GET, uri='coap://172.20.10.1/time', transport_tuning=TransportTuning2)
    try:
        protocol = await Context.create_client_context()
        request = Message(code=POST, uri='coap://'+IP_receiver+'/time', transport_tuning=TransportTuning2, payload=payload.encode('utf-8'))
        response = await asyncio.wait_for(protocol.request(request).response, timeout=30)

        print("Message sent with CoAP")
        print('packets sent', packet_count)
    except Exception as e:
        #await protocol.shutdown()
        pass
    finally:
        await protocol.shutdown()



def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_publish(client, userdata, mid):
    global packet_count
    print("Message "+str(mid)+" published.")
    print('packets sent', packet_count)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def sendmsg_MQTT(payload, qos):
    global client
    client.publish("python/mqtt", payload, qos)

async def sendmsg():
    global packet_loss, mode
    payload = str(round(datetime.now(timezone.utc).timestamp(),6)).ljust(17,'0')
    if mode== "MQTT" or (mode == "Adaptive" and packet_loss<0.3):
        sendmsg_MQTT(payload, 1)
    else:
        asyncio.create_task(sendmsg_CoAP(payload))

async def setup_coap():
    global protocol
    protocol = await Context.create_client_context()

def setup_mqtt():
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect(IP_broker, 1883)
    client.socket().setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
    thread1=threading.Thread(target=client.loop_forever)
    thread1.start()
    qos=1

def set_mode(m):
    global mode
    mode = m

def calculate_packet_loss(target_ip):
    global packet_loss
    while True:
        go_ping = f"ping -c 20 -i 0.5 {target_ip}"
        result = subprocess.run(go_ping, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in result.stdout.split('\n'):
            if 'packet loss' in line:
                packet_loss = float(line.split('%')[0].split()[-1]) / 100
                print(f"Jado my baby the packet loss is: {packet_loss} wink wink")

def upldate_packet_loss():
    global IP_receiver
    packet_loss_thread = threading.Thread(target=calculate_packet_loss, args=(IP_receiver,))
    packet_loss_thread.start()

async def main():
    set_mode("MQTT")
    await setup_coap()
    setup_mqtt()
    upldate_packet_loss()
    threading.Thread(target=counter).start()
    i=0
    while i<1000:
        try:
            await sendmsg()
        except Exception as e:
            print('Failed to send resource:')
            print(e)
            exit()
        await asyncio.sleep(0.1)
        i+=1
    await asyncio.sleep(10)

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


if __name__ == "__main__":
    asyncio.run(main())
