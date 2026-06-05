#!/bin/bash

# Configuration des couleurs pour le terminal
GREEN='\e[1;32m'
BLUE='\e[1;34m'
YELLOW='\e[1;33m'
RED='\e[1;31m'
NC='\e[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}         Démarrage du projet StudyHub               ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Création du dossier de logs s'il n'existe pas
LOG_DIR="$(pwd)/logs"
mkdir -p "$LOG_DIR"

# Chargement d'un éventuel fichier .env
if [ -f ".env" ]; then
    echo -e "Chargement des variables d'environnement depuis le fichier .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Variables pour suivre les processus
OLLAMA_SPAWNED=false
BACKEND_PID=""
FRONTEND_PID=""
OLLAMA_PID=""

# Fonction de nettoyage à l'arrêt
cleanup() {
    echo -e "\n${YELLOW}🛑 Arrêt des services en cours...${NC}"
    
    if [ -n "$FRONTEND_PID" ]; then
        echo -e "Arrêt du frontend Vue.js (PID $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null
    fi
    
    if [ -n "$BACKEND_PID" ]; then
        echo -e "Arrêt du backend Flask (PID $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null
    fi
    
    if [ "$OLLAMA_SPAWNED" = true ] && [ -n "$OLLAMA_PID" ]; then
        echo -e "Arrêt de l'instance locale Ollama (PID $OLLAMA_PID)..."
        kill "$OLLAMA_PID" 2>/dev/null
    fi
    
    echo -e "${GREEN}✅ Tous les services ont été arrêtés proprement.${NC}"
    exit 0
}

# Capturer Ctrl+C, SIGTERM, SIGINT et EXIT
trap cleanup SIGINT SIGTERM EXIT

# 1. Vérification des prérequis de base
echo -e "\n${BLUE}[1/4] Vérification des prérequis...${NC}"

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Erreur : Node.js n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js est installé ($(node -v))${NC}"

# Vérifier npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Erreur : npm n'est pas installé.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm est installé ($(npm -v))${NC}"

# 2. Vérification de la configuration Gemini
echo -e "\n${BLUE}[2/4] Vérification de la configuration Gemini...${NC}"
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  Attention : La clé GEMINI_API_KEY n'est pas configurée dans votre environnement ou votre fichier .env.${NC}"
    echo -e "Les fonctionnalités IA (blurting, fiches de révision automatiques) ne seront pas disponibles."
else
    echo -e "${GREEN}✓ GEMINI_API_KEY est configurée (Modèle ciblé : ${GEMINI_MODEL:-gemini-1.5-flash})${NC}"
fi

# 3. Démarrage du Flask Backend
echo -e "\n${BLUE}[3/4] Démarrage du backend Flask...${NC}"
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Erreur : Le dossier 'backend' est introuvable.${NC}"
    exit 1
fi

# Configuration des variables par défaut
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_APP=${FLASK_APP:-app}
export GEMINI_MODEL=${GEMINI_MODEL:-"gemini-3.5-flash"}

# Démarrage avec le Python du venv ou le Python global
if [ -f "backend/venv/bin/python" ]; then
    echo -e "Utilisation de l'environnement virtuel (venv)..."
    (cd backend && venv/bin/python -m flask run --port 5000 --debug) > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
else
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé dans backend/venv. Essai avec le python3 global...${NC}"
    (cd backend && python3 -m flask run --port 5000 --debug) > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
fi

# Attente que le backend réponde
echo -e "Attente du backend Flask..."
for i in {1..15}; do
    if curl -s http://localhost:5000/api/v1/health &> /dev/null; then
        echo -e "${GREEN}✓ Backend Flask actif sur http://localhost:5000${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 15 ]; then
        echo -e "${RED}❌ Le backend Flask n'a pas répondu dans le délai imparti. Vérifiez les logs dans logs/backend.log.${NC}"
        cleanup
    fi
done

# 4. Démarrage du Frontend Vue.js
echo -e "\n${BLUE}[4/4] Démarrage du frontend Vue.js...${NC}"
if [ ! -d "web" ]; then
    echo -e "${RED}❌ Erreur : Le dossier 'web' est introuvable.${NC}"
    exit 1
fi

# Lancement de Vite sur le port 3000
(cd web && npm run dev -- --port 3000) > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

# Attente que le frontend réponde
echo -e "Attente du frontend Vue.js..."
for i in {1..15}; do
    if curl -s http://localhost:3000/ &> /dev/null; then
        echo -e "${GREEN}✓ Frontend Vue.js actif sur http://localhost:3000${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 15 ]; then
        echo -e "${RED}❌ Le frontend n'a pas répondu. Vérifiez les logs dans logs/frontend.log.${NC}"
        cleanup
    fi
done

echo -e "\n${GREEN}====================================================${NC}"
echo -e "${GREEN}🚀 Tous les services ont démarré avec succès !      ${NC}"
echo -e "   - Frontend : http://localhost:3000"
echo -e "   - Backend  : http://localhost:5000"
echo -e "${GREEN}====================================================${NC}"
echo -e "\n${BLUE}Pour suivre les logs en temps réel :${NC}"
echo -e " - Backend  : tail -f logs/backend.log"
echo -e " - Frontend : tail -f logs/frontend.log"
echo -e "\nAppuyez sur ${YELLOW}Ctrl+C${NC} pour arrêter tous les services d'un coup."

# Garder le script en cours d'exécution
wait
