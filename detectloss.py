from scapy.all import *

packet_count=0

def count_packet_loss(packet):
    global packet_count
    print(packet_count)
    while True:
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
    sniff(filter="", prn=count_packet_loss, iface="wlan0")

if __name__ == "__main__":
    counter()