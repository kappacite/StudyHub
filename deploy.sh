#!/bin/bash
# Script de déploiement pour exécuter les migrations et préparer la production

GREEN='\e[1;32m'
BLUE='\e[1;34m'
RED='\e[1;31m'
NC='\e[0m'

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}        Déploiement et Migration de la DB          ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Charger le .env
if [ -f ".env" ]; then
    echo -e "Chargement des variables d'environnement..."
    set -a
    source .env
    set +a
fi

export FLASK_APP=app
export FLASK_ENV=production

# Déterminer la commande python / flask
if [ -f "backend/venv/bin/flask" ]; then
    FLASK_CMD="backend/venv/bin/flask"
else
    FLASK_CMD="flask"
fi

echo -e "Exécution des migrations Alembic (flask db upgrade)..."
if (cd backend && PYTHONPATH=. ../$FLASK_CMD db upgrade); then
    echo -e "${GREEN}✓ Les migrations de la base de données ont été appliquées avec succès.${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'application des migrations.${NC}"
    exit 1
fi
