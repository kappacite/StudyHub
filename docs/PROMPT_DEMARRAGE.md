# Prompt de démarrage Claude Code — StudyHub

> Document source, conservé **verbatim** tel que fourni par l'utilisateur au lancement du
> chantier agentique (2026-08-23). C'est la référence canonique et durable pour l'intégralité
> des phases 0 à 5 — `ETAT.md` ne conserve qu'un résumé de l'avancement, `AGENTS.md` que les
> décisions déjà tranchées. En cas de doute sur ce qu'une phase future doit produire, c'est
> **ce fichier** qui fait foi, pas la mémoire d'une conversation.
>
> Arbitrage acté au démarrage de la phase 1 : **on prend ce prompt intégralement, pas l'état
> déjà documenté dans le dépôt** (`docs/design-system.md`, `docs/performance-audit.md`,
> `docs/ui-redesign-plan.md` traités comme non acquis pour les phases 2 et 3 — voir `ETAT.md`).
>
> Ne pas modifier ce fichier pour refléter l'avancement — c'est le rôle d'`ETAT.md`. Ce fichier
> ne change que si l'utilisateur fournit de nouvelles instructions de fond qui remplacent
> celles-ci ; dans ce cas, la mise à jour se fait par ajout d'une section datée, pas par
> réécriture silencieuse du texte original.

---

## 0. Contexte

Tu interviens sur **StudyHub**, un monorepo d'application d'étude (web + mobile) :

- `backend/` — Flask 3, Python 3.12, SQLAlchemy 2.x avec patron **DAO**, Alembic/Flask-Migrate (auto-migration au démarrage), JWT via `flask-jwt-extended`, validation Pydantic v2, PostgreSQL (prod) / SQLite (dev).
- `web/` — Vue 3 `<script setup>`, Vite 5, TailwindCSS 3 + HeadlessUI, Pinia, Vue Router 4. Dépendances lourdes : Tiptap, Mermaid.js, PDF.js, KaTeX.
- `mobile/` — Capacitor 6 encapsulant le build `web/` (stockage local, notifications locales, haptique).
- `docs/` — documentation technique.
- `AGENTS.md` — règles d'architecture existantes. **Lis-le avant toute chose ; il fait autorité sur ce prompt en cas de contradiction sur l'architecture.**

> **Note phase 1** : la description technique ci-dessus (stack, `mobile/`) date de la rédaction
> initiale de ce prompt et s'est révélée en partie fausse par rapport au dépôt réel (cartographie
> phase 0, `docs/audit/00-CARTOGRAPHIE.md`) — Capacitor 8 et non 6, `web/android` et non `mobile/`,
> pas de Tiptap/Mermaid/PDF.js en dépendance réelle, `desktop/` Electron absent de cette
> description. `AGENTS.md` a été réécrit pour refléter l'état réel ; ce fichier-ci reste
> inchangé comme trace de l'intention d'origine.

Modules fonctionnels : notes Markdown/LaTeX, flashcards SM-2, révision « blurting » assistée par Gemini, diagrammes SVG/Mermaid, annotations PDF géoréférencées, marketplace de classeurs, partage public en lecture seule, dashboard avec heatmap et streaks.

## 1. Mission

Quatre chantiers, **dans cet ordre strict**, sans chevauchement :

1. **Outillage agentique** — installer le socle `.claude/` (règles scopées, permissions, hooks, skills, subagents) qui contraindra tout le travail suivant.
2. **Revue technique** — audit en lecture seule sur quatre axes : sécurité/auth, dette et cohérence architecturale, performance et scalabilité, couverture de tests et CI. **Aucune correction pendant cette phase.**
3. **Refonte totale du layer UI** — nouveau design system puis réécriture complète des écrans, direction « chaleureuse / gamifiée ».
4. **Refonte de l'outil de diagrammes** — reconstruction fonctionnelle, pas cosmétique : un canevas libre où l'utilisateur place chaque élément exactement où il veut, couvrant tous les types de schémas utiles à l'étude, manipulable au clavier comme au doigt.

Tu ne démarres jamais une phase sans que la précédente ait passé ses critères d'acceptation et fait l'objet d'un commit.

## 2. Règles non négociables

- **Jamais de `git push`.** Aucune commande de publication distante, dans aucun script, hook ou commit. Blocage explicite en permissions.
- **Commits atomiques, format Conventional Commits**, en français pour le corps, un commit = un changement cohérent testable.
- **Aucune modification de code pendant la phase d'audit.** L'audit produit des documents, pas des diffs.
- **Aucun secret en clair** (clé Gemini, `SECRET_KEY`, `JWT_SECRET_KEY`) dans le code, les tests, les fixtures ou les documents produits.
- **Rien ne casse en cours de route** : la suite `pytest` et `vitest` doit être verte avant chaque commit. Un test rouge se corrige ou se marque `xfail` avec justification écrite — il ne se supprime pas.
- **Tout développement se fait en TDD** (voir section 2 bis). Aucun code de production n'est écrit avant le test qui le justifie.
- **On ne compacte jamais le contexte.** À 90 % de remplissage, on écrit une passation et on repart d'une session vide (voir section 4.4).
- **La documentation suit le code dans le même commit.** Un changement qui rend fausse une phrase de `README.md`, d'`AGENTS.md` ou d'un `CLAUDE.md` n'est pas terminé tant que cette phrase n'est pas corrigée.
- **Tu ne rebases pas, ne squashes pas, ne réécris pas l'historique.**
- Tu écris et documentes **en français**.

## 2 bis. Discipline TDD

À partir de la phase 3, **le test précède l'implémentation, sans exception**. Le raisonnement sur le comportement attendu se fait avant l'écriture du code, pas après.

### Le cycle

1. **Réfléchir** — avant d'écrire la moindre ligne, énonce en clair le comportement attendu : entrées, sorties, cas limites, cas d'erreur. Pour un écran : les cinq états (vide, chargement, erreur, dense, hors ligne). Pour un service : les invariants métier. Ce raisonnement est écrit dans `ETAT.md` avant le premier test.
2. **Rouge** — écris le ou les tests. **Exécute-les et constate qu'ils échouent, pour la bonne raison.** Un test qui passe du premier coup est un test qui ne teste rien : tu le corriges ou tu le supprimes. Un test qui échoue sur un `ImportError` alors qu'il devrait échouer sur une assertion ne compte pas comme un rouge valide.
3. **Vert** — écris le minimum de code de production pour faire passer le test. Rien de plus : pas d'anticipation, pas de généralisation spéculative.
4. **Refactor** — nettoie à tests verts, en les relançant après chaque modification.

Tu ne fais pas passer plusieurs cycles en une seule fois. Un cycle = un comportement.

### Ce qui est interdit

- Écrire du code de production puis « rajouter les tests derrière ». Si tu te surprends à le faire, tu supprimes le code, tu écris le test, tu recommences.
- Adapter un test à une implémentation qui ne marche pas. Le test est la spécification ; c'est le code qui a tort.
- Faire passer un test en le rendant plus permissif (assertion affaiblie, `mock` qui court-circuite le comportement testé, `sleep` pour masquer une course).
- Commiter un cycle incomplet : chaque commit contient le test **et** son implémentation, tous deux verts.

### Périmètre

- **Backend** : tout DAO, service, contrôleur, schéma. Les invariants SM-2 sont couverts par les fixtures de la skill `invariants-sm2`, qui font foi.
- **Frontend** : stores Pinia et logique de composition en test unitaire ; primitives et composants en test de rendu (états, interactions clavier, variantes) ; parcours critiques (connexion, session de révision, partage public) en test d'intégration.
- **Exception unique** : le pur travail de tokens et de mise en page visuelle, non testable utilement en automatique, se valide par capture d'écran clair/sombre × desktop/mobile. Cette exception ne couvre **pas** le comportement des composants (états, focus, accessibilité, interactions), qui reste sous TDD.

### Préalable

Le TDD n'est applicable que si la boucle de test est rapide et fiable. Si la phase 2 révèle une suite lente, instable ou sans harnais exploitable, la remise à niveau du harnais devient le premier cycle de la phase 3 — avant les tokens.

## 3. Phase 0 — Reconnaissance (lecture seule)

Avant de produire quoi que ce soit :

1. Lis `AGENTS.md`, `README.md`, `docs/**`, `docker-compose.yml`, `backend/requirements.txt`, `web/package.json`, la config Tailwind et les fichiers de config Vite.
2. Cartographie le backend : liste des modèles, des DAO, des services, des blueprints/contrôleurs, des schémas Pydantic. Repère les endroits où le patron DAO est court-circuité (accès direct à la session depuis un contrôleur, requête ORM dans un service, etc.).
3. Cartographie le frontend : inventaire exhaustif des **vues** (`web/src/views` ou équivalent), des **composants** réutilisables, des **stores** Pinia, des routes. Compte les composants et estime leur taille en lignes.
4. Recense l'existant en tests : nombre de tests backend/frontend, présence ou absence de CI, de coverage, de linters, de pre-commit.
5. Recense l'existant **documentaire et prescriptif** : tout fichier portant des règles ou décrivant le système (`AGENTS.md`, `README.md`, `CLAUDE.md` éventuel, `docs/**`, `CONTRIBUTING.md`). Pour chacun, note ce qu'il prescrit, sa date de dernière modification, et les points où il décrit manifestement un état antérieur au code actuel. Cet inventaire alimente directement la reprise décrite en section 4.1.

**Livrable** : `docs/audit/00-CARTOGRAPHIE.md` — inventaires bruts, chiffrés, sans jugement de valeur ni recommandation. Les tableaux d'écrans et de modules de ce document serviront de référence à toutes les phases suivantes.

**Critère d'acceptation** : chaque route déclarée dans le router Vue et chaque blueprint Flask apparaît dans le document. Commit : `docs(audit): cartographie initiale du dépôt`.

> **Fait** — voir `docs/audit/00-CARTOGRAPHIE.md`, commit `5929bb7`.

---

## 4. Phase 1 — Outillage agentique

### 4.1 Règles scopées — reprise de l'existant, puis hiérarchie

#### Reprendre l'existant, ne pas l'écraser

Le dépôt contient déjà des fichiers d'instructions et de documentation : `AGENTS.md`, `README.md`, éventuellement un `CLAUDE.md`, `docs/**`, des commentaires de configuration. **Tu ne les remplaces pas, tu les reprends.** Écraser un fichier de règles fait perdre des décisions dont personne ne se souvient qu'elles ont été prises, et qui seront reprises à l'envers six semaines plus tard.

Procédure, dans cet ordre :

1. **Inventaire.** Liste tout fichier qui porte de l'instruction ou de la documentation : `AGENTS.md`, `README.md`, `CLAUDE.md` existants, `docs/**`, `CONTRIBUTING.md`, en-têtes de configuration. Note pour chacun ce qu'il prescrit.
2. **Confrontation.** Compare chaque prescription existante aux nouvelles consignes de ce prompt — TDD, interdiction de compacter, interdiction de `git push`, environnement multi-architecture, canevas libre pour les diagrammes, design system. Classe chaque écart en trois catégories : **compatible** (rien à faire), **à compléter** (l'existant ne dit rien, on ajoute), **en contradiction**.
3. **Les contradictions ne se tranchent pas toutes seules.** Tu me présentes la liste des contradictions, chacune en deux lignes — ce que dit l'existant, ce que dit le nouveau prompt — et **tu attends mon arbitrage**. C'est particulièrement vrai pour `AGENTS.md`, qui fait autorité sur l'architecture : si une nouvelle consigne le contredit, c'est peut-être la consigne qui a tort.
4. **Application.** Une fois arbitré, tu modifies les fichiers existants par ajouts et corrections ciblés. Tu ne réécris intégralement un fichier que si je l'ai validé explicitement.

> **Fait** — contradictions A→E présentées, arbitrage rendu : « on prend tout du nouveau
> prompt, rien de l'ancien ». Voir `ETAT.md` et l'historique de commits de la phase 1.

#### Une règle, un seul endroit

Après reprise, aucune règle n'existe en deux exemplaires. Une consigne dupliquée entre `AGENTS.md` et `CLAUDE.md` finit par diverger, et plus personne ne sait laquelle s'applique.

- `AGENTS.md` garde l'architecture et les décisions de conception. Il fait autorité.
- Les `CLAUDE.md` portent les conventions de travail de l'agent et **renvoient** à `AGENTS.md` au lieu d'en recopier le contenu.
- Le `README.md` s'adresse à un humain qui découvre le projet ; il ne porte pas de règle opposable.

Si l'inventaire révèle qu'une même règle est déjà écrite à trois endroits, la déduplication fait partie du travail.

#### Maintenir à jour, phase après phase

La documentation existante décrit un état qui va cesser d'être vrai. Le `README.md` décrit deux éditeurs de diagrammes qui vont disparaître ; il décrit une interface qui va être refaite ; `AGENTS.md` ne mentionne ni TDD, ni contrainte multi-architecture.

- **Un changement qui rend une phrase de la documentation fausse est incomplet tant que la phrase n'est pas corrigée, dans le même commit.** Pas de commit « docs » de rattrapage en fin de semaine : la dérive documentaire s'installe entre les deux.
- **En fin de chaque phase**, une passe de cohérence dédiée : relire `README.md`, `AGENTS.md` et les `CLAUDE.md` à la lumière de ce qui a changé, et corriger. Commit `docs(<phase>): mise à jour après <chantier>`.
- La phase 5 en particulier invalide toute la documentation sur les diagrammes : la décision « canevas libre, Mermaid en format d'échange » et ses conséquences remontent dans `AGENTS.md`, avec la raison du choix — pas seulement le choix.

#### Hiérarchie cible

Tu poses une hiérarchie de règles, en gardant à l'esprit qu'un `CLAUDE.md` **oriente** mais ne **contraint** pas — la contrainte réelle vient des hooks et des permissions.

- `CLAUDE.md` (racine) — conventions transverses : langue, format de commit, interdiction de `git push`, **cycle TDD obligatoire**, séquence de phases, rappel de la primauté d'`AGENTS.md`, pointeurs vers les règles enfants. **Court** : 60 lignes maximum, sinon il est ignoré.
- `backend/CLAUDE.md` — flux obligatoire Contrôleur → Service → DAO → Modèle ; interdiction d'accéder à `db.session` hors DAO ; validation Pydantic systématique en entrée et en sortie ; gestion des transactions ; conventions de nommage des migrations Alembic ; interdiction de générer une migration sans l'avoir relue.
- `web/CLAUDE.md` — Composition API `<script setup>` uniquement, TypeScript si présent, aucun style en dur (toute couleur, tout rayon, toute ombre passe par les tokens Tailwind), stores Pinia pour l'état partagé uniquement, pas d'appel `fetch` hors couche API.
- `web/src/components/CLAUDE.md` — règles du design system : primitives autorisées, contraintes d'accessibilité, contraintes tactiles Capacitor.

### 4.2 Permissions — `.claude/settings.json`

Autorise sans confirmation la lecture, les tests, les linters, le formatage, `git add`/`git commit`/`git status`/`git diff`.
Refuse durement : `git push`, `git reset --hard`, `git rebase`, `rm -rf`, `flask db upgrade` hors dev, `docker compose down -v`, toute écriture dans `.env`.
Demande confirmation pour : installation de dépendance (`pip install`, `npm install`), génération de migration.

### 4.3 Hooks

Écris les scripts dans `.claude/hooks/`, en Python 3 ou bash POSIX, chacun autonome et rapide (< 2 s). Rappel : **seul un code de sortie 2 dans un hook `Stop` bloque réellement l'exécution** ; un code 2 en `PreToolUse` bloque l'outil et renvoie le message d'erreur à l'agent.

| Hook | Déclencheur | Rôle |
|---|---|---|
| `SessionStart` | ouverture de session | Injecte : branche courante, `git status --short`, contenu de `ETAT.md` (phase en cours, chantier suivant), et — en phase 3 — la liste des écrans restant à migrer. |
| `PreToolUse` (Bash) | toute commande | Rejette `git push`, `rm -rf`, `git reset --hard`, toute commande contenant une chaîne ressemblant à une clé API. Code 2 + message explicite. |
| `PreToolUse` (Edit/Write) | phase 2 active | Si `ETAT.md` indique la phase d'audit et que le fichier ciblé n'est pas sous `docs/audit/`, rejette. C'est ce hook qui rend le « pas de correction pendant l'audit » réel. |
| `PostToolUse` (Edit/Write sur `backend/**.py`) | après écriture | `ruff check --fix` puis `ruff format` sur le fichier. |
| `PostToolUse` (Edit/Write sur `web/**.{vue,ts,js}`) | après écriture | `eslint --fix` + `prettier --write`, puis **détection de valeurs brutes** : tout `#rrggbb`, `rgb(`, ou `px` hors `1px`/`0px` dans un `<style>` ou une classe arbitraire Tailwind `[...]` déclenche un avertissement nommant le token à utiliser. |
| `PreToolUse` (Edit/Write sur code de production) | phase 3+ | **Garde TDD** : refuse l'écriture d'un fichier de production si le fichier de test correspondant n'existe pas, ou si son horodatage de dernière modification est antérieur à celui du fichier de production. Code 2 + message nommant le test attendu. Contournable pour les fichiers purement visuels via une liste blanche explicite et courte, tenue dans `.claude/tdd-exempt.txt`. |
| `Stop` | fin de cycle | Porte de sortie : `pytest` vert **et** `vitest` vert **et** `ETAT.md` mis à jour **et** aucun `TODO`/`FIXME` ajouté sans ticket dans le backlog d'audit **et** — en phase 3+ — le diff en attente contient au moins un fichier de test modifié ou ajouté. Sinon **exit 2** avec la raison précise. |
| `Stop` (volet documentaire) | fin de cycle | Signale — sans bloquer — que le diff touche une zone couverte par la documentation (module de diagrammes, composants d'interface, schéma de données, environnement) sans qu'aucun `.md` correspondant n'ait été modifié. Un avertissement, pas un rejet : la corrélation fichier ↔ documentation est trop imprécise pour bloquer, mais assez utile pour rappeler la vérification. |
| `TaskCompleted` | fin de tâche | Vérifie les critères d'acceptation de la phase courante lus depuis `ETAT.md`, dont la trace du rouge : `ETAT.md` doit consigner, pour chaque cycle, la formulation du comportement attendu et la raison de l'échec initial du test. |

`ETAT.md` (racine, versionné) est le fichier d'état de la boucle : phase courante, dernier commit, checklist de la phase, écrans migrés / restants. Il est mis à jour à chaque cycle, et le hook `Stop` refuse de rendre la main s'il est obsolète.

> **Fait, avec adaptations** — voir `ETAT.md` et le récapitulatif de phase 1 dans
> `docs/development_journal.md` (entrée 2026-08-23). Principales adaptations à
> l'environnement réel (Windows, deux shells, pas de venv local) : voir le plan archivé
> `docs/passations/2026-08-23_2135_phase1.md` et le journal. `TaskCompleted` n'a pas été
> implémenté comme hook séparé — son rôle (vérifier les critères d'acceptation de fin de
> phase) est absorbé par la checklist `ETAT.md` elle-même, revue manuellement à chaque
> clôture de phase.

### 4.4 Mécanique de passation de contexte (permanente)

**Principe** : au-delà de 90 % de la fenêtre de contexte, on ne compacte pas — **on coupe**. La compaction dégrade en silence : elle conserve un résumé appauvri et perd précisément ce dont dépend la suite du travail (chemins de fichiers, décisions écartées et pourquoi, pièges rencontrés). Une passation écrite explicitement, en revanche, est relue intégralement au démarrage de la session suivante.

Cette mécanique est **permanente** : elle s'applique à toutes les phases, du premier commit au dernier.

#### Ce qui est automatisable, et ce qui ne l'est pas

| Étape | Automatisable ? |
|---|---|
| Mesurer le taux de remplissage du contexte | Oui — via `transcript_path`, présent dans l'entrée JSON de tous les hooks. |
| Bloquer la compaction automatique | Oui — `PreCompact` (matcher `auto`) est un des événements bloquants : un code de sortie 2 empêche la compaction. |
| Forcer la rédaction de la passation avant de rendre la main | Oui — `Stop`, code de sortie 2. |
| Déclencher `/clear` lui-même | **Non.** Aucun hook ne pilote les commandes de l'interface. Le hook affiche l'ordre, l'humain tape `/clear` — une frappe. |
| Relancer le travail automatiquement après le `/clear` | Oui — `SessionStart` avec matcher `clear` réinjecte la passation en contexte et peut fournir un `initialUserMessage` qui relance la session sans intervention. |

Autrement dit : **tout est automatique sauf la frappe `/clear`**. Vérifie aussi dans `/config` si ta version expose un réglage d'auto-compaction à désactiver ; si oui, désactive-le — le hook `PreCompact` reste le filet, mais autant ne pas déclencher l'événement pour rien.

#### Le cycle

1. Fin de tâche. Le hook `Stop` calcule le taux de remplissage.
2. Sous 90 % : rien ne se passe, le travail continue normalement.
3. À 90 % ou plus : **si un cycle TDD est en cours** (rouge non résolu, ou vert non commité), le hook laisse d'abord finir le cycle — on ne coupe jamais au milieu d'un rouge. Sinon il sort en code 2 avec pour consigne d'écrire la passation.
4. L'agent écrit `PASSATION.md`, en archive une copie horodatée dans `docs/passations/`, met à jour `ETAT.md`, et rend la main.
5. Le hook laisse passer cette fois-ci et affiche : `Contexte à N %. Tape /clear — la reprise est automatique.`
6. Au `/clear`, le hook `SessionStart` (matcher `clear`) lit `PASSATION.md` et `ETAT.md`, les injecte en contexte et relance la prochaine action via `initialUserMessage`.

Si une compaction automatique se déclenche malgré tout (seuil interne atteint avant le tien), `PreCompact` la bloque et exige la passation. **Filet de sécurité obligatoire** : si la passation est déjà fraîche et que la compaction se représente une seconde fois, le hook la laisse passer. Une session figée par un hook qui bloque en boucle est pire qu'une compaction subie.

#### Format de `PASSATION.md`

Contrainte dure : **40 lignes maximum**. Une passation longue est une compaction déguisée, avec les mêmes défauts.

```markdown
# Passation — <horodatage> — phase <n>

## Fait
<5 puces maximum, factuelles, une ligne chacune>

## État
- Tests : <vert / rouge, lesquels>
- Dernier commit : <sha court + message>
- Branche : <nom>

## Prochaine action
<Une seule action, précise, avec les chemins de fichiers concernés.>

## Pièges rencontrés
<Ce qui a coûté du temps et se reproduira. Rien d'autre.>

## À relire en priorité
<3 chemins maximum>
```

**Interdits** : recopier du code, raconter la démarche, lister ce qui a été envisagé puis écarté sans dire pourquoi. La passation répond à une seule question — *que fait la prochaine session, et que doit-elle savoir pour ne pas refaire les mêmes erreurs ?*

#### Implémentation

Un script unique, `.claude/hooks/contexte.py`, branché sur trois événements et distinguant son rôle via `hook_event_name` :

```python
#!/usr/bin/env python3
"""Mesure le contexte, force la passation, bloque la compaction."""
import json, os, sys, pathlib, datetime

SEUIL = 0.90
FENETRE = int(os.environ.get("CLAUDE_FENETRE_CONTEXTE", "200000"))
RACINE = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
PASSATION = RACINE / "PASSATION.md"
SENTINELLE = RACINE / ".claude" / "state" / "seuil-atteint"

def remplissage(chemin_transcript):
    """Somme des tokens du dernier message assistant du transcript."""
    if not chemin_transcript or not os.path.exists(chemin_transcript):
        return 0.0
    dernier = None
    with open(chemin_transcript, encoding="utf-8") as f:
        for ligne in f:
            try:
                e = json.loads(ligne)
            except ValueError:
                continue
            u = (e.get("message") or {}).get("usage")
            if u:
                dernier = u
    if not dernier:
        return 0.0
    total = sum(dernier.get(k, 0) for k in (
        "input_tokens", "cache_read_input_tokens",
        "cache_creation_input_tokens", "output_tokens"))
    return total / FENETRE

def fraiche(minutes=10):
    if not PASSATION.exists():
        return False
    age = datetime.datetime.now().timestamp() - PASSATION.stat().st_mtime
    return age < minutes * 60

ev = json.load(sys.stdin)
evt = ev.get("hook_event_name")
taux = remplissage(ev.get("transcript_path"))

if evt == "Stop":
    if taux < SEUIL:
        SENTINELLE.unlink(missing_ok=True)
        sys.exit(0)
    if SENTINELLE.exists() and fraiche():
        SENTINELLE.unlink(missing_ok=True)
        print(json.dumps({"systemMessage":
            f"Contexte à {taux:.0%}. Passation écrite. Tape /clear — "
            "la reprise est automatique."}))
        sys.exit(0)
    SENTINELLE.parent.mkdir(parents=True, exist_ok=True)
    SENTINELLE.touch()
    print(f"Contexte à {taux:.0%}, au-dessus du seuil de {SEUIL:.0%}. "
          "Termine le cycle TDD en cours s'il y en a un (vert + commit), "
          "puis écris PASSATION.md au format imposé (40 lignes max), "
          "archive-la dans docs/passations/, mets ETAT.md à jour, "
          "et arrête-toi. N'entame aucune nouvelle tâche.", file=sys.stderr)
    sys.exit(2)

if evt == "PreCompact":
    if fraiche():
        sys.exit(0)          # filet : passation prête, on ne fige pas la session
    print(json.dumps({"decision": "block", "reason":
        "Compaction refusée : ce projet coupe au lieu de compacter. "
        "Écris PASSATION.md (40 lignes max), archive-la dans docs/passations/, "
        "mets ETAT.md à jour, puis demande un /clear."}))
    sys.exit(0)

if evt == "SessionStart":
    contexte = PASSATION.read_text(encoding="utf-8") if PASSATION.exists() else ""
    etat = (RACINE / "ETAT.md").read_text(encoding="utf-8") if (RACINE / "ETAT.md").exists() else ""
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": f"{contexte}\n\n---\n\n{etat}",
        "initialUserMessage":
            "Reprends le travail. Lis la passation et ETAT.md ci-dessus, "
            "relis les fichiers listes en priorite, confirme-moi en trois "
            "lignes ce que tu as compris de l'état, puis exécute la prochaine "
            "action indiquée — en TDD, test d'abord."}}))
    sys.exit(0)
```

Câblage dans `.claude/settings.json` :

```json
{
  "hooks": {
    "PreCompact": [
      { "matcher": "auto",
        "hooks": [{ "type": "command", "command": "python3",
                    "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/contexte.py"] }] }
    ],
    "SessionStart": [
      { "matcher": "clear",
        "hooks": [{ "type": "command", "command": "python3",
                    "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/contexte.py"] }] }
    ]
  }
}
```

Le volet `Stop` se greffe sur le hook `Stop` existant décrit plus haut : la porte de sortie enchaîne d'abord les vérifications de tests et de TDD, puis la mesure de contexte. **Un seul hook `Stop`**, pas deux qui se marchent dessus.

#### Garde-fous

- **Anti-boucle** : la sentinelle `.claude/state/seuil-atteint` garantit que le `Stop` ne bloque qu'une seule fois par franchissement de seuil. Un hook `Stop` qui bloque systématiquement fige la session pour de bon — c'est le piège classique de cet événement.
- **Jamais au milieu d'un rouge** : la coupure attend la fin du cycle TDD en cours. Un contexte perdu sur un test rouge non résolu, c'est un état que la session suivante ne saura pas reconstruire.
- **`FENETRE` est un paramètre**, pas une constante devinée : ajuste `CLAUDE_FENETRE_CONTEXTE` au modèle réellement utilisé, sinon le seuil de 90 % ne veut rien dire.
- **`docs/passations/` est versionné** : la suite des passations devient le journal de bord du projet, et permet de retrouver pourquoi une décision a été prise dix sessions plus tôt.

> **Fait, avec une différence d'implémentation** — le script unique `contexte.py` décrit
> ci-dessus a été scindé en trois fichiers réels (`stop_gate.py` pour le volet `Stop`,
> `contexte_precompact.py` pour `PreCompact`, `session_start_resume.py` pour `SessionStart`
> matcher `clear`), partageant une bibliothèque commune `_context_lib.py` — même
> comportement, code plus lisible. `session_start.py` (sans matcher `clear`) couvre en plus
> le démarrage normal (branche/statut/`ETAT.md`), non détaillé dans l'exemple ci-dessus mais
> prévu par le tableau de hooks de la section 4.3. Mécanique testée réellement en fin de
> phase 1 (`docs/passations/2026-08-23_2135_phase1.md`) : Stop bloqué à seuil abaissé,
> passation écrite, `/clear`, reprise automatique confirmée.

### 4.5 Environnement conteneurisé multi-architecture

Le TDD ne tient que si la boucle de test est rapide **et identique partout**. Un environnement qui se comporte différemment selon la machine transforme chaque rouge en enquête. L'environnement conteneurisé doit donc fonctionner nativement sur **x86-64** et sur **arm64**, sans émulation — l'émulation QEMU divise les performances par trois à cinq, ce qui suffit à rendre le TDD insupportable.

#### Structure

Un socle commun et deux surcouches minces, plutôt que deux fichiers dupliqués qui divergeront en trois semaines :

- `docker-compose.yml` — le socle, **écrit pour fonctionner tel quel sur les deux architectures**. C'est le fichier de référence ; dans le cas nominal, il suffit.
- `docker-compose.amd64.yml` et `docker-compose.arm64.yml` — surcouches ne contenant **que les différences irréductibles** (image sans variante native, dépendance compilée, variable de build). Si une surcouche est vide, elle reste vide et c'est un bon signe.
- `docker-compose.override.yml` — confort de développement local (montages, rechargement à chaud, ports), indépendant de l'architecture, non versionné.

Usage : `docker compose -f docker-compose.yml -f docker-compose.arm64.yml up`. Fournis un `Makefile` ou un script court qui détecte l'architecture via `uname -m` et compose la bonne commande, pour que personne n'ait à s'en souvenir.

#### Ce qui casse réellement entre architectures

Tu ne découvres pas ces points en cours de route, tu les vérifies dès le départ, service par service :

- **Images de base** : Postgres, Python et Node publient des manifestes multi-architecture — la même étiquette fonctionne des deux côtés. Vérifie-le pour chaque image du fichier ; toute image sans variante arm64 est un problème à traiter explicitement, pas à contourner par de l'émulation silencieuse.
- **Ne jamais épingler une image par empreinte** (`@sha256:…`) : une empreinte désigne une architecture, et fige le fichier sur une seule. Épingle par version, pas par empreinte.
- **Roues Python précompilées** : `psycopg2-binary`, `cryptography`, `pydantic-core`, `lxml` et consorts n'ont pas systématiquement de roue arm64 selon la version. Sans roue, l'installation compile — ou échoue. Recense les dépendances concernées de `backend/requirements.txt` et tranche : version plus récente disposant d'une roue, ou dépendances de compilation installées dans l'image.
- **Modules Node natifs** et binaires téléchargés à l'installation (esbuild, sharp, moteurs de navigateur pour les tests) : mêmes symptômes, même traitement.
- **`platform:` est une échappatoire de dernier recours**, pas une solution. Chaque usage porte un commentaire disant pourquoi et ce qui le lèvera. Un `platform: linux/amd64` non commenté est une dette invisible qui ralentit tout le monde sur Mac.

#### Construction et publication

Les images se construisent avec `docker buildx build --platform linux/amd64,linux/arm64`. Les `Dockerfile` utilisent `TARGETARCH` et `TARGETPLATFORM` fournis par buildx pour leurs rares branchements, jamais une détection maison.

Les fichiers de verrouillage (`requirements.txt` épinglé, `package-lock.json`) sont communs aux deux architectures : c'est la résolution qui doit être reproductible, pas les binaires.

#### Vérification — critère d'acceptation

Une déclaration de compatibilité ne vaut rien. **La suite `pytest` et `vitest` complète doit tourner au vert dans les conteneurs sur les deux architectures**, et le résultat est consigné dans `docs/ENVIRONNEMENT.md` avec, pour chacune : la commande exacte, la durée d'un run complet et d'un run ciblé, et la version de Docker utilisée.

Si tu ne disposes que d'une architecture pour tester, tu peux valider la seconde en émulation — **en le notant explicitement comme non concluant sur les performances**, et en indiquant ce qui reste à vérifier sur machine native.

Le pipeline CI proposé dans l'audit de phase 2 tourne en matrice sur les deux architectures. Une régression spécifique à une architecture qui n'est pas détectée en CI sera découverte par un utilisateur, ce qui coûte incomparablement plus cher.

`docs/ENVIRONNEMENT.md` documente aussi le démarrage à froid : commande unique, durée attendue, prérequis, et que faire quand ça échoue.

> **Fait** — `docker-compose.amd64.yml`/`arm64.yml` créés (vides, aucune différence
> irréductible trouvée), `Makefile` + `scripts/dev-up.sh`. Vérifié réellement en natif sur
> arm64 (cette machine), pas en émulation : détail complet, chiffres mesurés et bug Docker
> corrigé en cours de route dans `docs/ENVIRONNEMENT.md`. amd64 non re-testé en session
> (aucun push) — repose sur la CI GitHub Actions existante, matrice non mise en place (CI
> actuelle mono-arch amd64 ; à revoir en phase 2 si jugé utile).

### 4.6 Skills

Dans `.claude/skills/`, une compétence par domaine, chacune avec son `SKILL.md` et ses ressources :

- **`audit-securite`** — checklist appliquée à cette stack : cycle de vie JWT (stockage, expiration, refresh, révocation, confusion d'algorithme), entropie et révocabilité des jetons de partage public, IDOR sur classeurs et notes, sanitisation du contenu utilisateur (HTML Tiptap, `trust` de KaTeX, `securityLevel` de Mermaid), injection de prompt dans les appels Gemini via le contenu des notes, `noindex` sur les pages publiques, rate limiting, CORS, en-têtes de sécurité.
- **`conventions-dao`** — la forme canonique d'un modèle, d'un DAO, d'un service, d'un contrôleur et de leurs tests, avec un exemple complet de bout en bout servant de gabarit.
- **`invariants-sm2`** — spécification formelle de SuperMemo-2 telle qu'implémentée ici : facteur de facilité, plancher à 1.30, progression des intervalles, traitement de l'échec, définition du « jour d'étude » et du fuseau horaire de référence pour les streaks. Fournit des fixtures de non-régression : toute modification touchant à la planification doit les faire passer à l'identique.
- **`design-system`** — les tokens, l'échelle typographique, les règles de composition, les contraintes d'accessibilité et les contraintes tactiles Capacitor. Rédigée en phase 3, utilisée par tous les cycles de migration d'écran.
- **`cycle-tdd`** — la forme canonique d'un cycle sur cette stack : gabarits de test `pytest` (DAO avec base transactionnelle, service avec dépendances substituées, contrôleur en client de test Flask) et `vitest` (store Pinia, composant avec Testing Library, parcours d'intégration), conventions de nommage et d'emplacement des tests, façon de formuler un comportement attendu avant de coder, liste des anti-patterns à refuser (assertion affaiblie, `mock` du sujet testé, attente temporisée).
- **`migration-ecran`** — procédure reproductible de refonte d'un écran : inventaire de l'existant → états à couvrir (vide, chargement, erreur, dense, hors ligne) → composition à partir des primitives → tests → capture d'écran → commit.

> **Fait pour 5 des 6** — `audit-securite`, `conventions-dao`, `invariants-sm2`,
> `cycle-tdd`, `migration-ecran` créées et adaptées à la stack réelle (pas la stack
> supposée par ce prompt — ex. pas de Tiptap/Mermaid en usage réel, `@vue/test-utils` et
> non Vue Testing Library). `design-system` volontairement différée à la phase 3 comme
> prévu ici.

### 4.7 Subagents

Dans `.claude/agents/`, avec des outils volontairement restreints :

- **`auditeur-securite`** — lecture + grep uniquement, aucun droit d'écriture hors `docs/audit/`. Produit des constats sourcés (fichier:ligne), jamais de correctif.
- **`architecte-backend`** — évalue la cohérence DAO/Service/Contrôleur, les transactions, les N+1, la stratégie de migration.
- **`designer-ui`** — ne touche qu'aux tokens et aux primitives du design system, jamais aux écrans.
- **`migrateur-ecran`** — applique la skill `migration-ecran` à un écran et un seul par invocation ; interdiction de modifier les tokens (s'il en manque un, il remonte le besoin au lieu d'improviser).
- **`specifieur-tests`** — intervient **avant** l'implémentation : formule le comportement attendu, écrit les tests et vérifie qu'ils échouent pour la bonne raison. Il n'a aucun droit d'écriture sur le code de production ; c'est cette restriction d'outils qui rend le TDD structurel plutôt que déclaratif.

**Critères d'acceptation de la phase 1** : les hooks sont exécutables et testés (déclenche volontairement un `git push`, un test rouge et une écriture de code de production sans test préalable, pour vérifier que les trois blocages fonctionnent réellement) ; la mécanique de passation est validée à seuil abaissé — mets temporairement `SEUIL = 0.01`, provoque un `Stop`, vérifie que la passation est exigée puis que la session se laisse arrêter, fais un `/clear`, et confirme que la reprise repart seule sur la bonne action ; la suite de tests complète est verte dans les conteneurs sur x86-64 **et** sur arm64, avec les durées consignées dans `docs/ENVIRONNEMENT.md` ; les fichiers d'instructions existants ont été repris et non écrasés, les contradictions relevées m'ont été soumises, et aucune règle n'apparaît en double ; `ETAT.md` existe et décrit la phase 2 ; le socle est commité en plusieurs commits atomiques (`chore(claude): …`).

> **Phase 1 terminée** (2026-08-23) — les 5 subagents sont créés (`.claude/agents/*.md`,
> outils restreints par frontmatter + renforcement structurel via `phase_guard.py`/
> `tdd_guard.py`). Tous les critères d'acceptation ci-dessus vérifiés réellement : voir
> `ETAT.md` (checklist complète) et `docs/development_journal.md` (entrée 2026-08-23) pour
> le détail. 21 commits atomiques. En attente du feu vert utilisateur pour ouvrir la phase 2.

---

## 5. Phase 2 — Revue technique

Quatre livrables dans `docs/audit/`, plus un backlog consolidé. Chaque constat porte : un identifiant, un emplacement précis (`fichier:ligne`), une description factuelle, un impact concret pour l'utilisateur ou l'exploitant, une gravité **S1 (critique) → S4 (cosmétique)**, un effort estimé **XS/S/M/L**, et une piste de correction — **sans l'appliquer**.

### `01-SECURITE.md`
Points d'attention prioritaires, à confirmer ou infirmer dans le code réel :
- Stockage et cycle de vie des JWT côté client ; existe-t-il un refresh, une révocation, une expiration effective ?
- **Liens de partage public** : entropie du jeton, possibilité d'énumération, révocation, expiration, fuite de données annexes dans la réponse (identité de l'auteur, identifiants internes), indexation par les moteurs.
- **Marketplace** : le clonage d'un classeur duplique-t-il des données privées ? Qui peut dépublier ? Quel contrôle sur le contenu importé ?
- **XSS** via contenu utilisateur rendu : HTML produit par Tiptap, `trust`/`macros` de KaTeX, `securityLevel` de Mermaid, annotations PDF.
- **Gemini** : la clé transite-t-elle côté client ? Une note malveillante peut-elle détourner le prompt de blurting ? Y a-t-il un plafond de coût, un timeout, une politique de retry ?
- Auto-migration Alembic au démarrage : comportement avec plusieurs workers en parallèle, absence de contrôle humain sur une migration destructrice en production. **Traite ce point comme suspect par défaut.**

> Note phase 1 : la skill `audit-securite` a déjà adapté ces points à la stack réelle
> (marked+DOMPurify au lieu de Tiptap, pas de Mermaid en runtime) — s'appuyer dessus plutôt
> que sur la description ci-dessus, qui reflète la stack supposée à l'origine.

### `02-ARCHITECTURE.md`
Respect du flux Contrôleur → Service → DAO ; fuites de session SQLAlchemy ; duplication entre services ; cohérence des schémas Pydantic entrée/sortie ; gestion des erreurs et codes HTTP ; couplage `web/` ↔ `mobile/` ; taille et responsabilités des composants Vue et des stores Pinia (repère les stores fourre-tout et les composants de plus de 300 lignes).

### `03-PERFORMANCE.md`
- Complexité et coût des requêtes de révision SM-2 sur un gros volume de cartes ; N+1 sur les classeurs et les notes ; index manquants.
- Taille du bundle : Tiptap + Mermaid + PDF.js + KaTeX chargés ensemble sont rédhibitoires sur mobile milieu de gamme. Mesure le bundle réel et le chemin critique, vérifie le découpage par route et le chargement paresseux du worker PDF.js.
- Consommation mémoire de la liseuse PDF sur mobile, rendu Mermaid bloquant le thread principal.
- Coût et latence des appels Gemini ; mise en cache éventuelle.
- Requêtes du dashboard (heatmap, streaks) : agrégation en base ou en Python ?

> Note phase 1 : le bundle réel n'a pas Tiptap/Mermaid/PDF.js (cartographie phase 0) — mais
> `docs/ENVIRONNEMENT.md` a mesuré un chunk KaTeX de 1,2 Mo minifié à lui seul, signalé comme
> point d'attention pour cet axe.

### `04-TESTS-CI.md`
Couverture réelle par couche, tests manquants sur les chemins critiques (auth, partage public, SM-2, clonage marketplace), absence de CI, de linters bloquants, de tests de non-régression sur l'algorithme de planification. Propose un pipeline minimal et une cible de couverture par couche, en distinguant ce qui doit être testé unitairement de ce qui relève de l'intégration.

Évalue en outre l'**aptitude au TDD** de la base actuelle, puisque tout le reste du travail en dépend : durée d'un run complet et d'un run ciblé, existence d'un mode `--watch` exploitable, tests instables (dépendance à l'ordre, au réseau, à l'horloge, à un état de base persistant), isolation transactionnelle des tests backend, facilité à monter un composant Vue en test, disponibilité de fabriques de données. Chiffre chaque point. Si la boucle dépasse quelques secondes en ciblé, c'est un constat **S1** : le TDD ne tiendra pas.

> Note phase 1 : CI déjà mature (6 jobs, coverage gate 80 %, garde anti-drift migrations,
> E2E Playwright) — à évaluer, pas à supposer absente. Un écart réel déjà repéré à traiter
> ici : la suite contre PostgreSQL réel échoue sur 12 tests liés à la recherche full-text
> (`db.create_all()` ne crée pas les index GIN définis uniquement en migration Alembic) —
> voir `docs/ENVIRONNEMENT.md` et `docs/development_journal.md` (entrée 2026-08-23).

### `05-BACKLOG.md`
Table unique triée par gravité puis par effort croissant, avec une section « à traiter avant la refonte UI » : tout ce qui, non corrigé, rendrait la refonte instable ou serait plus coûteux à corriger après.

**Critères d'acceptation** : aucun fichier hors `docs/audit/` modifié ; chaque constat sourcé ; les quatre axes traités ; le backlog ne contient aucun constat absent des documents détaillés.

Présente-moi le backlog et **attends ma validation** avant d'ouvrir la phase 3.

---

## 6. Phase 3 — Design system

### Brief

**Produit** : outil d'étude quotidien, utilisé en session longue par des étudiants du supérieur, sur desktop pour rédiger et sur mobile pour réviser.
**Direction** : chaleureuse et gamifiée. L'énergie et la récompense d'une application d'apprentissage grand public, mais **sans infantilisation** — l'utilisateur écrit des mathématiques en LaTeX et annote des articles scientifiques. La gamification doit rester lisible comme un signal de progression réel, jamais comme une décoration.

**Garde-fous de direction** :
- La récompense visuelle s'accroche à un signal vrai : streak, rétention mesurée, cartes dues, lacunes comblées après un blurting. Pas de confettis sur une action sans mérite.
- **Ne reprends pas le vert Duolingo (`#58CC02`) ni sa hiérarchie visuelle.** L'inspiration porte sur le registre émotionnel et la mécanique de feedback, pas sur la palette.
- Évite également le triptyque par défaut des interfaces générées : fond crème `#F4F1EA` + serif à fort contraste + accent terre cuite proche de `#D97757`. C'est un réflexe, pas une décision.
- Le mode sombre est un mode de premier rang, pas une inversion automatique : les sessions de révision nocturnes sont un cas d'usage central.

**Contraintes dures** :
- Cibles tactiles ≥ 44 px, respect des `safe-area-inset` iOS, gestes ne rentrant pas en conflit avec le retour arrière natif.
- Contraste AA minimum sur tout texte, y compris sur les états colorés de feedback SM-2.
- `prefers-reduced-motion` respecté : toute animation a un chemin dégradé fonctionnel.
- 60 fps sur Android milieu de gamme — les animations de cartes 3D existantes sont à vérifier sur ce critère.
- Les couleurs de notation SM-2 ne doivent pas être le seul porteur d'information (daltonisme) : forme, libellé ou icône en renfort.

> Note phase 1 : `docs/design-system.md` documente déjà une direction en production
> partielle (« White/Pink × Material », primaire `#F06292`) et `docs/ui-redesign-plan.md`
> montre 8 lots sur 12 déjà faits. Arbitrage rendu au démarrage de la phase 1 : **cette
> phase 3 repart de zéro** (deux nouvelles directions proposées, garde-fous ci-dessus
> appliqués tels quels), l'existant n'est pas traité comme acquis. Voir `ETAT.md`.

### Travail attendu

1. **Deux directions esthétiques** proposées sous forme de plan compact, pas de code : palette de 4 à 6 valeurs nommées avec hex, appariement typographique display/texte/données (une police de caractère à personnalité utilisée avec retenue, pas la même que sur n'importe quel projet), échelle typographique, principe de mise en page, et **l'élément signature** — la seule chose par laquelle l'interface sera reconnue. Pour StudyHub, le candidat naturel est la représentation de l'assiduité et de la mémoire dans le temps ; ne t'y limite pas, mais justifie ton choix.
2. Critique tes deux propositions contre le brief avant de me les montrer : si une partie ressemble à ce que tu produirais pour n'importe quelle application d'étude, révise-la et dis ce que tu as changé.
3. **Attends mon arbitrage.** Une seule direction part en implémentation.
4. Implémente ensuite : tokens dans la config Tailwind (couleur, espacement, rayon, ombre, typographie, durées et courbes de transition), puis les primitives — bouton, champ, carte, modale, onglet, badge, info-bulle, état vide, squelette de chargement, toast — avec leurs états et leurs variantes.
5. Écris `.claude/skills/design-system/SKILL.md` à partir du résultat, et une page de démonstration interne recensant toutes les primitives dans tous leurs états, en clair et en sombre.

Chaque primitive est développée en TDD : ses états, ses variantes, sa navigation au clavier et son comportement de focus sont spécifiés en test avant d'être codés. Seuls les tokens eux-mêmes et le rendu purement visuel relèvent de l'exception « capture d'écran ».

**Critère d'acceptation** : aucune primitive n'utilise de valeur brute ; la page de démonstration passe une vérification de contraste ; le hook de détection de valeurs brutes ne remonte rien ; aucune primitive n'est dépourvue de test de comportement.

Commits : `feat(design): …`, un commit par famille de primitives.

---

## 7. Phase 4 — Refonte totale du layer UI

Migration écran par écran en s'appuyant sur la skill `migration-ecran` et le subagent `migrateur-ecran`, **un écran par cycle**, dans cet ordre — du plus structurant au plus périphérique :

1. Coquille applicative : navigation, en-tête, barre mobile, thème, états d'authentification.
2. Dashboard (heatmap, streaks, métriques de rétention) — c'est là que vit l'élément signature.
3. Session de révision flashcards (le chemin le plus emprunté, et le plus sensible au feedback tactile et à la fluidité).
4. Éditeur de notes et mode Zen.
5. Blurting IA.
6. Liseuse PDF et annotations.
7. Éditeur de diagrammes — **coquille uniquement** : navigation, en-tête, panneaux, états. Ne touche pas au canevas ni au moteur, ils sont reconstruits en phase 5. Le but ici est seulement que l'écran ne détonne plus visuellement.
8. Marketplace et pages de partage public.
9. Réglages, profil, écrans d'authentification.

Pour chaque écran, le cycle est : inventaire des fonctionnalités existantes → **formulation écrite du comportement attendu, état par état (vide, chargement, erreur, dense, hors ligne) dans `ETAT.md`** → **écriture des tests et constat du rouge** → composition à partir des primitives uniquement, jusqu'au vert → réécriture de la copie selon les principes ci-dessous → refactor à tests verts → capture d'écran clair/sombre, desktop/mobile → mise à jour d'`ETAT.md` → commit.

L'inventaire de l'existant sert de source aux tests : chaque fonctionnalité recensée devient une assertion avant d'être réimplémentée. C'est ce qui garantit que la refonte ne perd rien en route.

**Règle d'or** : la refonte ne supprime aucune fonctionnalité existante sans que je l'aie validé explicitement. Si un élément d'interface te semble superflu, tu le signales dans `ETAT.md` — tu ne le retires pas de ta propre initiative.

**Copie d'interface** : verbes actifs, casse de phrase, vocabulaire constant d'un bout à l'autre d'un flux (le bouton « Publier » produit le message « Publié »). Les erreurs disent ce qui s'est passé et comment le réparer, sans s'excuser et sans vague. Un écran vide est une invitation à agir, pas un constat de vide.

---

## 8. Phase 5 — Refonte de l'outil de diagrammes

### 8.1 Pourquoi une phase à part

L'existant superpose deux éditeurs — un canevas SVG en glisser-déposer et un éditeur textuel Mermaid — ce qui pose un problème que le redesign ne résout pas : **lequel fait foi ?** Mermaid ne sait pas représenter une position manuelle de nœud ; un aller-retour texte → visuel → texte détruit donc toute mise en page faite à la main. C'est pour ça que ce module se reconstruit au lieu de se repeindre.

> Note phase 1 : la cartographie confirme un canevas SVG maison existant (`Diagrams.vue`,
> 1789 lignes) mais **aucune dépendance Mermaid réelle** dans `web/package.json` — l'éditeur
> textuel Mermeid décrit ici n'existe pas (ou plus) dans le code actuel. À vérifier
> concrètement en phase 2/5 avant de bâtir la logique d'import/export sur cette prémisse.

L'objectif : un **canevas libre** où l'utilisateur place ce qu'il veut où il veut, couvrant tous les types de schémas utiles à l'étude, avec une manipulation assez rapide pour qu'on schématise **pendant** un cours et pas seulement après.

### 8.2 Décision d'architecture — tranchée

**Le canevas libre est le mode d'édition de référence.** L'utilisateur place chaque élément à la position exacte qu'il choisit, et rien ne la déplace sans qu'il le demande. Cette décision est prise ; elle n'est pas à rediscuter, et elle en entraîne trois autres :

1. **Un modèle de document propre fait foi**, sérialisé dans un format versionné, portant les coordonnées, les dimensions, l'ordre de superposition, les styles, les points de routage des liens et les objets propres à StudyHub. C'est la seule option compatible avec le placement libre.
2. **Mermaid devient un format d'échange, pas la source de vérité.** L'import sert à amorcer un schéma depuis du texte ; l'export produit une approximation qui perd les positions. **La perte est annoncée à l'utilisateur au moment de l'export** — jamais silencieuse. Aucun aller-retour automatique : le texte ne réécrit jamais un document existant.
3. **La mise en page automatique devient une commande, pas un moteur.** « Ranger la sélection », « aligner », « distribuer » sont des actions explicites, déclenchées par l'utilisateur, annulables comme n'importe quelle autre. Aucun algorithme ne repositionne quoi que ce soit de sa propre initiative.

Le format persisté porte un **numéro de version de schéma** et dispose d'un chemin de migration : les diagrammes partagés via la marketplace doivent continuer à s'ouvrir dans six mois.

**Contrepartie à assumer** : le placement libre produit des schémas mal rangés si l'outil ne rattrape pas. C'est le magnétisme, les guides d'alignement et les commandes de rangement qui font la différence entre « libre » et « brouillon » — ils ne sont pas optionnels, ils sont la condition de viabilité du choix.

### 8.3 Couverture fonctionnelle visée

Le placement libre change la nature de cette liste : il n'y a **pas un moteur par type de diagramme**, mais un seul canevas, un vocabulaire d'éléments, et des gabarits de départ. Un organigramme et une carte conceptuelle sont le même canevas avec des formes et des liens différents. C'est une simplification majeure — moins de code, moins de bundle, et surtout aucun type « impossible » puisque rien n'est contraint.

**Le vocabulaire d'éléments** — c'est lui qu'il faut couvrir, pas les types :

- Formes (rectangle, ovale, losange, cercle, forme libre) avec libellé.
- Liens : droits, orthogonaux, courbes, avec points de routage déplaçables à la main, extrémités fléchées configurables et libellé posé sur le lien.
- Blocs de texte libres, indépendants de toute forme.
- **Conteneurs et zones** — un cadre nommé qui regroupe des éléments et les déplace avec lui. C'est ce qui permet les couloirs, les regroupements, les ensembles.
- **LaTeX dans les libellés** via KaTeX, déjà dans la stack.
- Images posées sur le canevas (schéma scanné à annoter).
- Traits libres à main levée, pour l'annotation rapide au doigt.

**Les gabarits** couvrent ensuite les situations : flux et arbres de décision, séquences, structures (classes, entité-association), automates et cycles, cartes conceptuelles et mentales, chronologies et frises, ensembles et classifications, schémas scientifiques annotés. Chacun n'est qu'un point de départ pré-rempli avec les bons éléments et les bons styles — l'utilisateur reste libre d'en sortir à tout moment.

Un gabarit ne s'ajoute que si un cas d'usage réel le justifie : huit gabarits irréprochables valent mieux que trente approximatifs.

### 8.4 Fluidité

C'est le critère qui décide de l'adoption du module, et le placement libre en déplace le centre de gravité : ce qui est difficile n'est plus de placer, c'est de placer **proprement et vite**.

- **Magnétisme et guides d'alignement.** Pendant le déplacement, l'élément s'aligne sur ses voisins et sur une grille, avec des repères visibles et des espacements suggérés. Le magnétisme est désactivable au clavier pendant le geste, pour les cas où l'utilisateur veut vraiment placer au pixel près. Sans ça, le canevas libre produit du désordre — c'est la fonctionnalité la plus rentable du module.
- **Commandes de rangement** sur une sélection : aligner, distribuer, égaliser les tailles, et un « ranger » qui applique une disposition automatique **à la sélection seulement**, annulable comme le reste.
- **Création au clavier de bout en bout.** On doit pouvoir construire une carte conceptuelle de trente nœuds sans toucher la souris : créer un frère, créer un enfant, naviguer entre éléments, renommer, supprimer. Un élément créé au clavier est placé automatiquement à côté de son origine, sans chevauchement — mais rien n'empêche de le déplacer ensuite. Sans ça, personne ne schématise en cours.
- **Manipulation directe complète** : poignées de redimensionnement, rotation, ordre de superposition (avant-plan, arrière-plan), duplication au glisser, copier-coller conservant les positions relatives.
- **Liens qui suivent.** Un lien reste attaché à ses formes quand elles bougent, se réancre au point le plus pertinent, et conserve les points de routage posés à la main.
- **Sélection multiple** au lasso et au rectangle, groupes, verrouillage d'un élément pour ne plus le déplacer par erreur.
- **Annuler/refaire irréprochable** sur toute la surface — déplacements, styles, suppressions multiples, rangement automatique. Un canevas libre sans undo fiable est inutilisable, parce que chaque geste est une modification.
- **Canevas infini**, avec panoramique et zoom, un aperçu global pour se repérer, et un « recadrer sur tout ».
- **Tactile de premier rang** : pincer pour zoomer, appui long, cibles ≥ 44 px, aucun conflit avec le défilement de page ni le geste de retour natif. Attention au conflit propre au canevas libre : distinguer un déplacement d'élément d'un panoramique du canevas au doigt demande une règle explicite, à décider et à tester sur appareil réel, pas en émulation navigateur.
- **Hors ligne** : l'édition fonctionne sans réseau, la synchronisation se fait au retour.

### 8.5 Intégration à StudyHub

C'est ce qui distingue ce module d'un outil de schéma générique, et c'est là que se trouve la valeur :

- **Nœud → note.** Un nœud peut pointer vers une note existante ; le lien est navigable dans les deux sens.
- **Diagramme → flashcards.** Générer des cartes depuis un schéma (relation entre deux nœuds, libellé masqué).
- **Diagramme muet.** Masquer les libellés et demander à l'utilisateur de les restituer — l'équivalent visuel du blurting, et un exercice de révision classique. Il s'articule avec le module IA existant pour évaluer la restitution.
- **Marketplace et partage public** : un diagramme se partage et se clone comme un classeur, avec les mêmes règles de sécurité que celles auditées en phase 2. Un schéma partagé est du contenu utilisateur rendu chez autrui — les conclusions de l'audit sur la sanitisation s'y appliquent intégralement.
- **Export** : image et PDF, cohérents avec l'export de notes existant.

### 8.6 Contraintes techniques

- **Rendu** : tranche SVG contre canevas **sur mesure**, pas sur préférence. Le seuil qui décide est le nombre d'éléments à partir duquel le déplacement descend sous 60 fps sur Android milieu de gamme. Mesure-le sur l'existant avant de choisir. Un canevas infini impose en plus de ne rendre que ce qui est visible : la fenêtre de vue borne le travail de rendu, quel que soit le nombre d'éléments du document.
- **Budget de bundle** : le module s'ajoute à Tiptap, PDF.js et KaTeX. Fixe un plafond en kilo-octets **avant** de choisir les bibliothèques. Le placement libre joue en ta faveur ici — un seul canevas au lieu d'un moteur par type de diagramme — mais l'import Mermaid et le rendu LaTeX se chargent à la demande, pas au démarrage. Si l'audit de phase 2 a classé le bundle en critique, ce plafond est un critère d'acceptation, pas un souhait.
- **Sécurité** : le rendu Mermaid de contenu importé ou partagé passe par une configuration restreinte. Le LaTeX des libellés est rendu sans autoriser les macros arbitraires.
- **Réutilise les tokens et primitives** de la phase 3. La palette et les libellés du module respectent le design system — aucun style local.

### 8.7 TDD sur ce module

Le modèle de document, les commandes d'édition et la mise en page sont de la logique pure : c'est le terrain le plus favorable du projet au TDD, sans exception applicable.

- Chaque commande d'édition est spécifiée par un test avant d'exister.
- **Invariant d'annulation, testé par propriété** : pour toute suite de commandes, annuler autant de fois qu'il y a eu de commandes ramène à un document strictement identique à l'état initial. C'est le test qui protège l'undo, et il doit être écrit en premier.
- **Invariant de placement** : aucune opération autre qu'un déplacement explicite ne modifie les coordonnées d'un élément. Ce test est la garantie mécanique de la promesse « ça reste où je l'ai mis » — ouverture, fermeture, import, changement de style, zoom, redimensionnement d'un voisin, rangement d'une autre sélection : rien ne bouge.
- **Géométrie testable à part** : magnétisme, guides d'alignement, ancrage et routage des liens sont des fonctions pures sur des coordonnées. Elles se testent sans canevas ni DOM, et c'est là que se cachent les régressions les plus pénibles à diagnostiquer visuellement.
- **Non-régression de format** : un corpus de documents sérialisés de chaque version doit continuer à s'ouvrir. Un test par version de schéma.
- Le rendu visuel relève de l'exception « capture d'écran » ; les interactions (clavier, sélection, zoom, tactile) n'en relèvent pas.

### 8.8 Corpus d'acceptation

Constitue **dix schémas d'étude réels**, un par type visé, tirés de matières différentes — et non des exemples jouets. Ils servent à la fois de fixtures de test, de banc de mesure de performance et de critère de recette.

**La phase est terminée quand** : les dix schémas se construisent intégralement dans l'outil ; chaque élément se pose exactement là où l'utilisateur le veut et n'en bouge plus ; la carte conceptuelle du corpus se saisit entièrement au clavier ; le plus lourd des dix reste au-dessus de 60 fps en déplacement sur Android milieu de gamme ; l'invariant d'annulation passe ; les documents de toutes les versions antérieures s'ouvrent encore ; le plafond de bundle est respecté.

### 8.9 Séquence

Un chantier par cycle, chacun commité séparément : modèle de document et sérialisation versionnée → commandes et annulation → canevas, panoramique, zoom et rendu borné à la fenêtre de vue → placement, sélection, magnétisme et guides d'alignement → liens, ancrage et routage → interactions clavier → interactions tactiles → conteneurs, texte libre, images, LaTeX → commandes de rangement → gabarits, un par un → intégrations StudyHub (notes, flashcards, diagramme muet) → import/export Mermaid → export image et PDF → partage et marketplace.

L'ordre n'est pas négociable : le modèle, l'annulation et le canevas sont la fondation, et les reprendre après avoir construit le reste dessus coûte le double. Note que l'import/export Mermaid arrive **tard** — c'est devenu une fonctionnalité de confort, plus le cœur du module.

---

## 9. Séquence de démarrage

Fais maintenant, dans l'ordre, sans me demander de confirmation intermédiaire jusqu'au point d'arrêt :

1. Lis `AGENTS.md` et la structure du dépôt.
2. Produis `docs/audit/00-CARTOGRAPHIE.md`.
3. Présente-moi en une dizaine de lignes ce que tu as trouvé et les écarts que tu constates entre `AGENTS.md`, le `README.md` et le code réel, **ainsi que les contradictions entre les instructions déjà en place et les consignes de ce prompt**.
4. **Arrête-toi là** et propose-moi le plan détaillé de la phase 1 avant de créer le moindre fichier dans `.claude/`.

> **Fait intégralement** — voir historique de commits (`5929bb7` à `8a49100`) et `ETAT.md`.
