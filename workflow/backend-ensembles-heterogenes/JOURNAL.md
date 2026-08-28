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
