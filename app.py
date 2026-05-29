import sys
import os

sys.path.insert(0, "/home/vboxuser/network_monitor")

from flask import Flask, jsonify, render_template
from database.database import get_connection

app = Flask(__name__)


def get_devices():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices ORDER BY last_seen DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_traffic():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM traffic_log ORDER BY timestamp DESC LIMIT 100")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_alerts():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 50")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_traffic_per_minute():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%Y-%m-%d %H:%M', timestamp) as minute,
                   COUNT(*) as count
            FROM traffic_log
            WHERE timestamp >= datetime('now', '-10 minutes')
            GROUP BY minute
            ORDER BY minute ASC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/devices")
def api_devices():
    return jsonify(get_devices())


@app.route("/api/traffic")
def api_traffic():
    return jsonify(get_traffic())


@app.route("/api/alerts")
def api_alerts():
    return jsonify(get_alerts())


@app.route("/api/traffic_per_minute")
def api_traffic_per_minute():
    return jsonify(get_traffic_per_minute())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)