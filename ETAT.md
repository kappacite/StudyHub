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
3. Session de révision flashcards
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

2. **Accueil** (`Accueil.vue`) — aucune restructuration visuelle nécessaire (déjà 100 %
   primitives + tokens, héritage automatique Direction A). Travail : suite de tests TDD créée
   de zéro (36 tests, `web/tests/views/Home/Accueil.spec.ts`) + ajout de l'état d'erreur au
   chargement (seule lacune réelle trouvée). 36/36 tests verts, 234/234 tests web verts,
   `vue-tsc -b` sans erreur. Détail complet ci-dessous.

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

3. **Session de révision flashcards** (`web/src/views/Decks/StudyDeck.vue`) — **en cours**.

### Écran 3 — Session de révision flashcards (`web/src/views/Decks/StudyDeck.vue`) — en cours

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

**Prochaine action** : dispatcher au subagent `migrateur-ecran` (étapes 3-6). Contraintes
supplémentaires à lui transmettre : lire les deux fichiers maquette avant de commencer,
préserver impérativement les 4 modes d'entrée et leurs 3 CTA de complétion distincts, ne pas
inventer d'autre écart avec la maquette sans le signaler au contrôleur.
