---
name: frontend-patterns
description: Patterns du frontend Vue 3 StudyHub (script setup TS, Pinia, services Axios, primitives UI, design system, responsive/dark). À charger avant de toucher à web/src/.
---

# frontend-patterns

Références canoniques : `docs/frontend.md` (archi) · `docs/design-system.md` (tokens & primitives).
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

## Design system — « White/Pink × Material épuré »

- **Couleurs = tokens sémantiques** (`bg-app`, `bg-surface`, `border-line`, `text-ink/-muted`,
  `bg-primary` Pink 400, `bg-accent` amber, `success/warning/danger/info`). Régler le thème =
  éditer les CSS custom properties dans `web/src/style.css`, **jamais** de couleur brute (`#...`,
  `indigo-500`) dans une vue nouvellement écrite.
- ⚠️ `danger` = **rouge** = erreur/destruction uniquement. Accent rose décoratif → `primary`/`primary-soft`.
- Fonds `*-soft` portent un texte en teinte forte (`text-primary` sur `bg-primary-soft`).
- Formes : cartes `rounded-2xl`, inputs `rounded-xl`, boutons/chips/FAB `rounded-full`.
- Élévation : `shadow-elev-1/2/3`, CTA `shadow-elev-primary`. Transitions `duration-200 ease-out`.
- Motion : `@vueuse/motion` + presets `@/composables/useMotionPresets` (`fadeUp`, `pop`, `listItem(i)`).

## Primitives — `@/components/ui/base`

Réutiliser plutôt que recopier : `BaseButton` (variant primary/secondary/ghost/soft/danger,
`loading`), `BaseCard`, `BaseBadge`, `BaseInput`, `BaseField`, `BaseToggle`, `BaseModal`,
`BaseEmptyState`, `BaseSkeleton`, `StatCard`, `PageContainer`, `PageHeader`, `Tabs`, `ListRow`,
`SplitView`. Elles sont typées et **sans appel API**.

## Checklist avant PR (web)

- `<script setup lang="ts">`, pas de `any`, pas de `console.log` de debug (un hook le signale).
- Responsive vérifié **375px** et **1440px**, **mode sombre** OK.
- États **loading / error / empty** gérés (`BaseSkeleton`, `BaseEmptyState`).
- `npm run build` (typecheck) + `npm run test:run` passent.

```bash
cd web && npm run dev -- --port 3000   # dev
npm run build                          # typecheck + build prod
```
