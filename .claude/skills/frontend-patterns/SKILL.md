---
name: frontend-patterns
description: Patterns du frontend Vue 3 StudyHub (script setup TS, Pinia, services Axios, primitives UI, design system, responsive/dark). À charger avant de toucher à web/src/.
---

# frontend-patterns

Références canoniques : `docs/frontend.md` (archi) · skill `design-system` (tokens & primitives).
Ce skill = règles à respecter avant d'éditer `web/src/`.

## Stack & conventions

- Vue 3 **Composition API** uniquement, `<script setup lang="ts">`. TypeScript strict — **pas de `any`**.
- Pinia (état) · Vue Router 4 (guards auth/guest) · TailwindCSS 3 (`dark:` natif) · Vite 5 · Vitest.
- Fichiers : `PascalCase.vue` · composables `useX.ts` · stores `x.ts` · services `xService.ts`.

## Où vit la logique (strict)

- **Appels API** : uniquement dans `stores/` et `services/` (`web/src/services/*Service.ts`,
  socle Axios `services/api.ts` qui injecte le JWT + gère le refresh sur 401).
  ❌ **Jamais** d'appel API dans `components/ui/` (primitives présentationnelles pures).
- **Composants** : consomment les stores/services, ne parlent pas à Axios directement.
- Conditionnel natif (web vs Capacitor) : `usePlatform()` (`isNative`), jamais de détection ad hoc.

## Design system — Direction A « Fiche »

Détail complet (palette, typo, rayons, ombres, primitives) : skill `design-system`
(`.claude/skills/design-system/SKILL.md`), à charger avant de toucher un token ou une
primitive. Résumé : couleurs = tokens sémantiques (`bg-app`, `bg-surface`, `border-line`,
`text-ink/-muted`, `bg-primary` encre indigo, `bg-accent` rehaut ocre) — jamais de couleur
brute dans une vue nouvellement écrite. `danger` = brique = erreur/destruction uniquement.
Formes : cartes/inputs `rounded-lg` (8px), boutons primaires `rounded-btn-primary` (10px),
pilules/badges/onglets `rounded-full`. Élévation `shadow-elev-1/2/3`, CTA
`shadow-elev-primary`. Police display (titres) = Bitter, corps = Karla, données = Space Mono.

## Primitives — `@/components/ui/base`

Réutiliser plutôt que recopier : `BaseButton` (variant primary/secondary/ghost/soft/danger,
`loading`), `BaseCard`, `BaseBadge`, `BaseInput`, `BaseField`, `BaseToggle`, `BaseModal`,
`BaseTooltip`, `BaseEmptyState`, `BaseSkeleton`, `BaseToast`, `StatCard`, `PageContainer`,
`PageHeader`, `Tabs`, `ListRow`, `SplitView`. Elles sont typées et **sans appel API**.

## Checklist avant PR (web)

- `<script setup lang="ts">`, pas de `any`, pas de `console.log` de debug (un hook le signale).
- Responsive vérifié **375px** et **1440px**, **mode sombre** OK.
- États **loading / error / empty** gérés (`BaseSkeleton`, `BaseEmptyState`).
- `npm run build` (typecheck) + `npm run test:run` passent.

```bash
cd web && npm run dev -- --port 3000   # dev
npm run build                          # typecheck + build prod
```
