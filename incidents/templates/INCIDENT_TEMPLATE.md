# Rapport d'Incident - [TITRE DE L'INCIDENT]

**Compétence C21 : Résolution d'incident avec documentation**

---

## 📋 Informations Générales

| Champ | Valeur |
|-------|--------|
| **ID Incident** | INC-YYYY-MM-DD-XXX |
| **Date de détection** | YYYY-MM-DD HH:MM |
| **Date de résolution** | YYYY-MM-DD HH:MM |
| **Durée totale** | X heures Y minutes |
| **Sévérité** | 🔴 Critique / 🟡 Majeure / 🟢 Mineure |
| **Service(s) affecté(s)** | audiomancy-backend, audiomancy-frontend, etc. |
| **Détecté par** | AlertManager, Monitoring manuel, Utilisateur |
| **Résolu par** | [Nom/Équipe] |

---

## 🚨 Description de l'Incident

### Symptômes observés
- [ ] Service indisponible
- [ ] Erreurs 5xx
- [ ] Latence élevée
- [ ] Perte de données
- [ ] Autre : _______

### Description détaillée
[Décrire ce qui s'est passé, quand, et comment cela a été détecté]

### Impact utilisateur
- **Nombre d'utilisateurs affectés** : ___
- **Fonctionnalités impactées** : ___
- **Perte de revenus estimée** : ___ (si applicable)

---

## 🔍 Analyse Technique

### Logs pertinents (Loki)

```
[Coller les logs pertinents ici]
Exemple de requête Loki :
{service="audiomancy-backend"} |= "ERROR" | json
```

### Métriques observées (Prometheus)

**Avant l'incident :**
- CPU : ____%
- Mémoire : ___ MB
- Taux d'erreur : ____%
- Latence P95 : ___ ms

**Pendant l'incident :**
- CPU : ____%
- Mémoire : ___ MB
- Taux d'erreur : ____%
- Latence P95 : ___ ms

**Requêtes Prometheus utilisées :**
```promql
rate(http_requests_total{job="Audiomancy_backend",status_code=~"5.."}[5m])
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Timeline de l'incident

| Heure | Événement |
|-------|-----------|
| HH:MM | Détection initiale via alerte [nom de l'alerte] |
| HH:MM | Début de l'investigation |
| HH:MM | Cause racine identifiée |
| HH:MM | Correction appliquée |
| HH:MM | Service restauré |
| HH:MM | Confirmation de la résolution |

---

## 🔧 Cause Racine

### Analyse RCA (Root Cause Analysis)

**Cause principale identifiée :**
[Décrire la cause racine de l'incident]

**Facteurs contributifs :**
1.
2.
3.

**Diagramme des 5 Pourquoi :**
```
Problème : [Description]
├─ Pourquoi 1 :
├─ Pourquoi 2 :
├─ Pourquoi 3 :
├─ Pourquoi 4 :
└─ Pourquoi 5 : [CAUSE RACINE]
```

---

## 💻 Solution Appliquée

### Modifications du code

**Fichiers modifiés :**
```
- path/to/file1.py
- path/to/file2.ts
- path/to/config.yml
```

**Diff des changements :**
```diff
# Exemple
- ancienne_ligne = "valeur incorrecte"
+ nouvelle_ligne = "valeur corrigée"
```

**Commit Git :**
```bash
git commit -m "fix: [description de la correction]

Resolves: INC-YYYY-MM-DD-XXX
- Description du changement 1
- Description du changement 2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Actions correctives immédiates

1. ✅ [Action 1]
2. ✅ [Action 2]
3. ✅ [Action 3]

### Tests de validation

- [ ] Tests unitaires passés
- [ ] Tests d'intégration passés
- [ ] Vérification manuelle en environnement de dev
- [ ] Tests de chaos (Pumba) si applicable
- [ ] Monitoring des métriques post-correction

---

## 📊 Conformité et Traçabilité

### Respect des normes RGPD (C20)
- [ ] Aucune donnée personnelle exposée
- [ ] Logs anonymisés vérifiés
- [ ] Conformité à la politique de rétention des données
- [ ] Notification CNIL si nécessaire : ⬜ Oui / ☑️ Non

### Traçabilité MLOps (si applicable)
- [ ] Version du modèle ML affectée : ___
- [ ] Métriques du modèle avant/après : ___
- [ ] Données d'entraînement vérifiées
- [ ] Pipeline de feedback loop mis à jour

---

## 🎯 Actions Préventives (Post-Mortem)

### Court terme (< 1 semaine)
1. [ ] [Action préventive 1]
2. [ ] [Action préventive 2]

### Moyen terme (< 1 mois)
1. [ ] [Action préventive 1]
2. [ ] [Action préventive 2]

### Long terme (< 3 mois)
1. [ ] [Action préventive 1]
2. [ ] [Action préventive 2]

### Améliorations du monitoring
- [ ] Nouvelle alerte à configurer : ___
- [ ] Dashboard à créer/modifier : ___
- [ ] Seuil d'alerte à ajuster : ___

---

## 📚 Leçons Apprises

### Ce qui a bien fonctionné ✅
1.
2.
3.

### Ce qui pourrait être amélioré 🔄
1.
2.
3.

### Recommandations pour l'équipe 💡
1.
2.
3.

---

## 📎 Annexes

### Captures d'écran
- [Screenshot 1 : Dashboard Grafana pendant l'incident]
- [Screenshot 2 : Alertes AlertManager]
- [Screenshot 3 : Logs Loki]

### Liens utiles
- Dashboard Grafana : http://localhost:19091/d/...
- Alerte Prometheus : http://localhost:19090/alerts
- AlertManager : http://localhost:19093
- Issue GitHub : #___
- Pull Request : #___

### Personnes contactées
| Nom | Rôle | Date/Heure |
|-----|------|------------|
|     |      |            |

---

**Signature :**
- Rédacteur : _____________
- Date : YYYY-MM-DD
- Validé par : _____________
- Date de validation : YYYY-MM-DD

---

*Ce document respecte les exigences de la compétence C21 : Résolution d'incidents avec documentation complète*
