#!/usr/bin/env python3
"""
Service de forwarding des alertes AlertManager vers Discord
"""

from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK', '')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Reçoit les alertes d'AlertManager et les envoie à Discord"""
    data = request.json

    print(f"Received webhook: {json.dumps(data, indent=2)}")

    if not DISCORD_WEBHOOK:
        print("ERROR: DISCORD_WEBHOOK not configured!")
        return "DISCORD_WEBHOOK not configured", 500

    # Extraire les informations des alertes
    alerts = data.get('alerts', [])

    for alert in alerts:
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        status = alert.get('status', 'unknown')

        alert_name = labels.get('alertname', 'Unknown')
        severity = labels.get('severity', 'unknown')
        job = labels.get('job', 'Unknown')
        summary = annotations.get('summary', 'No summary')
        description = annotations.get('description', 'No description')

        # Déterminer l'emoji selon la sévérité
        if severity == 'critical':
            emoji = '🔴'
            color = 15158332  # Rouge
        elif severity == 'warning':
            emoji = '🟡'
            color = 16776960  # Jaune
        else:
            emoji = '🔵'
            color = 3447003  # Bleu

        # Déterminer si c'est une résolution
        if status == 'resolved':
            emoji = '✅'
            color = 3066993  # Vert
            title = f"{emoji} RÉSOLU: {alert_name}"
        else:
            title = f"{emoji} ALERTE: {alert_name}"

        # Créer le message embed Discord
        discord_message = {
            "embeds": [{
                "title": title,
                "description": summary,
                "color": color,
                "fields": [
                    {
                        "name": "Sévérité",
                        "value": severity.upper(),
                        "inline": True
                    },
                    {
                        "name": "Service",
                        "value": job,
                        "inline": True
                    },
                    {
                        "name": "Status",
                        "value": status.upper(),
                        "inline": True
                    },
                    {
                        "name": "Description",
                        "value": description,
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "AlertManager - OrionTrader Monitoring"
                }
            }]
        }

        # Envoyer à Discord
        try:
            response = requests.post(
                DISCORD_WEBHOOK,
                json=discord_message,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            print(f"✅ Alert sent to Discord: {alert_name}")
        except Exception as e:
            print(f"❌ Error sending to Discord: {e}")
            return f"Error: {e}", 500

    return "OK", 200

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return "OK", 200

if __name__ == '__main__':
    if not DISCORD_WEBHOOK:
        print("WARNING: DISCORD_WEBHOOK environment variable not set!")

    print(f"Starting webhook forwarder on 0.0.0.0:9094")
    app.run(host='0.0.0.0', port=9094, debug=False)
