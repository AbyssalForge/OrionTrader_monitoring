# Chaosd Configuration

Chaosd est la version standalone de Chaos Mesh pour Docker.

## Configuration

Chaosd fonctionne principalement via son API REST sur le port 31767 (exposé sur 19095).

Le service a accès au socket Docker pour pouvoir manipuler les conteneurs.

## Sécurité

- Le conteneur tourne en mode `privileged` pour accéder aux ressources système
- Il a accès en lecture/écriture au socket Docker
