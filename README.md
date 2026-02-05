# OrionTrader Monitoring & Chaos Engineering

Stack complète de monitoring et tests de résilience pour OrionTrader.

## Services déployés

### 📊 Monitoring
- **Prometheus** (port 19090) - Collecte de métriques
- **Grafana** (port 19091) - Visualisation et dashboards
- **Pushgateway** (port 19092) - Push de métriques
- **Alertmanager** (port 19093) - Gestion des alertes
- **Alertmanager Discord** (port 19094) - Notifications Discord
- **Loki** (port 19100) - Agrégation de logs
- **Promtail** - Collecte de logs Docker

### 🔥 Chaos Engineering
- **Chaosd** (port 19095) - Daemon de chaos engineering
- **Chaosd UI** (port 19096) - Interface web de tests de casse

## Démarrage rapide

### Environnement local
```bash
docker-compose up -d
```

### Environnement production
```bash
docker-compose -f docker-compose.prod.yaml up -d
```

## Accès aux interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:19091 | admin / admin |
| Prometheus | http://localhost:19090 | - |
| Alertmanager | http://localhost:19093 | - |
| Chaosd UI | http://localhost:19096 | - |

## Dashboards Grafana - Audiomancy

Trois dashboards simples pour le monitoring et le debugging :

### Dashboards disponibles
1. **Audiomancy Backend** : Requêtes HTTP, codes 200/400/500, erreurs, logs
2. **Audiomancy Frontend** : Requêtes HTTP, codes 200/400/500, erreurs, logs
3. **Monitoring d'Incidents** : Status des services (UP/DOWN) + logs agrégés de tous les services

### Compétences couvertes
- **C20** : Surveillance d'application IA avec monitoring et journalisation (MLOps)
- **C21** : Résolution d'incidents techniques avec analyse des logs

### Workflow de debugging
1. Ouvrir "Monitoring d'Incidents" pour détecter l'incident
2. Identifier le service concerné (Backend/Frontend/MongoDB)
3. Consulter le dashboard spécifique pour analyser les logs
4. Corriger le code et vérifier la résolution dans le dashboard

### Documentation complète
Voir [grafana/dashboards/README.md](./grafana/dashboards/README.md) pour le guide complet

## Chaosd - Tests de casse

L'interface Chaosd permet de tester la résilience de votre infrastructure :

### Fonctionnalités disponibles
- ⏸️ **Arrêter un conteneur** : Arrêt propre d'un conteneur audiomancy

### Exemple d'utilisation
```bash
# 1. Accéder à l'interface
open http://localhost:19096

# 2. Tester la résilience du backend
# Dans l'interface, arrêter audiomancy-backend
# Observer la réaction dans Grafana

# 3. Redémarrer le conteneur en cliquant sur "Arrêter" dans l'expérience
```

## Configuration des alertes

Les alertes Prometheus sont configurées dans :
- `prometheus/alert.rules.yml` (production)
- `prometheus/alert.rules.local.yml` (local)

Les notifications sont envoyées sur Discord via le webhook configuré.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OrionTrader Stack                     │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   App    │  │   API    │  │   DB     │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │              │                     │
│       │  Metrics    │   Metrics    │   Metrics          │
│       └─────────────┴──────────────┴────────────────┐   │
│                                                      │   │
│       ┌──────────────────────────────────────────────┘   │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────┐        ┌──────────┐       ┌──────────┐   │
│  │Prometheus│────────│ Grafana  │───────│  Loki    │   │
│  └────┬─────┘        └──────────┘       └────┬─────┘   │
│       │                                       │          │
│       │                                       │          │
│       ▼                                       ▼          │
│  ┌──────────┐                          ┌──────────┐     │
│  │Alertmgr  │──────────────────────────│ Promtail │     │
│  └────┬─────┘                          └──────────┘     │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────┐                                           │
│  │ Discord  │                                           │
│  └──────────┘                                           │
│                                                          │
│  ┌──────────┐        ┌──────────┐                      │
│  │ Chaosd   │────────│Chaosd UI │  (Chaos Engineering) │
│  └──────────┘        └──────────┘                      │
└─────────────────────────────────────────────────────────┘
```

## Documentation

- [Chaosd UI](./chaosd-ui/README.md) - Documentation complète de l'interface de chaos engineering
- [Configuration Chaosd](./chaosd/README.md) - Configuration du daemon Chaosd

## Développement

### Ajouter une alerte
1. Éditer `prometheus/alert.rules.yml`
2. Redémarrer Prometheus : `docker-compose restart prometheus`
3. Vérifier dans Alertmanager

### Ajouter un dashboard Grafana
1. Placer le JSON dans `grafana/dashboards/`
2. Redémarrer Grafana : `docker-compose restart grafana`

## Sécurité

⚠️ **ATTENTION** : L'interface Chaosd peut perturber votre infrastructure
- Utiliser uniquement en environnement de test
- Ne pas exposer publiquement sans authentification
- Les tests de casse peuvent impacter les performances

## Dépannage

### Les métriques n'apparaissent pas dans Prometheus
```bash
# Vérifier la configuration
docker logs orion_prometheus

# Vérifier les targets
open http://localhost:19090/targets
```

### Les alertes ne fonctionnent pas
```bash
# Vérifier Alertmanager
docker logs orion_alertmanager

# Tester le webhook Discord
curl -X POST http://localhost:19094/webhook -d '{}'
```

### Chaosd ne répond pas
```bash
# Vérifier les logs
docker logs orion_chaosd

# Vérifier l'accès au socket Docker
docker exec orion_chaosd ls -la /var/run/docker.sock
```