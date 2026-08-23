# StudyHub — Application d'étude tout-en-un

StudyHub est une plateforme web et mobile conçue pour centraliser tous les outils d'apprentissage des étudiants. Elle propose un ensemble de modules riches pour prendre des notes scientifiques, réviser avec un algorithme de répétition espacée, créer des diagrammes interactifs, annoter des PDF, et s'auto-évaluer à l'aide de l'intelligence artificielle.

---

## 🚀 Fonctionnalités principales

*   **📚 Prise de notes intelligente** : Éditeur supportant simultanément le Markdown et le LaTeX, avec mode Zen sans distraction, définitions interactives sous forme d'info-bulles et export PDF fluide.
*   **🗃️ Flashcards & Répétition Espacée** : Révisions optimisées grâce à l'algorithme SuperMemo-2 (SM-2) avec retour haptique sur mobile et animations de cartes en 3D.
*   **🧠 Révision Blurting (Feuille Blanche) IA** : Saisissez tout ce dont vous vous souvenez sur une note, et l'intelligence artificielle (Gemini) analyse votre restitution pour identifier vos lacunes et vous proposer des flashcards ciblées.
*   **📊 Diagrammes interactifs** : Éditeur visuel SVG en glisser-déposer (une refonte en canevas libre est prévue).
*   **📄 Annotations PDF** : Liseuse PDF avec possibilité d'épingler des commentaires géoréférencés directement sur les pages.
*   **🤝 Espace Communautaire (Marketplace)** : Partagez vos classeurs de révision avec d'autres étudiants sous forme de packages publics téléchargeables et clonables en un clic.
*   **🔗 Partage Public** : Générez des liens de partage uniques pour vos notes ou vos classeurs afin de les rendre accessibles en lecture seule sans inscription.
*   **📈 Dashboard & Statistiques** : Suivez votre assiduité quotidienne (heatmap GitHub-style), vos séries d'études (streaks) et vos métriques de rétention.

---

## 🛠️ Stack Technique

### Backend (Flask)
*   **Langage** : Python 3.12+
*   **Framework** : Flask 3.x
*   **Base de données** : PostgreSQL (production) / SQLite (développement)
*   **ORM** : SQLAlchemy 2.x avec patron de conception DAO
*   **Migrations** : Alembic & Flask-Migrate (avec auto-migration automatique au démarrage)
*   **Sécurité** : JWT via `flask-jwt-extended`
*   **Validation** : Pydantic v2

### Frontend Web (Vue.js)
*   **Framework** : Vue.js 3 (Composition API, `<script setup>`)
*   **Build** : Vite 5
*   **Style** : TailwindCSS 3 + HeadlessUI (mode sombre pris en charge nativement)
*   **State Management** : Pinia
*   **Routage** : Vue Router 4
*   **Librairies tierces** : `marked` + DOMPurify + highlight.js (Markdown/coloration syntaxique), KaTeX (LaTeX)

### Mobile (Capacitor)
*   **Wrapper** : Capacitor 8 pour encapsuler l'application Web sans réécriture de code (projet natif Android dans `web/android`).
*   **Intégration native** : Accès au stockage local, aux notifications locales et retours haptiques.

### Bureau (Electron)
*   **Wrapper** : Electron encapsule le même build Web (`desktop/`), packagé via electron-builder pour Windows/macOS/Linux.

---

## 📦 Installation et Lancement local

### Prérequis
*   **Docker** et **Docker Compose**
*   Ou pour un lancement manuel : **Python 3.12+** et **Node.js 18+**

### Option 1 : Lancement rapide avec Docker Compose
Pour lancer toute la stack (Flask backend + Vue.js frontend + base de données PostgreSQL + Redis) :

```bash
# Copier .env.example en .env et renseigner les valeurs (obligatoire, pas de valeurs par défaut)
cp .env.example .env

# Lancer les conteneurs — ./scripts/dev-up.sh détecte l'architecture (amd64/arm64)
./scripts/dev-up.sh --build
# ou directement :
docker compose up --build
```
*   Le frontend est accessible sur : `http://localhost:3000`
*   Le backend API est accessible sur : `http://localhost:5000`

### Option 2 : Lancement manuel (développement sans conteneur)

#### 1. Lancer le Backend
```bash
# Se placer dans le dossier backend
cd backend

# Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Modifiez .env si nécessaire (la base SQLite studyhub_dev.db est configurée par défaut)

# Lancer le serveur Flask
flask run --port=5000
```
*Note : Les migrations de base de données s'exécutent automatiquement au démarrage du serveur Flask.*

#### 2. Lancer le Frontend
```bash
# Se placer dans le dossier web
cd ../web

# Installer les dépendances npm
npm install

# Lancer le serveur de développement Vite
npm run dev -- --port 3000
```

---

## 🧪 Exécution des tests

### Backend
```bash
cd backend
source venv/bin/activate
python -m pytest
```

### Frontend
```bash
cd web
npm run test  # ou vitest
```

---

## 📂 Structure du dépôt

*   [`backend/`](backend/) : Code source de l'API Flask (Modèles, DAO, Services, Contrôleurs).
*   [`web/`](web/) : Code source de l'application Web Vue.js 3 / Vite ; `web/android` contient le projet natif généré par Capacitor.
*   [`desktop/`](desktop/) : Coque bureau Electron, packagée via electron-builder.
*   [`docs/`](docs/) : Documentation technique approfondie de l'API, du frontend et du backend.
*   [`AGENTS.md`](AGENTS.md) : Définition des règles de conception architecturales et spécifications globales.