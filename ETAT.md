# État du projet — StudyHub

> Source de vérité sur "où on en est". Mis à jour à chaque cycle. Les hooks
> (`phase_guard.py`, `tdd_guard.py`, `stop_gate.py`) lisent le champ **Phase**
> ci-dessous — format `Phase: N` sur sa propre ligne, ne pas le reformuler.

Phase: 4

## Phase précédente — 1 : Outillage agentique

**Feuille de route complète et durable (phases 0→5, règles, critères d'acceptation) :
`docs/PROMPT_DEMARRAGE.md`** — versionné dans le dépôt, annoté phase par phase de ce qui
est fait. C'est la référence à relire pour toute question sur une phase future ; ne pas se
fier à une conversation passée ou à un fichier de plan local
(`~/.claude/plans/*.md`, propre à une machine, non versionné, non durable). Arbitrage
acté : on prend ce prompt intégralement, pas l'ancien état documenté (`docs/design-system.md`,
`docs/performance-audit.md`, `docs/ui-redesign-plan.md` traités comme non acquis en phase 2/3).

### Checklist phase 1

- [x] `docs/audit/00-CARTOGRAPHIE.md` (phase 0)
- [x] `AGENTS.md`, `CLAUDE.md`, `README.md` réécrits
- [x] `backend/CLAUDE.md`, `web/CLAUDE.md`, `web/src/components/CLAUDE.md`
- [x] Permissions `settings.json` (allow/deny/ask, Bash+PowerShell)
- [x] Hook `PreToolUse` de garde (push/rm -rf/reset --hard/rebase/secrets)
- [x] `ETAT.md` (ce fichier)
- [x] Garde d'écriture phase 2 (`phase_guard.py`)
- [x] Garde TDD phase 3+ (`tdd_guard.py`, `.claude/tdd-exempt.txt`)
- [x] Outillage format (ruff backend, ESLint+Prettier web) + hooks `PostToolUse`
- [x] Hook `Stop` unifié (`stop_gate.py`, remplace `commit_reminder.py`)
- [x] Mécanique de passation de contexte (`PreCompact`, `SessionStart`)
- [x] 5 skills de process (`audit-securite`, `conventions-dao`, `invariants-sm2`,
      `cycle-tdd`, `migration-ecran`) — `design-system` différée à la phase 3
- [x] 5 subagents (`.claude/agents/*.md`)
- [x] Environnement conteneurisé multi-arch + `docs/ENVIRONNEMENT.md` (backend 100 % vert
      SQLite arm64 natif 56,4s ; frontend 100 % vert arm64 natif 7,8s ; amd64 via CI existante,
      non re-déclenchée cette session — pas de push)
- [x] Vérification des gardes : `git push --help` bloqué (guard_dangerous_commands),
      écriture hors docs/audit/ bloquée en phase 2 simulée (phase_guard), écriture sans
      test bloquée en phase 3 simulée (tdd_guard), test réellement rouge bloque le Stop
      (stop_gate — cassé/réparé TagBadge.spec.ts pour le vérifier ; a révélé et corrigé
      2 bugs réels : encodage UTF-8 et résolution de chemin relatif dans les hooks)
- [x] Drill de passation à seuil abaissé — déclenché réellement (Stop bloqué à 290 %,
      seuil 1 %), `PASSATION.md` écrite et archivée dans `docs/passations/`, `/clear` fait
      par l'utilisateur, reprise automatique confirmée (relance sur la bonne action : seuil
      remis à 0.90, commit, présentation du récap).
- [x] Passe de cohérence documentaire finale

**Phase 1 terminée — tous les critères d'acceptation vérifiés.**

## Phase précédente — 2 : Revue technique (lecture seule)

Feu vert utilisateur reçu le 2026-08-23. Spécification complète des quatre axes :
`docs/PROMPT_DEMARRAGE.md` §5.

### Checklist phase 2

- [x] `docs/audit/01-SECURITE.md` (9 constats : S1×2, S2×3, S3×4)
- [x] `docs/audit/02-ARCHITECTURE.md` (12 constats : S2×4, S3×5, S4×3)
- [x] `docs/audit/03-PERFORMANCE.md` (7 constats : S1×1, S2×3, S3×3)
- [x] `docs/audit/04-TESTS-CI.md` (7 constats : S1×1, S2×2, S3×2, S4×2)
- [x] `docs/audit/05-BACKLOG.md` (35 constats consolidés, triés gravité puis effort,
      section « à traiter avant la refonte UI »)
- [x] Aucun fichier hors `docs/audit/` (et ce fichier) modifié pendant la phase
- [x] Backlog présenté à l'utilisateur — validé le 2026-08-24 : le backlog devient une
      phase à part entière (**phase 6**, ajoutée en fin de séquence dans
      `docs/PROMPT_DEMARRAGE.md` §10), pas un préalable à la phase 3. Quelques constats
      restent traités au fil des phases 3-5 aux moments indiqués dans
      `docs/audit/05-BACKLOG.md` (« à traiter avant la refonte UI »).

**Phase 2 terminée.** 4 constats S1 : SEC-01 (clé secrète de repli, conditionnel), SEC-02
(fuite de contenu privé sous classeur public), PERF-05 (rendu KaTeX bloquant à chaque
frappe dans `NoteEdit.vue`), TEST-01 (CI PostgreSQL rouge en permanence). Détail et
séquencement : `docs/audit/05-BACKLOG.md`.

## Phase précédente — 3 : Design system

Feu vert utilisateur reçu le 2026-08-24. Spécification complète (brief, garde-fous,
contraintes dures, travail attendu) : `docs/PROMPT_DEMARRAGE.md` §6.

### Checklist phase 3

- [x] Deux directions esthétiques proposées (palette 4-6 valeurs hex, appariement
      typographique display/texte/données, échelle typographique, principe de mise en
      page, élément signature) + auto-critique de chacune contre le brief
- [x] Arbitrage utilisateur reçu — une seule direction retenue
- [x] Tokens Tailwind (couleur, espacement, rayon, ombre, typographie, durées/courbes de
      transition)
- [x] Primitives développées en TDD, états et variantes couverts (bouton, champ, carte,
      modale, onglet, badge, info-bulle, état vide, squelette de chargement, toast)
- [x] Page de démonstration interne (toutes primitives, tous états, clair/sombre) +
      vérification de contraste AA
- [x] Skill `.claude/skills/design-system/SKILL.md` rédigée à partir du résultat
- [x] Hook de détection de valeurs brutes : aucune remontée sur les primitives

### Round de direction en cours (2026-08-24, reprise après revirement)

**Revirement utilisateur (2026-08-24)** : la direction « Foyer » (palette, recolorage,
contenu enrichi — voir `docs/passations/2026-08-24_0127_phase3.md` et
`_0144_phase3.md`) est abandonnée sur demande explicite. Repart entièrement de zéro via
les skills `frontend-design` puis `design` (Claude Design), nouveau répertoire de travail
(scratchpad, hors dépôt — pas de réutilisation de `studyhub-design-foyer`).

**Clarification Accueil/Dashboard (levée par lecture du code, pas par supposition)** :
`web/src/router/index.ts:52` porte le commentaire « S1 : Accueil = fusion Dashboard +
Focus (vue action-first) » — la fusion a déjà eu lieu au niveau routage. `/dashboard` et
`/focus` redirigent tous deux vers `Accueil` (lignes 85-86) ; `Dashboard/Dashboard.vue` et
`Focus/FocusPage.vue` ne sont importés par aucune route active : ce sont des fichiers
orphelins, pas des écrans à designer. **Un seul écran à concevoir : `Home/Accueil.vue`**,
qui porte déjà le contenu des deux (streak, file de révision, focus). Suppression des deux
fichiers orphelins à consigner dans le backlog phase 6 (`docs/audit/05-BACKLOG.md`), pas
une action de la phase 3.

**IA déjà partiellement restructurée** (à ne pas re-découvrir plus tard) : le routeur
définit 5 « sections canoniques » (`accueil`, `bibliotheque/:id?`, `reviser`, `classes`,
et l'ancien `decks`/`notes`/etc. pas encore repliés) — `Binders` a été renommé
`Bibliothèque`, `Reviews` renommé `Réviser`, `Groups` et `ClassesTeacher/Student` sont
devenus des onglets de la page `Classes` unique (`ClassesLanding.vue`, query `?tab=`).
La liste des 35 vues de `docs/audit/00-CARTOGRAPHIE.md` §3.2 nomme encore les anciens
écrans séparés — à corriger dans cette référence en phase 4, mais pour la phase 3 se fier
au routeur réel (`web/src/router/index.ts`), pas à la cartographie figée. Confirmé : aucune
route Réglages/Profil n'existe (la maquette « Foyer » l'avait inventée à tort — ne pas
en redessiner une par supposition).

**Publié pour arbitrage** — deux directions esthétiques sur l'écran Accueil (desktop,
bascule clair/sombre intégrée) :
https://claude.ai/code/artifact/366dcc95-8da4-41dd-8bbd-1e625a68e2c5
- **Direction A — « Fiche »** : papier chaud, encre indigo, rehaut ocre, empreinte
  « tampon » sur la série, coins nets façon fiche bristol.
- **Direction B — « Courbe »** : gris-bleu froid, accent sarcelle unique, typo
  géométrique + mono technique, la courbe d'oubli (SM-2) comme motif structurel
  (séparateurs, mini-graphiques par fiche, jauge de série).
Auto-critique de chacune contre le brief consignée dans les annotations du canevas.
Ni l'une ni l'autre ne reprend le rose/violet/orange de « Foyer ».

**Arbitrage reçu (2026-08-24)** : direction **A « Fiche »** retenue. Consigne utilisateur :
construire l'ensemble des écrans réels sur Claude Design dans cette direction, faire
valider par l'utilisateur écran par écran, **puis seulement** reprendre la suite de la
phase 3 (tokens Tailwind, primitives TDD).

**Les 33 écrans construits et republiés (2026-08-24)** — même artifact, 7 pages :
https://claude.ai/code/artifact/366dcc95-8da4-41dd-8bbd-1e625a68e2c5
1. Coquille & Accueil — coquille nav desktop/mobile, Accueil
2. Auth & Marketplace — Connexion, Inscription, Marketplace (accueil/explorer/aperçu),
   Note publique
3. Bibliothèque & Notes — Bibliothèque, Notes (liste/éditeur/blurting/quiz/évaluation)
4. Decks & sessions de révision — Decks, session deck (desktop+mobile), session QCM
   (desktop+mobile), session set de révision, gestion d'un set
5. Stats & Réviser — stats set, stats classeur, accueil section Réviser
6. Classes & Groupes — Classes (onglet Enseignant), Groupe, Devoir
7. Examens, Planning, PDF, Diagrammes — configuration/session/résultats examen,
   planning, liseuse PDF, diagrammes (coquille liste seulement, pas l'éditeur — hors
   périmètre phase 5)

Chaque écran a la bascule clair/sombre intégrée. Une seule fiche par écran (pas de
variantes loading/error/empty systématiques — couvert plus tard par `migration-ecran`
en phase 4). Spec de la direction (palette, typo, composants réutilisables) :
`_DIRECTION_A_SPEC.md` dans le dossier de travail (hors dépôt, voir historique de
session pour le chemin si besoin). Relecture qualité en cours (agent tâche de fond).

**Prochaine action** : recueillir la validation utilisateur écran par écran (le canevas
est éditable/commentable directement). Une fois validé → reprendre la phase 3 : tokens
Tailwind, primitives en TDD, page de démonstration, skill `design-system`.

**Arrêt contexte 139 % (2026-08-24 10:58)** : livrable publié, rien de bloquant — résolu à
la reprise (voir ci-dessous).

**Utilisateur satisfait des 33 écrans (2026-08-24)** : « les pages sont très bien, continue
le travail ? » — validation acquise, la reprise de la phase 3 (tokens/primitives) est
lancée. Découverte au passage : l'ancien thème **White/Pink** (« Foyer ») est toujours en
prod sur `main` (commits `6f6a457`, `1a01215`) — ce n'est pas de la maquette jetable, la
suite de la phase 3 le remplace réellement.

**Plan d'implémentation écrit et committé (`c01bbd9`)** :
`docs/superpowers/plans/2026-08-24-design-system-direction-a.md` — 14 tâches TDD couvrant
le reste de la checklist ci-dessus (tokens Tailwind + test de contraste AA automatisé, les
10 primitives requises dont 2 nouvelles à créer — `BaseTooltip`, `BaseToast` —, page de
démonstration `/dev/design-system`, hook `raw_value_guard.py`, skill `design-system`). Spec
source (`_DIRECTION_A_SPEC.md`, palette/typo/patterns exacts) récupérée depuis le scratchpad
d'une session précédente et reprise dans le plan.

**Arrêt contexte 125 % (2026-08-24 12:15)** : résolu à la reprise — utilisateur a choisi
l'exécution pilotée par sous-agents.

**Exécution du plan démarrée (2026-08-24, skill `subagent-driven-development`)** : worktree
isolée créée (`.worktrees/design-system-direction-a`, branche
`feature/design-system-direction-a`, baseline 69/69 tests verts). Ledger de suivi :
`.superpowers/sdd/2026-08-24-design-system-direction-a/progress.md` (dans la worktree) — un
défaut de plan trouvé et tranché au scan de pré-vol (Tâche 12 : import `@/...` inexistant →
import relatif, cf. ledger). Les 14 briefs de tâches extraits (le script `task-brief` attend
des titres anglais, le plan est en français — contournement documenté dans le ledger).

**Arrêt contexte 155 % (2026-08-24 13:05)** : résolu à la reprise — Tâche 1 terminée par le
sous-agent (`8b1c860`, 8/8 tests contraste verts), revuée (spec ✅, qualité Approved, 1
constat Important sur un commentaire obsolète dans `style.css`), tour de correction 1/5
dispatché à l'implémenteur original.

**Arrêt contexte 165 % (2026-08-24 14:10, voir `PASSATION.md`)** : tour de correction 1 en
cours — résolu à la reprise (voir ci-dessous).

**Exécution du plan terminée (2026-08-24)** : les 14 tâches du plan
(`docs/superpowers/plans/2026-08-24-design-system-direction-a.md`) sont closes — tokens,
10 primitives (dont 2 nouvelles, `BaseTooltip`/`BaseToast`), page de démo `/dev/design-system`,
hook `raw_value_guard.py`, skill `design-system`. 5 des 14 tâches ont demandé un ou plusieurs
tours de correction après revue (Tâches 1, 6 ×2, 11, 14), toutes re-revuées propres ensuite.
Revue finale de branche (modèle le plus capable) : prête à merger « avec correctifs » — 6
constats Important, aucun Critical. Un correctif unique (16 constats, la seule vague autorisée
par le process) appliqué et re-revué propre.

Deux constats **délibérément non corrigés**, faute de vérification visuelle possible cette
session (extension Chrome déconnectée) — arbitrage explicite de l'utilisateur, reçu après
consultation d'un artifact dédié montrant les écarts mesurés sur les tokens réels : **reportés
en phase 4** dans les deux cas.
- Contraste AA : certaines paires `*-soft` + texte fort (badge « Difficile », etc.) sous 4,5:1
  en mode clair — documenté dans la skill `design-system` (« Garde-fous ») et ci-dessous.
- Cibles tactiles : `BaseButton` (sm/md) et l'onglet actif de `Tabs` restent sous 44px — seuls
  les boutons de fermeture (`BaseToast`, `BaseModal`) ont été remontés.
- `web/src/style.css` (`.markdown-body`/`.katex-display`, rendu des notes) reste sur l'ancienne
  palette rose — hors périmètre de la Tâche 1, territoire phase 4 (migration écran par écran).

**Branche `feature/design-system-direction-a` poussée, PR ouverte** :
https://github.com/kappacite/StudyHub/pull/123 — 20 commits, 145/145 tests verts, build propre.
En attente de revue/merge humain.

**Checklist phase 3 ci-dessus** : tous les items cochés dans la branche (à jour dans
`ETAT.md` de la worktree/PR) — ce fichier sur `main` se met à jour au merge de la PR.

**Plan exécuté, 14 tâches terminées (2026-08-24)** : exécution via `subagent-driven-development`
(un subagent implémenteur puis un subagent relecteur frais par tâche, `1cd074c..c655585`). Les
13 tâches de production (1-13) sont toutes complétées et relues — 2 (tâche 1 tokens, tâche 11
`BaseToast`) ont nécessité un tour de correction après relecture, la tâche 6 (`BaseModal`) deux
tours ; toutes approuvées en l'état final. Tâche 14 (celle-ci) documente le résultat. Une revue
de branche entière reste prévue comme dernière étape du plan et **n'a pas encore eu lieu** — ne
pas la considérer faite avant qu'elle ait tourné.

Résultat : les tokens remplacent entièrement l'ancien thème White/Pink par la Direction A
« Fiche » (palette, typographie, rayons, ombres — `web/src/style.css` — + test de contraste
AA automatisé, `web/tests/design-tokens/contrast.spec.ts`). Les 10 primitives requises par la
checklist ci-dessus sont faites, testées en TDD (`web/tests/components/ui/base/`), dont 2
entièrement nouvelles (`BaseTooltip`, `BaseToast`). Page de démonstration interne
`/dev/design-system` (`web/src/views/Dev/DesignSystemDemo.vue`) présentant les 10 primitives
avec bascule clair/sombre. Hook `PostToolUse` non bloquant `raw_value_guard.py` : avertit sur
toute valeur de style brute écrite dans `web/src/components/ui/`.

**Écarts connus (revue finale de branche, non bloquants, consignés délibérément)** :
- `contrast.spec.ts` vérifie 8 paires de tokens choisies à la main, pas toutes les paires
  réellement rendues par les primitives ; certaines combinaisons fond `*-soft` + texte fort
  mesurent sous l'AA (4,5:1) en clair une fois vérifiées contre leur fond réel d'affichage.
  Reporté à un suivi avec vérification visuelle.
- La contrainte cible tactile ≥44px a été appliquée aux deux boutons de fermeture (BaseToast,
  BaseModal) mais pas encore auditée sur les variantes de taille de `BaseButton` ni la hauteur
  des pilules de `Tabs` — reporté, nécessiterait une passe visuelle sur les ~100+ sites d'appel
  existants.
- `web/src/style.css` (`.markdown-body`/`.katex-display`, rendu des notes) utilise encore
  l'ancienne palette rose — hors périmètre de ce plan (la tâche 1 n'a touché que la définition
  des tokens), migration écran par écran prévue en phase 4.

## Phase courante — 4 : Refonte totale du layer UI

Feu vert utilisateur reçu le 2026-08-24 (« continue »). Spécification complète (ordre des
écrans, cycle par écran, règle d'or, copie) : `docs/PROMPT_DEMARRAGE.md` §7, procédure
détaillée : skill `migration-ecran`.

### Ordre des écrans (du plus structurant au plus périphérique)

1. Coquille applicative — navigation, en-tête, barre mobile, thème, états d'authentification
   (`web/src/components/layout/AppLayout.vue`) — **terminé**
2. Accueil (dashboard fusionné : heatmap, streaks, métriques de rétention, file de révision)
   (`web/src/views/Home/Accueil.vue`) — **terminé**
3. Session de révision flashcards (`web/src/views/Decks/StudyDeck.vue`) — **terminé**
4. Éditeur de notes et mode Zen
5. Blurting IA
6. Liseuse PDF et annotations
7. Éditeur de diagrammes — coquille uniquement (pas le canevas/moteur, phase 5)
8. Marketplace et pages de partage public
9. Réglages, profil, écrans d'authentification

### Note (rappel du process)

Chaque écran suit le cycle en 8 étapes de la skill `migration-ecran` : inventaire → états
écrits dans ce fichier → tests rouges → composition depuis les primitives seules → copie →
refactor vert → capture d'écran clair/sombre × desktop/mobile → mise à jour de ce fichier +
commit. Le sous-agent `migrateur-ecran` n'a pas le droit de modifier les tokens ; toute
lacune de token remonte au contrôleur plutôt que d'être improvisée. Contraste AA, cibles
tactiles ≥44px, `safe-area-inset` iOS, `prefers-reduced-motion` : non négociables à chaque
écran — c'est notamment l'occasion de résorber au fil de l'eau les deux écarts reportés en
phase 3 (contraste sur badges `*-soft`, cibles tactiles `BaseButton`/`Tabs`) sur les écrans
qui les utilisent réellement, avec cette fois une vérification visuelle réelle.

### Plan global par flux — extension révision hétérogène + assistant IA (2026-08-27)

**Migré vers `workflow/` le 2026-08-28** : les 8 flux ci-dessous sont désormais suivis comme 6
chantiers dans `workflow/{backend-ensembles-heterogenes,editeur-notes-notation-ia,
bibliotheque-ensembles,reviser-hub,ecrans-peripheriques-visuels,classes-examens-planning}/`
(`CONTEXT.md`/`PLAN.md`/`JOURNAL.md` chacun). **C'est désormais là qu'il faut cocher
l'avancement et journaliser** — la section ci-dessous reste la référence historique des
décisions (pourquoi l'architecture hétérogène a été retenue, correction de correspondance
Notes.dc.html/Binders.vue, etc.), non mise à jour au fil de l'exécution des flux.

**Outillage (hooks guards + skill `gestion-chantier`) en place le 2026-08-28.**

Périmètre ajouté en cours de phase 4, en plus des 9 écrans ci-dessus : le canevas Direction A
a été étendu (session Claude Design, artefact `366dcc95-8da4-41dd-8bbd-1e625a68e2c5`, 37
artboards) pour couvrir la hiérarchie Classeur → Ensembles de révision → Éléments (6 types :
Flashcards, QCM, Vrai/Faux, Association, Définition, Ordre) et l'Assistant IA de l'éditeur de
note (Évaluation mixte, Méthode de la feuille blanche, Méthode Feynman, + bouton Notation
distinct). **Décision utilisateur (2026-08-27) : on garde le canevas tel quel** — ensembles
hétérogènes (un ensemble peut mélanger plusieurs types d'éléments, y compris les flashcards),
quitte à ce que ça diverge de l'architecture `RevisionSet`/`RevisionItem` actuelle (homogène,
flashcards à part dans `Deck`) et impose une vraie migration de schéma plutôt qu'un ajout.

**Règle pour ce périmètre, à ne pas perdre en route** : chaque flux ci-dessous reçoit son
propre plan détaillé (spec + tâches TDD pas-à-pas, format `docs/superpowers/plans/YYYY-MM-DD-
<flux>.md`, sur le modèle du plan écran 4 `2026-08-25-noteedit-migration-plan.md`) **avant
d'être exécuté** — jamais d'implémentation à partir de ce résumé seul. Cette liste est mise à
jour à chaque cycle (statut + lien vers le plan écrit + lien vers le plan/spec exécuté), comme
la liste « Écrans migrés » ci-dessous pour les 9 écrans historiques.

**Correction de correspondance** (à ne pas refaire) : l'artboard du canevas nommé
`Notes.dc.html` correspond en réalité à l'écran `web/src/views/Binders/Binders.vue` (détail
d'un classeur : notes/decks/ensembles), **pas** à `web/src/views/Notes/Notes.vue` (liste plate
de toutes les notes, filtrable par classeur).

**Ordre des flux (dépendances) :**

1. **Backend — migration ensembles hétérogènes** — bloquant pour les flux 3 et 4. Déplace
   `type` de `RevisionSet` vers `RevisionItem`, décide du sort des flashcards existantes
   (`Deck`/`Flashcard`) vis-à-vis de `RevisionItem`, migration Alembic, réécrit
   `validate_item_payload`/`check_answer` (`backend/app/services/revision_service.py`) pour
   dispatcher sur le type de l'item et non plus de l'ensemble. — **pas commencé, plan pas
   encore écrit**
2. **Backend — « Notation de la note »** — nouvelle méthode `ai_service` (note la qualité de la
   fiche sur 100, distincte de l'« Évaluation mixte » qui note la performance de l'élève sur
   des exercices générés), route dédiée, pas de dépendance au flux 1. — **pas commencé, plan
   pas encore écrit**
3. **Frontend — Bibliothèque/classeur** (`Binders.vue`) : bascule Notes/Révision, liste
   d'ensembles hétérogènes. Dépend du flux 1. — **pas commencé, plan pas encore écrit**
4. **Frontend — Ensemble détail + modales** (nouveaux `RevisionSetDetail.vue`,
   `RevisionSetModal.vue`, `RevisionItemModal.vue` à 6 types). Dépend des flux 1 et 3. — **pas
   commencé, plan pas encore écrit**
5. **Frontend — Éditeur de notes** : suite du plan écran 4 existant
   (`docs/superpowers/plans/2026-08-25-noteedit-migration-plan.md`), déjà amendé pour inclure
   la Tâche 4 (Assistant IA à 3 méthodes à jour) et la Tâche 5 (nouvelle, `NoteFeynman.vue`) —
   le bouton Notation (Tâche 4) reste désactivé tant que le flux 2 n'a pas livré sa cible. —
   **plan écrit, exécution pas commencée** (prochaine action de la phase 4, cf. section
   Écrans migrés ci-dessous)
6. **Frontend — Réviser (hub global)** : `RevisionSetManage.vue`, `RevisionSetStats.vue`,
   `RevisionBinderStats.vue`, `Reviews.vue` à mettre à jour pour les types déjà migrés au flux
   1. Dépend du flux 1. — **pas commencé, plan pas encore écrit**
7. **Écrans 5-9 restants** (Blurting — retonation visuelle seulement, le contenu ne change pas
   au-delà de la Tâche 5 du flux 5 ; PDF ; Diagrammes coquille ; Marketplace ; Auth/Réglages) —
   indépendants des flux 1-6, pure migration visuelle `migration-ecran`, peuvent avancer en
   parallèle. — **pas commencés**
8. **Classes/Groupes/Devoirs, Examens, Planning** — indépendants des flux 1-6, pure migration
   visuelle, à ajouter formellement à l'ordre des écrans ci-dessus quand on y arrive. — **pas
   commencés**

### Écran 1 — Coquille applicative (`AppLayout.vue`) — terminé

**Inventaire de l'existant** (lecture complète du fichier, 2026-08-24) :
- Sidebar gauche (desktop statique, drawer mobile) : logo + wordmark cliquable (→ `/`), 6
  destinations (Accueil, Bibliothèque, Réviser, Planning, Classes, Communauté) avec icône +
  libellé, état actif par préfixe de route ; pied : bascule thème (`BaseToggle`), bloc profil
  (avatar initiales, nom, email, déconnexion) si authentifié sinon CTA « Se connecter ».
- Mode Zen (édition de note) : sidebar devient overlay déclenché au survol/toggle plutôt que
  statique ; en-tête se masque et réapparaît au survol d'une bande invisible en haut.
- En-tête (masqué si `route.meta.immersive`) : hamburger mobile, titre de route courante,
  recherche globale (`⌘K`/`Ctrl+K` → `SearchModal`), `NotificationBell` (si authentifié), date
  du jour (masquée en très petit écran).
- Widgets globaux : `SearchModal`, `PomodoroTimer` (masqué si immersif).
- Raccourcis clavier : `Ctrl/Cmd+K` (recherche), événement custom
  `studyhub:toggle-sidebar` (bascule menu mobile ou sidebar Zen selon le mode).
- Persistance thème : `localStorage['sh_theme']`, résolution initiale via
  `prefers-color-scheme` si rien de sauvegardé.
- Aucun appel API direct dans ce composant (délégué à `authStore`, aux enfants) — conforme.

**Écart maquette Direction A vs existant, arbitré par l'utilisateur (2026-08-24)** : la
maquette (`docs/design-system-direction-a-spec.md:105-154`) ne montre que 4 destinations
primaires (Accueil/Bibliothèque/Réviser/Classes) en nav horizontale desktop + barre basse
mobile, contre 6 aujourd'hui. **Décision** : 5 pills primaires (Accueil, Bibliothèque,
Réviser, **Planning**, Classes) dans la nav desktop ; **Communauté** devient une icône
secondaire dans le cluster d'actions à droite (à côté recherche/thème/avatar) — cohérent avec
le commentaire déjà présent dans le code actuel (« 5 sections par intention + lien
Communauté »). Mobile : barre basse conforme à la maquette (4 onglets, Accueil/Bibliothèque/
Réviser/Classes inchangés) ; Planning et Communauté deviennent des icônes dans le mini-en-tête
mobile (52px), miroir du traitement desktop de Communauté. Aucune destination supprimée.

**Amendement (fix round 2, voir plus bas)** : Planning et Communauté sont finalement retirés
du mini-en-tête mobile (ils restent dans le tiroir hamburger, qui liste déjà les 6
destinations) — la densité initialement prévue ci-dessus s'est révélée cassante en pratique.
Communauté reste une icône desktop uniquement (`hidden lg:flex`).

**États à couvrir** (skill `migration-ecran` étape 2) :
- **Vide** : non authentifié → sidebar/nav affiche le CTA « Se connecter » au lieu du bloc
  profil ; pas de `NotificationBell`.
- **Chargement** : non applicable à ce composant — `authStore.init()` est synchrone (lecture
  `localStorage` directe, aucun appel réseau), aucun état de chargement à couvrir ici.
- **Erreur** : échec de déconnexion (API) — confirmé sur `authStore.logout()`
  (`web/src/stores/auth.ts:68-82`) : l'appel réseau est déjà avalé dans un `try/catch` vide et
  l'état local (token, user, `localStorage`) est toujours nettoyé dans un `finally`. Le bouton
  déconnexion de la coquille doit donc systématiquement rediriger vers `/login`, y compris
  quand l'API échoue — comportement déjà garanti par le store, à tester tel quel côté
  composant (pas de nouveau comportement à inventer).
- **Dense** : nom d'utilisateur/email longs → troncature déjà présente (`truncate`), à
  conserver ; badge de notifications à 2+ chiffres ne doit pas casser la mise en page de
  l'en-tête.
- **Hors ligne** (mobile/Capacitor) : **fonctionnalité absente aujourd'hui** (`grep` confirmé :
  aucune détection `navigator.onLine`/`online`/`offline` nulle part dans `web/src`). Ajout
  scopé à ce cycle : indicateur discret (pill neutre, non bloquant, pas de modale) dans
  l'en-tête quand `navigator.onLine === false`, basé sur les événements `online`/`offline` de
  `window`. N'affecte aucune fonctionnalité existante — pur ajout.

**Implémentation (étapes 3-6) faite** par le subagent `migrateur-ecran` : 41 nouveaux tests
(rouge confirmé 24/40 échecs → vert 41/41, suite complète 186/186), bascule structurelle
sidebar→nav en-tête desktop (conforme à la maquette Direction A), 5 pastilles + Communauté
en icône, indicateur hors ligne ajouté. Rapport complet :
`docs/passations/scratch-appshell-migration-report.md`.

**Revue de code (contrôleur, modèle le plus capable)** : conforme sur la règle d'or et
l'arbitrage nav (vérifié directement contre le diff, pas seulement le rapport). 4 constats
Important réels : bug de modèle de boîte sur `pb-safe` (rétrécit la barre au lieu de
l'étendre), collision avec le FAB Pomodoro existant sur mobile, 3 contrôles sous 44px malgré
le rapport, densité de l'en-tête mobile à 375px probablement trop serrée.

**Captures d'écran réelles (contrôleur, ~1080px — largeur maximale atteignable dans cet
environnement, juste au-dessus du seuil `lg`)** : **bug confirmé, clair et sombre** — la
boîte de recherche chevauche visuellement la pastille « Réviser », la cloche de notification
chevauche « Classes ». Reproductible dans les deux thèmes (donc un problème de largeur, pas
de thème). Captures : `screenshot-1787603976843-0.jpg` (clair),
`screenshot-1787603990027-1.jpg` (sombre).

**Tour de correction 1 dispatché** au même sous-agent : 8 constats consolidés (le
chevauchement confirmé + les 4 de la revue + 3 corrections mineures rapides pendant qu'il est
dans le fichier). Ruling consigné : la couleur de la pastille active (indigo `bg-primary`,
pas l'ocre `var(--accent)` de la maquette littérale) est conservée telle quelle — cohérente
avec le reste de l'app, pas une régression à corriger.

**Re-vérification visuelle du tour de correction 1** (navigateur connecté, contournement par
iframe de largeur contrôlée — `resize_window` de la fenêtre réelle plafonné dans cet
environnement, voir passation) : **item 1 (chevauchement) confirmé corrigé**, testé à 1045px,
1100px et 1279px (toute la plage critique lg→xl), clair et sombre — plus aucun chevauchement.

**Item 5 (titre mobile) : bug réel trouvé, pire que l'estimation** — mesure DOM (pas
seulement visuelle) à 375px avec l'indicateur hors ligne affiché : le titre de route tombait à
**1px de large, invisible**. Cause : le groupe gauche de l'en-tête mobile portait hamburger +
titre + [badge hors ligne] + recherche + Planning (icône) + Communauté (icône) + cloche +
thème — trop dense pour 375px ; seul le titre a `min-w-0`, donc lui seul absorbait tout le
déficit d'espace jusqu'à disparaître.

**Décision utilisateur** (question posée avec 3 options : retirer Planning/Communauté du
mini-en-tête vs. en-tête mobile deux lignes vs. masquer le titre mobile) : **retirer
Planning/Communauté du mini-en-tête mobile**, conservés dans le tiroir hamburger (déjà
présents, aucune destination perdue).

**Tour de correction 2 appliqué** (TDD : tests rouges d'abord — `header-planning-link`
retiré du DOM, `header-communaute-link` passé en `hidden lg:flex` — puis code) :
`web/src/components/layout/AppLayout.vue`. Suite complète re-confirmée verte : **198/198**.
Re-vérifié visuellement (mesure DOM + capture) : titre repasse à 55,6px (« Accueil ») / 139px
(« Planning des révisions », cas long) à 375px avec indicateur hors ligne — lisible, troncature
gracieuse, plus de chevauchement avec les icônes.

**Limite d'environnement rencontrée en fin de cycle** : la fenêtre du navigateur (extension
Chrome) est devenue non-réactive après plusieurs `resize_window` — capture desktop finale de
confirmation (Communauté visible en desktop après le fix round 2) non reprise, jugée à faible
risque : classe `hidden lg:flex` identique au pattern déjà utilisé et testé ailleurs dans ce
même fichier (logo, nav desktop), et couverte par un test dédié qui passe.

**Écran 1 terminé** — étape 8 (skill `migration-ecran`) : cette section à jour, commit à
suivre.

## Écrans migrés (phase 4)

1. **Coquille applicative** (`AppLayout.vue`) — 2 tours de correction (chevauchement en-tête
   1024-1279px ; titre mobile écrasé à 1px avec indicateur hors ligne, résolu en retirant
   Planning/Communauté du mini-en-tête mobile). 198/198 tests verts. Détail complet ci-dessus.

2. **Accueil** (`Accueil.vue`) — **corrigé en deux temps** : premier passage limité à tort aux
   tests + état d'erreur (conclusion « déjà 100 % tokens donc rien à restructurer » jamais
   vérifiée contre la vraie maquette) ; réouvert après une question directe de l'utilisateur,
   maquette (`Main.dc.html`) enfin lue, écarts réels trouvés et recomposés (bandeau narratif,
   badge série en cercle pointillé, 2 nouveaux widgets réels — « Cette semaine » dérivé du
   heatmap déjà chargé, « Maturité des cartes » via `GET /stats/dashboard`, endpoint déjà
   fonctionnel côté backend mais jamais branché — tous les widgets préexistants conservés en
   dessous, inchangés). 41/41 tests écran verts, 276/276 tests web verts, `vue-tsc -b` sans
   erreur, vérification visuelle réelle clair/sombre × desktop/mobile faite par le contrôleur.
   Détail complet ci-dessous.

3. **Session de révision flashcards** (`StudyDeck.vue`) — vraie recomposition (aucune
   primitive/token utilisé auparavant, 6 couleurs Tailwind brutes + `dark:` redondants + 5
   classes arbitraires éliminés). 6 boutons de notation → 4 (mapping SM-2 0/3/4/5 tranché par
   l'utilisateur), raccourcis clavier 1-4 ajoutés, distinction vide/complet introduite, 2
   lacunes d'erreur corrigées (dont le premier câblage réel de `BaseToast`). 37 tests créés de
   zéro, 271/271 tests web verts, `vue-tsc -b` sans erreur. Détail complet ci-dessous.

4. **Éditeur de notes et mode Zen** (`NoteEdit.vue`) — chantier dédié `editeur-notes-notation-ia`
   (10 tâches) : 3 modales extraites (`NoteEditHelpModal`, `NoteInputModal`,
   `NoteEvaluationModal`), `NoteSidebar.vue` créée (Assistant IA à 3 méthodes conformes au
   canevas — Évaluation mixte / Feuille blanche / Feynman, sans « Générer un quiz » — + bouton
   Notation désactivé en attendant le backend de notation IA, hors périmètre), en-tête/barre
   d'outils/HTML généré retonés, fil d'ariane et état d'erreur de chargement ajoutés en mode
   lecture. 48 tests dédiés à `NoteEdit.vue` (+ 19 sur les 4 composants extraits), 508/508 tests
   web verts. Vérification visuelle réelle en environnement natif (Task 10) : 1 bug réel trouvé
   et corrigé (débordement horizontal de la barre d'actions du mode lecture à 375px). Détail
   complet ci-dessous.

### Écran 2 — Accueil (`web/src/views/Home/Accueil.vue`) — terminé

**Inventaire de l'existant** (lecture complète du fichier, 2026-08-25) : le fichier est déjà
composé à 100 % à partir des primitives (`PageContainer`, `PageHeader`, `BaseCard`,
`BaseButton`, `BaseEmptyState`, `StatCard`, `ListRow`) et de classes-token uniquement (aucune
valeur brute) — dernier commit de fond `a617bdc` (refonte pré-Direction A). Confirmé en
production locale (capture navigateur pendant la vérification de l'écran 1) : la palette
Direction A s'applique déjà entièrement via les tokens. **Aucun fichier de test n'existe
actuellement pour cette vue.**

Éléments d'interface / actions / appels API recensés :
- En-tête : titre « Accueil », sous-titre statique, bouton d'action « Continuer à réviser (N)
  » / « Tout est à jour » (désactivé si `totalDue === 0`) → `continueReview()` →
  `focusStore.startUnifiedReview()` puis navigation vers l'item.
- Carte « hero » : salutation + nom d'utilisateur, résumé du jour, série (streak).
- Carte « À réviser maintenant » : liste des items dus (`ListRow`, icône par type, badge « En
  retard », bouton « Réviser » → `studyItem(item)`, route selon type deck/note/assignment) ;
  état vide dédié déjà présent (« Tout est à jour ! »).
- Carte « Aujourd'hui » : 5 compteurs (À réviser, En retard, Flashcards, Feuilles blanches,
  Devoirs).
- Carte « Charge à venir (14j) » : histogramme de prévision, info-bulle par barre au survol,
  légende Bas/Moyen/Fort.
- Ligne de 4 `StatCard` (Cartes révisées, Taux de réussite, Temps d'étude, Decks actifs).
- Carte heatmap (365 jours, grille 7×52), info-bulle par cellule, légende Moins→Plus,
  compteur total de sessions.
- Carte « Objectif Hebdomadaire » : barre de progression + texte de statut.
- Carte « Rétention par matière » : liste par classeur (nom tronqué, % + tendance ▲/▼), état
  vide texte (« Aucun classeur créé. »).
- Appels API au montage (`onMounted`, en parallèle) : `focusStore.loadFocusData()`,
  `decksStore.fetchDecks()`, puis `GET /stats/overview`, `GET /stats/heatmap`,
  `GET /stats/sessions?from&to`.

**Comportement attendu, état par état** (skill `migration-ecran` étape 2) :
- **Chargement** : déjà présent (spinner + texte, remplace tout le contenu) — à couvrir par
  un test.
- **Vide** : déjà couvert section par section (file de révision → `BaseEmptyState` « Tout est
  à jour ! » ; rétention → texte « Aucun classeur créé. »). Heatmap/prévision toutes-zéro
  déjà gérées gracieusement par la logique de couleur/hauteur existante (pas de cas
  particulier à ajouter). À couvrir par des tests, pas de nouveau code.
- **Erreur** — **lacune réelle trouvée, à corriger** : `onMounted` avale actuellement toute
  erreur réseau dans un `try/catch` unique (`console.error` seul), sans état d'erreur ni
  retour utilisateur — l'écran affiche silencieusement des données par défaut/vides,
  indistinguable d'un vrai « rien à réviser ». Aucune maquette Claude Design ne couvre ce cas
  (confirmé : le canevas Direction A ne contient qu'une fiche par écran, pas de variante
  erreur). Décision de conception (réutilise la primitive déjà présente sur cet écran, aucun
  nouveau composant) : ajouter un ref `loadError`, et en cas d'échec remplacer tout le
  contenu par `BaseEmptyState` (icône alerte, titre « Le chargement a échoué », description «
  Vos données n'ont pas pu être récupérées. Vérifiez votre connexion et réessayez. », action «
  Réessayer » qui relance le chargement) — masquer aussi le bouton d'action de l'en-tête
  pendant l'erreur (dépend de données non fiables).
- **Dense** : déjà couvert par la composition existante (troncature sur les noms de classeur,
  défilement horizontal sur la heatmap `overflow-x-auto`). À couvrir par un test avec beaucoup
  d'items/classeurs, pas de nouveau code.
- **Hors ligne** : pas de traitement spécifique à cet écran — un échec réseau au montage tombe
  dans l'état erreur ci-dessus ; l'indicateur hors ligne global (coquille, écran 1) reste
  affiché indépendamment.

**Réalisé** (étapes 3-6 du subagent `migrateur-ecran`) : suite de tests rouge d'abord
(`web/tests/views/Home/Accueil.spec.ts`, 36 tests — un par élément/action/état recensé
ci-dessus), confirmée en échec pour la bonne raison contre le fichier non modifié (5 échecs,
tous et uniquement sur les tests d'état d'erreur qui n'existait pas encore ; 31/36 déjà verts
car l'écran héritait déjà des primitives/tokens). Implémentation ensuite : ref `loadError`,
capture dans le `catch` de `loadDashboard` (fonction extraite de `onMounted` pour être
réutilisable par le bouton « Réessayer »), remplacement de tout le contenu par
`BaseEmptyState` (icône `AlertCircle`, titre « Le chargement a échoué », description « Vos
données n'ont pas pu être récupérées. Vérifiez votre connexion et réessayez. », action «
Réessayer » → relance `loadDashboard`), bouton d'action de l'en-tête masqué pendant l'erreur
(`<template v-if="!loadError" #actions>`). 36/36 tests verts, 234/234 tests web verts au
global, `vue-tsc -b` sans erreur. Aucune primitive ni token modifié — réutilisation intégrale
de `BaseEmptyState`/`BaseButton`/`AlertCircle` (icône déjà utilisée pour ce même usage
ailleurs dans l'app, ex. `GroupDetail.vue`). Aucune fonctionnalité existante supprimée.

Écart relevé sans agir dessus (hors périmètre de ce cycle, à signaler) : `Accueil.vue` appelle
`api.get(...)` directement dans la vue (import de `services/api`) plutôt que de passer
exclusivement par un store/service, ce qui contrevient à la règle `web/CLAUDE.md` (« Appels
API uniquement dans stores/ et services/ »). C'est un écart préexistant (présent avant ce
cycle, hérité du fichier source), pas introduit ici ; je ne l'ai pas corrigé pour rester dans
le périmètre strict de la tâche (état d'erreur + tests), mais il mériterait sa propre
migration (extraire un `useAccueilStats` composable/service) dans un cycle dédié.

**Vérification du contrôleur** : suite complète et `vue-tsc -b` relancés indépendamment
(234/234, propre). Captures d'écran clair/sombre × desktop/mobile (étape 7) **non prises** —
l'environnement navigateur de cette session est resté instable tout du long (fenêtre bloquée
à pleine taille, renderer gelé à plusieurs reprises) ; à la place, vérification directe par
DOM sur navigateur réel (réseau bloqué via un patch temporaire d'`XMLHttpRequest`/`fetch`
côté page, retiré ensuite) : l'état erreur affiche bien « Le chargement a échoué » + la
description + le bouton « Réessayer », et le bouton d'action de l'en-tête est bien absent du
DOM pendant l'erreur. Rendu normal (chargé, sombre, desktop ~1485px) confirmé par capture
avant l'injection de la panne. Pas de vérification visuelle mobile (375px) ni clair pour cet
écran — écart à combler si l'environnement de capture se stabilise avant la fin de la phase.

**Écran 2 terminé** — étape 8 : cette section à jour, déjà committé par le subagent
(`c7a6093`).

3. **Session de révision flashcards** (`web/src/views/Decks/StudyDeck.vue`) — **terminé**.
   Vraie recomposition (aucune primitive/token utilisé auparavant) : 6 boutons de notation en
   couleurs Tailwind brutes remplacés par 4 boutons tokens (Encore/Difficile/Bien/Facile,
   mapping SM-2 0/3/4/5 tranché par l'utilisateur), raccourcis clavier 1-4 ajoutés, distinction
   vide/complet introduite, 2 lacunes d'erreur corrigées (chargement → `BaseEmptyState`,
   notation → premier câblage réel de `BaseToast`). 37 tests nouveaux, suite complète
   271/271, `vue-tsc -b` propre.

### Écran 3 — Session de révision flashcards (`web/src/views/Decks/StudyDeck.vue`) — terminé

**Inventaire de l'existant** (lecture complète du fichier, 2026-08-25) : contrairement à
l'écran 2, ce fichier **n'utilise aucune primitive** et **aucun token** pour ses éléments les
plus visibles — les 6 boutons de notation sont en couleurs Tailwind brutes
(`bg-rose-50`, `bg-amber-50`, `bg-indigo-50`, `bg-emerald-50`, doublées de variantes `dark:`
manuelles). Certains autres éléments utilisent déjà les tokens (`bg-primary`, `text-ink`,
`border-line`) mais avec des préfixes `dark:` redondants et incorrects hérités de l'ancien
système (les tokens se re-thématisent déjà seuls via les variables CSS — un `dark:bg-surface-soft`
posé sur un `bg-surface` de base mélange deux teintes différentes au lieu de simplement laisser
le token faire son travail). **Aucun fichier de test n'existe actuellement pour cette vue.**

Éléments d'interface / actions / appels API recensés :
- Fil d'ariane : bouton retour (libellé variable selon le mode d'entrée : « Retour au Focus »
  / « Retour au Planning » / « Retour aux decks ») → `goBack()` (route différente selon
  isFocusMode / advance=true / isBinderMode / mode simple) + pastille nom du deck/dossier.
- **4 modes d'entrée distincts, tous à préserver** (règle d'or) : mode deck simple
  (`/decks/:id/study`), mode dossier/binder (`StudyBinder`, cartes dues agrégées sur tous les
  decks d'un classeur), mode focus (`?focus=true`, vient de l'écran Accueil), mode révision
  anticipée (`?advance=true`, cartes vient de `planningStore.advanceReviewCards`). Chaque mode
  a sa propre source de données ET sa propre destination de retour/complétion.
- Chargement : spinner + « Préparation de la session... ».
- **Carte recto/verso (effet 3D)** : face recto (label, question, indice), face verso (label,
  réponse, indice), clic n'importe où sur la carte → `flipCard()`.
- Barre de progression : « Carte N sur Total » + « X% complété ».
- Contrôles de notation (visibles seulement carte retournée) → `rateCard(score)` →
  `decksStore.answerCard(deckId, cardId, score)` ; si `score < 3` la carte est replacée en fin
  de file (revue à nouveau dans la session) ; sinon on avance ; fin de file → état complet.
- État complet (`studyCards.length === 0` après chargement) : icône succès, titre, description,
  **1 des 3 CTA selon le mode** (focus → continuer les révisions/retour focus ; advance →
  retour planning ; sinon → retour liste).
- `watch` sur `route.params.id` : recharge la session en SPA sans démonter le composant
  (changement de deck/dossier sans revenir à `/decks` entre deux).

**Maquette Claude Design validée pour cet écran** (déjà construite et approuvée par
l'utilisateur, page 4 de l'artifact) — extraite et copiée dans le dépôt pour référence exacte
(non trackée par git, `.superpowers/` est gitignoré) :
`.superpowers/mockups/StudyDeckDesktop.html` et `StudyDeckMobile.html`. **Écart réel trouvé et
tranché par l'utilisateur (2026-08-25)** : la maquette montre **4 boutons de notation**
(Encore/Difficile/Bien/Facile) au lieu des 6 actuels (Oubli/Flou/Difficile/Correct/Bien/Facile,
score brut 0-5). Décision utilisateur : adopter les 4 boutons de la maquette, avec le mapping
suivant vers `calculate_sm2` (`backend/app/services/spaced_repetition.py`, cf. skill
`invariants-sm2`) :

| Bouton | Score envoyé | Branche SM-2 |
|---|---|---|
| Encore | 0 | échec (`score < 3`) — repetitions/interval reset |
| Difficile | 3 | réussite de justesse |
| Bien | 4 | réussite normale |
| Facile | 5 | réussite forte |

Aucun bouton ne peut plus produire un score de 1 ou 2 — ces valeurs restent valides côté
`calculate_sm2` (fonction pure, non modifiée) mais ne sont plus atteignables depuis cette UI.
La logique existante « `score < 3` → carte remise en fin de file » continue de fonctionner sans
changement : seul « Encore » (0) est `< 3`, donc c'est le seul bouton qui redemande la carte
dans la session — comportement inchangé, vérifié par le mapping choisi.

**Style exact des 4 boutons** (lu directement dans la maquette, tokens du projet entre
parenthèses — correspondance déjà documentée dans la skill `design-system` et les commentaires
de `style.css`) :
- **Encore** : contour 1.5px `--danger` (`border-danger`), fond transparent, texte `--danger`
  (`text-danger`), icône croix (X, `lucide` `X` ou équivalent), raccourci clavier « 1 ».
- **Difficile** : contour 1.5px `--highlight` (`border-accent`), fond transparent, texte
  `--highlight` (`text-accent`), icône flèche (`ArrowRight` ou équivalent bifurqué), raccourci
  « 2 ».
- **Bien** : rempli `--accent` (`bg-primary`), texte `--accent-ink` (`text-primary-ink`), pas de
  bordure, icône coche simple (`Check`), raccourci « 3 ».
- **Facile** : contour 1.5px `--success` (`border-success`), fond transparent, texte `--success`
  (`text-success`), icône double coche (`CheckCheck`), raccourci « 4 ».
- Les 4 boutons sont en grille (`grid-cols-4`), `min-h-11` (44px, cible tactile) déjà respecté
  dans la maquette mobile — à vérifier explicitement dans l'implémentation.
- **Raccourcis clavier 1-4 visibles dans la maquette (`<span class="kbd">`) — fonctionnalité
  additive à implémenter** : touches 1/2/3/4 déclenchent respectivement Encore/Difficile/
  Bien/Facile quand la carte est retournée (cohérent avec le raccourci `Ctrl/Cmd+K` déjà
  existant pour la recherche globale, même registre d'écouteur clavier au niveau composant).
- Libellés recto/verso alignés sur la maquette (cohérence avec le vocabulaire « fiche » de la
  Direction A, déjà utilisé ailleurs) : « Recto » / « Verso » (au lieu de « Question / Terme » /
  « Réponse / Définition »), indice recto « Cliquer sur la fiche pour retourner ».

**Comportement attendu, état par état** (skill `migration-ecran` étape 2) :
- **Chargement** : déjà présent (spinner + texte) — à couvrir par un test, restylé en tokens
  purs (retrait des `dark:` redondants).
- **Vide** — **distinction à introduire** : le code actuel confond « aucune carte due dès le
  départ » et « session terminée après révision » sous le même message « Session terminée ! 🎉 »,
  copie trompeuse si l'utilisateur n'a jamais rien révisé. Nouveau : si `totalCards === 0` dès
  le chargement initial (aucune carte n'a jamais été présentée), afficher un message distinct
  (« Rien à réviser ici pour le moment. »), sinon garder le message de complétion actuel.
  Les 3 CTA selon le mode restent inchangés dans les deux cas.
- **Erreur** — **deux lacunes réelles trouvées, à corriger** (même pattern que l'écran 2,
  cohérence d'app) :
  - Échec de `loadSession` (chargement initial) : actuellement avalé en `console.error` seul.
    Remplacer par `BaseEmptyState` (titre « Le chargement a échoué », description, action
    Réessayer → relance `loadSession`), même traitement que `Accueil.vue`.
  - Échec de `rateCard` (notation en cours de session) : actuellement avalé en `console.error`
    seul, la carte reste retournée sans aucun retour visuel — l'utilisateur ne sait pas que sa
    notation n'a pas été enregistrée. Utiliser `BaseToast` (variante erreur) — **premier
    câblage réel de cette primitive, prévu explicitivement en phase 4 par la skill
    `design-system`** (« présentationnel seul — pas de file d'attente globale — à câbler en
    phase 4 au premier besoin réel »). Message : « La notation n'a pas été enregistrée.
    Réessayez. » — la carte reste sur place, l'utilisateur peut recliquer un bouton de notation.
- **Dense** : texte recto/verso long — déjà en layout flexible (pas de troncature nécessaire,
  le contenu doit rester lisible en entier) ; à couvrir par un test avec texte long qui ne casse
  pas la mise en page. Beaucoup de cartes dans la session : déjà géré par la barre de
  progression générique (aucun cas particulier).
- **Hors ligne** : pas de traitement spécifique — un échec réseau tombe dans l'état erreur
  ci-dessus ; indicateur hors ligne global (coquille) indépendant.

**Réalisé** (étapes 3-6 du subagent `migrateur-ecran`) : suite de tests rouge d'abord
(`web/tests/views/Decks/StudyDeck.spec.ts`, 37 tests créés de zéro — le fichier n'avait aucun
test avant ce cycle), confirmée en échec pour la bonne raison contre le fichier non modifié (29
échecs sur les libellés « Recto »/« Verso », les 4 boutons de notation et leur mapping, le
raccourci clavier, la distinction vide/complet, les 2 états d'erreur et l'usage de `BaseButton`
sur les CTA — tous absents du code d'origine ; 8 tests déjà verts car les 4 modes d'entrée et
leurs 3 destinations de retour fonctionnaient déjà). Deux corrections de test apportées après
ce premier rouge (bugs de test, pas de composant) : `flushPromises()` manquant après un clic
déclenchant une navigation asynchrone, et une assertion erronée supposant que la face verso
n'existe pas dans le DOM tant que la carte n'est pas retournée (l'effet 3D affiche les deux
faces en permanence, seule une classe `rotate-y-180` bascule laquelle est visible — corrigée
pour vérifier cette classe plutôt que l'absence du texte).

Composition : recomposition complète depuis les primitives (`BaseCard`, `BaseButton`,
`BaseEmptyState`, `BaseToast`) et les tokens du design system — élimination des 6 couleurs
Tailwind brutes (`bg-rose-*`/`bg-amber-*`/`bg-indigo-*`/`bg-emerald-*` et leurs variantes
`dark:`), des préfixes `dark:` redondants sur des classes déjà tokenisées, et de 5 classes
Tailwind arbitraires (`min-h-[320px]` → `min-h-80`, `text-[10px]`/`text-[9px]` → `text-tiny`,
tokens déjà présents dans `tailwind.config.js` sans qu'aucun n'ait eu besoin d'être ajouté).
Les 4 boutons de notation sont composés directement avec les tokens (`border-danger`/
`text-danger`, `border-accent`/`text-accent`, `bg-primary`/`text-primary-ink`,
`border-success`/`text-success`, `rounded-btn-primary`, `min-h-11`) plutôt qu'avec `BaseButton` :
la primitive ne propose pas de disposition icône-au-dessus-du-libellé avec repère clavier
sous-jacent (layout horizontal uniquement) — jugé hors de son périmètre actuel plutôt qu'un
manque à corriger dans ce cycle, signalé au contrôleur. Premier câblage réel de `BaseToast`
(présentationnel, sans file d'attente globale, conforme à ce qui était prévu dans la skill
`design-system`). Icônes `@lucide/vue` : `X`, `ArrowRight`, `Check`, `CheckCheck` (notation),
`Inbox` (état « jamais eu de carte », nouvelle), `AlertCircle`/`Sparkles`/`ChevronLeft`
(déjà utilisées ailleurs dans l'app pour les mêmes usages). Animation d'entrée locale
(`@keyframes fadeIn` dupliquée) remplacée par le token d'animation existant `animate-fade-up`
(déjà défini dans `tailwind.config.js`, non utilisé par cet écran auparavant) — suppression
d'une redondance plutôt qu'ajout.

Copie : « Recto »/« Verso » remplacent « Question / Terme »/« Réponse / Définition », indice
recto aligné sur la maquette (« Cliquer sur la fiche pour retourner »). Nouveau texte de l'état
« jamais eu de carte » : « Rien à réviser ici pour le moment. » + « Aucune carte n'est due pour
le moment dans ce deck. » — distinct du texte de complétion existant (« Session terminée ! 🎉 »),
inchangé. Les 3 CTA de fin de session (focus/advance/normal) conservés à l'identique, y compris
l'aiguillage préexistant du mode dossier vers « Retour à la liste » plutôt que vers le classeur
d'origine (comportement déjà présent avant ce cycle, non modifié — hors périmètre).

37/37 tests de l'écran verts, **271/271 tests web verts** au global, `vue-tsc -b` sans erreur.
Aucune primitive ni token modifié. Aucune fonctionnalité existante supprimée : les 4 modes
d'entrée et leurs sources/destinations respectives sont couverts chacun par un test dédié.

**Écarts relevés sans agir dessus (hors périmètre de ce cycle, signalés)** :
- `StudyDeck.vue` appelle `api.get(...)` directement (mode dossier) plutôt que de passer par un
  store/service dédié — écart préexistant (même famille que celui déjà signalé sur
  `Accueil.vue`), non corrigé ici sur consigne explicite du contrôleur.
- `eslint.config.js` ne déclare aucun environnement navigateur (`window`, `document`, `console`,
  `KeyboardEvent`, `localStorage`, `navigator` sont rapportés `no-undef`) — gap de configuration
  projet préexistant, confirmé identique sur `AppLayout.vue` déjà mergé (18 erreurs strictement
  analogues à l'exécution directe d'ESLint), donc non introduit par ce cycle ; non corrigé, hors
  périmètre d'une migration d'un seul écran.
- Le hook `raw_value_guard` signale `perspective: 1000px` et `transform: translateY(20px)` dans
  le `<style scoped>` (effet de retournement 3D et transition d'entrée) : valeurs déjà présentes
  à l'identique dans le fichier d'origine, structurelles (dimensions de transformation CSS, pas
  des couleurs/espacements de design), non modifiables via une classe Tailwind sans passer par
  une syntaxe arbitraire tout aussi proscrite — laissées telles quelles.
- Aucun token manquant : la palette de la maquette (`--danger`/`--highlight`/`--success`/
  `--accent`/`--accent-ink`) correspond exactement aux tokens `danger`/`accent`/`success`/
  `primary`/`primary-ink` déjà définis dans `web/src/style.css` (confirmé par lecture directe,
  pas par supposition) — rien à remonter au `designer-ui` sur ce point.

**Vérification du contrôleur** : suite complète et `vue-tsc -b` relancés indépendamment
(271/271, propre) ; diff de `StudyDeck.vue` relu ligne à ligne contre la spec écrite plus haut
(mapping de score, classes de tokens, API réelle de `BaseToast` vérifiée dans son fichier
source) — conforme. **Vérification bout-en-bout sur navigateur réel** (deck + carte créés via
l'API pour ce test, supprimés ensuite) : capture confirmant les 4 boutons rendus exactement
comme spécifié (Encore contour brique, Difficile contour ocre, Bien rempli indigo, Facile
contour sauge, raccourcis 1-4 visibles) ; clic sur « Bien » → carte notée, session complétée
(« Session terminée ! 🎉 », CTA « Retour à la liste ») ; **score vérifié jusqu'au bout de la
chaîne réelle** via l'API backend après coup : `repetitions: 0→1`, `interval: 1`,
`ease_factor` inchangé à 2.5 — exactement la sortie attendue de `calculate_sm2` pour un score 4
sur une carte neuve, confirmant que le mapping Bien→4 arrive intact jusqu'à l'algorithme SM-2
réel. Pas de vérification visuelle mobile (375px) ni du thème sombre pour cet écran —
environnement de capture resté instable (mêmes limites que l'écran 2), écart cumulé à combler
si l'environnement se stabilise avant la fin de la phase.

**Écran 3 terminé** — étape 8 : cette section à jour, déjà committé (`0766c40`).

## Réouverture Écran 2 — Accueil : recomposition selon la maquette réelle (2026-08-25)

**Défaut de process trouvé (question directe de l'utilisateur)** : lors du premier passage sur
l'écran 2, j'ai conclu « aucune restructuration nécessaire » sur la seule base que le fichier
utilisait déjà primitives/tokens — sans jamais ouvrir la maquette Claude Design réelle de cet
écran (`Main.dc.html`, page « Coquille & Accueil » de l'artifact). C'est la même erreur de
raisonnement qu'évitée de justesse sur l'écran 3 (« utilise des tokens » ne dit rien de
l'organisation), appliquée à tort ici. Extraction et lecture de `Main.dc.html` faite a
posteriori (copiée dans `.superpowers/mockups/Main.html`, gitignore) : révèle une organisation
réellement différente, pas seulement une question de couleur.

**Écarts réels trouvés** (maquette vs `Accueil.vue` actuel) :
- Bandeau du jour : phrase narrative + badge série en cercle pointillé (maquette) vs carte hero
  générique + badge flamme (actuel).
- « À réviser maintenant » : regroupement par **deck/matière** avec badge AUJOURD'HUI/DEMAIN et
  « dernier passage il y a N jours » (maquette) vs liste par **item individuel** dû aujourd'hui
  (actuel, `focusStore.items` — inclut aussi notes/devoirs, pas seulement des decks).
- 3 widgets de la maquette absents du code : « Cette semaine » (7 barres), « Maturité des
  cartes » (Nouvelles/En cours/Maîtrisées), « Activité récente » (timeline horodatée).
- 6 widgets réels du code absents de la maquette : compteurs « Aujourd'hui » (5 lignes), «
  Charge à venir » (14j), 4 `StatCard`, heatmap 365j, « Objectif Hebdomadaire », « Rétention par
  matière » SM-2.

**Vérification backend faite avant de proposer un plan** (pas d'hypothèse) :
- `GET /stats/dashboard` (`backend/app/services/stats_service.py:161`, schéma
  `DashboardStatsResponse`) existe, est déjà fonctionnel, **jamais appelé par `Accueil.vue`** —
  renvoie `maturity_distribution: {learning, young, mature}` (classification par `interval` de
  carte : `<1` apprentissage, `1-21` jeune, `>21` mature), soit exactement le widget « Maturité
  des cartes » de la maquette avec de vraies données. Seul appelant actuel : la vue **orpheline**
  `web/src/views/Dashboard/Dashboard.vue:511` (non routée, cf. phase 3 — à supprimer en phase 6,
  pas dans ce cycle), qui contient déjà un calcul de pourcentages réutilisable comme référence
  (`Dashboard.vue:431-449`, `maturityLearningPercent`/`maturityYoungPercent`/
  `maturityMaturePercent`).
- « Cette semaine » (7 barres) : dérivable des données de heatmap déjà chargées par
  `Accueil.vue` (`GET /stats/heatmap`, déjà appelé) — 7 derniers jours du dictionnaire existant,
  **aucun nouvel appel réseau**.
- « Activité récente » (timeline d'événements) : **aucune fonctionnalité backend équivalente**
  (`grep` confirmé : seul un flux d'activité de **classe/groupe** existe
  `group_service.py`/`add_group_activity`, rien de personnel). Comme « À faire » (checklist,
  également sans backend), ces deux éléments de la maquette sont illustratifs, pas une spec
  fonctionnelle — non implémentés.

**Décisions utilisateur (2026-08-25)** :
1. Recomposer selon la maquette, adapté aux vraies données (pas une copie littérale).
2. Garder tous les widgets réels actuels absents de la maquette, **en plus** de la structure de
   la maquette (rien ne disparaît) — ils viennent après la section réorganisée, inchangés.

**Plan de recomposition retenu** :
- En-tête : titre + sous-titre dynamique « Bon retour, {username}. » (remplace le sous-titre
  statique actuel) + CTA action inchangé dans sa logique (`continueReview`, désactivé si
  `totalDue === 0`), copie rapprochée du format maquette (« Continuer à réviser · N cartes »).
- Bandeau du jour : **copie `todaySummary` existante conservée telle quelle** (déjà testée,
  déjà correcte — pas de raison de la ré-écrire) ; conteneur restylé façon maquette (bordure
  d'accent, ton narratif) ; badge série passe de la pastille flamme à un badge cercle pointillé
  (même valeur `streak`, traitement visuel de la maquette).
- Grille principale 2/1 colonnes (comme la maquette, breakpoint `lg` déjà utilisé ailleurs sur
  cet écran) :
  - Gauche : **contenu de « À réviser maintenant » inchangé** (tous les items réels, decks ET
    notes ET devoirs — ne pas régresser vers un regroupement par deck qui perdrait les
    notes/devoirs), habillage visuel de la maquette (barre d'accent colorée par ligne, badge
    d'échéance). Sans donnée « dû demain » disponible dans `focusStore.items`, ne pas inventer
    de badge DEMAIN : tout item non en retard de cette liste est par construction dû aujourd'hui
    (l'API ne retourne que les items dus aujourd'hui) → badge « AUJOURD'HUI » par défaut, «
    EN RETARD » si `is_late` (inchangé dans le fond, juste dans le style).
  - Droite : « Cette semaine » (nouveau, dérivé du heatmap déjà chargé) + « Maturité des cartes »
    (nouveau, `GET /stats/dashboard`, nouvel appel réseau ajouté au `Promise.all` du montage).
- **Après** la grille principale, dans l'ordre déjà existant, inchangés : compteurs
  « Aujourd'hui », « Charge à venir (14j) », 4 `StatCard`, heatmap 365j, « Objectif
  Hebdomadaire », « Rétention par matière ».
- « À faire » et « Activité récente » : non implémentés (pas de backend, cf. ci-dessus).

**États à revérifier** (le cycle `migration-ecran` reste actif, ne pas juste patcher) : le
nouvel appel `GET /stats/dashboard` doit être couvert par les états déjà définis à l'écran 2
(chargement/erreur groupés avec les autres appels existants, pas un état séparé).

**Prochaine action** : dispatcher au subagent `migrateur-ecran` pour l'implémentation (tests
d'abord pour la nouvelle structure et le nouvel appel réseau, puis composition, puis refactor à
tests verts).

**Réalisé** (étapes 3-6 du subagent `migrateur-ecran`, 2026-08-25) : suite de tests étendue
d'abord (`web/tests/views/Home/Accueil.spec.ts`, 36 → 41 tests), rouge confirmé pour la bonne
raison (10 échecs contre le fichier non modifié : sous-titre statique au lieu du sous-titre
dynamique, copie CTA à l'ancien format `(N)`, absence du badge cercle pointillé, absence du
badge d'échéance par défaut « Aujourd'hui » sur les items non en retard, absence des deux
nouveaux widgets et de l'appel `/stats/dashboard` ; 31 tests déjà verts confirmant que le
contenu inchangé — todaySummary, navigation, empty state, compteurs, forecast, StatCard,
heatmap, objectif hebdo, rétention — n'était pas cassé par la réécriture des tests). Une
correction de test après ce premier rouge (bug de test, pas de composant) : le mock `api.get`
étant partagé (`vi.hoisted`) et son historique d'appels non réinitialisé entre tests (seule son
implémentation change), l'assertion sur le nombre d'appels à `/stats/heatmap` comptait tous les
tests précédents du fichier — corrigée pour mesurer le delta propre au montage testé plutôt que
le compte absolu.

Composition, uniquement depuis les primitives/tokens existants :
- En-tête : sous-titre `greeting` devenu `` `Bon retour, ${authStore.user?.username}.` `` ; CTA
  reformaté `` `Continuer à réviser · ${totalDue} cartes` `` (logique de désactivation
  inchangée).
- Bandeau du jour : `todaySummary` conservé verbatim ; conteneur restylé `border-l-4
  border-l-accent` (accent = highlight maquette, mapping déjà établi à l'écran 3) ; le heading
  « Prêt·e à apprendre, {username} ? 👋 » supprimé de cette carte — son rôle de salutation
  personnalisée est repris par le nouveau sous-titre de l'en-tête, pas dupliqué. Badge série :
  pastille flamme remplacée par un cercle `w-24 h-24 rounded-full border-2 border-dashed
  border-accent` tourné `-rotate-6`, nombre en `font-mono text-primary`, libellé visuel
  compacté à « jour(s) » (au lieu de « jour(s) de suite », qui ne tient pas dans un badge de
  cette taille) — le texte complet accessible (« Série de N jour(s) de suite ») est conservé
  via un `<span class="sr-only">` pour ne perdre aucune information aux lecteurs d'écran.
  Aucun token manquant : `border-dashed`/`rounded-full`/`-rotate-6` sont des utilitaires
  Tailwind natifs (pas des valeurs brutes), la couleur vient du token `accent` existant — rien
  à remonter au `designer-ui` sur ce badge.
- Grille 2/1 : à gauche, contenu de `focusStore.items` strictement inchangé (mêmes items, même
  navigation `studyItem`, même distinction icône/couleur par `is_late`) ; habillage ajouté :
  barre d'accent `w-1 self-stretch` (`bg-danger` si en retard, `bg-accent` sinon) dans le slot
  `leading` de `ListRow`, et le badge texte brut (`text-[9px]`, valeur arbitraire préexistante)
  remplacé par la primitive `BaseBadge` (`variant="danger"|"accent"`, `size="sm"`) — supprime
  au passage une valeur Tailwind arbitraire au lieu d'en ajouter une. Badge toujours présent
  (texte « En retard » ou « Aujourd'hui », capitalisation visuelle via classe `uppercase`
  plutôt que texte figé en capitales, cohérent avec la convention déjà en place dans ce fichier
  pour l'accessibilité — un lecteur d'écran épelle moins bien un texte tout capitales). Pas de
  badge « DEMAIN » : absent des données `focusStore.items`, non inventé.
  À droite : nouveau widget « Cette semaine » (7 barres `bg-primary` de hauteur en `%`, dérivées
  de `heatmapData` déjà chargé via `getStartAndEndOfWeek()` réutilisé tel quel, aucun nouvel
  appel réseau) et nouveau widget « Maturité des cartes » (barre empilée
  `bg-line`/`bg-accent`/`bg-primary` + 3 pourcentages, nouvelle interface locale
  `MaturityDistribution`, nouvel appel `api.get<{ maturity_distribution: MaturityDistribution }>
  ('/stats/dashboard')` ajouté au `Promise.all` existant, même pattern d'appel direct que les
  appels `/stats/*` déjà présents dans ce fichier — écart d'architecture préexistant non corrigé
  sur consigne explicite).
- Après la grille : les cartes « Aujourd'hui » (compteurs) et « Charge à venir (14j) » sortent
  de l'ancienne grille 3 colonnes pour devenir une grille 2 colonnes séparée juste en dessous —
  seul le conteneur change, le contenu de chaque carte (classes, structure, valeurs calculées)
  est resté strictement identique caractère pour caractère. Les 4 `StatCard`, la heatmap 365j,
  « Objectif Hebdomadaire » et « Rétention par matière » n'ont subi aucune modification (aucun
  `Edit` appliqué à ces blocs).
- « À faire » et « Activité récente » : non implémentés, conforme à la décision actée plus haut.

Un écart mineur assumé sans instruction explicite : la légende « N session(s) cette semaine »
du widget « Cette semaine » (au lieu de « N cartes révisées » dans la maquette littérale) — la
heatmap ne fournit que des compteurs de *sessions* par jour, pas de cartes révisées par jour ;
inventer une correspondance directe session→carte aurait été une donnée fabriquée. Choix : nom
de métrique honnête plutôt que copie littérale de la maquette, cohérent avec le vocabulaire déjà
utilisé par `getTooltipText` (« N session(s) ») dans ce même fichier.

41/41 tests de l'écran verts, **276/276 tests web verts** au global (271 avant ce cycle + 5 nets
: 10 tests nouveaux/réécrits sur des comportements changés, 5 tests obsolètes retirés — ancienne
salutation dans la carte hero et ancien badge « En retard uniquement » fusionnés dans les
nouvelles assertions), `vue-tsc -b` propre (aucune erreur). Aucun token ni primitive modifié.
Aucune fonctionnalité existante supprimée : tous les widgets déjà présents avant ce cycle
(compteurs, charge à venir, StatCard, heatmap, objectif hebdo, rétention, et le fond complet de
« À réviser maintenant » avec decks/notes/devoirs) restent accessibles avec le même contenu.

Captures d'écran (étape 7) **non prises** — hors périmètre de ce cycle sur consigne explicite du
contrôleur (« pas de captures d'écran à ce stade, je m'en charge, contrôleur, à la fin »).

**Vérification du contrôleur** : suite complète et `vue-tsc -b` relancés indépendamment
(276/276, propre) ; diff de `Accueil.vue` relu ligne à ligne contre le plan — conforme, rien
en dessous de la grille n'a bougé. **Correctif appliqué** : la copie du CTA (« Continuer à
réviser · N cartes ») ne gérait pas le singulier (« 1 cartes ») — corrigé
(`carte${totalDue > 1 ? 's' : ''}`), 41/41 toujours verts après coup.

**Vérification visuelle réelle** (navigateur stable maintenant, renderer non gelé) : capture
clair et sombre en desktop (~1500px) + clair et sombre en mobile (375px, technique iframe,
`resize_window` de la fenêtre réelle toujours bloqué en plein écran dans cet environnement) —
**les 4 combinaisons confirmées propres**. Vérifié avec un deck+carte réels créés via l'API
pour le test (supprimés ensuite) : le badge d'échéance, la barre d'accent par ligne et le CTA
d'en-tête (« Continuer à réviser · 1 carte ») s'affichent correctement avec de vraies données
dues. Widget « Maturité des cartes » vérifié à 0 % avec ce jeu de données (le calcul et
l'appel réseau sont corrects ; une nouvelle carte fraîchement créée n'apparaît pas
immédiatement dans le pourcentage à cause du cache serveur 5 min déjà en place sur
`GET /stats/dashboard` — comportement préexistant, identique sur `/stats/heatmap` et
`/stats/overview`, pas une régression de ce cycle).

**Écran 2 (réouverture) terminé** — étape 8 : cette section à jour, commit à suivre.

## Re-vérification écrans 1 et 3 contre les vraies maquettes (2026-08-25)

Sur demande explicite de l'utilisateur (« refais le même travail sur toutes les pages déjà
faites pour être sûr que c'est bon ») : appliquer la même rigueur que la réouverture de l'écran 2
(ouvrir le vrai fichier `.dc.html`, pas le spec écrit ni la seule présence de tokens) aux écrans
1 et 3. L'écran 2 avait déjà eu sa vraie comparaison de maquette lors de sa réouverture
ci-dessus — pas de nouvelle action dessus. L'écran 3 avait déjà été comparé à ses vrais fichiers
maquette (`StudyDeckDesktop.dc.html`/`StudyDeckMobile.dc.html`) lors de son cycle initial — la
lacune restante n'était pas la comparaison de structure, mais la vérification visuelle mobile/
sombre jamais faite (signalée comme écart à combler « si l'environnement se stabilise »).

**Écran 1 (Coquille, `AppLayout.vue`) — comparaison contre la vraie maquette `AppShell.dc.html`**
(jamais ouverte auparavant ; la décision de nav avait été basée sur `docs/design-system-
direction-a-spec.md`, un document dérivé, pas le fichier `.dc.html` lui-même). Extraction via
la procédure documentée (artifact → `appifact-doc` JSON → fichier). Comparaison élément par
élément :
- Nav 4 pastilles (Accueil/Bibliothèque/Réviser/Classes) vs 5 + Communauté en icône du code :
  écart déjà identifié et tranché explicitement par l'utilisateur le 2026-08-24 (cf. plus haut,
  section écran 1 originale) — confirmé cohérent avec la maquette, pas un nouvel écart.
- Couleur de la pastille active et de l'avatar (indigo plein `--accent` maquette = token
  `primary` du projet, pas `accent` — mapping confirmé via la mémoire d'extraction) : cohérent
  avec le code (`bg-primary`/`text-primary-ink`).
- Avatar desktop : maquette = cercle plein indigo/blanc ; code = cercle `bg-primary-soft
  text-primary` (fond teinté, texte coloré). Vérifié que ce traitement « soft » est la
  convention établie dans tout le projet (44 fichiers l'utilisent pour badges/avatars/chips) —
  jugé cohérent avec le reste de l'app, pas une régression à corriger (même famille de décision
  que la pastille active le 2026-08-24).
- Avatar dans le mini-en-tête mobile : présent dans la maquette (à côté de la bascule thème),
  absent du code (profil accessible uniquement via le tiroir hamburger). Non ajouté : l'en-tête
  mobile a déjà été signalé une fois pour débordement réel (titre tombé à 1px, cf. plus haut,
  tour de correction 2) ; ajouter un élément de plus dans cette zone déjà dense referait courir
  ce risque pour un gain cosmétique mineur (le profil reste accessible via le tiroir). Écart
  assumé, pas corrigé.
- **2 icônes réellement fausses trouvées et corrigées** : « Bibliothèque » utilisait
  `FolderClosed` (dossier) au lieu du livre ouvert de la maquette → `BookOpen` ; « Classes »
  utilisait `GraduationCap` (chapeau de diplômé) au lieu du pictogramme deux-personnes de la
  maquette → `Users`. Les deux icônes existent dans `@lucide/vue` (vérifié). Aucun test
  n'existait sur l'identité des icônes avant ce cycle — 3 tests ajoutés d'abord (rouge confirmé
  contre le code non modifié), puis le correctif (vert). 279/279 → 280/280 tests verts au fil du
  cycle (voir plus bas pour le compte final), `vue-tsc -b` propre.

**Vérification visuelle réelle, écran 1** (desktop clair/sombre déjà faits lors des tours de
correction précédents, jamais confirmés en dernière instance après le fix round 2 — capture
finale manquante signalée comme « jugée à faible risque » ; mobile 375px jamais fait du tout) :
les 4 combinaisons clair/sombre × desktop/mobile capturées cette fois (technique iframe de
largeur contrôlée, `resize_window` de la fenêtre réelle toujours plafonné dans cet
environnement). **Aucun chevauchement, nouvelles icônes rendues correctement dans les 4
combinaisons.** Referme définitivement l'écart de capture reporté au fix round 1/2.

**Écran 3 (StudyDeck) — vérification visuelle mobile/sombre jamais faite, comblée maintenant.**
En la faisant, **bug réel trouvé et confirmé par interaction, pas seulement visuel** : sur mobile
(375px), le widget flottant `PomodoroTimer` (position fixe `bottom-28 right-6`, cf.
`PomodoroTimer.vue`) chevauche entièrement le 4e bouton de notation (« Facile ») dans la grille
`grid-cols-4` de l'écran de session. Vérifié par clic réel à l'emplacement du bouton : ouvre le
minuteur Pomodoro au lieu de noter la carte — le bouton est fonctionnellement inatteignable, pas
seulement visuellement gêné. Confirmé systématique (pas un cas limite) : la hauteur de contenu
de cet écran est quasi constante (1 seule carte affichée à la fois + fil d'ariane + grille de
boutons), donc la collision se produit sur toute session, indépendamment de la taille du deck.

**Correctif** (TDD : test rouge d'abord dans `AppLayout.spec.ts`, route `StudyDeck` ajoutée au
routeur de test, puis le code) : `PomodoroTimer` masqué pendant une session de révision
(`v-if="!$route.meta.immersive && route.name !== 'StudyDeck'"` dans `AppLayout.vue`) — un
minuteur flottant superposé à la zone de notation active n'est de toute façon pas souhaitable
pendant la notation, indépendamment de la collision technique. Le minuteur reste disponible sur
tous les autres écrans, y compris juste avant/après une session.

**Vérification bout-en-bout après correctif** : bouton « Facile » de nouveau cliquable à 375px
(clair et sombre), session complétée normalement. Score vérifié jusqu'au bout de la chaîne
réelle via l'API backend (deck + carte de test créés puis supprimés) :
`repetitions: 0→1`, `interval: 0→1`, `ease_factor: 2.5→2.6` — sortie exacte attendue de
`calculate_sm2` pour un score 5 (Facile) sur une carte neuve.

**Suite complète et types** : 280/280 tests web verts (279 avant ce cycle + 3 tests d'icônes
nouveaux + 1 test Pomodoro/StudyDeck nouveau − 3 tests obsolètes n'existaient pas, net +1 déjà
compté), `vue-tsc -b` propre. Aucun token ni primitive modifié.

**Écran 2 (Accueil)** : pas de nouvelle vérification nécessaire, déjà faite rigoureusement à sa
réouverture ci-dessus (comparaison structurelle complète contre `Main.dc.html`, vérification
visuelle 4 combinaisons déjà confirmée).

**Prochaine action (avant écran 4)** : écran 4 — Éditeur de notes et mode Zen (`NoteEdit.vue`),
premier écran non encore migré à ce moment, cycle complet `migration-ecran` (inventaire,
comparaison à `NoteEdit.dc.html`, états, tests, composition). Voir sa clôture ci-dessous.

## Écran 4 — Éditeur de notes et mode Zen (`NoteEdit.vue`) — terminé

Exécuté comme chantier dédié `workflow/editeur-notes-notation-ia/` (10 tâches TDD,
`docs/superpowers/plans/2026-08-30-editeur-notes-redesign.md`), plutôt qu'en ligne directe dans
ce fichier comme les écrans 1-3 — cf. `workflow/editeur-notes-notation-ia/{CONTEXT,PLAN,
JOURNAL}.md` pour le détail tâche par tâche (extraction des 3 modales, `NoteSidebar.vue`,
retonage en-tête/barre d'outils/HTML généré, fil d'ariane + état d'erreur de chargement,
suite de tests comportementale). Cette section documente uniquement la clôture (Tâche 10) :
vérification visuelle réelle en environnement natif, dernier filet avant la revue de branche.

**Environnement natif monté (pas de Docker, conforme au précédent StudyDeck/Accueil)** — deux
vrais accrocs d'environnement trouvés et contournés, tous deux propres à cette machine (Windows
**ARM64**), aucun n'a touché de code applicatif :
- `psycopg2-binary` et `cryptography==42.0.7` (pin du `requirements.txt`) n'ont pas de wheel
  ARM64 Windows et échouent à la compilation (pas de `pg_config`/Rust sur la machine). L'app ne
  nécessite que SQLite en dev, et PyJWT retombe proprement sans `cryptography`
  (`except ModuleNotFoundError` dans `jwt/utils.py`, HS256 ne le nécessite pas) : `psycopg2` non
  installé, `cryptography` installé en 46.0.3 (wheel ARM64 existant) puis retiré à nouveau car
  bloqué au chargement par la stratégie de contrôle d'application Windows de cette machine
  (Code Integrity/WDAC, `UsermodeCodeIntegrityPolicyEnforcementStatus=2` confirmé via
  `Get-CimInstance Win32_DeviceGuard`) — fallback PyJWT sans crypto utilisé à la place.
- `flask run` chargeait silencieusement `DATABASE_URL=postgresql://...@db:5432/...` depuis le
  `.env` racine du dépôt (orienté Docker Compose, un niveau au-dessus de la worktree) via
  l'auto-chargement `.env`/`.flaskenv` du CLI Flask (absent d'un import direct de `wsgi.py` ou de
  `ScriptInfo.load_app()` — comportement propre à la commande `run`). Contourné avec
  `FLASK_SKIP_DOTENV=1` au lancement, aucune modification de fichier.

Backend servi en SQLite (migrations auto-appliquées, cache Redis en repli mémoire — avertissement
attendu), frontend Vite servi normalement. Données de test réelles créées **via l'app elle-même**
(pas de fixture) : inscription UI, un classeur (« Chimie Organique »), deux notes (une note
principale exerçant `{{trou::}}`/`{{qcm::}}`/`{{vf::}}`/`{{ordre::}}`/`{{assoc::}}` + LaTeX
inline, une seconde note pour vérifier le lien entre notes).

**Outillage de vérification** : l'extension Chrome (`claude-in-chrome`) n'a pas pu être utilisée
— aucune installation de Chrome présente sur cette machine (confirmé : ni
`Program Files\Google\Chrome`, ni `AppData\Local\Google\Chrome`, ni dans le PATH). Sur arbitrage
du contrôleur, bascule vers **Playwright piloté directement** (dépendance déjà présente,
Chromium déjà téléchargé localement, `web/playwright.config.ts`) via un script Node jetable
(non commité, hors de la suite `tests-e2e` qui mocke l'API) pointant le vrai backend/frontend
ci-dessus — même principe que la « technique iframe » utilisée aux écrans 1-3 pour contourner un
`resize_window` plafonné, en plus direct.

**Checklist vérifiée en direct, chaque item avec capture d'écran réelle** :
- Sidebar Assistant IA : exactement 3 méthodes (Évaluation mixte / Méthode de la feuille
  blanche / Méthode Feynman), pas de « Générer un quiz » — confirmé par lecture DOM + capture.
- Bouton Notation : visible, `disabled`, tooltip
  « Bientôt disponible : nécessite le backend de notation IA (non encore livré). » — confirmé.
- Fil d'ariane : « BIBLIOTHÈQUE / CHIMIE ORGANIQUE / NOTES » (nom du classeur réel) — confirmé,
  visible uniquement en mode lecture comme prévu par la maquette.
- Méthode Feynman : navigation réelle depuis la sidebar vers `/notes/:id/feynman`, page rendue
  avec le vrai titre de la note et un textarea fonctionnel — aucune régression.
- `NoteQuiz.vue` : accessible par URL directe (`/notes/:id/quiz`), rendu complet du générateur
  de QCM IA (curseur nombre de questions, bouton Gemini) bien que retiré du panneau — conforme.
- Mode édition : frappe réelle dans le textarea + bouton « Gras » de la barre flottante
  vérifiés bout en bout (sélection encadrée de `**...**` dans le contenu réel), autosave
  fonctionnel — aucune régression fonctionnelle, seul le visuel a changé (tâches 6-7).
- Export PDF : modale d'options (styles Modern Pro/Académique/Éco Minimal, taille d'écriture,
  éléments du document) rendue et fonctionnelle — aucune régression.
- Lien entre notes : lien ajouté depuis le tiroir Contexte/Liens vers une seconde note réelle,
  badge visible en mode lecture, clic → navigation réelle vers la note liée — aucune régression.
- Révision Active : bascule fonctionnelle, `{{trou::}}` masqué puis révélé au clic (« glucose »),
  QCM/Vrai-Faux/Ordre/Association rendus avec leurs contrôles interactifs — aucune régression.
- Responsive 375px/1440px × clair/sombre, mode édition **et** mode lecture (8 captures) + sidebar
  (visible dans les captures du mode lecture) : les 8 combinaisons confirmées propres après le
  correctif ci-dessous (0 erreur console sur l'ensemble des scénarios testés).

**1 bug réel trouvé et corrigé (TDD)** — même discipline que le bug PomodoroTimer/StudyDeck
ci-dessus : la rangée d'actions du mode lecture (« Retour aux notes » / bascule Lecture-Révision
Active à gauche, « Modifier la fiche » / « Guide » / « Exporter en PDF » à droite,
`NoteEdit.vue` ligne ~479) n'avait pas `flex-wrap`, contrairement à la rangée équivalente du mode
édition (ligne ~106, qui l'a déjà). Mesure DOM réelle à 375px (pas seulement visuelle) : les
boutons « Guide » (x=416) et « Exporter en PDF » (x=525) se retrouvaient positionnés hors du
viewport (375px de large), et donc **inatteignables** — sans que la page ne scrolle
horizontalement (`document.scrollWidth === 375`, donc clippés silencieusement plutôt que
scrollables). Reproduit par capture d'écran (texte « Modifier la fi[che] » tronqué pile au bord)
puis confirmé par mesure de `getBoundingClientRect()`. Correctif TDD : test rouge d'abord
(`web/tests/views/Notes/NoteEdit.spec.ts`, vérifie que la classe `flex-wrap` est présente sur la
rangée), confirmé en échec pour la bonne raison contre le fichier non modifié, puis `flex-wrap`
ajouté à la rangée et à ses deux groupes enfants (même pattern que la rangée du mode édition) —
vert. Reverifié en navigateur réel après correctif : les 6 boutons/contrôles de la rangée
tiennent tous dans 375px de large (x max ≈ 305), répartis sur 3 lignes, aucun débordement.

**Suite finale** : 508/508 tests web verts (507 avant Task 10 + 1 nouveau test du correctif),
`vue-tsc -b` sans erreur, `eslint` propre sur le diff (les ~77 erreurs `no-undef`/`no-explicit-
any` restantes dans `NoteEdit.vue` sont préexistantes — gap de configuration ESLint déjà
documenté à l'écran 3, aucune sur les lignes touchées par ce correctif).

**Concern signalé, non corrigé (architectural, hors périmètre)** : `NoteResponse`
(`backend/app/schemas/note_schema.py`) ne renvoie jamais de champ `flashcards` — confirmé par
lecture de `note_service.get_note`/`update_note` et de `app/api/v1/notes.py`. Le code de
`NoteEdit.vue` qui lit `(note as any).flashcards` pour lier un `{{trou::}}` à une vraie
flashcard (déclenchant la modale d'évaluation SM-2 différée après révélation) ne peut donc
jamais s'activer avec de vraies données aujourd'hui — confirmé en pratique : la révélation du
trou fonctionne (affiche « glucose »), mais aucune modale d'évaluation n'apparaît, faute de
`cardId`. C'est cohérent avec le rapport de la Tâche 9 (« Aucune des 4 notes de test n'inclut de
`flashcards` dans la réponse mockée ») : ce sous-flux n'a jamais été exercé qu'en mock. Pas un
bug introduit par ce chantier ni par cette tâche — la liaison note↔flashcard pour les trous
semble ne jamais avoir été câblée côté backend. Signalé pour un futur chantier ciblé plutôt que
corrigé ici (architectural, pas un correctif ponctuel).

**Déviation documentée (Tâche 6)** : le menu flottant de sélection de texte du mode édition
(couleurs `pink-50`/`cyan-50`/`teal-50`/`sky-50` et leurs variantes `dark:`, `NoteEdit.vue`
lignes ~866/896/906/916) reste volontairement non retoné sur les tokens du design system — celui-ci
n'expose que 8 teintes distinctes (5 sémantiques + 3 catégories bibliothèque) pour les 9 actions
d'insertion du menu, ce qui exigerait une décision de design dédiée plutôt qu'un simple
remplacement de token (détail complet dans le corps du commit `2f947a8`). Candidat pour un futur
audit de tokens couleur, au même titre que le concern `flashcards` ci-dessus.

**Documentation** : `workflow/editeur-notes-notation-ia/{PLAN,JOURNAL}.md` mis à jour (tâches
cochées, entrée de clôture). `docs/superpowers/plans/2026-08-30-editeur-notes-redesign.md`
reste la référence détaillée des 10 tâches. Volet backend « Notation de la note » (flux 2)
toujours hors périmètre, cases non cochées intentionnellement.

**Écran 4 terminé** — étape 8 : cette section à jour, commit à suivre.

**Prochaine action** : écran 5 — Blurting IA (`web/src/views/Notes/Blurting.vue`,
route `notes/:id/blurting`), cycle complet `migration-ecran` (inventaire, comparaison à la
maquette Direction A correspondante, états, tests, composition). Rappel de la note déjà actée
plus haut (§ « Ordre des flux ») : retonation visuelle seulement, le contenu fonctionnel ne
change pas au-delà de ce qui a déjà été livré par le flux 5 (ce chantier).
