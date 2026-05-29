import sys
import os
import threading

sys.path.insert(0, "/home/vboxuser/network_monitor")

from scapy.all import sniff, IP, TCP, UDP
from datetime import datetime
from database.database import insert_traffic, init_db
from ids.detector import analyze_packet

def process_packet(packet):
    if not packet.haslayer(IP):
        return

    src_ip = packet[IP].src
    dst_ip = packet[IP].dst
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    protocol = None
    src_port = None
    dst_port = None

    if packet.haslayer(TCP):
        protocol = "TCP"
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
    elif packet.haslayer(UDP):
        protocol = "UDP"
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
    else:
        return

    print(f"[{timestamp}] {protocol} {src_ip}:{src_port} -> {dst_ip}:{dst_port}")

    insert_traffic(src_ip, dst_ip, src_port, dst_port, protocol, timestamp)
    analyze_packet(src_ip, dst_port, protocol, timestamp)


def start_sniffing(interface="enp0s8"):
    print(f"Starter sniffer på {interface}...")
    print("Tryk Ctrl+C for at stoppe\n")

    sniffer_thread = threading.Thread(
        target=lambda: sniff(
            iface=interface,
            promisc=True,
            store=False,
            prn=process_packet
        )
    )

    sniffer_thread.daemon = True
    sniffer_thread.start()
    return sniffer_thread


if __name__ == "__main__":
    init_db()
    thread = start_sniffing()

    try:
        thread.join()
    except KeyboardInterrupt:
        print("\nSniffer stoppet.")