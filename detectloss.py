from scapy.all import *

coap_sequence_numbers = set()
mqtt_sequence_numbers = set()

def packet_handler(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst

        if UDP in packet and packet[UDP].dport == 5683:
            # CoAP
            if packet.haslayer(Raw):
                print(packet[Raw].load)
                # sequence_number = packet[UDP].seq
                # if sequence_number in coap_sequence_numbers:
                #     print(f"CoAP Retransmission Detected! Sequence Number: {sequence_number}")
                # else:
                #     coap_sequence_numbers.add(sequence_number)

        elif TCP in packet and packet[TCP].dport == 1883:
            # MQTT
            sequence_number = packet[TCP].seq
            if sequence_number in mqtt_sequence_numbers:
                print(f"MQTT Retransmission Detected! Sequence Number: {sequence_number}")
            else:
                mqtt_sequence_numbers.add(sequence_number)

def main():
    # Adjust the filter as needed to capture the desired traffic
    sniff(filter="ip", prn=packet_handler, store=0, iface="en0")

if __name__ == "__main__":
    main()
