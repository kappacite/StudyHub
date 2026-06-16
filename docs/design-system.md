# Design System StudyHub — « Soft & Friendly »

Direction esthétique du refacto UI : **moderne, simple, épurée, chaleureuse**, animations
**subtiles & rapides** (≈200 ms, ease-out, pas de rebond marqué). Déploiement **incrémental** :
on style via une couche centralisée (tokens + primitives + motion), puis on migre les vues par lots.

## 1. Tokens de design

Les couleurs sont des **CSS custom properties** définies dans `web/src/style.css`
(`:root` clair, `.dark` sombre), exposées comme tokens Tailwind sémantiques dans
`web/tailwind.config.js` (`rgb(var(--sh-…) / <alpha-value>)`). **Régler le thème = éditer
les variables**, jamais des couleurs brutes dans les vues.

| Rôle | Token Tailwind | Exemple d'usage |
|---|---|---|
| Fond d'app | `bg-app` | `<main class="bg-app">` |
| Surface (carte) | `bg-surface`, `bg-surface-soft` | cartes, champs |
| Bordures | `border-line`, `border-line-soft` | contours discrets |
| Texte | `text-ink`, `text-ink-muted`, `text-ink-subtle` | titres / secondaire / ténu |
| Marque | `bg-primary`, `text-primary`, `bg-primary-soft`, `hover:bg-primary-strong` | boutons, liens, état actif |
| Accent (gamification) | `bg-accent`, `text-accent`, `bg-accent-soft` | séries, objectifs |
| Sémantiques | `success` · `warning` · `danger` (+`-strong`) · `info`, chacun + `-soft` | états |

Règle pastel : les fonds `*-soft` portent toujours un texte en teinte forte (`text-primary`
sur `bg-primary-soft`, etc.) — jamais l'inverse (contraste).

Élévations douces : `shadow-soft`, `shadow-soft-lg`, `shadow-soft-primary`.
Animations utilitaires : `animate-fade-up`, `animate-pop-in`.

## 2. Motion

`@vueuse/motion` (plugin enregistré dans `web/src/main.ts`). Presets partagés dans
`web/src/composables/useMotionPresets.ts` :

```vue
<script setup lang="ts">
import { fadeUp, pop, listItem } from '@/composables/useMotionPresets'
</script>

<template>
  <BaseCard v-motion="fadeUp" />
  <li v-for="(it, i) in items" :key="it.id" v-motion="listItem(i)">…</li>
</template>
```

`prefers-reduced-motion: reduce` est neutralisé globalement (cf. `style.css`). Pas de spring marqué.

## 3. Primitives — `web/src/components/ui/base/`

Composants typés, **sans appel API** (règle CLAUDE.md). Import : `@/components/ui/base`.

| Composant | Props clés | Rôle |
|---|---|---|
| `BaseButton` | `variant` (primary/secondary/ghost/soft/danger), `size`, `block`, `loading` | tous les boutons |
| `BaseCard` | `padding` (none/sm/md/lg), `interactive` | conteneur canonique (remplace le bloc carte recopié) |
| `BaseBadge` | `variant`, `size` | pills d'état |
| `BaseInput` | `v-model`, `type`, slot `#icon` | champ texte |
| `BaseField` | `label`, `error`, `hint`, `required` | label + erreur autour d'un champ |
| `BaseToggle` | `v-model`, slot (icône du curseur) | interrupteur (ex. dark mode) |
| `BaseModal` | `open`, `title`, `size`, `@close`, slots `#title/#footer` | modale (HeadlessUI + backdrop blur) |
| `BaseEmptyState` | `title`, `description`, slots `#icon/#actions` | états vides |
| `BaseSkeleton` | `rounded`, `customClass` | chargement |
| `StatCard` | `label`, `value`, `accent`, slot `#icon` | métriques dashboard |

Exemple :

```vue
<script setup lang="ts">
import { BaseButton, BaseCard, StatCard } from '@/components/ui/base'
</script>

<template>
  <StatCard label="Série" :value="`${streak} j`" accent="accent">
    <template #icon><Flame class="w-5 h-5" /></template>
  </StatCard>
  <BaseButton variant="primary" :loading="saving">Enregistrer</BaseButton>
</template>
```

## 4. Migration par lots

Lot 0 (fondations, ce document) → Lot 1 shell + Dashboard → puis vues par domaine.
Chaque lot : app fonctionnelle, vérif `npm run build` + visuel 375/1440 px en clair/sombre,
zen mode (Notes) et immersive (Examen) préservés.
