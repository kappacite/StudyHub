# Passation — 2026-08-23 21:35 — phase 1

## Fait
- Phase 0 (cartographie) et Phase 1 (outillage `.claude/`) faites : docs réécrites,
  permissions, 6 hooks, 5 skills, 5 subagents — tous vérifiés en conditions réelles.
- Environnement multi-arch vérifié : suites backend+web 100 % vertes sur arm64 natif
  (`docs/ENVIRONNEMENT.md`), amd64 non re-testé cette session (pas de push).
- Guard TDD/push/phase-2 déclenchés volontairement et confirmés fonctionnels.
- Drill de passation en cours : `SEUIL` abaissé à 0.01 dans `.claude/settings.json`
  (`env.CLAUDE_SEUIL_PASSATION`) pour forcer ce `Stop` — **à remettre à `0.90` après le `/clear`**.

## État
- Tests : vert (dernière suite complète vérifiée : backend 100 %, web 100 %, arm64 natif).
- Dernier commit : `05c318b` fix(claude): encodage UTF-8 et chemins absolus dans les hooks.
- Branche : `main`.

## Prochaine action
Remettre `CLAUDE_SEUIL_PASSATION` à `0.90` dans `.claude/settings.json`, committer ce
retour à la normale (`chore(claude): ...`), puis présenter à l'utilisateur le récapitulatif
de fin de phase 1 (checklist `ETAT.md` cochée) et attendre son feu vert avant d'ouvrir la
phase 2 (revue technique). Ne pas commencer la phase 2 seul.

## Pièges rencontrés
`subprocess.run(text=True)` sans `encoding="utf-8"` plante silencieusement sur la sortie
Node (cp1252 par défaut sous Windows) ; `RACINE = Path(os.environ.get(...))` sans
`.resolve()` produit un chemin double-relatif si `CLAUDE_PROJECT_DIR` est absent au moment
de l'appel — les deux corrigés dans tous les hooks (`05c318b`).

## À relire en priorité
- `ETAT.md`
- `.claude/settings.json`
- `docs/ENVIRONNEMENT.md`
