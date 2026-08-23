---
name: audit-securite
description: Checklist de sécurité StudyHub (JWT, partage public, marketplace, XSS contenu utilisateur, IA Gemini, auto-migration). À charger pour la phase 2 (docs/audit/01-SECURITE.md) ou toute question de sécurité applicative.
---

# audit-securite

Checklist appliquée à la stack **réelle** de StudyHub (pas une stack générique) — chaque
point est à confirmer ou infirmer dans le code, avec `fichier:ligne`, pas supposé.

## Cycle de vie JWT

- Stockage du token côté client (`web/src/stores/auth.ts`, `services/api.ts`) : localStorage ?
  mémoire ? Expiration effective (`JWT_ACCESS_TOKEN_EXPIRES`), refresh, révocation possible
  (logout invalide-t-il vraiment le refresh token, ou juste côté client) ?
- Confusion d'algorithme (`flask-jwt-extended` : algorithme forcé, pas négociable depuis le
  token) ; `SECRET_KEY`/`JWT_SECRET_KEY` distincts et non par défaut en prod.

## Partage public

- `Note.share_token` (`backend/app/models/note.py`) : entropie (longueur, source aléatoire),
  énumérable ? révocable (régénération du token) ? expire-t-il ?
- `GET /api/v1/notes/public/:token`, `GET /api/v1/binders/public/:id` : la réponse fuit-elle
  des données annexes (identité réelle de l'auteur, ids internes d'autres ressources) ?
- `noindex` sur les pages publiques côté frontend (`PublicNote.vue`, `PackagePreview.vue`) ?

## Marketplace (`packages_bp`)

- `POST /packages/:binder_id/clone` : clone-t-il des données privées annexes (notes cachées,
  tags internes) ? Qui peut dépublier (`community_service.py`) ? Contrôle sur le contenu
  importé avant clonage ?

## Contenu utilisateur rendu (XSS)

Stack réelle (pas Tiptap/Mermaid malgré ce que documentaient les anciens AGENTS.md/README) :
- **Notes** : `marked` (Markdown → HTML) + **DOMPurify** — la configuration DOMPurify
  (`web/src/**`) autorise-t-elle des balises/attributs dangereux (`on*`, `javascript:`) ?
- **KaTeX** : `trust`/macros arbitraires activés ou non pour le rendu LaTeX des notes/libellés ?
- **Diagrammes** : éditeur SVG maison (`Diagrams.vue`) — pas de `securityLevel` Mermaid à
  vérifier puisque Mermaid n'est pas utilisé en runtime ; vérifier plutôt l'échappement du
  contenu texte des nœuds/libellés injecté dans le SVG.
- **PDF** : annotations géoréférencées — le texte d'annotation est-il échappé à l'affichage ?

## IA (Gemini)

- `ai_service.py`, `blurting.py`, `feynman.py`, `evaluations.py`, `quizzes.py` : la clé
  `GEMINI_API_KEY` transite-t-elle jamais côté client ? Une note malveillante (contenu
  utilisateur envoyé dans le prompt) peut-elle détourner l'instruction système (injection de
  prompt) ? Plafond de coût, timeout, politique de retry sur les tâches Celery associées ?

## Auto-migration au démarrage

**Traiter comme suspect par défaut**, mais le mécanisme réel est documenté et plus prudent que
le cas générique : `backend/wsgi.py` → `run_auto_migrations`, verrou `pg_advisory_lock`
sérialisant les workers gunicorn (voir skill `deployment`). Vérifier quand même : que se
passe-t-il si une migration échoue à mi-chemin (rollback, état de la base) ? Y a-t-il un
contrôle humain avant une migration destructrice (colonne supprimée, `NOT NULL` sans défaut)
en production ?

## Transversal

Rate limiting (`flask-limiter`, `RATELIMIT_ENABLED`), CORS (liste blanche dans
`backend/app/__init__.py` — vérifier qu'elle n'admet pas `*`), en-têtes de sécurité
(Flask-Talisman, CSP déjà présente dans `create_app` — vérifier `unsafe-inline`/`unsafe-eval`
dans `script-src`).

## Livrable

`docs/audit/01-SECURITE.md` : un constat = un id, `fichier:ligne`, description factuelle,
impact concret, gravité S1→S4, effort XS/S/M/L, piste de correction **sans l'appliquer**.
