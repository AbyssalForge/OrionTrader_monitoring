# Tests de Chaos Engineering avec Pumba

## Installation de Pumba

```bash
# Windows (via Docker)
docker pull gaiaadm/pumba
```

## Tests de Résilience

### 1. Test d'arrêt aléatoire de conteneurs

Simule l'arrêt inattendu d'un service :

```bash
# Arrêter le backend pendant 30 secondes toutes les 5 minutes
docker run -d --name pumba-stop \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  --interval 5m \
  stop --duration 30s \
  --restart \
  audiomancy-backend
```

### 2. Test de latence réseau

Ajoute de la latence pour simuler des problèmes réseau :

```bash
# Ajouter 500ms de latence sur le backend
docker run -d --name pumba-delay \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  netem --duration 2m \
  delay --time 500 \
  audiomancy-backend
```

### 3. Test de perte de paquets

Simule une mauvaise connexion réseau :

```bash
# 20% de perte de paquets pendant 1 minute
docker run -d --name pumba-loss \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  netem --duration 1m \
  loss --percent 20 \
  audiomancy-frontend
```

### 4. Test de surcharge CPU

Simule une surcharge CPU :

```bash
# Stress CPU pendant 2 minutes
docker run -d --name pumba-stress \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  stress --duration 2m \
  --stress-type cpu \
  audiomancy-backend
```

### 5. Test d'arrêt de services critiques

Teste la reprise de service après un crash :

```bash
# Killer aléatoire de conteneurs
docker run -d --name pumba-kill \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  --interval 10m \
  --random \
  kill --signal SIGKILL \
  "re2:audiomancy-.*"
```

## Scénarios de Test Complets

### Scénario 1 : Test de résilience de l'infrastructure

```bash
# 1. Démarrer le monitoring
docker-compose -f docker-compose.local.yaml up -d

# 2. Vérifier que tout fonctionne
curl http://localhost:19090/-/healthy  # Prometheus
curl http://localhost:19091/api/health # Grafana

# 3. Lancer les tests de chaos
docker run -d --name chaos-test-1 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  --interval 2m \
  kill --signal SIGTERM \
  audiomancy-backend

# 4. Observer les alertes dans Grafana et AlertManager
# http://localhost:19091 - Grafana
# http://localhost:19093 - AlertManager

# 5. Vérifier les logs dans Loki
# Rechercher "ERROR" ou "restart" dans Grafana > Explore > Loki

# 6. Arrêter les tests
docker stop chaos-test-1 && docker rm chaos-test-1
```

### Scénario 2 : Test de dégradation progressive

```bash
# Simulation d'une dégradation progressive du réseau
docker run -d --name chaos-progressive \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gaiaadm/pumba \
  --interval 30s \
  netem --duration 1m \
  delay --time 100 --jitter 50 \
  "re2:audiomancy-.*"
```

## Vérification des Résultats

Après chaque test, vérifier :

1. **Alertes générées** : http://localhost:19093
2. **Dashboards Grafana** : http://localhost:19091
3. **Logs dans Loki** : Grafana > Explore > Loki
4. **Métriques Prometheus** : http://localhost:19090

## Nettoyage

```bash
# Arrêter tous les tests de chaos
docker stop $(docker ps -q --filter "name=pumba*")
docker rm $(docker ps -aq --filter "name=pumba*")
```

## Bonnes Pratiques

1. ✅ **Toujours tester en environnement de développement d'abord**
2. ✅ **Documenter les résultats des tests** (voir INCIDENT_TEMPLATE.md)
3. ✅ **Vérifier que les alertes se déclenchent correctement**
4. ✅ **S'assurer que les services redémarrent automatiquement**
5. ✅ **Analyser les logs pour comprendre les impacts**

## Métriques à Surveiller Pendant les Tests

- Taux d'erreurs HTTP 5xx
- Latence des requêtes (P95, P99)
- Disponibilité des services (uptime)
- Utilisation CPU/Mémoire
- Nombre de redémarrages de conteneurs
