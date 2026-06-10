# Référence de l'API REST v1 — StudyHub

Ce document décrit en détail chaque endpoint de l'API v1 de StudyHub pour faciliter la connexion et l'intégration du frontend (Vue.js / Axios).

---

## Sommaire
1. [Authentification](#1-authentification)
2. [Profil Utilisateur](#2-profil-utilisateur)
3. [Classeurs (Binders)](#3-classeurs-binders)
4. [Decks (Paquets de cartes)](#4-decks-paquets-de-cartes)
5. [Flashcards (Cartes mémoire)](#5-flashcards-cartes-mémoire)
6. [Notes](#6-notes)
7. [Diagrammes](#7-diagrammes)
8. [PDFs](#8-pdfs)
9. [Dashboard & Statistiques](#9-dashboard--statistiques)
10. [Espace Communautaire (Packages)](#10-espace-communautaire-packages)
11. [Révision Blurting (Feuille Blanche IA)](#11-révision-blurting-feuille-blanche-ia)

---

## 🔑 Conventions globales
* **URL de base** : `http://localhost:5000/api/v1`
* **Format des données** : Les corps de requêtes et de réponses sont au format `application/json` (sauf l'upload de PDF qui utilise `multipart/form-data`).
* **En-tête d'authentification** : Pour tous les endpoints protégés (notés `[Sécurisé]`), vous devez fournir l'en-tête suivant avec un access token valide :
  ```http
  Authorization: Bearer <your_access_token>
  ```
* **Format de réponse paginée** : Les listes paginées retournent toujours cet objet JSON :
  ```json
  {
    "data": [],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 12,
      "pages": 1
    }
  }
  ```

---

## 1. Authentification

### 📝 Inscription
Crée un nouveau compte utilisateur.
* **Route** : `POST /auth/register`
* **Type** : Public
* **Request Body** :
  ```json
  {
    "email": "student@example.com",
    "username": "superstudent",
    "password": "strongpassword123"
  }
  ```
* **Response** (Status `201 Created`) :
  ```json
  {
    "id": 1,
    "email": "student@example.com",
    "username": "superstudent",
    "is_active": true,
    "created_at": "2026-06-01T20:50:00.123456",
    "updated_at": "2026-06-01T20:50:00.123456"
  }
  ```

### 🔓 Connexion
Génère l'access token (courte durée) et le refresh token (longue durée) pour l'utilisateur.
* **Route** : `POST /auth/login`
* **Type** : Public
* **Request Body** :
  ```json
  {
    "email": "student@example.com",
    "password": "strongpassword123"
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "user": {
      "id": 1,
      "email": "student@example.com",
      "username": "superstudent",
      "is_active": true,
      "created_at": "2026-06-01T20:50:00",
      "updated_at": "2026-06-01T20:50:00"
    }
  }
  ```

### 🔄 Rafraîchir le token
Obtient un nouvel access token à partir du refresh token.
* **Route** : `POST /auth/refresh`
* **Type** : `[Sécurisé]` (Nécessite le **Refresh Token** dans l'en-tête `Authorization: Bearer <refresh_token>`)
* **Response** (Status `200 OK`) :
  ```json
  {
    "access_token": "eyJhbGciOi_new_access_token..."
  }
  ```

### 🚪 Déconnexion
* **Route** : `POST /auth/logout`
* **Type** : Public / Sans état sur le serveur
* **Response** (Status `204 No Content`) : *Corps vide*

### ⚠️ Suppression du compte (RGPD)
Supprime définitivement le compte utilisateur et toutes ses données associées (binders, decks, etc.).
* **Route** : `DELETE /auth/account`
* **Type** : `[Sécurisé]` (Nécessite l'**Access Token**)
* **Response** (Status `204 No Content`) : *Corps vide*

---

## 2. Profil Utilisateur

### 👤 Récupérer mon profil
* **Route** : `GET /users/me`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "email": "student@example.com",
    "username": "superstudent",
    "is_active": true,
    "created_at": "2026-06-01T20:50:00",
    "updated_at": "2026-06-01T20:50:00"
  }
  ```

### ✏️ Modifier mon profil
Met à jour l'email, le username ou le mot de passe de l'utilisateur connecté.
* **Route** : `PUT /users/me`
* **Type** : `[Sécurisé]`
* **Request Body** (Tous les champs sont optionnels) :
  ```json
  {
    "email": "new.email@example.com",
    "username": "newusername",
    "password": "newpassword456"
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "email": "new.email@example.com",
    "username": "newusername",
    "is_active": true,
    "created_at": "2026-06-01T20:50:00",
    "updated_at": "2026-06-01T20:56:00"
  }
  ```

---

## 3. Classeurs (Binders)

### 📁 Lister les classeurs
Récupère les classeurs d'un niveau donné. Pour lister les classeurs à la racine, omettez `parent_id` ou laissez-le vide.
* **Route** : `GET /binders`
* **Type** : `[Sécurisé]`
* **Query Parameters** :
  * `page` (int, défaut `1`)
  * `per_page` (int, défaut `20`)
  * `parent_id` (int, optionnel)
* **Response** (Status `200 OK`) :
  ```json
  {
    "data": [
      {
        "id": 2,
        "name": "Chimie Organique",
        "parent_id": 1,
        "user_id": 1,
        "created_at": "2026-06-01T20:51:00",
        "updated_at": "2026-06-01T20:51:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
  ```

### ➕ Créer un classeur
* **Route** : `POST /binders`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "name": "Semestre 1",
    "parent_id": null
  }
  ```
* **Response** (Status `201 Created`) :
  ```json
  {
    "id": 1,
    "name": "Semestre 1",
    "parent_id": null,
    "user_id": 1,
    "created_at": "2026-06-01T20:50:50",
    "updated_at": "2026-06-01T20:50:50"
  }
  ```

### 🔍 Détails d'un classeur
* **Route** : `GET /binders/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "name": "Semestre 1",
    "parent_id": null,
    "user_id": 1,
    "created_at": "2026-06-01T20:50:50",
    "updated_at": "2026-06-01T20:50:50"
  }
  ```

### ✏️ Modifier un classeur
Permet de renommer ou de déplacer un classeur dans un autre (changement de parent).
* **Route** : `PUT /binders/<id>`
* **Type** : `[Sécurisé]`
* **Request Body** (Tous les champs sont optionnels) :
  ```json
  {
    "name": "Semestre 1 - V2",
    "parent_id": 3
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "name": "Semestre 1 - V2",
    "parent_id": 3,
    "user_id": 1,
    "created_at": "2026-06-01T20:50:50",
    "updated_at": "2026-06-01T20:56:00"
  }
  ```

### ❌ Supprimer un classeur
Supprime le classeur, tous les sous-classeurs récursivement, et tout son contenu (decks, notes, diagrams, pdfs).
* **Route** : `DELETE /binders/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `204 No Content`) : *Corps vide*

### 🔓 Modifier la visibilité d'un classeur (Public / Privé)
Rend le classeur public pour l'espace communautaire ou le repasse en privé.
* **Route** : `PATCH /binders/<id>/visibility`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "is_public": true
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "name": "Semestre 1 - V2",
    "parent_id": 3,
    "user_id": 1,
    "is_public": true,
    "description": null,
    "tags": null,
    "fork_count": 0,
    "original_author_id": null,
    "created_at": "2026-06-01T20:50:50",
    "updated_at": "2026-06-01T20:56:00"
  }
  ```

### 🔍 Détails publics d'un classeur
Permet de récupérer les détails d'un classeur public (sans authentification).
* **Route** : `GET /binders/public/<id>`
* **Type** : Public
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "name": "Semestre 1 - V2",
    "parent_id": 3,
    "user_id": 1,
    "is_public": true,
    "description": null,
    "tags": null,
    "fork_count": 0,
    "original_author_id": null,
    "created_at": "2026-06-01T20:50:50",
    "updated_at": "2026-06-01T20:56:00"
  }
  ```

---

## 4. Decks (Paquets de cartes)

### 🗃️ Lister les decks
Récupère les decks de l'utilisateur, filtrables par classeur ou recherche textuelle.
* **Route** : `GET /decks`
* **Type** : `[Sécurisé]`
* **Query Parameters** :
  * `page` (int, défaut `1`)
  * `per_page` (int, défaut `20`)
  * `binder_id` (int, optionnel)
  * `search` (string, optionnel)
* **Response** (Status `200 OK`) :
  ```json
  {
    "data": [
      {
        "id": 1,
        "name": "Espagnol A1",
        "description": "Vocabulaire de base",
        "binder_id": 2,
        "user_id": 1,
        "created_at": "2026-06-01T20:52:00",
        "updated_at": "2026-06-01T20:52:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
  ```

### ➕ Créer un deck
* **Route** : `POST /decks`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "name": "Espagnol A1",
    "description": "Vocabulaire de base",
    "binder_id": 2
  }
  ```
* **Response** (Status `201 Created`) :
  ```json
  {
    "id": 1,
    "name": "Espagnol A1",
    "description": "Vocabulaire de base",
    "binder_id": 2,
    "user_id": 1,
    "created_at": "2026-06-01T20:52:00",
    "updated_at": "2026-06-01T20:52:00"
  }
  ```

### 🔍 Détails d'un deck
* **Route** : `GET /decks/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "name": "Espagnol A1",
    "description": "Vocabulaire de base",
    "binder_id": 2,
    "user_id": 1,
    "created_at": "2026-06-01T20:52:00",
    "updated_at": "2026-06-01T20:52:00"
  }
  ```

### ✏️ Modifier un deck
* **Route** : `PUT /decks/<id>`
* **Type** : `[Sécurisé]`
* **Request Body** (Tous les champs sont optionnels) :
  ```json
  {
    "name": "Espagnol A2",
    "description": "Verbes irréguliers",
    "binder_id": null
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "name": "Espagnol A2",
    "description": "Verbes irréguliers",
    "binder_id": null,
    "user_id": 1,
    "created_at": "2026-06-01T20:52:00",
    "updated_at": "2026-06-01T20:57:00"
  }
  ```

### ❌ Supprimer un deck
* **Route** : `DELETE /decks/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `204 No Content`) : *Corps vide*

### 📖 Récupérer les cartes à réviser (SM-2)
Récupère les cartes du deck qui sont arrivées à échéance ou sont nouvelles (prêtes pour étude aujourd'hui).
* **Route** : `GET /decks/<id>/study`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  [
    {
      "id": 15,
      "deck_id": 1,
      "front": "Hola",
      "back": "Bonjour",
      "ease_factor": 2.5,
      "interval": 0,
      "repetitions": 0,
      "next_review": "2026-06-01T20:52:00",
      "created_at": "2026-06-01T20:52:00",
      "updated_at": "2026-06-01T20:52:00"
    }
  ]
  ```

### 💬 Soumettre une réponse de révision
Enregistre l'évaluation de l'étudiant pour une carte mémoire donnée et recalcule sa prochaine date de révision.
* **Route** : `POST /decks/<deck_id>/study/answer/<card_id>`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "score": 5
  }
  ```
  *Note sur les scores (0 à 5)* :
  * `5` : Réponse parfaite.
  * `4` : Réponse correcte après hésitation.
  * `3` : Réponse correcte mais difficile à retrouver.
  * `2` : Faux, mais la bonne réponse semblait familière.
  * `1` : Faux, la bonne réponse revient facilement en tête.
  * `0` : Oubli total.
* **Response** (Status `200 OK` - Retourne la carte mise à jour) :
  ```json
  {
    "id": 15,
    "deck_id": 1,
    "front": "Hola",
    "back": "Bonjour",
    "ease_factor": 2.6,
    "interval": 1,
    "repetitions": 1,
    "next_review": "2026-06-02T20:58:30.456789",
    "created_at": "2026-06-01T20:52:00",
    "updated_at": "2026-06-01T20:58:30"
  }
  ```

---

## 5. Flashcards (Cartes mémoire)

### 🃏 Lister toutes les cartes d'un deck
* **Route** : `GET /decks/<deck_id>/cards`
* **Type** : `[Sécurisé]`
* **Query Parameters** :
  * `page` (int, défaut `1`)
  * `per_page` (int, défaut `20`)
* **Response** (Status `200 OK`) :
  ```json
  {
    "data": [
      {
        "id": 15,
        "deck_id": 1,
        "front": "Hola",
        "back": "Bonjour",
        "ease_factor": 2.5,
        "interval": 0,
        "repetitions": 0,
        "next_review": "2026-06-01T20:52:00",
        "created_at": "2026-06-01T20:52:00",
        "updated_at": "2026-06-01T20:52:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
  ```

### ➕ Ajouter une carte
* **Route** : `POST /decks/<deck_id>/cards`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "front": "Hola",
    "back": "Bonjour"
  }
  ```
* **Response** (Status `201 Created`) :
  ```json
  {
    "id": 15,
    "deck_id": 1,
    "front": "Hola",
    "back": "Bonjour",
    "ease_factor": 2.5,
    "interval": 0,
    "repetitions": 0,
    "next_review": "2026-06-01T20:52:00",
    "created_at": "2026-06-01T20:52:00",
    "updated_at": "2026-06-01T20:52:00"
  }
  ```

### 🔍 Détails d'une carte
* **Route** : `GET /decks/<deck_id>/cards/<card_id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 15,
    "deck_id": 1,
    "front": "Hola",
    "back": "Bonjour",
    "ease_factor": 2.5,
    "interval": 0,
    "repetitions": 0,
    "next_review": "2026-06-01T20:52:00",
    "created_at": "2026-06-01T20:52:00",
    "updated_at": "2026-06-01T20:52:00"
  }
  ```

### ✏️ Modifier une carte
* **Route** : `PUT /decks/<deck_id>/cards/<card_id>`
* **Type** : `[Sécurisé]`
* **Request Body** (Tous les champs sont optionnels) :
  ```json
  {
    "front": "Hola (Español)",
    "back": "Bonjour (Français)"
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 15,
    "deck_id": 1,
    "front": "Hola (Español)",
    "back": "Bonjour (Français)",
    "ease_factor": 2.5,
    "interval": 0,
    "repetitions": 0,
    "next_review": "2026-06-01T20:52:00",
    "created_at": "2026-06-01T20:52:00",
    "updated_at": "2026-06-01T20:59:00"
  }
  ```

### ❌ Supprimer une carte
* **Route** : `DELETE /decks/<deck_id>/cards/<card_id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `204 No Content`) : *Corps vide*

---

## 6. Notes

### 📝 Lister les notes
* **Route** : `GET /notes`
* **Type** : `[Sécurisé]`
* **Query Parameters** :
  * `page` (int, défaut `1`)
  * `per_page` (int, défaut `20`)
  * `binder_id` (int, optionnel)
  * `search` (string, optionnel)
* **Response** (Status `200 OK`) :
  ```json
  {
    "data": [
      {
        "id": 1,
        "title": "Cours de Physiologie",
        "content": "<p>Introduction au système cardiovasculaire...</p>",
        "binder_id": 1,
        "user_id": 1,
        "created_at": "2026-06-01T20:53:00",
        "updated_at": "2026-06-01T20:53:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
  ```

### ➕ Créer une note
* **Route** : `POST /notes`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "title": "Cours de Physiologie",
    "content": "<p>Introduction au système cardiovasculaire...</p>",
    "binder_id": 1
  }
  ```
* **Response** (Status `201 Created`) :
  ```json
  {
    "id": 1,
    "title": "Cours de Physiologie",
    "content": "<p>Introduction au système cardiovasculaire...</p>",
    "binder_id": 1,
    "user_id": 1,
    "created_at": "2026-06-01T20:53:00",
    "updated_at": "2026-06-01T20:53:00"
  }
  ```

### 🔍 Détails d'une note
* **Route** : `GET /notes/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "title": "Cours de Physiologie",
    "content": "<p>Introduction au système cardiovasculaire...</p>",
    "binder_id": 1,
    "user_id": 1,
    "created_at": "2026-06-01T20:53:00",
    "updated_at": "2026-06-01T20:53:00"
  }
  ```

### ✏️ Modifier une note
* **Route** : `PUT /notes/<id>`
* **Type** : `[Sécurisé]`
* **Request Body** (Tous les champs sont optionnels) :
  ```json
  {
    "title": "Cours de Physiologie Humaine",
    "content": "<p>Mise à jour...</p>",
    "binder_id": null
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "title": "Cours de Physiologie Humaine",
    "content": "<p>Mise à jour...</p>",
    "binder_id": null,
    "user_id": 1,
    "created_at": "2026-06-01T20:53:00",
    "updated_at": "2026-06-01T20:59:30"
  }
  ```

### ❌ Supprimer une note
* **Route** : `DELETE /notes/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `204 No Content`) : *Corps vide*

### 🔓 Modifier la visibilité d'une note (Public / Privé)
* **Route** : `PATCH /notes/<id>/visibility`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "is_public": true
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "title": "Cours de Physiologie Humaine",
    "content": "<p>Mise à jour...</p>",
    "binder_id": null,
    "user_id": 1,
    "is_public": true,
    "share_token": "a1b2c3d4e5f6g7h8i9j0",
    "created_at": "2026-06-01T20:53:00",
    "updated_at": "2026-06-01T20:59:30"
  }
  ```

### 🔍 Consulter une note publique (via token de partage)
Permet de consulter une note de manière anonyme.
* **Route** : `GET /notes/public/<token>`
* **Type** : Public
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "title": "Cours de Physiologie Humaine",
    "content": "<p>Mise à jour...</p>",
    "binder_id": null,
    "user_id": 1,
    "is_public": true,
    "share_token": "a1b2c3d4e5f6g7h8i9j0",
    "created_at": "2026-06-01T20:53:00",
    "updated_at": "2026-06-01T20:59:30"
  }
  ```

---

## 7. Diagrammes

### 📊 Lister les diagrammes
* **Route** : `GET /diagrams`
* **Type** : `[Sécurisé]`
* **Query Parameters** :
  * `page` (int, défaut `1`)
  * `per_page` (int, défaut `20`)
  * `binder_id` (int, optionnel)
* **Response** (Status `200 OK`) :
  ```json
  {
    "data": [
      {
        "id": 1,
        "title": "Cycle de Krebs",
        "code": "graph TD; A-->B; B-->C; C-->A;",
        "binder_id": 1,
        "user_id": 1,
        "created_at": "2026-06-01T20:54:00",
        "updated_at": "2026-06-01T20:54:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
  ```

### ➕ Créer un diagramme
* **Route** : `POST /diagrams`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "title": "Cycle de Krebs",
    "code": "graph TD; A-->B; B-->C; C-->A;",
    "binder_id": 1
  }
  ```
* **Response** (Status `201 Created`) :
  ```json
  {
    "id": 1,
    "title": "Cycle de Krebs",
    "code": "graph TD; A-->B; B-->C; C-->A;",
    "binder_id": 1,
    "user_id": 1,
    "created_at": "2026-06-01T20:54:00",
    "updated_at": "2026-06-01T20:54:00"
  }
  ```

### 🔍 Détails d'un diagramme
* **Route** : `GET /diagrams/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "title": "Cycle de Krebs",
    "code": "graph TD; A-->B; B-->C; C-->A;",
    "binder_id": 1,
    "user_id": 1,
    "created_at": "2026-06-01T20:54:00",
    "updated_at": "2026-06-01T20:54:00"
  }
  ```

### ✏️ Modifier un diagramme
* **Route** : `PUT /diagrams/<id>`
* **Type** : `[Sécurisé]`
* **Request Body** (Tous les champs sont optionnels) :
  ```json
  {
    "title": "Cycle de Krebs mis à jour",
    "code": "graph TD; A-->B;"
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "title": "Cycle de Krebs mis à jour",
    "code": "graph TD; A-->B;",
    "binder_id": 1,
    "user_id": 1,
    "created_at": "2026-06-01T20:54:00",
    "updated_at": "2026-06-01T21:00:00"
  }
  ```

### ❌ Supprimer un diagramme
* **Route** : `DELETE /diagrams/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `204 No Content`) : *Corps vide*

---

## 8. PDFs

### 📂 Lister les PDFs
* **Route** : `GET /pdfs`
* **Type** : `[Sécurisé]`
* **Query Parameters** :
  * `page` (int, défaut `1`)
  * `per_page` (int, défaut `20`)
  * `binder_id` (int, optionnel)
* **Response** (Status `200 OK`) :
  ```json
  {
    "data": [
      {
        "id": 1,
        "name": "Manuel d'Anatomie",
        "filename": "f8a9e1d2c3b4a5e6.pdf",
        "binder_id": 1,
        "user_id": 1,
        "created_at": "2026-06-01T20:55:00",
        "updated_at": "2026-06-01T20:55:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
  ```

### 📤 Uploader un PDF
Envoie le fichier physique sur le serveur avec ses métadonnées.
* **Route** : `POST /pdfs`
* **Type** : `[Sécurisé]`
* **Content-Type** : `multipart/form-data`
* **Form-data Fields** :
  * `file` (File, obligatoire, format `.pdf`)
  * `name` (string, optionnel, défaut : nom original du fichier)
  * `binder_id` (int, optionnel)
* **Response** (Status `201 Created`) :
  ```json
  {
    "id": 1,
    "name": "Manuel d'Anatomie.pdf",
    "filename": "f8a9e1d2c3b4a5e6.pdf",
    "binder_id": 1,
    "user_id": 1,
    "created_at": "2026-06-01T20:55:00",
    "updated_at": "2026-06-01T20:55:00"
  }
  ```

### 🔍 Métadonnées d'un PDF
* **Route** : `GET /pdfs/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  {
    "id": 1,
    "name": "Manuel d'Anatomie.pdf",
    "filename": "f8a9e1d2c3b4a5e6.pdf",
    "binder_id": 1,
    "user_id": 1,
    "created_at": "2026-06-01T20:55:00",
    "updated_at": "2026-06-01T20:55:00"
  }
  ```

### 📥 Télécharger / Streamer le fichier PDF
Renvoie le flux binaire brut du fichier PDF pour affichage avec PDF.js dans le navigateur.
* **Route** : `GET /pdfs/<id>/file`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  * **Headers** : `Content-Type: application/pdf`
  * **Body** : Fichier binaire PDF.

### ❌ Supprimer un PDF
Efface les métadonnées de la base et détruit le fichier physique sur le disque du serveur.
* **Route** : `DELETE /pdfs/<id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `204 No Content`) : *Corps vide*

---

## 9. Dashboard & Statistiques

### 📊 Vue d'ensemble du Dashboard
Récupère les statistiques agrégées globales.
* **Route** : `GET /stats/overview`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  {
    "streak": 5,
    "total_time_seconds": 15400,
    "total_reviewed": 152,
    "total_correct": 134
  }
  ```

### 📈 Récupérer les sessions d'étude
* **Route** : `GET /stats/sessions`
* **Type** : `[Sécurisé]`
* **Query Parameters** :
  * `from` (string ISO8601 optionnel, ex: `2026-05-01T00:00:00`)
  * `to` (string ISO8601 optionnel, ex: `2026-06-01T23:59:59`)
  * `module` (string optionnel, ex: `flashcard`, `note`, `diagram`)
* **Response** (Status `200 OK`) :
  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "module": "flashcard",
      "duration_seconds": 600,
      "cards_reviewed": 10,
      "cards_correct": 8,
      "created_at": "2026-06-01T18:50:00"
    }
  ]
  ```

### ➕ Enregistrer une session d'étude
Enregistre le temps passé par l'étudiant dans un module à la fin de son étude.
* **Route** : `POST /stats/sessions`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "module": "note",
    "duration_seconds": 900,
    "cards_reviewed": 0,
    "cards_correct": 0
  }
  ```
* **Response** (Status `201 Created`) :
  ```json
  {
    "id": 2,
    "user_id": 1,
    "module": "note",
    "duration_seconds": 900,
    "cards_reviewed": 0,
    "cards_correct": 0,
    "created_at": "2026-06-01T21:02:00"
  }
  ```

### 📅 Heatmap de calendrier d'activité
Retourne le temps d'étude agrégé par date sur les 365 derniers jours pour construire le calendrier de type GitHub.
* **Route** : `GET /stats/heatmap`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  [
    {
      "date": "2026-06-01",
      "duration": 1500,
      "count": 2
    }
  ]
  ```

### 📊 Statistiques de révision par Deck
Renvoie le score de rétention et l'échéance de révision d'un deck de flashcards.
* **Route** : `GET /stats/decks/<deck_id>`
* **Type** : `[Sécurisé]`
* **Response** (Status `200 OK`) :
  ```json
  {
    "deck_id": 1,
    "retention_rate": 88.16,
    "next_review": "2026-06-02T12:00:00",
    "cards_to_review": 5,
    "total_cards": 38
  }
  ```

---

## 10. Espace Communautaire (Packages)

Le module communautaire permet de publier des classeurs (et tout leur contenu sous-jacent : notes, decks, diagrammes) de manière publique pour que d'autres étudiants puissent les explorer et les cloner dans leur propre espace.

### 🌐 Lister les packages publics (Marketplace)
* **Route** : `GET /packages`
* **Type** : Public
* **Query Parameters** :
  * `page` (int, défaut `1`)
  * `per_page` (int, défaut `20`)
  * `search` (string, optionnel - recherche par nom, description ou tags)
* **Response** (Status `200 OK`) :
  ```json
  {
    "data": [
      {
        "id": 1,
        "name": "Physiologie S1",
        "parent_id": null,
        "user_id": 2,
        "is_public": true,
        "description": "Classeur complet contenant les cours de physio du S1",
        "tags": ["Médecine", "S1", "Biologie"],
        "fork_count": 12,
        "original_author_id": null,
        "created_at": "2026-06-01T20:50:50",
        "updated_at": "2026-06-01T20:56:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 1,
      "pages": 1
    }
  }
  ```

### 🔍 Consulter le contenu d'un package public
Retourne les métadonnées du classeur et un aperçu textuel à plat de tout ce qu'il contient (les titres des notes, les noms des decks, etc.).
* **Route** : `GET /packages/<binder_id>`
* **Type** : Public
* **Response** (Status `200 OK`) :
  ```json
  {
    "binder": {
      "id": 1,
      "name": "Physiologie S1",
      "parent_id": null,
      "user_id": 2,
      "is_public": true,
      "description": "Classeur complet contenant les cours de physio du S1",
      "tags": ["Médecine", "S1", "Biologie"],
      "fork_count": 12,
      "original_author_id": null,
      "created_at": "2026-06-01T20:50:50",
      "updated_at": "2026-06-01T20:56:00"
    },
    "notes": ["Système cardiovasculaire", "Système rénal"],
    "decks": ["Anatomie cardiaque"],
    "diagrams": ["Cycle cardiaque"],
    "pdfs": ["cours-physio.pdf"]
  }
  ```

### 👯 Cloner un package public
Copie récursivement tout le contenu d'un package public (classeurs enfants, notes, decks, flashcards, diagrammes, PDFs) dans le compte de l'utilisateur connecté. Le clone incrémente le compteur de forks (`fork_count`) du package source.
* **Route** : `POST /packages/<binder_id>/clone`
* **Type** : `[Sécurisé]`
* **Response** (Status `201 Created` - Retourne le nouveau classeur cloné racine) :
  ```json
  {
    "id": 15,
    "name": "Physiologie S1",
    "parent_id": null,
    "user_id": 1,
    "is_public": false,
    "description": "Classeur complet contenant les cours de physio du S1",
    "tags": ["Médecine", "S1", "Biologie"],
    "fork_count": 0,
    "original_author_id": 2,
    "created_at": "2026-06-09T22:50:00",
    "updated_at": "2026-06-09T22:50:00"
  }
  ```

---

## 11. Révision Blurting (Feuille Blanche IA)

Le Blurting consiste à rédiger sur une feuille blanche tout ce dont on se rappelle par rapport à un cours, puis à le comparer au cours réel. StudyHub automatise ce procédé grâce à l'IA de Gemini.

### 🧠 Analyser une restitution écrite (Blurting)
Compare le texte restitué par l'étudiant avec le contenu d'une note de cours.
* **Route** : `POST /blurting/analyze`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "note_id": 1,
    "user_blurting": "Le système cardiovasculaire comprend le cœur qui pompe le sang...",
    "duration_seconds": 300
  }
  ```
* **Response** (Status `200 OK`) :
  ```json
  {
    "feedback": "Votre restitution est excellente concernant les fonctions de pompage...",
    "coverage_score": 75,
    "key_points_missed": [
      "Le rôle des valves auriculo-ventriculaires",
      "La régulation nerveuse par le système sympathique"
    ],
    "suggested_flashcards": [
      {
        "front": "Quel est le rôle des valves auriculo-ventriculaires ?",
        "back": "Empêcher le reflux du sang des ventricules vers les oreillettes lors de la systole."
      }
    ]
  }
  ```

### 🃏 Créer les flashcards suggérées par l'analyse
Crée en une fois les flashcards sélectionnées suite à l'analyse et les insère dans un deck.
* **Route** : `POST /blurting/create-flashcards`
* **Type** : `[Sécurisé]`
* **Request Body** :
  ```json
  {
    "deck_id": 1,
    "flashcards": [
      {
        "front": "Quel est le rôle des valves auriculo-ventriculaires ?",
        "back": "Empêcher le reflux du sang des ventricules vers les oreillettes lors de la systole."
      }
    ]
  }
  ```
* **Response** (Status `201 Created`) :
  ```json
  {
    "created_count": 1,
    "flashcards": [
      {
        "id": 105,
        "deck_id": 1,
        "front": "Quel est le rôle des valves auriculo-ventriculaires ?",
        "back": "Empêcher le reflux du sang des ventricules vers les oreillettes lors de la systole.",
        "ease_factor": 2.5,
        "interval": 0,
        "repetitions": 0,
        "next_review": "2026-06-09T22:55:00",
        "created_at": "2026-06-09T22:55:00",
        "updated_at": "2026-06-09T22:55:00"
      }
    ]
  }
  ```
