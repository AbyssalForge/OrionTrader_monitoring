# Guide de Monitoring OrionTrader - Audiomancy

## 📋 Vue d'ensemble

Ce système de monitoring répond aux compétences professionnelles :

- **C20** : Surveillance d'application avec monitoring, journalisation, détection automatique d'incidents et conformité RGPD
- **C21** : Résolution d'incidents techniques avec documentation complète

## 🏗️ Architecture du Système

```
┌─────────────────────────────────────────────────────────────┐
│                    Stack de Monitoring                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 Prometheus (19090)  ─────►  📈 Grafana (19091)         │
│       │                              │                       │
│       │                              │                       │
│       ▼                              ▼                       │
│  🚨 AlertManager (19093)        📋 Loki (19100)            │
│       │                              ▲                       │
│       │                              │                       │
│       ▼                              │                       │
│  📮 Pushgateway (19092)         🚚 Promtail                 │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│              Services Surveillés                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🎵 Audiomancy Backend (8000)                               │
│  🎨 Audiomancy Frontend (3000)                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Démarrage Rapide

### 1. Lancer le système de monitoring

```bash
# Démarrer tous les services
docker-compose -f docker-compose.local.yaml up -d

# Vérifier que tout fonctionne
docker-compose -f docker-compose.local.yaml ps
```

### 2. Accéder aux interfaces

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Grafana** | http://localhost:19091 | admin / admin |
| **Prometheus** | http://localhost:19090 | - |
| **AlertManager** | http://localhost:19093 | - |
| **Loki** | http://localhost:19100 | - |

## 📊 Compétence C20 : Surveillance et Monitoring

### Métriques Collectées

#### Pour le Backend (audiomancy-backend:8000/metrics)
- `http_requests_total` - Nombre total de requêtes HTTP
- `http_request_duration_seconds` - Durée des requêtes
- `process_cpu_seconds_total` - Utilisation CPU
- `process_resident_memory_bytes` - Utilisation mémoire

#### Pour le Frontend (audiomancy-frontend:3000/api/metrics)
- `http_requests_total` - Requêtes HTTP
- `http_request_duration_seconds` - Latence
- `nodejs_heap_size_used_bytes` - Mémoire heap Node.js

### Dashboards Grafana

1. **Dossier Audiomancy**
   - `Audiomancy Backend` - Métriques du backend
   - `Audiomancy Frontend` - Métriques du frontend

2. **Visualisations disponibles**
   - Taux de requêtes
   - Latence (P50, P95)
   - Taux d'erreurs
   - Utilisation CPU/Mémoire

### Détection Automatique d'Incidents

Les alertes suivantes sont configurées :

#### Alertes Critiques 🔴
- `ServiceDown` - Service indisponible (>2min)
- `HighErrorRate` - Taux d'erreur >5% (>3min)
- `ModelAccuracyDrop` - Précision modèle ML <85% (>10min)

#### Alertes d'Avertissement 🟡
- `HighLatency` - Latence P95 >2s (>5min)
- `HighCPUUsage` - CPU >80% (>5min)
- `HighMemoryUsage` - Mémoire >2GB (>5min)

### Journalisation Centralisée (Loki)

#### Accéder aux logs dans Grafana

1. Grafana → **Explore**
2. Sélectionner **Loki** comme datasource
3. Exemples de requêtes :

```logql
# Tous les logs du backend
{container="audiomancy-backend"}

# Logs d'erreur uniquement
{container="audiomancy-backend"} |= "ERROR"

# Logs avec niveau de log extrait
{container="audiomancy-backend"} | json | level="ERROR"

# Recherche dans un intervalle de temps
{container="audiomancy-backend"} |= "ERROR" [5m]
```

### Conformité RGPD

✅ **Anonymisation automatique** dans Promtail :
- Emails : remplacés par `***EMAIL_REDACTED***`
- Mots de passe/tokens : remplacés par `***REDACTED***`
- Données personnelles : anonymisées

✅ **Rétention des données** :
- Logs : 31 jours (configurable dans loki-config.yml)
- Métriques : 15 jours par défaut (configurable dans prometheus.yml)

## 🔧 Compétence C21 : Résolution d'Incidents

### Processus de Gestion d'Incident

#### 1. Détection
- Alerte automatique via AlertManager
- Observation dans Grafana
- Notification utilisateur

#### 2. Création du rapport d'incident

```bash
# Méthode 1 : Script automatique (Linux/Mac)
bash incidents/create_incident.sh

# Méthode 2 : Manuel
cp incidents/templates/INCIDENT_TEMPLATE.md incidents/in_progress/INC-2025-XX-XX-001.md
```

#### 3. Investigation

**Outils disponibles :**

```bash
# Vérifier les métriques Prometheus
curl "http://localhost:19090/api/v1/query?query=up{job=\"Audiomancy_backend\"}"

# Voir les alertes actives
curl "http://localhost:19090/api/v1/alerts"

# Consulter les logs Docker
docker logs audiomancy-backend --tail 100

# Requête Loki via API
curl -G -s "http://localhost:19100/loki/api/v1/query_range" \
  --data-urlencode 'query={container="audiomancy-backend"} |= "ERROR"'
```

#### 4. Résolution

1. **Identifier la cause racine** (RCA)
2. **Appliquer les modifications au code**
3. **Tester la solution**
4. **Déployer**
5. **Vérifier les métriques**

#### 5. Documentation

Remplir le template d'incident avec :
- Description du problème
- Logs et métriques
- Cause racine (5 Pourquoi)
- Solution appliquée (diff de code)
- Tests de validation
- Actions préventives

#### 6. Archivage

```bash
# Déplacer vers les incidents résolus
mv incidents/in_progress/INC-2025-XX-XX-001.md incidents/resolved/
```

### Exemple de Workflow Complet

```bash
# 1. Alerte reçue : "HighErrorRate sur audiomancy-backend"

# 2. Créer le rapport
bash incidents/create_incident.sh

# 3. Consulter Grafana
# http://localhost:19091/d/audiomancy-backend

# 4. Analyser les logs
{container="audiomancy-backend"} |= "ERROR" [30m]

# 5. Identifier la cause (ex: bug dans l'API)

# 6. Corriger le code
git checkout -b fix/INC-2025-02-04-001
# ... modifications ...
git commit -m "fix: correction bug API

Resolves: INC-2025-02-04-001
- Ajout validation des paramètres
- Correction gestion erreur DB

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# 7. Tester
pytest tests/

# 8. Déployer et vérifier
docker-compose restart audiomancy-backend

# 9. Documenter dans le rapport d'incident

# 10. Archiver
mv incidents/in_progress/INC-2025-02-04-001.md incidents/resolved/
```

## 🐒 Tests de Chaos Engineering (Pumba)

### Pourquoi tester le chaos ?

- Valider la résilience du système
- Tester la détection automatique d'incidents
- S'entraîner à la résolution d'incidents
- Identifier les points faibles

### Tests disponibles

Voir le guide complet : [pumba/chaos-tests.md](pumba/chaos-tests.md)

**Tests principaux :**

1. **Arrêt de service** - Simule un crash
2. **Latence réseau** - Simule des problèmes réseau
3. **Perte de paquets** - Simule une connexion instable
4. **Surcharge CPU** - Simule une charge élevée
5. **Killer aléatoire** - Teste la reprise automatique

### Exemple : Test de résilience complet

```bash
# 1. S'assurer que le monitoring fonctionne
docker-compose -f docker-compose.local.yaml ps

# 2. Lancer un test de chaos
docker run -it --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  --interval 1m \
  kill --signal SIGTERM \
  audiomancy-backend

# 3. Observer dans Grafana :
#    - Dashboard "Audiomancy Backend"
#    - Alertes dans AlertManager
#    - Logs dans Loki (Explore)

# 4. Vérifier que :
#    ✅ L'alerte "ServiceDown" se déclenche
#    ✅ Le service redémarre automatiquement
#    ✅ Les métriques reviennent à la normale
#    ✅ Les logs sont collectés

# 5. Documenter le test dans un rapport d'incident
```

## 🔍 Requêtes Utiles

### Prometheus (PromQL)

```promql
# Taux de requêtes par seconde
rate(http_requests_total[5m])

# Taux d'erreur 5xx
rate(http_requests_total{status_code=~"5.."}[5m])

# Latence P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Services UP/DOWN
up{job=~"Audiomancy_.*"}

# Utilisation CPU
rate(process_cpu_seconds_total[5m])

# Utilisation mémoire
process_resident_memory_bytes / 1024 / 1024 / 1024  # en GB
```

### Loki (LogQL)

```logql
# Logs d'un service
{container="audiomancy-backend"}

# Erreurs uniquement
{container="audiomancy-backend"} |= "ERROR"

# Avec parsing JSON
{container="audiomancy-backend"} | json | level="ERROR"

# Compter les erreurs
sum(count_over_time({container="audiomancy-backend"} |= "ERROR" [1h]))

# Logs d'une période spécifique
{container="audiomancy-backend"} |= "ERROR" [2025-02-04T10:00:00Z]
```

## 📚 Structure des Fichiers

```
OrionTrader_monitoring/
├── alertmanager/
│   └── alertmanager.yml              # Configuration AlertManager
├── prometheus/
│   ├── prometheus.local.yml          # Config Prometheus
│   ├── alert.rules.yml               # Règles d'alerte de base
│   └── alert.rules.local.yml         # Règles complètes (C20/C21)
├── loki/
│   └── loki-config.yml               # Configuration Loki
├── promtail/
│   └── promtail-config.yml           # Config collecte de logs
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   ├── prometheus.local.yml  # Datasource Prometheus
│   │   │   └── loki.yml              # Datasource Loki
│   │   └── dashboards/
│   │       └── audiomancy.yml        # Config dossier Audiomancy
│   └── dashboards/
│       └── audiomancy/
│           ├── backend.json          # Dashboard backend
│           └── frontend.json         # Dashboard frontend
├── pumba/
│   └── chaos-tests.md                # Guide tests de chaos
├── incidents/
│   ├── templates/
│   │   └── INCIDENT_TEMPLATE.md      # Template C21
│   ├── in_progress/                  # Incidents en cours
│   ├── resolved/                     # Incidents résolus
│   └── create_incident.sh            # Script création incident
├── docker-compose.local.yaml         # Configuration Docker
└── MONITORING_GUIDE.md               # Ce guide
```

## 🎓 Compétences Démontrées

### C20 : Surveillance d'application IA

✅ **Techniques de monitorage**
- Prometheus pour les métriques
- Grafana pour la visualisation
- Dashboards personnalisés

✅ **Journalisation**
- Loki pour centralisation des logs
- Promtail pour collecte automatique
- Anonymisation RGPD

✅ **Détection automatique d'incidents**
- 10+ règles d'alerte configurées
- AlertManager pour le routage
- Notifications automatiques

✅ **Conformité RGPD**
- Anonymisation des données personnelles
- Rétention limitée (31 jours)
- Logs auditables

✅ **Feedback loop MLOps**
- Métriques de modèle ML
- Détection de drift
- Monitoring de la performance

### C21 : Résolution d'incidents techniques

✅ **Modifications au code**
- Documentation des changements
- Commits Git traçables
- Diff des corrections

✅ **Documentation complète**
- Template standardisé
- RCA (Root Cause Analysis)
- Actions préventives

✅ **Tests de validation**
- Tests unitaires
- Tests d'intégration
- Tests de chaos (Pumba)

✅ **Fonctionnement opérationnel**
- Monitoring post-correction
- Vérification des métriques
- Archivage des incidents

## 🆘 Dépannage

### Le monitoring ne démarre pas

```bash
# Vérifier les logs
docker-compose -f docker-compose.local.yaml logs

# Redémarrer les services
docker-compose -f docker-compose.local.yaml restart

# Reconstruire si nécessaire
docker-compose -f docker-compose.local.yaml up -d --build
```

### Les métriques ne s'affichent pas

1. Vérifier que les services exposent `/metrics`
2. Vérifier la configuration Prometheus
3. Consulter les targets : http://localhost:19090/targets

### Les logs ne s'affichent pas dans Loki

1. Vérifier que Promtail est en cours d'exécution
2. Vérifier les permissions Docker socket
3. Consulter les logs de Promtail : `docker logs orion_promtail`

## 📞 Support

Pour toute question ou problème :

1. Consulter ce guide
2. Vérifier les logs : `docker-compose logs [service]`
3. Consulter la documentation officielle :
   - [Prometheus](https://prometheus.io/docs/)
   - [Grafana](https://grafana.com/docs/)
   - [Loki](https://grafana.com/docs/loki/latest/)
   - [AlertManager](https://prometheus.io/docs/alerting/latest/alertmanager/)

---

**Version** : 1.0
**Date** : 2025-02-04
**Conforme aux compétences** : C20, C21
