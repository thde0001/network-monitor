import sqlite3
import os

DB_PATH = "/home/vboxuser/network_monitor/database/network_monitor.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                ip         TEXT NOT NULL,
                mac        TEXT NOT NULL UNIQUE,
                hostname   TEXT,
                first_seen TEXT NOT NULL,
                last_seen  TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                src_ip     TEXT NOT NULL,
                dst_ip     TEXT NOT NULL,
                src_port   INTEGER,
                dst_port   INTEGER,
                protocol   TEXT NOT NULL,
                timestamp  TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                src_ip     TEXT NOT NULL,
                details    TEXT,
                timestamp  TEXT NOT NULL
            )
        """)

        conn.commit()
        print("Database initialiseret korrekt.")


def insert_traffic(src_ip, dst_ip, src_port, dst_port, protocol, timestamp):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO traffic_log (src_ip, dst_ip, src_port, dst_port, protocol, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (src_ip, dst_ip, src_port, dst_port, protocol, timestamp))
        conn.commit()


def insert_alert(alert_type, src_ip, details, timestamp):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (alert_type, src_ip, details, timestamp)
            VALUES (?, ?, ?, ?)
        """, (alert_type, src_ip, details, timestamp))
        conn.commit()


if __name__ == "__main__":
    init_db()