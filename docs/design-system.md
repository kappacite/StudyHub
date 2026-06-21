# Design System StudyHub — « White/Pink × Material épuré »

Direction esthétique : **blanc/rose, épuré, inspiré Material** — élévation par ombres douces,
coins arrondis, typographie claire, états hover/focus nets, animations **subtiles & rapides**
(≈200 ms, ease-out, pas de rebond marqué, pas de ripple). Primaire = **Pink 400 `#F06292`**.
Light **et** dark supportés. Déploiement **incrémental** : couche centralisée (tokens +
primitives + motion), puis migration des vues par lots.

## 1. Tokens de design

Les couleurs sont des **CSS custom properties** définies dans `web/src/style.css`
(`:root` clair, `.dark` sombre), exposées comme tokens Tailwind sémantiques dans
`web/tailwind.config.js` (`rgb(var(--sh-…) / <alpha-value>)`). **Régler le thème = éditer
les variables**, jamais des couleurs brutes dans les vues.

| Rôle | Token Tailwind | Light | Dark |
|---|---|---|---|
| Fond d'app | `bg-app` | `#FDF7F9` (blanc rosé) | `#1A1618` |
| Surface (carte) | `bg-surface` / `bg-surface-soft` | `#FFFFFF` / `#FCF1F4` | `#231D20` / `#2C2428` |
| Bordures | `border-line` / `border-line-soft` | `#F4E0E7` | `#382E33` |
| Texte | `text-ink` / `-muted` / `-subtle` | `#281E23` / gris rosé | clair |
| **Marque** | `bg-primary` / `text-primary` / `bg-primary-soft` / `hover:bg-primary-strong` | Pink 400 `#F06292` / soft `#FCE4EC` / strong `#D81B60` | Pink 300 `#F48FB1` |
| Accent (gamification) | `bg-accent`, `text-accent`, `bg-accent-soft` | amber `#FFA726` | amber-400 |
| Sémantiques | `success` · `warning` · `danger` (+`-strong`) · `info`, chacun + `-soft` | — | — |

> ⚠️ **`danger` = ROUGE** (`#DC2626`), distinct du rose de marque. Ne jamais utiliser `danger`
> comme accent décoratif : il signifie **erreur / destruction** uniquement. Pour un accent rose
> décoratif, utiliser `primary` / `primary-soft`.

Règle pastel : les fonds `*-soft` portent toujours un texte en teinte forte (`text-primary`
sur `bg-primary-soft`, etc.) — jamais l'inverse (contraste AA).

### Élévation, formes, typo (Material épuré)

- **Élévation** (ombres douces, jamais dures) : `shadow-elev-1` (cartes au repos),
  `shadow-elev-2` (hover, menus), `shadow-elev-3` (modales, panneaux flottants),
  `shadow-elev-primary` (CTA principal, ombre teintée rose). Alias rétro-compat :
  `shadow-soft` → elev-1, `shadow-soft-lg` → elev-2, `shadow-soft-primary` → elev-primary.
- **Formes** : cartes/panneaux `rounded-2xl` ; champs/inputs `rounded-xl` ;
  boutons d'action / chips / badges / FAB `rounded-full` (pilule).
- **Typographie** : **Inter**. Titres semi-bold (`font-bold`/`font-extrabold`), sur-titres de
  section en `uppercase tracking-wider text-ink-subtle`, corps `text-ink-muted`.
- **États** : hover = `bg-surface-soft` + léger lift (`-translate-y-0.5`) sur les cartes
  interactives ; focus = `ring-2 ring-primary/40` ; transitions `duration-200 ease-out`.

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
| `PageContainer` | `size` (default/narrow/wide) | wrapper de page (`max-w` + `space-y-6`) |
| `PageHeader` | `title`, `subtitle`, `breadcrumbs`, slots `#actions/#tabs` | en-tête de page |
| `Tabs` | `v-model`, `tabs[{key,label,icon?,badge?}]` | segmented control présentationnel |
| `ListRow` | `as` (div/button/router-link), `to`, `title`, `subtitle`, `interactive`, slots `#leading/#trailing` | ligne de liste |
| `SplitView` | `leftWidth`, slots `#left/#right` | colonne latérale + contenu (responsive) |

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

**Lot T** (theming white/pink + Material, ce document) → **Lot S0** (socle structurel : routing
5 sections + nav) → **S1** Accueil → **S2** Bibliothèque → **S3** Réviser → **S4** Classes →
**S5** Planning → **S6** Communauté → **S7** finition. Plan détaillé : `docs/ui-redesign-plan.md`.

Chaque lot : app fonctionnelle, vérif `npm run build` + `npm run test:run` + visuel 375/1440 px
en clair/sombre, zen mode (Notes) et immersive (Examen) préservés. Les vues conservent encore
des couleurs brutes (indigo/blue) tant que leur lot n'est pas passé — c'est attendu pendant la
transition ; elles migrent vers les tokens lors de leur lot.
