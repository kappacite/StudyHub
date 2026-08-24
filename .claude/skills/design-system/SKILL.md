---
name: design-system
description: Référence canonique du design system StudyHub — Direction A « Fiche » (palette, typographie, rayons, ombres, primitives ui/base, garde-fous). À charger avant de créer un nouvel écran (phase 4, skill migration-ecran) ou de toucher un token/une primitive.
---

# design-system

Référence canonique du design system StudyHub — Direction A « Fiche ». À charger avant de
créer un nouvel écran (phase 4, skill `migration-ecran`) ou de toucher un token/une primitive.
Spec source complète (patterns HTML de référence) : `docs/design-system-direction-a-spec.md`.

## Palette (tokens sémantiques — jamais de hex/rgb brut, cf. `web/src/style.css`)

`bg-app` (papier chaud) · `bg-surface`/`bg-surface-soft` (cartes/fonds imbriqués) ·
`border-line`/`border-line-soft` · `text-ink`/`text-ink-muted`/`text-ink-subtle` ·
`bg-primary`/`primary-strong`/`primary-soft` + `text-primary-ink` (encre indigo — action,
"Bien" en SM2) · `bg-accent`/`accent-soft` (rehaut ocre — échéance, "Difficile" en SM2) ·
`bg-success`/`success-soft` (sauge — "Facile") · `bg-danger`/`danger-strong`/`danger-soft`
(brique — suppression, "Encore") · `bg-warning`/`info` (alias de accent/primary, pas de
teinte distincte en Direction A) · `bg-cat-{note,pdf,diagram,deck,set}(-soft)` (catégories
Bibliothèque, dérivées — pas dans les maquettes validées, ajustables sans revalidation).

## Typographie

`font-display` (Bitter, serif — titres de page 30px/700 `text-display-lg`, titres de carte
19px/700 `text-display-md` — jamais pour le corps de texte) · `font-sans` (Karla, corps par
défaut — 16px lecture longue, `text-sm` 14px UI standard, `text-meta` 13px secondaire,
`text-xs` 12px labels) · `font-mono` (Space Mono — nombres, dates, compteurs, `text-tiny`
10px pour les badges compacts).

## Rayons

`rounded-btn-primary` (10px, boutons primaires uniquement) · `rounded-lg` (8px — cartes,
boutons secondaires, inputs) · `rounded` (4px — bandeaux "fiche bristol") ·
`rounded-checkbox` (3px) · `rounded-full` (999px — pilules, badges, onglets, avatars).
Échelle d'espacement : la numérotation Tailwind par défaut suffit (4/8/12/16/20/24/28/32/40/
48px = `1`/`2`/`3`/`4`/`5`/`6`/`7`/`8`/`10`/`12`) — jamais de valeur `[...]` arbitraire.

## Ombres

`shadow-elev-1` (carte au repos) · `shadow-elev-2`/`elev-3` (carte au survol, modale) ·
`shadow-elev-primary` (lueur indigo, CTA). Alias rétro-compat `shadow-soft*` préservés pour
les écrans non encore migrés (phase 4).

## Primitives — `@/components/ui/base`

Les 10 primitives couvertes par la checklist phase 3 (bouton, champ, carte, modale, onglet,
badge, info-bulle, état vide, squelette, toast) sont testées (`web/tests/components/ui/base/`)
et conformes Direction A. Page de démonstration : route `/dev/design-system`
(`web/src/views/Dev/DesignSystemDemo.vue`). Toujours réutiliser une primitive existante avant
d'en écrire une nouvelle (`web/src/components/CLAUDE.md`).

- `BaseButton` : variantes `primary` (rempli indigo, rayon 10px) / `secondary` / `ghost` /
  `soft` / `danger` (**outline**, pas rempli — changement vs l'ancien thème).
- `BaseField`/`BaseInput` : label en majuscules muettes (`text-xs uppercase text-ink-muted`),
  input `rounded-lg bg-surface` (pas `surface-soft`).
- `BaseCard` : `rounded-lg` + `shadow-elev-1`.
- `BaseModal` : `rounded-xl`, titre en `font-display`.
- `Tabs` : pilules pleines (`rounded-full`), actif = `bg-primary text-primary-ink` — même
  traitement que la navigation applicative.
- `BaseBadge` : pilule, variantes de couleur sémantiques.
- `BaseTooltip` (nouveau) : survol/focus, pas de dépendance de positionnement externe.
- `BaseEmptyState` : icône en cercle pointillé, titre `font-display`.
- `BaseSkeleton` : `rounded-lg` par défaut.
- `BaseToast` (nouveau) : présentationnel seul — pas de file d'attente globale (à câbler en
  phase 4 au premier besoin réel).

## Garde-fous

- `.claude/hooks/raw_value_guard.py` (`PostToolUse`, non bloquant) : avertit sur toute
  couleur hex/`rgb()`, `px` hors 0-1px, ou classe Tailwind arbitraire écrite dans
  `web/src/components/ui/`.
- `web/tests/design-tokens/contrast.spec.ts` : contraste AA (≥4.5:1) sur les paires
  texte/fond critiques, clair et sombre — à relancer si une valeur de `style.css` change.
- `BaseToggle`, `ListRow`, `PageContainer`, `PageHeader`, `SplitView`, `StatCard` se
  re-thématisent automatiquement pour la couleur (tokens sémantiques) mais n'ont pas été
  auditées structurellement (rayons/typo) contre Direction A — à faire au fil de la
  migration phase 4, écran par écran, pas en bloc.
- Écarts connus (revue finale de branche) : `contrast.spec.ts` ne couvre que 8 paires
  choisies à la main, pas toutes les combinaisons réellement rendues — certains fonds
  `*-soft` + texte fort passent sous l'AA en clair une fois vérifiés contre leur fond réel.
  Cible tactile ≥44px appliquée seulement aux boutons de fermeture (BaseToast, BaseModal),
  pas encore auditée sur `BaseButton`/`Tabs`. `.markdown-body`/`.katex-display` de
  `style.css` gardent l'ancienne palette rose (hors périmètre, migration phase 4).
