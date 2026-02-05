# Dashboards Grafana - Audiomancy

## Vue d'ensemble

Dashboards simplifiés pour le monitoring et le debugging d'Audiomancy conformément aux compétences C20 et C21.

## 📊 Dashboards disponibles

### 1. Audiomancy Backend
**Objectif**: Surveiller les requêtes HTTP et erreurs du backend

**Panneaux**:
- **Requêtes par seconde** - Graphique du trafic HTTP (GET, POST, PUT, DELETE, PATCH)
- **Codes HTTP par minute** - Répartition 2xx (succès), 4xx (erreur client), 5xx (erreur serveur)
- **Jauges 2xx/4xx/5xx** - Compteurs visuels sur 5 minutes
- **Erreurs détectées** - Jauge des erreurs applicatives (5min)
- **Logs en temps réel** - Flux complet des logs du backend

### 2. Audiomancy Frontend
**Objectif**: Surveiller les requêtes HTTP et erreurs du frontend

**Panneaux**:
- **Requêtes par seconde** - Graphique du trafic HTTP (GET, POST, PUT, DELETE, PATCH)
- **Codes HTTP par minute** - Répartition 2xx (succès), 4xx (erreur client), 5xx (erreur serveur)
- **Jauges 2xx/4xx/5xx** - Compteurs visuels sur 5 minutes
- **Erreurs détectées** - Jauge des erreurs applicatives (5min)
- **Logs en temps réel** - Flux complet des logs du frontend

### 3. Audiomancy - Monitoring d'Incidents
**Objectif**: Vue globale pour détecter et résoudre les incidents

**Panneaux**:
- **Status des services** - Indicateurs UP/DOWN pour Backend, Frontend, MongoDB
- **Erreurs par service** - Comparaison des erreurs entre tous les services
- **Avertissements par service** - Comparaison des warnings entre tous les services
- **Logs tous services** - Flux agrégé de tous les logs avec filtrage par service

## 🎯 Compétences couvertes

### ✅ C20 - Surveillance d'application IA avec MLOps
- **Journalisation centralisée** via Loki pour tous les services
- **Détection automatique d'incidents** via comptage d'erreurs/warnings
- **Monitoring temps réel** avec rafraîchissement automatique
- **Feedback loop** pour amélioration continue

### ✅ C21 - Résolution des incidents techniques
- **Identification rapide** via les graphiques d'erreurs
- **Analyse des logs** en temps réel pour debugging
- **Statut des services** pour localiser la source du problème
- **Documentation automatique** via l'historique des métriques

## 🚀 Utilisation

### Accès aux dashboards
1. Ouvrir Grafana: http://localhost:19091
2. Login: `admin` / `admin`
3. Navigation: "Dashboards" → "Browse"
4. Sélectionner un des 3 dashboards Audiomancy

### Workflow de debugging (C21)

#### 1️⃣ Détection d'incident
- Ouvrir **"Monitoring d'Incidents"**
- Vérifier les status des services (rouge = DOWN)
- Observer les graphiques d'erreurs (pic = incident)

#### 2️⃣ Identification du service
- Si un service est DOWN, vérifier le dashboard spécifique
- Si erreurs détectées, comparer les graphiques entre services
- Identifier quel service génère le plus d'erreurs

#### 3️⃣ Analyse des logs
- Ouvrir le dashboard du service concerné
- Consulter les logs en temps réel
- Utiliser la recherche Loki pour filtrer (ex: `error`, `exception`, `failed`)
- Cliquer sur une ligne de log pour voir les détails

#### 4️⃣ Résolution
- Identifier la cause dans les logs (stack trace, message d'erreur)
- Corriger le code de l'application
- Redémarrer le conteneur via Chaosd UI ou docker
- Vérifier dans le dashboard que les erreurs ont disparu

#### 5️⃣ Documentation
- Les métriques historiques documentent automatiquement:
  - Quand l'incident s'est produit
  - Combien d'erreurs ont été générées
  - Quand le problème a été résolu
- Exporter les graphiques (PNG) pour rapports

## 🔍 Fonctionnalités avancées

### Filtrage des logs
Dans les panneaux de logs, utiliser la syntaxe LogQL:
```
# Afficher uniquement les erreurs
{container_name="audiomancy-backend"} |~ "(?i)error"

# Exclure les warnings
{container_name="audiomancy-backend"} !~ "(?i)warning"

# Rechercher un mot spécifique
{container_name="audiomancy-backend"} |= "database"
```

### Période temporelle
- Utiliser le sélecteur de temps (coin supérieur droit)
- Options rapides: Last 5m, Last 1h, Last 24h
- Ou sélectionner une période personnalisée

### Actualisation automatique
- Les dashboards se rafraîchissent toutes les 5 secondes
- Modifier l'intervalle dans les paramètres du dashboard

## 🔔 Alertes automatiques

Les alertes Prometheus sont configurées pour notifier sur Discord:
- ✉️ Plus de 10 erreurs en 5 minutes
- ✉️ Service DOWN pendant plus de 1 minute
- ✉️ Plus de 50 warnings en 10 minutes

Configuration: `prometheus/alert.rules.yml`

## 📝 Best Practices

### Pour C20 (Surveillance)
1. **Consulter quotidiennement** le dashboard "Monitoring d'Incidents"
2. **Surveiller les tendances** des erreurs/warnings
3. **Configurer des alertes** adaptées à votre application
4. **Centraliser tous les logs** dans Loki

### Pour C21 (Résolution)
1. **Utiliser les logs** comme première source d'information
2. **Documenter** les incidents résolus (annotations Grafana)
3. **Exporter les graphiques** pour les rapports
4. **Analyser les patterns** d'erreurs récurrentes

## 🛠️ Dépannage

### Les logs ne s'affichent pas
```bash
# Vérifier Promtail
docker logs orion_promtail

# Vérifier Loki
curl http://localhost:19100/ready

# Vérifier que les conteneurs sont en cours d'exécution
docker ps | grep audiomancy
```

### Les status sont incorrects
```bash
# Vérifier Prometheus
curl http://localhost:19090/api/v1/targets

# Vérifier cAdvisor
docker logs orion_prometheus | grep cadvisor
```

### Pas d'erreurs détectées alors qu'il y en a
- Vérifier le format des logs de votre application
- Les dashboards détectent: "error", "ERROR", "Error" (insensible à la casse)
- Modifier les requêtes LogQL si format différent

## 📚 Documentation supplémentaire

- [Loki LogQL](https://grafana.com/docs/loki/latest/logql/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [Prometheus Queries](https://prometheus.io/docs/prometheus/latest/querying/basics/)
