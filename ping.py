import subprocess, threading

packet_loss = 0
IP_receiver = "192.168.0.111"

def calculate_packet_loss(target_ip):
    global packet_loss
    go_ping = f"ping -c 20 -i 2 {target_ip}"
    result = subprocess.run(go_ping, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in result.stdout.split('\n'):
        if 'packet loss' in line:
            print(f"Updated packet loss: {float(line.split('%')[0].split()[-1]) / 100}")

def upldate_packet_loss():
    global IP_receiver
    packet_loss_thread = threading.Thread(target=calculate_packet_loss, args=(IP_receiver,))
    packet_loss_thread.start()

upldate_packet_loss()