# OrionTrader Monitoring Stack

Stack complète de monitoring, logging et chaos engineering pour les applications Audiomancy, déployable en local et sur VPS avec WireGuard VPN.

## Architecture

Cette stack de monitoring est conçue pour surveiller des applications externes (frontend/backend Audiomancy) tout en étant déployable sur un VPS avec accès via WireGuard VPN.

### Services de Monitoring

- **Prometheus** - Collecte et stockage de métriques time-series
- **Grafana** - Visualisation de métriques et logs via dashboards
- **Pushgateway** - Réception de métriques push pour jobs batch
- **Alertmanager** - Gestion et routage des alertes
- **Alertmanager Discord** - Forwarding des alertes vers Discord via webhook

### Services de Logging

- **Loki** - Agrégation et stockage de logs
- **Promtail** - Collecte de logs depuis les conteneurs Docker

### Chaos Engineering

- **Chaosd** - Daemon de chaos engineering pour tester la résilience
- **Chaosd UI** - Interface web pour déclencher des tests de chaos

## Environnements

### Local Development

Tous les services sont accessibles via `localhost` avec des ports mappés:

| Service | Port | URL |
|---------|------|-----|
| Grafana | 19091 | http://localhost:19091 |
| Prometheus | 19090 | http://localhost:19090 |
| Alertmanager | 19093 | http://localhost:19093 |
| Pushgateway | 19092 | http://localhost:19092 |
| Loki | 19100 | http://localhost:19100 |
| Chaosd UI | 19096 | http://localhost:19096 |

Credentials Grafana: `admin` / `admin`

### Production (VPS avec WireGuard)

En production, tous les services partagent le réseau du conteneur WireGuard (`network_mode: "container:wg-easy"`). Les services sont accessibles via l'IP VPN `10.8.0.1`:

| Service | URL (via VPN) |
|---------|---------------|
| Grafana | http://10.8.0.1:9091 |
| Prometheus | http://10.8.0.1:9090 |
| Alertmanager | http://10.8.0.1:9093 |
| Pushgateway | http://10.8.0.1:9092 |
| Loki | http://10.8.0.1:3100 |
| Chaosd UI | http://10.8.0.1:8080 |
| Frontend | http://10.8.0.1:3000 |
| Backend | http://10.8.0.1:8000 |

## Installation et Déploiement

### Prérequis

- Docker et Docker Compose
- (Production) Serveur VPS avec WireGuard configuré
- (Production) GitHub Actions configuré pour le déploiement automatique

### Configuration

1. Copier le fichier d'environnement:
```bash
cp .env.example .env
```

2. Éditer `.env` avec vos valeurs:
```env
# Ports locaux
PROMETHEUS_PORT=19090
GRAFANA_PORT=19091
PUSHGATEWAY_PORT=19092
ALERTMANAGER_PORT=19093
ALERTMANAGER_DISCORD_PORT=19094
LOKI_PORT=19100
CHAOSD_PORT=19095
CHAOSD_UI_PORT=19096

# Credentials Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password
GRAFANA_HTTP_PORT=9091

# Discord webhook pour les alertes
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Démarrage Local

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

### Déploiement Production (VPS)

Le déploiement en production se fait automatiquement via GitHub Actions lors d'un push sur la branche `main`.

Pour déployer manuellement sur le VPS:

```bash
# Sur le VPS, dans le dossier du projet
git pull
docker-compose -f docker-compose.prod.yaml down
docker-compose -f docker-compose.prod.yaml up -d
```

**Important**: En production, tous les services doivent utiliser l'IP `10.8.0.1` au lieu de `localhost` ou des noms de services Docker, car ils partagent le réseau du conteneur WireGuard.

## Configuration des Services

### Structure des Fichiers

```
OrionTrader_monitoring/
├── prometheus/
│   ├── prometheus.yml              # Config production
│   ├── prometheus.local.yml        # Config locale
│   ├── alert.rules.yml             # Règles d'alertes production
│   └── alert.rules.local.yml       # Règles d'alertes locales
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   ├── prod/              # Sources de données production (10.8.0.1)
│   │   │   └── local/             # Sources de données locales (noms de services)
│   │   └── dashboards/
│   └── dashboards/                 # Dashboards JSON
├── alertmanager/
│   ├── alertmanager.yml            # Config locale
│   └── alertmanager.prod.yml       # Config production (webhooks à 10.8.0.1:9098)
├── loki/
│   └── loki-config.yml
├── promtail/
│   ├── promtail-config.yml         # Config locale
│   └── promtail-config.prod.yml    # Config production (Loki à 10.8.0.1:3100)
├── alertmanager-discord/
│   └── webhook_forwarder.py        # Service Flask sur port 9098
├── chaosd-daemon/
│   └── Dockerfile
└── chaosd-ui/
    └── app.py
```

### Prometheus - Collecte de Métriques

Prometheus scrappe les endpoints `/metrics` des applications:

**Local** (`prometheus.local.yml`):
- Services internes: via noms Docker (`prometheus:9090`, `grafana:9091`)
- Applications externes: via noms Docker (`audiomancy-backend:8000`, `audiomancy-frontend:3000`)

**Production** (`prometheus.yml`):
- Tous les services: via IP VPN `10.8.0.1:PORT`

Les applications doivent exposer un endpoint `/metrics` (ou `/api/metrics` pour le frontend) au format Prometheus.

### Grafana - Dashboards

Trois dashboards préconfigurés:

1. **Audiomancy Backend** - Monitoring du backend FastAPI
   - Requêtes HTTP par route et code de statut
   - Latence des requêtes
   - Logs d'erreurs
   - Taux d'erreurs

2. **Audiomancy Frontend** - Monitoring du frontend React
   - Requêtes HTTP par route
   - Distribution des codes HTTP (2xx, 4xx, 5xx)
   - Logs du frontend

3. **Monitoring d'Incidents** - Vue d'ensemble de la santé du système
   - État des services (UP/DOWN)
   - Logs agrégés de tous les services
   - Alertes actives

### Alertmanager - Gestion des Alertes

Les alertes Prometheus sont routées vers Discord via le service `alertmanager-discord` qui expose un webhook sur le port 9098.

Types d'alertes configurées:
- **ServiceDown**: Service inaccessible pendant 2+ minutes
- **HighErrorRate**: Taux d'erreur > 5% pendant 5 minutes
- **HighLatency**: Latence > 1s pendant 5 minutes
- **HighCPU/HighMemory**: Ressources système critiques
- **SecurityAlert**: Tentatives d'accès non autorisées
- **PrivacyViolation**: Violation de conformité RGPD

### Loki & Promtail - Agrégation de Logs

**Promtail** collecte les logs de tous les conteneurs Docker et les envoie à **Loki**.

Configuration:
- Collecte automatique via `docker_sd_configs` (Docker service discovery)
- Filtrage par projet Docker Compose: `oriontrader_monitoring` et `audiomancy`
- Anonymisation automatique des données sensibles (emails, passwords, tokens)
- Extraction des niveaux de log (DEBUG, INFO, WARN, ERROR, CRITICAL)

**Important en production**: Loki rejette les logs trop anciens (> 1h par défaut). Si Promtail redémarre, il peut y avoir des erreurs temporaires le temps de rattraper les nouveaux logs.

### Chaos Engineering avec Chaosd

Chaosd permet de tester la résilience en injectant des pannes:

**Via l'interface web** (http://localhost:19096 ou http://10.8.0.1:8080):
- Arrêter/redémarrer des conteneurs
- Ajouter de la latence réseau
- Simuler une charge CPU/mémoire
- Tuer des processus

**Via API**:
```bash
# Arrêter un conteneur pendant 30 secondes
curl -X POST http://10.8.0.1:31767/api/attack/container \
  -H "Content-Type: application/json" \
  -d '{
    "action": "container-stop",
    "container_names": ["audiomancy-backend"],
    "duration": "30s"
  }'
```

## Troubleshooting

### Grafana: "Datasource not found"

En production avec WireGuard, Grafana ne peut pas utiliser les noms de services Docker. Vérifier que les datasources pointent vers `10.8.0.1:PORT`.

### Promtail: "entry too far behind"

Loki rejette les vieux logs. C'est normal au démarrage de Promtail. Attendez quelques minutes ou générez de nouveaux logs en utilisant les applications.

### Alertmanager-Discord: Port conflict

Le service utilise le port 9098 (pas 9094) pour éviter les conflits avec d'autres services sur le réseau WireGuard.

### Dashboards vides

Vérifier que:
1. Les applications exposent bien leurs métriques (`/metrics` ou `/api/metrics`)
2. Prometheus scrappe correctement les targets (Status > Targets dans Prometheus UI)
3. Promtail envoie les logs à Loki (vérifier `docker logs orion_promtail`)
4. Les datasources Grafana sont connectées (Configuration > Data Sources)

### Chaosd-ui contrôle les mauvais conteneurs

Assurez-vous d'accéder à Chaosd UI via l'IP VPN (`10.8.0.1:8080`) et non en local. Le conteneur Chaosd doit avoir accès au Docker socket du VPS.

## Documentation

- [MONITORING_GUIDE.md](MONITORING_GUIDE.md) - Guide détaillé des compétences de monitoring couvertes
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Chaosd Documentation](https://chaos-mesh.org/docs/simulate-physical-chaos-on-kubernetes/)

## Maintenance

### Nettoyage des Données

```bash
# Arrêter les services
docker-compose down

# Supprimer les volumes (attention: perte de données!)
docker volume rm oriontrader_monitoring_grafana-data
docker volume rm oriontrader_monitoring_prometheus-data
docker volume rm oriontrader_monitoring_loki-data

# Redémarrer
docker-compose up -d
```

### Mise à Jour des Images

```bash
docker-compose pull
docker-compose up -d
```

## Sécurité

- Les credentials Grafana sont définis dans `.env` (non versionné)
- Le webhook Discord est configuré via variable d'environnement
- En production, les services ne sont accessibles que via VPN WireGuard
- Chaosd tourne en mode `privileged` - limiter l'accès à l'interface
- Les logs sont anonymisés automatiquement (emails, passwords, tokens)

## Contribuer

1. Créer une branche pour vos modifications
2. Tester en local avec `docker-compose up`
3. Tester en production avec `docker-compose -f docker-compose.prod.yaml up`
4. Créer une pull request

## Licence

Projet interne OrionTrader
