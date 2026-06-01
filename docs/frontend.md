# Documentation Technique Frontend Web — StudyHub

Cette documentation détaille l'architecture, les technologies utilisées, l'intégration des fonctionnalités scientifiques (LaTeX/Markdown) et le fonctionnement de l'éditeur visuel interactif du module Frontend de StudyHub.

---

## 1. Choix Technologiques & Structure
Le frontend est conçu comme une **Single Page Application (SPA)** moderne :
* **Vue.js 3** : Utilisation exclusive de la **Composition API** avec la syntaxe `<script setup lang="ts">`.
* **Vite 5** : Outil de build et serveur de développement ultra-rapide.
* **TypeScript** : Typage statique strict sur l'ensemble de l'application (pas de type `any`).
* **TailwindCSS 3** : Intégration du Design System du projet, incluant le support natif du mode sombre (`dark:`).
* **Pinia** : Gestionnaire d'état centralisé pour découpler la logique métier des composants visuels.
* **Vue Router 4** : Routage dynamique avec gardes de navigation (auth/guest).

### Structure des dossiers (`web/src/`)
```
src/
├── main.ts             # Initialisation de l'application (Pinia, Router, localStorage)
├── App.vue             # Point d'entrée racine avec router-view
├── style.css           # Directives Tailwind CSS et scrollbars personnalisés
│
├── router/
│   └── index.ts        # Définition des routes et guards de sécurité
│
├── stores/             # Gestion de l'état (Pinia)
│   ├── auth.ts         # Session utilisateur & Mock API d'authentification
│   ├── binders.ts      # Arborescence de dossiers
│   ├── decks.ts        # Decks, cartes et algorithme de répétition espacée SM-2
│   └── notes.ts        # Notes de cours
│
├── composables/        # Logique réutilisable
│   └── usePlatform.ts  # Détection Web vs Capacitor Natif
│
├── components/
│   └── layout/
│       └── AppLayout.vue  # Layout principal (Sidebar rétractable, Dark mode, Profil)
│
└── views/              # Pages et Vues applicatives
    ├── Auth/           # Connexion & Inscription
    ├── Dashboard/      # Heatmap d'activité, objectifs et statistiques
    ├── Binders/        # Explorateur de dossiers et documents associés
    ├── Decks/          # Gestionnaire de decks et module d'étude (Flashcards 3D)
    ├── Notes/          # Liste des notes et éditeur enrichi (Markdown/LaTeX/PDF)
    ├── Diagrams/       # Créateur de diagrammes interactif (Drag & Drop + Mermaid)
    └── PDFs/           # Liseuse PDF et gestionnaire d'annotations épinglées
```

---

## 2. Authentification Mockée & Persistance
Afin de permettre le développement décorrélé du backend, l'authentification est simulée de façon asynchrone (délais de latence réseau de 1s) :
* **Stockage** : Lors d'une connexion réussie, l'utilisateur et le jeton JWT fictif sont stockés dans le `localStorage` de l'hôte.
* **Initialisation** : Au rechargement de la page, le store d'authentification ([auth.ts](file:///home/robyn/Documents/Dev/StudyHub/web/src/stores/auth.ts)) vérifie la présence de ces identifiants pour reconnecter automatiquement la session.
* **Sécurité** : Les routes protégées redirigent systématiquement vers `/login` si aucun token n'est présent.

---

## 3. Notes Scientifiques : Intégration Markdown + LaTeX
Le module de notes ([NoteEdit.vue](file:///home/robyn/Documents/Dev/StudyHub/web/src/views/Notes/NoteEdit.vue)) intègre un parseur hybride permettant d'écrire en Markdown tout en insérant des expressions mathématiques en LaTeX.

### Fonctionnement du Rendu Hybride
Pour éviter que le parseur Markdown n'interprète de façon erronée les formules LaTeX contenant des caractères réservés (comme les étoiles `*` ou les underscores `_`), le processus de rendu est découpé en 4 étapes :
1. **Extraction LaTeX Bloc (`$$...$$`)** : Recherche des équations hors-ligne, génération de leur structure HTML/SVG via `katex.renderToString` et remplacement de la formule par un code temporaire unique (ex : `LATEXBLOCKPLACEHOLDER0`).
2. **Extraction LaTeX en Ligne (`$...$`)** : Même procédé pour les équations au milieu du texte (ex : `LATEXINLINEPLACEHOLDER1`).
3. **Compilation Markdown** : Le texte intermédiaire est compilé en HTML par la librairie `marked`. Comme les codes temporaires ne contiennent que des lettres majuscules et des chiffres, ils restent inchangés.
4. **Réinjection LaTeX** : Remplacement de tous les codes temporaires par le HTML KaTeX précédemment généré.

### Export PDF
L'export en PDF s'appuie sur la fonction `window.print()` du navigateur. Des feuilles de style CSS spécifiques `@media print` masquent dynamiquement toute l'interface de l'application (menus, boutons d'action, barres d'outils) pour formater la note sur un fond blanc neutre, idéale pour une impression papier ou une sauvegarde PDF nette.

---

## 4. Éditeur de Diagrammes Interactif (Sans Clavier)
Le module diagrammes ([Diagrams.vue](file:///home/robyn/Documents/Dev/StudyHub/web/src/views/Diagrams/Diagrams.vue)) intègre un canvas interactif codé en SVG pur, permettant de manipuler des schémas de façon visuelle :
* **Géométrie des Nœuds** : Les coordonnées `(x, y)` d'un nœud correspondent au centre de la forme. Les rectangles, cercles et losanges sont rendus en les centrant sur ces coordonnées.
* **Drag and Drop** : Les événements `mousedown`, `mousemove` et `mouseup` sont capturés pour déplacer les formes sur une grille invisible. Les coordonnées de déplacement sont limitées par les bordures du plan.
* **Liaisons Mobiles** : Les flèches de connexion connectent directement le centre géométrique des nœuds. SVG recalcule automatiquement l'orientation et la longueur des lignes dès qu'un nœud est déplacé.
* **Interface Tactile** : Les liaisons se créent visuellement en sélectionnant un nœud de départ, puis un nœud cible.

---

## 5. Liseuse PDF & Annotations
Le module de gestion documentaire ([PDFs.vue](file:///home/robyn/Documents/Dev/StudyHub/web/src/views/PDFs/PDFs.vue)) simule un lecteur A4 :
* **Zoom et Navigation** : Gestion d'une échelle de zoom (70 % à 150 %) et de pagination.
* **Annotations géoréférencées** : L'étudiant peut taper un commentaire et l'épingler sur le document. Chaque commentaire génère un picto numéroté placé à des coordonnées en pourcentage `(X%, Y%)` sur la page virtuelle.

---

## 6. Commandes Utiles
Pour travailler sur la partie Web :
```bash
# Se placer dans le répertoire
cd web

# Installer les dépendances
npm install

# Lancer le serveur de développement local (sur le port 3000)
npm run dev -- --port 3000

# Valider la compilation TypeScript et compiler pour la production
npm run build
```
