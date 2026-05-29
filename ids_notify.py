from mailjet_rest import Client

API_KEY = "din_api_key"
API_SECRET = "din_secret_key"
EMAIL_FROM = "din_afsender@gmail.com"
EMAIL_TO = "din_modtager@gmail.com"


def send_alert_email(alert_type, src_ip, details, timestamp):
    try:
        mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')

        data = {
            'Messages': [{
                "From": {
                    "Email": EMAIL_FROM,
                    "Name": "Network Monitor"
                },
                "To": [{
                    "Email": EMAIL_TO,
                    "Name": "Admin"
                }],
                "Subject": f"[ALARM] {alert_type} detekteret – {src_ip}",
                "TextPart": f"""
Network Monitor Alarm

Type:      {alert_type}
Kilde IP:  {src_ip}
Detaljer:  {details}
Tidspunkt: {timestamp}

Log ind på dashboardet:
http://192.168.0.19:5000
                """
            }]
        }

        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print(f"[EMAIL] Alarm sendt til {EMAIL_TO}")
        else:
            print(f"[EMAIL FEJL] Status: {result.status_code}")

    except Exception as e:
        print(f"[EMAIL FEJL] {e}")