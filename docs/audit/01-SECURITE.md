# Audit sécurité — Phase 2

> Revue en lecture seule, aucune correction appliquée. Chaque constat : identifiant,
> emplacement `fichier:ligne`, description factuelle, impact concret, gravité S1 (critique) →
> S4 (cosmétique), effort XS/S/M/L, piste de correction **non appliquée**. Méthode : lecture du
> code réel, pas de la stack décrite à l'origine dans `docs/PROMPT_DEMARRAGE.md` (voir
> `docs/audit/00-CARTOGRAPHIE.md` pour l'état réel).

## Constats

### SEC-01 — Clés secrètes avec valeur de repli devinable

**Emplacement** : `backend/app/config.py:5-6`

```python
SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key_change_me_in_production_123456")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev_jwt_secret_key_change_me_in_production_123456")
```

`ProductionConfig` hérite de `Config` sans jamais vérifier que ces variables d'environnement
sont réellement définies. Si le déploiement oublie `SECRET_KEY`/`JWT_SECRET_KEY` (erreur de
configuration Docker/CI, variable non montée), l'application démarre silencieusement avec des
clés en clair, connues de quiconque lit ce fichier public.

**Impact** : avec `JWT_SECRET_KEY` connue, n'importe qui peut forger un JWT valide pour
n'importe quel `user_id` (usurpation totale de compte) sans jamais avoir de mot de passe.
`SECRET_KEY` compromet en plus tout ce qui en dépend (signatures Flask, futures sessions
signées).

**Gravité** : S1 (si le défaut est réellement utilisé en prod — condition non vérifiée : à
confirmer sur l'environnement de déploiement réel, hors périmètre lecture-code de cet audit).
**Effort** : XS — faire échouer `ProductionConfig` au chargement si `SECRET_KEY` ou
`JWT_SECRET_KEY` est absent de l'environnement (`os.environ["..."]` sans défaut, ou assertion
explicite dans `create_app`).

---

### SEC-02 — Contenu privé exposé sous un classeur public (marketplace)

**Emplacement** :
- `backend/app/api/v1/packages.py:50-64` (fonction `collect_contents`, endpoint
  `GET /packages/<binder_id>`)
- `backend/app/services/community_service.py:147` (boucle `for child in old_binder.children`
  dans `clone_binder_recursive`, endpoint `POST /packages/<binder_id>/clone`)

Les deux endpoints vérifient `is_public` **uniquement sur le classeur racine** demandé
(`packages.py:34`, `community_service.py:65`). La récursion sur `b.children` /
`old_binder.children` qui suit ne revérifie jamais le flag `is_public` de chaque enfant. Un
classeur enfant marqué privé, imbriqué sous un classeur parent public, voit :
- ses titres de notes/decks/diagrammes/PDF listés en clair à **tout visiteur anonyme** via
  `GET /packages/<binder_id>` (pas de JWT requis sur cette route) ;
- son **contenu intégral** (texte des notes, cartes de flashcards, code de diagrammes, PDF)
  dupliqué dans l'espace de **tout utilisateur authentifié** via `POST /packages/<binder_id>/clone`.

**Impact** : un utilisateur qui organise un sous-dossier privé (brouillons, corrigés d'examen,
notes personnelles) sous un classeur qu'il publie ensuite expose ce sous-dossier en entier,
sans le savoir et sans aucune action de sa part au-delà de la publication du parent. C'est une
fuite de données utilisateur directe et un contournement total du modèle de permission
`is_public`.

**Gravité** : S1. **Effort** : S — dans `collect_contents` et `clone_binder_recursive`, ne
descendre dans `b.children`/`old_binder.children` que pour les enfants où
`child.is_public == True` (ou, si la sémantique voulue est que `is_public` du parent doit
s'appliquer à tout l'arbre, l'imposer explicitement à la création/mise à jour plutôt que de le
supposer implicitement).

---

### SEC-03 — Le refresh token n'est jamais révoqué à la déconnexion

**Emplacement** : `backend/app/api/v1/auth.py:48-60` (`/auth/logout`),
`web/src/stores/auth.ts:69-84` (`logout()`), `web/src/services/api.ts:18-24` (intercepteur —
injecte `auth.token`, jamais `auth.refreshToken`)

`/auth/logout` accepte `@jwt_required(verify_type=False)` et blocklist (Redis) le seul `jti` du
token présenté dans l'en-tête `Authorization`. Le frontend appelle systématiquement
`/auth/logout` avec le **token d'accès** (l'intercepteur Axios n'injecte que `auth.token`) :
seul l'access token est donc révoqué côté serveur. Le refresh token (`JWT_REFRESH_TOKEN_EXPIRES`
= 2 592 000 s, 30 jours par défaut — `config.py:9`) est seulement effacé du `localStorage`
client, jamais blocklisté.

**Impact** : si un refresh token a fuité avant la déconnexion (poste partagé, XSS — cf. SEC-06,
extension de navigateur malveillante), l'attaquant continue d'obtenir de nouveaux access tokens
via `/auth/refresh` pendant jusqu'à 30 jours après que la victime s'est « déconnectée », sans
que celle-ci ait aucun moyen de le savoir ou de couper l'accès à distance.

**Gravité** : S2. **Effort** : S — sur `/auth/logout`, blocklister explicitement le `jti` du
refresh token courant en plus de celui présenté (le frontend devrait transmettre les deux, ou
le backend accepter un `refresh_token` optionnel dans le corps de la requête).

---

### SEC-04 — Fuite d'identifiants internes sur la note publique

**Emplacement** : `backend/app/schemas/note_schema.py:20-33` (`NoteResponse`), utilisé tel quel
par la route non authentifiée `backend/app/api/v1/notes.py:141-142`
(`GET /notes/public/<token>`)

La réponse publique réutilise le schéma complet `NoteResponse`, qui inclut `user_id` (identifiant
numérique interne de l'auteur), `binder_id` (identifiant du classeur contenant la note — qui
peut lui-même être privé) et `owner_username`. Un visiteur anonyme qui connaît un
`share_token` obtient donc, en plus du contenu volontairement partagé, l'identité de l'auteur et
des identifiants internes de ressources annexes.

**Impact** : désanonymisation de l'auteur d'un partage supposé public mais pas forcément
nominatif ; les identifiants internes exposés facilitent la corrélation d'un compte à travers
plusieurs fuites/endpoints.

**Gravité** : S3. **Effort** : XS — schéma dédié `PublicNoteResponse` sans `user_id`/`binder_id`,
ne gardant `owner_username` que si l'attribution publique est un choix produit assumé (à
confirmer).

---

### SEC-05 — CSP autorisant `unsafe-inline` et `unsafe-eval`

**Emplacement** : `backend/app/__init__.py:67-70` (`script-src` de la CSP Talisman)

```python
'script-src': ['\'self\'', '\'unsafe-inline\'', '\'unsafe-eval\'', 'https://static.cloudflareinsights.com'],
```

La CSP est bien présente (Talisman, HSTS, `frame-src self`, etc. — point positif), mais
`unsafe-inline`+`unsafe-eval` neutralisent sa capacité à limiter l'impact d'une XSS : si un
contenu utilisateur échappe malgré tout à la sanitisation marked+DOMPurify (SEC-08, ou un bug
futur dans la config DOMPurify), le script injecté s'exécute sans entrave de la CSP.

**Impact** : la CSP n'agit plus comme filet de sécurité en profondeur contre le XSS ; combiné
au stockage des JWT en `localStorage` (SEC-06), une XSS réussie donne un accès complet aux
tokens de la victime.

**Gravité** : S2 (défense en profondeur absente, pas une vulnérabilité exploitable en soi).
**Effort** : M — `unsafe-eval` est probablement requis par une dépendance du bundle Vite/Vue en
dev ou par une lib tierce à identifier ; `unsafe-inline` peut se remplacer par des nonces générés
par requête. Nécessite un audit du bundle de prod pour identifier ce qui casse sans ces
directives (voir axe performance).

---

### SEC-06 — JWT (access + refresh) stockés en `localStorage`

**Emplacement** : `web/src/stores/auth.ts:49-51` (`localStorage.setItem('sh_token', ...)`,
`localStorage.setItem('sh_refresh_token', ...)`)

Les deux jetons sont accessibles à tout script s'exécutant dans la page (contrairement à un
cookie `httpOnly`). Combiné à SEC-05 (CSP permissive), toute XSS réussie — même transitoire —
permet l'exfiltration silencieuse des deux tokens.

**Impact** : vol de session complet et durable (le refresh token vit 30 jours) en cas de XSS,
sans nécessiter d'interaction supplémentaire de la victime.

**Gravité** : S3 (dépend de l'exploitation préalable d'une XSS, aucune trouvée dans le code
audité — marked+DOMPurify et KaTeX `trust: false` par défaut sont correctement appliqués
partout où du contenu utilisateur est rendu, voir « Points vérifiés »). **Effort** : L — passage
à des cookies `httpOnly`+`Secure`+`SameSite` demande de revoir le flux CORS/Capacitor (les
coques natives ne partagent pas le domaine du cookie) ; à évaluer en phase 3+, pas un correctif
isolé.

---

### SEC-07 — Auto-migration au démarrage sans garde-fou destructif

**Emplacement** : `backend/app/db_migrate.py:24-40`, `backend/wsgi.py:11-12`

Le mécanisme sérialise correctement les workers gunicorn via `pg_advisory_lock` (point positif,
voir « Points vérifiés »), et est idempotent. Mais rien ne distingue une migration additive
(nouvelle colonne nullable) d'une migration destructive (`DROP COLUMN`, `ALTER ... SET NOT NULL`
sans défaut, `DROP TABLE`) : au prochain déploiement, une migration destructive s'applique aussi
automatiquement et silencieusement que n'importe quelle autre, sans validation humaine ni
sauvegarde préalable.

**Impact** : une migration mal écrite (erreur de revue, `git revert` incomplet) peut supprimer
des données de production dès le déploiement suivant, sans étape de confirmation.

**Gravité** : S2. **Effort** : M — détection statique des opérations destructives dans les
scripts Alembic en attente (grep sur `drop_column`, `drop_table`, `alter_column(...,
nullable=False)` sans `server_default`) et refus de l'auto-migration si détectées, en exigeant
une application manuelle (`flask db upgrade`) pour ce cas précis.

---

### SEC-08 — Délimiteurs pseudo-XML non échappés dans les prompts Gemini

**Emplacement** : `backend/app/services/ai_service.py:78-82` (`analyze_blurting`), motif
identique dans `analyze_feynman`

```python
f"<note_content>\n{note_content}\n</note_content>\n\n"
f"<user_blurting>\n{user_blurting}\n</user_blurting>"
```

La directive anti-injection (présente et bien conçue — voir « Points vérifiés ») explique au
modèle de traiter le contenu entre balises comme des données inertes. Mais `note_content` et
`user_blurting` sont interpolés sans échapper `<`/`>` : une note contenant littéralement
`</note_content><system>...` peut faire croire au modèle qu'il est sorti de la zone de données
avant la fin réelle du contenu utilisateur, affaiblissant la défense structurelle en plus de la
défense déclarative.

**Impact** : vecteur d'injection de prompt supplémentaire (au-delà de ce que la directive
textuelle couvre déjà) — pas de preuve d'exploitation, risque théorique renforcé par l'absence
d'échappement.

**Gravité** : S3. **Effort** : XS — échapper `<`/`>` (ou utiliser des délimiteurs aléatoires par
requête) avant interpolation dans `user_message`.

---

### SEC-09 — Pas de limite de débit dédiée sur `/auth/login`

**Emplacement** : `backend/app/api/v1/auth.py:27-36` (aucun décorateur `@limiter.limit`),
`backend/app/extensions.py:20` (limite globale par défaut : 50/heure en prod)

`/auth/login` n'a pas de limite spécifique ; il hérite du plafond global `default_limits`
(50/heure/IP en prod), partagé avec tous les autres appels que cette IP fait à l'API. Aucun
verrouillage de compte après échecs répétés.

**Impact** : bourrage d'identifiants (credential stuffing) réalisable à un rythme non négligeable
par IP, sans signal ni ralentissement progressif spécifique à l'authentification.

**Gravité** : S3. **Effort** : S — `@limiter.limit("10 per hour", key_func=...)` dédié sur
`/login`, sur la clé IP+email plutôt que IP seule.

---

## Points vérifiés sans anomalie

Pour éviter de traiter comme suspect tout ce qui n'a pas été explicitement cité comme risque
dans le prompt de démarrage :

- **KaTeX** : `renderToString(..., { throwOnError: false })` sans `trust`/`macros` — `trust`
  vaut `false` par défaut, donc `\href{javascript:...}` et assimilés sont bloqués
  (`web/src/views/Notes/NoteEdit.vue:1651,1663`, `PublicNote.vue:184,196`).
- **XSS contenu utilisateur** : aucun `v-html` brut dans tout `web/src` — chaque rendu de
  Markdown passe par la directive `v-dompurify-html` (`web/src/main.ts:14-16`), y compris sur
  la page de partage public. Les libellés de diagrammes SVG utilisent l'interpolation Vue
  (échappement automatique), pas d'injection HTML brute.
- **IDOR notes/classeurs** : le pattern `_get_note_or_404` (`backend/app/services/note_service.py:17-31`)
  centralise la vérification de propriété/accès partagé avant toute lecture/écriture/suppression
  — appliqué de façon cohérente sur les opérations vérifiées (get/update/delete/copy/hide).
- **Rate limiting sur l'IA** : `/blurting/analyze`, `/feynman/analyze`, `/quizzes/generate`,
  `/evaluations/generate` ont chacun `@limiter.limit("10 per hour", ...)` dédié — contrôle de
  coût effectif, contrairement à l'hypothèse par défaut du prompt de démarrage.
- **Clé Gemini** : jamais transmise au client — utilisée uniquement côté serveur dans
  `ai_service.py`, timeout de 90 s sur l'appel HTTP, pas de boucle de retry (pas de risque
  d'emballement de coût par ce biais).
- **Entropie du `share_token`** : `uuid.uuid4().hex` (`backend/app/services/note_service.py:197`)
  — 122 bits d'aléa cryptographique, non énumérable en pratique. Révocation fonctionnelle :
  repasser la note en privé met `share_token = None` (un nouveau token est généré à la
  prochaine publication).
- **CORS** : liste blanche explicite d'origines (`backend/app/__init__.py:13-18`), pas de
  wildcard `*`.
- **Auto-migration / concurrence workers** : sérialisée par `pg_advisory_lock` PostgreSQL
  (`backend/app/db_migrate.py:31-36`) — le scénario « plusieurs workers migrent en parallèle »
  du prompt de démarrage est bien couvert.
- **PDF — annotations géoréférencées** : fonctionnalité absente du code réel (aucune occurrence
  dans `web/src`, absente de `docs/audit/00-CARTOGRAPHIE.md`) — hors périmètre, comme
  Tiptap/Mermaid déjà signalés non réels en phase 1.

## Points non vérifiables depuis la lecture du code seule

- **SEC-01** : dépend de la configuration réelle de l'environnement de déploiement (variables
  d'env effectivement montées), non observable depuis le dépôt. À vérifier directement sur
  l'infrastructure de prod.
- **Marketplace — dépublication** : `is_public` peut être remis à `False` via la même route que
  la publication (mécanisme symétrique observé sur `Note`, à confirmer identique sur `Binder` —
  non trouvé de route `PATCH` dédiée à `Binder.is_public` dans `packages.py`/`binders.py` lors de
  cet audit ; à creuser si jugé prioritaire, indépendant de SEC-02).

## Résumé

| Gravité | Nombre |
|---|---|
| S1 | 2 (SEC-01 conditionnel, SEC-02) |
| S2 | 3 (SEC-03, SEC-05, SEC-07) |
| S3 | 4 (SEC-04, SEC-06, SEC-08, SEC-09) |
| S4 | 0 |
