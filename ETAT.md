# État du projet — StudyHub

> Source de vérité sur "où on en est". Mis à jour à chaque cycle. Les hooks
> (`phase_guard.py`, `tdd_guard.py`, `stop_gate.py`) lisent le champ **Phase**
> ci-dessous — format `Phase: N` sur sa propre ligne, ne pas le reformuler.

Phase: 1

## Phase courante — 1 : Outillage agentique

Plan détaillé : `C:\Users\denoe\.claude\plans\fuzzy-petting-waffle.md` (séquence de
15 commits atomiques). Arbitrage acté : on prend le nouveau prompt de démarrage,
pas l'ancien état documenté (`docs/design-system.md`, `docs/performance-audit.md`,
`docs/ui-redesign-plan.md` seront traités comme non acquis en phase 2/3).

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
- [ ] Vérification des gardes (déclenchement volontaire + nettoyage)
- [ ] Drill de passation à seuil abaissé (point de passage interactif avec l'utilisateur)
- [ ] Passe de cohérence documentaire finale

### Prochaine phase

Phase 2 — Revue technique (lecture seule, 4 axes : sécurité, architecture, performance,
tests/CI). Ne commence pas tant que la checklist ci-dessus n'est pas cochée et que le
backlog de phase 1 n'a pas été présenté pour validation.

## Écrans migrés (phase 4)

Aucun — phase non commencée.
