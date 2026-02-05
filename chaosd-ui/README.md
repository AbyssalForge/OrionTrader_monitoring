# Chaosd UI - Interface Web de Chaos Engineering

Interface web pour gérer les tests de casse (chaos engineering) avec Chaosd.

## Fonctionnalités

### 💀 Tuer un conteneur
- Envoie un signal SIGKILL ou SIGTERM à un conteneur Docker
- Utile pour tester la résilience en cas de crash

### ⏸️ Arrêter un conteneur
- Arrête proprement un conteneur Docker
- Simule une maintenance planifiée

### ⚡ Stress CPU
- Génère une charge CPU artificielle
- Configure le nombre de workers et le pourcentage de charge
- Teste la réaction sous forte charge

### 💾 Stress Mémoire
- Alloue une quantité spécifique de mémoire
- Simule un leak mémoire ou une forte utilisation

### 🌐 Latence réseau
- Ajoute une latence artificielle aux connexions réseau
- Configure la latence et le jitter
- Teste la résilience aux problèmes réseau

### 📡 Perte de paquets
- Simule une perte de paquets réseau
- Configure le pourcentage de perte
- Teste la gestion des connexions instables

## Utilisation

1. Démarrer les services :
```bash
docker-compose up -d
```

2. Accéder à l'interface :
- URL: http://localhost:19096
- L'interface se connecte automatiquement à Chaosd

3. Lancer une expérience :
- Remplir les champs du type d'attaque souhaité
- Cliquer sur le bouton pour démarrer
- L'expérience apparaît dans la liste en bas de page

4. Arrêter une expérience :
- Cliquer sur "Arrêter" dans la liste des expériences

## Exemples d'utilisation

### Tester la résilience du monitoring
```
1. Aller dans "Arrêter un conteneur"
2. Entrer "orion_prometheus"
3. Cliquer sur "Arrêter le conteneur"
4. Observer dans Grafana comment le système réagit
5. Redémarrer le conteneur : docker-compose start prometheus
```

### Tester les alertes de CPU
```
1. Aller dans "Stress CPU"
2. Workers: 4
3. Charge: 100%
4. Démarrer le stress
5. Vérifier que Prometheus déclenche une alerte
6. Arrêter l'expérience dans la liste
```

### Tester la latence réseau
```
1. Aller dans "Latence réseau"
2. Latence: 500ms
3. Jitter: 100ms
4. Démarrer
5. Observer l'impact sur les métriques Prometheus
```

## API Endpoints

L'interface expose également une API REST :

### GET /api/experiments
Liste toutes les expériences en cours

### POST /api/attack/container-kill
```json
{
  "container_id": "orion_prometheus",
  "signal": "SIGKILL"
}
```

### POST /api/attack/container-stop
```json
{
  "container_id": "orion_grafana"
}
```

### POST /api/attack/stress-cpu
```json
{
  "workers": 2,
  "load": 100
}
```

### POST /api/attack/stress-memory
```json
{
  "size": "256MB"
}
```

### POST /api/attack/network-delay
```json
{
  "latency": "100ms",
  "jitter": "10ms"
}
```

### POST /api/attack/network-loss
```json
{
  "percent": 10
}
```

### DELETE /api/recover/:uid
Arrête une expérience par son UID

## Architecture

```
┌─────────────┐      HTTP      ┌──────────────┐      Docker API     ┌────────────┐
│   Browser   │ ────────────▶  │  Chaosd UI   │ ──────────────────▶ │  Chaosd    │
│             │                │  (Flask)     │                     │  (Daemon)  │
└─────────────┘                └──────────────┘                     └────────────┘
                                                                           │
                                                                           │
                                                                           ▼
                                                                    ┌──────────────┐
                                                                    │    Docker    │
                                                                    │  Containers  │
                                                                    └──────────────┘
```

## Sécurité

⚠️ **ATTENTION** : Cette interface permet de perturber votre infrastructure.

- Utiliser uniquement dans un environnement de test
- Ne pas exposer sur internet sans authentification
- Les conteneurs peuvent être arrêtés/tués sans confirmation
- Les expériences de stress peuvent impacter les performances

## Dépannage

### L'interface ne se connecte pas à Chaosd
- Vérifier que le conteneur `chaosd` est démarré : `docker ps | grep chaosd`
- Vérifier les logs : `docker logs orion_chaosd`

### Les attaques Docker ne fonctionnent pas
- Vérifier que Chaosd a accès au socket Docker
- Vérifier que le conteneur est en mode `privileged`

### Les expériences ne s'arrêtent pas
- Redémarrer le conteneur Chaosd : `docker-compose restart chaosd`
