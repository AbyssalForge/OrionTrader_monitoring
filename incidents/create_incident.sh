#!/bin/bash

# Script de création automatique de rapport d'incident (C21)

echo "==================================="
echo "   Création d'un rapport d'incident"
echo "==================================="
echo ""

# Générer l'ID de l'incident
INCIDENT_ID="INC-$(date +%Y-%m-%d)-$(printf "%03d" $((RANDOM % 1000)))"
INCIDENT_FILE="incidents/in_progress/${INCIDENT_ID}.md"

# Créer le dossier si nécessaire
mkdir -p incidents/in_progress

echo "📝 Création du rapport : ${INCIDENT_ID}"
echo ""

# Demander les informations de base
read -p "Titre de l'incident : " TITLE
read -p "Service(s) affecté(s) (ex: audiomancy-backend) : " SERVICE
read -p "Sévérité (critique/majeure/mineure) : " SEVERITY

# Convertir la sévérité en emoji
case $SEVERITY in
  critique)
    SEVERITY_EMOJI="🔴 Critique"
    ;;
  majeure)
    SEVERITY_EMOJI="🟡 Majeure"
    ;;
  mineure)
    SEVERITY_EMOJI="🟢 Mineure"
    ;;
  *)
    SEVERITY_EMOJI="⚪ Non spécifiée"
    ;;
esac

# Copier le template et remplir les informations de base
cp incidents/templates/INCIDENT_TEMPLATE.md "$INCIDENT_FILE"

# Remplacer les placeholders
sed -i "s/\[TITRE DE L'INCIDENT\]/${TITLE}/g" "$INCIDENT_FILE"
sed -i "s/INC-YYYY-MM-DD-XXX/${INCIDENT_ID}/g" "$INCIDENT_FILE"
sed -i "s/YYYY-MM-DD HH:MM/$(date '+%Y-%m-%d %H:%M')/g" "$INCIDENT_FILE"
sed -i "s/audiomancy-backend, audiomancy-frontend, etc./${SERVICE}/g" "$INCIDENT_FILE"
sed -i "s/🔴 Critique \/ 🟡 Majeure \/ 🟢 Mineure/${SEVERITY_EMOJI}/g" "$INCIDENT_FILE"

echo ""
echo "✅ Rapport d'incident créé : ${INCIDENT_FILE}"
echo ""

# Récupérer automatiquement des informations de monitoring
echo "📊 Récupération des métriques Prometheus..."

# Taux d'erreur actuel
ERROR_RATE=$(curl -s "http://localhost:19090/api/v1/query?query=rate(http_requests_total{job=\"Audiomancy_backend\",status_code=~\"5..\"}[5m])" | grep -oP '"result":\[\{"metric".*?"value":\[\d+,"([^"]+)"\]' | grep -oP '\d+\.\d+' || echo "N/A")

# Latence P95
LATENCY_P95=$(curl -s "http://localhost:19090/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket{job=\"Audiomancy_backend\"}[5m]))" | grep -oP '"result":\[\{"metric".*?"value":\[\d+,"([^"]+)"\]' | grep -oP '\d+\.\d+' || echo "N/A")

echo "  - Taux d'erreur : ${ERROR_RATE}%"
echo "  - Latence P95 : ${LATENCY_P95}s"
echo ""

# Récupérer les derniers logs avec erreur via Loki
echo "📋 Récupération des logs récents (Loki)..."
echo "  URL : http://localhost:19100/loki/api/v1/query_range"
echo "  Requête : {service=\"${SERVICE}\"} |= \"ERROR\""
echo ""

# Créer un TODO dans le fichier
echo "" >> "$INCIDENT_FILE"
echo "## ✏️ TODO" >> "$INCIDENT_FILE"
echo "" >> "$INCIDENT_FILE"
echo "- [ ] Compléter la description de l'incident" >> "$INCIDENT_FILE"
echo "- [ ] Analyser les logs dans Loki" >> "$INCIDENT_FILE"
echo "- [ ] Identifier la cause racine" >> "$INCIDENT_FILE"
echo "- [ ] Appliquer la correction" >> "$INCIDENT_FILE"
echo "- [ ] Tester la solution" >> "$INCIDENT_FILE"
echo "- [ ] Déplacer vers incidents/resolved/" >> "$INCIDENT_FILE"
echo ""

echo "🔗 Liens utiles :"
echo "  - Grafana : http://localhost:19091"
echo "  - Prometheus : http://localhost:19090"
echo "  - AlertManager : http://localhost:19093"
echo "  - Loki : http://localhost:19100"
echo ""
echo "📝 Ouvrez le fichier pour compléter le rapport :"
echo "   ${INCIDENT_FILE}"
echo ""
