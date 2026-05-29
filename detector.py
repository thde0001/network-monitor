import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, "/home/vboxuser/network_monitor")
from database.database import insert_alert
from ids.notify import send_alert_email

PORTSCAN_THRESHOLD = 10
PORTSCAN_WINDOW = 10
HIGH_TRAFFIC_THRESHOLD = 100
HIGH_TRAFFIC_WINDOW = 60

port_tracker = defaultdict(list)
traffic_tracker = defaultdict(list)


def detect_portscan(src_ip, dst_port, timestamp):
    now = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    cutoff = now - timedelta(seconds=PORTSCAN_WINDOW)

    port_tracker[src_ip].append((dst_port, now))
    port_tracker[src_ip] = [
        (port, t) for port, t in port_tracker[src_ip]
        if t > cutoff
    ]

    unique_ports = set(port for port, t in port_tracker[src_ip])

    if len(unique_ports) >= PORTSCAN_THRESHOLD:
        details = f"Ramte {len(unique_ports)} unikke porte inden for {PORTSCAN_WINDOW} sekunder"
        print(f"[ALARM] PORTSCAN detekteret fra {src_ip} – {details}")
        insert_alert("PORTSCAN", src_ip, details, timestamp)
        send_alert_email("PORTSCAN", src_ip, details, timestamp)
        port_tracker[src_ip] = []


def detect_high_traffic(src_ip, timestamp):
    now = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    cutoff = now - timedelta(seconds=HIGH_TRAFFIC_WINDOW)

    traffic_tracker[src_ip].append(now)
    traffic_tracker[src_ip] = [
        t for t in traffic_tracker[src_ip]
        if t > cutoff
    ]

    packet_count = len(traffic_tracker[src_ip])

    if packet_count >= HIGH_TRAFFIC_THRESHOLD:
        details = f"Sendte {packet_count} pakker inden for {HIGH_TRAFFIC_WINDOW} sekunder"
        print(f"[ALARM] HIGH_TRAFFIC detekteret fra {src_ip} – {details}")
        insert_alert("HIGH_TRAFFIC", src_ip, details, timestamp)
        send_alert_email("HIGH_TRAFFIC", src_ip, details, timestamp)
        traffic_tracker[src_ip] = []


def analyze_packet(src_ip, dst_port, protocol, timestamp):
    if protocol == "TCP":
        detect_portscan(src_ip, dst_port, timestamp)
    detect_high_traffic(src_ip, timestamp)