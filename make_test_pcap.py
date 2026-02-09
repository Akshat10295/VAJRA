from scapy.all import Ether, IP, TCP, UDP, wrpcap
import random

pkts = []

# benign traffic
for i in range(300):
    src = f"10.0.0.{random.randint(2,50)}"
    p = Ether()/IP(src=src, dst="192.168.1.100")/TCP(sport=random.randint(1024,65000), dport=80, flags="PA")
    pkts.append(p)

# UDP flood-like
for i in range(700):
    src = f"198.51.{random.randint(0,255)}.{random.randint(1,254)}"
    p = Ether()/IP(src=src, dst="192.168.1.100")/UDP(sport=random.randint(1024,65000), dport=53)
    pkts.append(p)

# SYN flood-like
for i in range(500):
    src = f"10.1.0.{random.randint(2,254)}"
    p = Ether()/IP(src=src, dst="192.168.1.100")/TCP(sport=random.randint(1024,65000), dport=80, flags="S")
    pkts.append(p)

import random
random.shuffle(pkts)

wrpcap("test_traffic.pcap", pkts)
print("Wrote test_traffic.pcap with", len(pkts), "packets")

