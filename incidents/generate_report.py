#!/usr/bin/env python3
"""
Script de génération automatique de rapport d'incident (C21)
Récupère les données depuis Prometheus, Loki et AlertManager
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Configuration
PROMETHEUS_URL = "http://localhost:19090"
LOKI_URL = "http://localhost:19100"
ALERTMANAGER_URL = "http://localhost:19093"
INCIDENT_DIR = "incidents/in_progress"

def get_alerts():
    """Récupère les alertes actives depuis AlertManager"""
    try:
        response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des alertes: {e}")
        return []

def get_metrics(service_name):
    """Récupère les métriques Prometheus pour un service"""
    metrics = {}

    queries = {
        "error_rate": f'rate(http_requests_total{{job="{service_name}",status_code=~"5.."}}[5m])',
        "latency_p95": f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{job="{service_name}"}}[5m]))',
        "cpu_usage": f'rate(process_cpu_seconds_total{{job="{service_name}"}}[5m])',
        "memory_usage": f'process_resident_memory_bytes{{job="{service_name}"}} / 1024 / 1024 / 1024',
    }

    for name, query in queries.items():
        try:
            response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
            response.raise_for_status()
            data = response.json()
            if data["data"]["result"]:
                metrics[name] = data["data"]["result"][0]["value"][1]
            else:
                metrics[name] = "N/A"
        except Exception as e:
            metrics[name] = f"Error: {e}"

    return metrics

def get_logs(container_name, search_term="ERROR", limit=50):
    """Récupère les logs depuis Loki"""
    try:
        # Requête pour les 30 dernières minutes
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=30)

        query = f'{{container="{container_name}"}} |= "{search_term}"'

        params = {
            "query": query,
            "limit": limit,
            "start": int(start_time.timestamp() * 1e9),  # nanoseconds
            "end": int(end_time.timestamp() * 1e9),
            "direction": "backward"
        }

        response = requests.get(f"{LOKI_URL}/loki/api/v1/query_range", params=params)
        response.raise_for_status()
        data = response.json()

        logs = []
        if data.get("data", {}).get("result"):
            for stream in data["data"]["result"]:
                for entry in stream.get("values", []):
                    timestamp = datetime.fromtimestamp(int(entry[0]) / 1e9)
                    log_line = entry[1]
                    logs.append(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {log_line}")

        return logs[:limit]  # Limiter le nombre de logs
    except Exception as e:
        return [f"❌ Erreur lors de la récupération des logs: {e}"]

def generate_incident_id():
    """Génère un ID unique pour l'incident"""
    return f"INC-{datetime.now().strftime('%Y-%m-%d')}-{datetime.now().strftime('%H%M%S')}"

def create_incident_report(alert_data=None, service_name="Audiomancy_backend"):
    """Génère un rapport d'incident complet"""

    incident_id = generate_incident_id()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Récupération des données
    print(f"📊 Récupération des métriques pour {service_name}...")
    metrics = get_metrics(service_name)

    print(f"📋 Récupération des logs...")
    logs = get_logs(service_name.replace("_", "-").lower())

    print(f"🚨 Récupération des alertes...")
    alerts = get_alerts()

    # Création du rapport
    report = f"""# Rapport d'Incident - {incident_id}

**Compétence C21 : Résolution d'incident avec documentation**

---

## 📋 Informations Générales

| Champ | Valeur |
|-------|--------|
| **ID Incident** | {incident_id} |
| **Date de détection** | {timestamp} |
| **Date de résolution** | À compléter |
| **Durée totale** | À calculer |
| **Sévérité** | 🟡 À déterminer |
| **Service(s) affecté(s)** | {service_name} |
| **Détecté par** | AlertManager / Script automatique |
| **Résolu par** | À compléter |

---

## 🚨 Description de l'Incident

### Alertes actives

"""

    # Ajout des alertes
    if alerts:
        for alert in alerts:
            alert_name = alert.get("labels", {}).get("alertname", "Unknown")
            severity = alert.get("labels", {}).get("severity", "unknown")
            status = alert.get("status", {}).get("state", "unknown")
            report += f"- **[{severity.upper()}]** {alert_name} - Status: {status}\n"
    else:
        report += "Aucune alerte active actuellement.\n"

    report += f"""

### Symptômes observés
- [ ] Service indisponible
- [ ] Erreurs 5xx
- [ ] Latence élevée
- [ ] Perte de données
- [ ] Autre : _______

### Description détaillée
[À compléter manuellement après analyse]

---

## 🔍 Analyse Technique

### Métriques observées (Prometheus)

**Actuellement :**
- **Taux d'erreur** : {metrics.get('error_rate', 'N/A')}
- **Latence P95** : {metrics.get('latency_p95', 'N/A')}s
- **CPU Usage** : {metrics.get('cpu_usage', 'N/A')}%
- **Mémoire** : {metrics.get('memory_usage', 'N/A')} GB

**Requêtes Prometheus utilisées :**
```promql
# Taux d'erreur
rate(http_requests_total{{job="{service_name}",status_code=~"5.."}}[5m])

# Latence P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{job="{service_name}"}}[5m]))

# CPU
rate(process_cpu_seconds_total{{job="{service_name}"}}[5m])

# Mémoire
process_resident_memory_bytes{{job="{service_name}"}} / 1024 / 1024 / 1024
```

### Logs pertinents (Loki)

**Derniers logs avec erreurs (30 dernières minutes) :**

```
"""

    # Ajout des logs
    if logs:
        report += "\n".join(logs[:20])  # Max 20 logs
    else:
        report += "Aucun log d'erreur trouvé."

    report += f"""
```

**Requête Loki utilisée :**
```logql
{{container="{service_name.replace("_", "-").lower()}"}} |= "ERROR"
```

---

## 🔧 Cause Racine

### Analyse RCA (Root Cause Analysis)

**Cause principale identifiée :**
[À compléter après investigation]

**Facteurs contributifs :**
1. [À compléter]
2. [À compléter]

**Diagramme des 5 Pourquoi :**
```
Problème : [Description]
├─ Pourquoi 1 : [À compléter]
├─ Pourquoi 2 : [À compléter]
├─ Pourquoi 3 : [À compléter]
├─ Pourquoi 4 : [À compléter]
└─ Pourquoi 5 : [CAUSE RACINE - À identifier]
```

---

## 💻 Solution Appliquée

### Modifications du code

**Fichiers modifiés :**
```
[À compléter]
```

**Commit Git :**
```bash
git commit -m "fix: {incident_id} - [description]

Resolves: {incident_id}
- [Description du changement]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Actions correctives immédiates

1. ☐ [Action 1]
2. ☐ [Action 2]
3. ☐ [Action 3]

---

## 📊 Conformité et Traçabilité

### Respect des normes RGPD (C20)
- [ ] Aucune donnée personnelle exposée
- [ ] Logs anonymisés vérifiés
- [ ] Conformité à la politique de rétention des données

---

## 🎯 Actions Préventives (Post-Mortem)

### Court terme (< 1 semaine)
1. [ ] [Action préventive 1]
2. [ ] [Action préventive 2]

### Améliorations du monitoring
- [ ] Nouvelle alerte à configurer : ___
- [ ] Dashboard à créer/modifier : ___
- [ ] Seuil d'alerte à ajuster : ___

---

## 📚 Leçons Apprises

### Ce qui a bien fonctionné ✅
1. Détection automatique via AlertManager
2. Récupération rapide des logs via Loki
3. Métriques disponibles dans Prometheus

### Ce qui pourrait être amélioré 🔄
[À compléter]

---

## 📎 Annexes

### Liens utiles
- Dashboard Grafana : http://localhost:19091/d/audiomancy-backend
- Prometheus : http://localhost:19090
- AlertManager : http://localhost:19093
- Loki : http://localhost:19100

---

**Généré automatiquement le {timestamp}**
*Script : generate_report.py - Conforme C21*
"""

    # Sauvegarde du rapport
    os.makedirs(INCIDENT_DIR, exist_ok=True)
    filename = f"{INCIDENT_DIR}/{incident_id}.md"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ Rapport d'incident généré : {filename}")
    print(f"\n📝 Étapes suivantes :")
    print(f"1. Ouvrir le fichier : {filename}")
    print(f"2. Compléter les sections 'À compléter'")
    print(f"3. Analyser la cause racine")
    print(f"4. Documenter la solution")
    print(f"5. Déplacer vers incidents/resolved/ une fois résolu")

    return filename

def main():
    print("=" * 60)
    print("  Génération de Rapport d'Incident (C21)")
    print("=" * 60)
    print()

    # Vérifier si les services sont accessibles
    print("🔍 Vérification des services...")

    services_ok = True
    for name, url in [("Prometheus", PROMETHEUS_URL), ("Loki", LOKI_URL), ("AlertManager", ALERTMANAGER_URL)]:
        try:
            requests.get(url, timeout=2)
            print(f"  ✅ {name} accessible")
        except:
            print(f"  ❌ {name} inaccessible ({url})")
            services_ok = False

    if not services_ok:
        print("\n⚠️  Certains services ne sont pas accessibles.")
        print("   Le rapport sera généré avec les données disponibles.\n")

    # Demander le service à surveiller
    if len(sys.argv) > 1:
        service = sys.argv[1]
    else:
        print("\n📋 Services disponibles :")
        print("  1. Audiomancy_backend")
        print("  2. Audiomancy_frontend")
        print()
        choice = input("Choisir un service (1 ou 2, ou nom complet) : ").strip()

        if choice == "1":
            service = "Audiomancy_backend"
        elif choice == "2":
            service = "Audiomancy_frontend"
        else:
            service = choice or "Audiomancy_backend"

    print(f"\n🎯 Génération du rapport pour : {service}\n")

    # Génération du rapport
    report_file = create_incident_report(service_name=service)

    print(f"\n📊 Rapport disponible à : {report_file}")
    print()

if __name__ == "__main__":
    main()
