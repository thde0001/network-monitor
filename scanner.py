import sys
import os
import socket
from datetime import datetime

sys.path.insert(0, "/home/vboxuser/network_monitor")

from scapy.all import ARP, Ether, srp
from database.database import get_connection, init_db

DB_PATH = "/home/vboxuser/network_monitor/database/network_monitor.db"

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return None


def scan_network(subnet, iface="enp0s8"):
    arp_request = ARP(pdst=subnet)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request
    answered, _ = srp(packet, timeout=2, verbose=False, iface=iface)

    devices = []
    for sent, received in answered:
        devices.append({
            "ip": received.psrc,
            "mac": received.hwsrc,
            "hostname": get_hostname(received.psrc)
        })
    return devices


def save_devices(devices):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for device in devices:
        cursor.execute("""
            INSERT INTO devices (ip, mac, hostname, first_seen, last_seen)
            VALUES (:ip, :mac, :hostname, :now, :now)
            ON CONFLICT(mac) DO UPDATE SET
                ip        = excluded.ip,
                hostname  = excluded.hostname,
                last_seen = excluded.last_seen
        """, {
            "ip": device["ip"],
            "mac": device["mac"],
            "hostname": device["hostname"],
            "now": now
        })

    conn.commit()
    conn.close()
    print(f"{len(devices)} enhed(er) gemt i databasen.")


if __name__ == "__main__":
    init_db()

    subnet = "192.168.0.0/24"
    print(f"Scanner {subnet}...\n")

    devices = scan_network(subnet)

    if devices:
        print(f"{'IP-adresse':<20} {'MAC-adresse':<20} {'Hostname'}")
        print("-" * 60)
        for device in devices:
            hostname = device["hostname"] or "Ukendt"
            print(f"{device['ip']:<20} {device['mac']:<20} {hostname}")
        save_devices(devices)
    else:
        print("Ingen enheder fundet.")