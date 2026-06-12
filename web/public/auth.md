# StudyHub auth.md

Bienvenue sur la plateforme StudyHub. Ce document décrit comment les agents IA peuvent s'authentifier et s'enregistrer pour utiliser nos APIs protégées.

## 1. Enregistrement des Agents
Les agents peuvent s'enregistrer de manière anonyme ou en utilisant une adresse email vérifiée :
*   **Enregistrement anonyme** : Permet d'obtenir une clé API d'invité.
*   **Enregistrement par email** : Permet de créer un compte étudiant complet.

L'URL de redirection d'enregistrement est : `https://study.leshen.cloud/register`

## 2. Authentification des APIs
Toutes les requêtes d'API protégées sous `/api/v1` doivent inclure un jeton de type Bearer JWT dans l'en-tête `Authorization` :
```http
Authorization: Bearer <votre_token_jwt>
```
Le jeton s'obtient via l'endpoint de connexion `https://study.leshen.cloud/api/v1/auth/login`.
