# Journal — backend-ensembles-heterogenes

## 2026-08-28

Chantier ouvert : migration du flux 1 (`ETAT.md` § « Plan global par flux », 2026-08-27) vers
le système de suivi par chantiers. Aucun travail d'implémentation fait — seule la décision de
garder le canevas hétérogène est actée (2026-08-27, consignée dans `ETAT.md`). Commit : à
suivre.

## 2026-08-28 (activation)

Chantier activé (`Statut : planifié → ouvert`, branche `feature/backend-ensembles-heterogenes`
créée depuis `main` à jour). Premier chantier de l'ordre fixé (flux 1). Aucun travail
d'implémentation encore fait. Prochain point du plan : écrire la spec détaillée du modèle de
données cible.

## 2026-08-28 (spec + plan)

Brainstorming fait avant d'écrire le spec — découverte majeure en lisant le code réel :
- `Flashcard.card_type`/`payload` (qui semblaient dupliquer qcm/vf/ordre avec `RevisionSet.type`)
  sont du code mort : jamais lus/écrits ailleurs, absents des schémas Pydantic exposés,
  confirmé par le commentaire de `flashcard_schema.py` (décision D3c : flashcard = strictement
  recto/verso). Pas de vraie duplication à résoudre.
- Une vraie fusion `Deck`/`Flashcard` → `RevisionSet`/`RevisionItem` toucherait 47 fichiers
  backend (tous les sous-systèmes majeurs) — décision utilisateur : reporter cette fusion à des
  chantiers futurs distincts, un par sous-système. Ce chantier-ci se limite au socle schéma.
- `RevisionSet.type` est activement utilisé par le frontend non-migré (`Reviews.vue` et 4 autres
  vues) — conservé pour rétrocompatibilité totale, devient seulement optionnel.
- Bug trouvé en écrivant le plan détaillé (pas en implémentant) : `grade_item` doit vérifier
  `GRADABLE_TYPES` contre `item.type`, pas `rset.type` — sinon un item `flashcard` créé dans un
  ensemble `vf` (possible dès ce chantier via `RevisionItemCreate.type` explicite) serait noté
  silencieusement avec la mauvaise logique. Corrigé dans le spec et le plan avant exécution.

Spec : `docs/superpowers/specs/2026-08-28-backend-ensembles-heterogenes-design.md`.
Plan (4 tâches TDD) : `docs/superpowers/plans/2026-08-28-backend-ensembles-heterogenes.md`.
Commit : `d5dd745`.

## 2026-08-28 (arrêt avant redémarrage PC — reprise en session propre)

**État exact** : spec + plan écrits et committés (`d5dd745`). **Aucun code de
production encore modifié** — les 4 tâches du plan (Task 1 : migration +
modèles ; Task 2 : `validate_item_payload`/`check_answer` + schémas ; Task 3 :
câblage service ; Task 4 : clôture) n'ont pas démarré. Rien à perdre au
redémarrage.

**Worktree d'exécution déjà prête** :
`.worktrees/backend-ensembles-heterogenes` (checkout de
`feature/backend-ensembles-heterogenes`, identique à cette branche). Ledger
SDD pas encore créé (`.superpowers/sdd/2026-08-28-backend-ensembles-heterogenes/`
absent) — l'exécution pilotée par sous-agents n'a pas encore commencé.

**Constat d'environnement important** (à ne pas redécouvrir) : Docker
Desktop s'est montré instable pendant cette session (`docker compose up`/
`docker stop` qui bloquent ou renvoient des erreurs de connexion EOF au
pipe `dockerDesktopLinuxEngine`). Un venv Python local a été mis en place
en secours dans `.worktrees/backend-ensembles-heterogenes/backend/.venv`
(non versionné) — **fonctionne, 8/8 tests de `test_revision.py` verts en
SQLite mémoire**. Pour le recréer si besoin :
```bash
cd backend && python -m venv .venv
cat requirements.txt requirements-dev.txt | grep -v "psycopg2\|cryptography\|^-r " > /tmp/req_minimal.txt
./.venv/Scripts/python.exe -m pip install -r /tmp/req_minimal.txt
```
`psycopg2-binary` et `cryptography` n'ont pas de wheel précompilée pour ce
Python arm64 Windows (cohérent avec `docs/ENVIRONNEMENT.md` — ce projet
utilise Docker précisément pour cette raison) ; ni l'un ni l'autre n'est
importé directement par `app/`, donc les omettre ne casse rien pour les
tests SQLite. Seule la vérification Postgres réelle de la migration
(Task 1, étapes 6-7 du plan — `flask db upgrade` + garde anti-drift CI)
nécessite encore Docker ou un Postgres réel.

Le PC redémarre pour débloquer Docker Desktop. **Prochaine action** :
reprendre l'exécution du plan (`superpowers:subagent-driven-development`)
à partir de la Task 1, dans la worktree ci-dessus — utiliser Docker si
stable après redémarrage (correspond exactement à la CI), sinon retomber
sur le venv local documenté ci-dessus pour les étapes SQLite (tout sauf
Task 1 étapes 6-7).

## 2026-08-28 (reprise après redémarrage — Task 1 et Task 2)

Reprise en session propre (`/clear`). Constat en arrivant : Task 1 (migration +
modèles, commit `1146955`) et Task 2 (`validate_item_payload`/`check_answer` +
schémas, cas `flashcard`, commit `44cdd10`) avaient déjà été exécutées et
committées avant l'arrêt pour redémarrage — le journal ci-dessus n'avait
simplement pas été mis à jour après coup. Vérifié directement dans le code
(pas supposé) avant de continuer : `create_item`/`update_item`/`grade_item`/
`answer_item` dispatchaient encore sur `rset.type`, confirmant que seule la
Task 3 restait à faire.

## 2026-08-28 (Task 3 — câblage service)

TDD : 4 tests écrits d'abord (rétrocompat type hérité, type explicite
divergent, gate `GRADABLE_TYPES` sur `item.type`, `StudySession.item_type`
reflète le type réel de l'item) — rouge confirmé pour la bonne raison contre
le code non modifié. **Bug de plan trouvé et corrigé en cours de route** :
les URLs utilisées par les tests du plan détaillé
(`/sets/{id}/items/{id}/grade|answer`) n'existent pas — les vraies routes
sont `/sets/{id}/study/grade/{id}` et `/sets/{id}/study/answer/{id}`
(`backend/app/api/v1/revision.py:123,141`). Corrigé dans les tests, pas dans
le plan (le plan reste tel quel comme trace historique).

Implémentation : `create_item` retombe sur `rset.type` si `data.type` est
absent (rétrocompat totale, le frontend actuel n'envoie jamais ce champ) ;
`update_item`/`grade_item`/`answer_item` dispatchent désormais sur
`item.type`. Corrige le bug D8 identifié dès l'écriture du plan (un item
`flashcard` créé dans un ensemble `vf` aurait été noté silencieusement avec
la logique `vf` si le gate était resté sur `rset.type`). 4/4 tests ciblés
verts, commit `9c29185`.

**Vérification de non-régression** : suite complète relancée via le venv
Python local de secours (SQLite mémoire, cf. entrée « arrêt avant
redémarrage » ci-dessus pour comment le recréer) — 85 % de couverture
(≥ 80 % requis), tous les tests `test_revision*.py` verts. 5 échecs dans
`test_import.py` (`PermissionError` sur un fichier temporaire Windows,
`tempfile.mkstemp()`) confirmés pré-existants et sans rapport avec ce
chantier (module import Anki, aucune dépendance à `revision_service`) —
propres à ce venv Windows local, absents de la CI Docker/Linux.

**Vérification Postgres réelle (Task 1, étapes 6-7 du plan détaillé) —
tentée, bloquée** : Docker Desktop stable cette fois (`docker compose up -d
db backend` réussi). Mais le volume `pgdata` de ce projet, créé lors d'une
session antérieure interrompue par l'instabilité Docker, s'est révélé
incohérent : `alembic_version` stampé à `4e6e094d2711` mais **aucune table
applicative présente** (`\dt` ne renvoie que `alembic_version`) — le worker
gunicorn crash en boucle au démarrage (`NoSuchTableError: revision_items`
levée par la migration `c1d2e3f4a5b6` qui inspecte cette table avant de lui
ajouter sa colonne). Ce n'est pas un défaut de la migration elle-même —
confirmé par lecture directe de son code, la logique est correcte pour un
Postgres réellement à jour. La remise à zéro du volume
(`docker compose down -v`) est bloquée par le hook `guard_dangerous_commands`
(protection légitime contre la destruction de volumes) — non contournée.
**Reste à faire par un humain (ou une session explicitement autorisée)** :
soit supprimer le volume `backend-ensembles-heterogenes_pgdata` et relancer
`docker compose up -d db backend` pour vérifier la migration à froid, soit
confirmer que la couverture SQLite (`create_all()`, ci-dessus) suffit et
clore sans cette vérification manuelle. Containers arrêtés proprement
(`docker compose stop`, sans `-v`) en attendant cette décision.

**Task 4 (clôture) — en cours** : cases de `PLAN.md` cochées à jour, cette
entrée de journal ajoutée, mise à jour de `workflow/JOURNAL.md` à suivre.
Suite (PR) non ouverte tant que la vérification Postgres ci-dessus n'est pas
tranchée.
