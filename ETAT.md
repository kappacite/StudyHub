# État du projet — StudyHub

> Source de vérité sur "où on en est". Mis à jour à chaque cycle. Les hooks
> (`phase_guard.py`, `tdd_guard.py`, `stop_gate.py`) lisent le champ **Phase**
> ci-dessous — format `Phase: N` sur sa propre ligne, ne pas le reformuler.

Phase: 3

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

## Phase courante — 3 : Design system

Feu vert utilisateur reçu le 2026-08-24. Spécification complète (brief, garde-fous,
contraintes dures, travail attendu) : `docs/PROMPT_DEMARRAGE.md` §6.

### Checklist phase 3

- [ ] Deux directions esthétiques proposées (palette 4-6 valeurs hex, appariement
      typographique display/texte/données, échelle typographique, principe de mise en
      page, élément signature) + auto-critique de chacune contre le brief
- [ ] Arbitrage utilisateur reçu — une seule direction retenue
- [ ] Tokens Tailwind (couleur, espacement, rayon, ombre, typographie, durées/courbes de
      transition)
- [ ] Primitives développées en TDD, états et variantes couverts (bouton, champ, carte,
      modale, onglet, badge, info-bulle, état vide, squelette de chargement, toast)
- [ ] Page de démonstration interne (toutes primitives, tous états, clair/sombre) +
      vérification de contraste AA
- [ ] Skill `.claude/skills/design-system/SKILL.md` rédigée à partir du résultat
- [ ] Hook de détection de valeurs brutes : aucune remontée sur les primitives

### Prochaine action

**Revirement utilisateur (2026-08-24)** : la direction « Foyer » (palette, recolorage,
contenu enrichi — voir `docs/passations/2026-08-24_0127_phase3.md` et
`_0144_phase3.md`) est abandonnée sur demande explicite. Repartir entièrement de zéro :
charger le skill `frontend-design` puis le skill `design` (Claude Design), concevoir une
interface neuve pour StudyHub (notes, diagrammes, flashcards, outils de révision,
statistiques ; clair + sombre ; desktop + mobile), **une maquette par écran** pour retour
individuel. Ne pas reprendre la palette/typo/signature de « Foyer » ni l'UI actuelle du
dépôt. Nouveau répertoire de travail et nouvel artifact (ne pas éditer
`studyhub-design-foyer`).

#### Liste exhaustive des pages à designer (35 vues réelles, `docs/audit/00-CARTOGRAPHIE.md` §3.2)

- **Coquille applicative** (transverse) : nav desktop + barre mobile, en-tête, thème
  clair/sombre, états d'auth (`AppLayout.vue`)
- **Auth** (2) : Connexion, Inscription
- **Accueil/Dashboard** (2) : `Home/Accueil.vue`, `Dashboard/Dashboard.vue` (coexistent
  toujours malgré un plan de fusion jamais terminé — clarifier avant de designer les deux)
- **Notes** (6) : liste, éditeur (`NoteEdit.vue`, 3024 lignes), blurting IA, quiz depuis
  note, évaluation de note, note publique
- **Flashcards/Decks** (2) : liste des decks, session d'étude d'un deck
- **Révisions** (6) : accueil révisions, session de révision, stats set, stats classeur,
  gestion d'un set, QCM
- **Diagrammes** (1) : coquille uniquement (canevas libre = phase 5, ne pas y toucher)
- **PDF** (1) : liseuse/annotations
- **Classeurs** (1) : `Binders.vue`
- **Marketplace** (3) : accueil, exploration, aperçu avant clonage
- **Groupes** (2) : liste, détail
- **Classes** (4) : atterrissage, dashboard enseignant, vue élève, détail devoir
- **Examens** (3) : configuration, session, résultats
- **Focus** (1), **Planning** (1)

**Point d'attention consigné** : aucune vue Réglages/Profil dans l'inventaire réel — ne pas
en designer une par supposition (la maquette « Foyer » l'avait inventée à tort), confirmer
d'abord si elle existe ailleurs ou doit être créée. Détail complet de la demande utilisateur :
`PASSATION.md` / `docs/passations/2026-08-24_0144_phase3.md`.

## Écrans migrés (phase 4)

Aucun — phase non commencée.
