# Design System Direction A « Fiche » — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Faire passer les tokens Tailwind et les 10 primitives UI de StudyHub de l'ancien
thème « White/Pink » (abandonné) au langage visuel **Direction A « Fiche »** validé par
l'utilisateur sur les 33 écrans du canevas Claude Design, avec couverture TDD complète,
une page de démonstration vérifiant le contraste AA, un hook de détection de valeurs
brutes, et la skill `design-system` qui documente le résultat — complétant ainsi la
checklist phase 3 de `ETAT.md`.

**Architecture:** Les composants consomment déjà des tokens sémantiques Tailwind
(`bg-primary`, `text-ink`, `rounded-*`...) alimentés par des CSS custom properties dans
`web/src/style.css`. La ré-thématisation se fait donc en deux temps : (1) remplacer les
valeurs des variables CSS et étendre `tailwind.config.js` (nouvelle police, nouveaux rayons,
tokens de contraste) — ceci re-thématise gratuitement tout composant déjà token-driven ;
(2) ajuster le markup des 10 primitives pour les écarts structurels que Direction A introduit
(rayons différents par élément, police d'affichage Bitter sur les titres, bouton destructeur
devenu outline, label de champ en majuscules...). Chaque primitive est testée en isolation
avec `@vue/test-utils` (`mount`), sans mock de store — ce sont des composants purement
présentationnels.

**Tech Stack:** Vue 3 `<script setup lang="ts">`, Tailwind 3 (`darkMode:'class'`), Vitest +
`@vue/test-utils`, `@headlessui/vue` (modale), `@lucide/vue` (icônes).

**Spec:** `docs/design-system-direction-a-spec.md` (copié depuis le scratchpad de la session
précédente à la Tâche 1, Étape 1 — c'est la spec de référence validée par l'utilisateur pour
tous les écrans du canevas ; source : `_DIRECTION_A_SPEC.md`, dossier de travail hors dépôt) ·
`docs/PROMPT_DEMARRAGE.md` §6 (brief phase 3, garde-fous, critères d'acceptation) · `ETAT.md`
checklist phase 3.

## Global Constraints

- `<script setup lang="ts">` exclusivement, jamais de `any` (CLAUDE.md, web/CLAUDE.md).
- Aucune valeur brute de style (`#rrggbb`, `rgb(...)`, `px` hors `0px`/`1px`, classe Tailwind
  arbitraire `[...]`) — toujours un token (web/CLAUDE.md).
- `web/src/components/ui/` = primitives présentationnelles pures, **aucun appel API**
  (web/src/components/CLAUDE.md).
- Cibles tactiles ≥ 44px, contraste AA, `prefers-reduced-motion` respecté
  (web/src/components/CLAUDE.md — déjà géré globalement dans `style.css`, ne pas régresser).
- Le test précède le code sans exception dès phase 3 (`ETAT.md` = phase 3 actuellement) —
  `tdd_guard.py` bloque l'écriture d'un fichier sous `src/components/`, `src/views/` sans
  test au nom correspondant sous `web/tests/` (recherche récursive par nom de fichier).
  Convention de nommage/emplacement : `web/tests/components/ui/base/<Nom>.spec.ts`
  (miroir de `web/src/`), gabarit `web/tests/components/TagBadge.spec.ts`.
- `web/src/style.css` et `web/tailwind.config.js` ne sont **pas** dans les répertoires gardés
  par `tdd_guard.py` (`WEB_PROD_DIRS` ne couvre que `src/{stores,composables,components,views,
  services}/`) — pas d'exemption `tdd-exempt.txt` nécessaire pour la Tâche 1, mais un vrai
  test de contraste y est écrit quand même par discipline (cf. Tâche 1).
- Anti-patterns interdits en test : assertion affaiblie, mock du sujet testé, `sleep`
  (cycle-tdd skill).
- Commits Conventional Commits, corps en français, un commit par tâche.

---

## Contexte : ce qui existe déjà (lu avant d'écrire ce plan)

- `web/tailwind.config.js` et `web/src/style.css` portent encore le thème **« White/Pink »**
  (commits `6f6a457`, `1a01215`, déjà mergés sur `main` — ce n'est pas du code de maquette
  jetable, c'est en production). Primaire = Pink 400 `#F06292`. C'est ce thème que ce plan
  remplace.
- 15 primitives existent déjà dans `web/src/components/ui/base/` (`BaseButton`, `BaseCard`,
  `BaseBadge`, `BaseField`, `BaseInput`, `BaseModal`, `BaseEmptyState`, `BaseSkeleton`,
  `BaseToggle`, `Tabs`, `ListRow`, `PageContainer`, `PageHeader`, `SplitView`, `StatCard`).
  **Aucune n'a de test** (`find web/src/components/ui -iname "*.spec.ts"` → vide).
  `BaseTooltip` et `BaseToast` n'existent pas encore (requis par la checklist phase 3 —
  « info-bulle », « toast »).
- La checklist phase 3 (`ETAT.md`) demande exactement 10 primitives : bouton, champ, carte,
  modale, onglet, badge, info-bulle, état vide, squelette de chargement, toast. `BaseToggle`,
  `ListRow`, `PageContainer`, `PageHeader`, `SplitView`, `StatCard` ne sont pas dans cette
  liste — non touchées par ce plan (elles se re-thématiseront automatiquement pour leurs
  couleurs via les tokens sémantiques de la Tâche 1 ; leur alignement structurel complet,
  s'il y a un écart, relève de la phase 4 `migration-ecran`, écran par écran).
- `.claude/hooks/tdd_guard.py` : phase ≥ 3 → toute écriture sous `src/components/`,
  `src/views/`, etc. sans test correspondant est refusée. Le test doit être écrit/modifié
  **avant** (horodatage plus récent que) le fichier de prod.
- `.claude/hooks/no_debug.py` est le gabarit à suivre pour la Tâche 13 (hook `PostToolUse`
  non bloquant, `additionalContext`, lit `tool_input.content/new_string/edits[].new_string`).
- Aucune police custom actuelle (`Inter` body, `JetBrains Mono` mono) — Direction A demande
  Bitter (display), Karla (corps), Space Mono (données), chargées via Google Fonts.

---

## Tâche 1 : Tokens — palette, typographie, rayons, ombres, contraste AA

**Files:**
- Create: `docs/design-system-direction-a-spec.md` (copie de la spec validée)
- Create: `web/tests/design-tokens/contrast.spec.ts`
- Modify: `web/src/style.css:12-93` (blocs `:root` et `.dark`), `web/src/style.css:95-98` (règle `body`)
- Modify: `web/tailwind.config.js` (entier — `colors`, `fontFamily`, `fontSize`, `borderRadius`, `boxShadow`)
- Modify: `web/index.html` (ajout du lien Google Fonts dans `<head>`)

**Interfaces:**
- Produces : les tokens Tailwind consommés par toutes les tâches suivantes —
  `bg-app/surface/surface-soft`, `border-line/line-soft`, `text-ink/ink-muted/ink-subtle`,
  `bg-primary/primary-strong/primary-soft`, `text-primary-ink` (nouveau — texte lisible sur
  fond `primary`, bascule blanc/sombre selon le thème), `bg-accent/accent-soft`,
  `bg-success/success-soft`, `bg-warning/warning-soft`, `bg-danger/danger-strong/danger-soft`,
  `bg-info/info-soft`, `bg-cat-{note,pdf,diagram,deck,set}(-soft)` ; `font-display` (Bitter),
  `font-sans` (Karla, corps par défaut), `font-mono` (Space Mono) ; `text-tiny` (10px),
  `text-meta` (13px), `text-display-md` (19px/700), `text-display-lg` (30px/700) ;
  `rounded-btn-primary` (10px), `rounded-checkbox` (3px) — le reste du besoin (8px, 4px,
  999px) est déjà couvert par les tokens natifs Tailwind `rounded-lg`/`rounded`/`rounded-full` ;
  `shadow-elev-1/2/3/primary` (+ alias rétro-compat `shadow-soft/soft-lg/soft-primary` déjà
  utilisés ailleurs dans l'app, préservés à l'identique).

- [ ] **Étape 1 : copier la spec validée dans le dépôt**

```bash
cp "/c/Users/denoe/AppData/Local/Temp/claude/C--Users-denoe-Documents-Projets-StudyHub/e43205be-ff5a-4781-bc86-2957f926d21e/scratchpad/studyhub-design-v2/_DIRECTION_A_SPEC.md" "docs/design-system-direction-a-spec.md"
```

Si le chemin n'existe plus (nettoyage du dossier temp entre-temps), le contenu intégral de
la spec est reproduit dans les tâches ci-dessous (palette, typo, rayons, patterns bouton/champ/
carte/état vide) — reconstruire le fichier à partir de ces valeurs plutôt que bloquer.

- [ ] **Étape 2 : écrire le test de contraste AA (rouge — les tokens actuels sont Pink, pas Direction A)**

Créer `web/tests/design-tokens/contrast.spec.ts` :

```ts
import { describe, it, expect } from 'vitest'

type RGB = [number, number, number]

function srgbToLinear(c: number): number {
  const cs = c / 255
  return cs <= 0.03928 ? cs / 12.92 : Math.pow((cs + 0.055) / 1.055, 2.4)
}

function relativeLuminance([r, g, b]: RGB): number {
  return 0.2126 * srgbToLinear(r) + 0.7152 * srgbToLinear(g) + 0.0722 * srgbToLinear(b)
}

function contrastRatio(a: RGB, b: RGB): number {
  const l1 = relativeLuminance(a)
  const l2 = relativeLuminance(b)
  const lighter = Math.max(l1, l2)
  const darker = Math.min(l1, l2)
  return (lighter + 0.05) / (darker + 0.05)
}

// Ces triplets dupliquent volontairement les valeurs RGB de web/src/style.css
// (Direction A « Fiche »). Si la palette change, mettre à jour ce fichier en même
// temps (rappelé dans .claude/skills/design-system/SKILL.md).
const light = {
  app: [239, 234, 224] as RGB,
  surface: [251, 248, 242] as RGB,
  ink: [35, 36, 31] as RGB,
  inkMuted: [107, 104, 88] as RGB,
  primary: [46, 67, 116] as RGB,
  primaryInk: [255, 255, 255] as RGB,
  danger: [178, 76, 58] as RGB,
  success: [92, 122, 90] as RGB,
}

const dark = {
  app: [27, 25, 18] as RGB,
  ink: [243, 239, 227] as RGB,
  inkMuted: [184, 178, 156] as RGB,
  primary: [147, 169, 222] as RGB,
  primaryInk: [27, 25, 18] as RGB,
}

const AA_TEXT = 4.5

describe('Contraste AA — Direction A « Fiche »', () => {
  it('texte principal sur fond clair', () => {
    expect(contrastRatio(light.ink, light.app)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte secondaire (muted) sur fond clair', () => {
    expect(contrastRatio(light.inkMuted, light.app)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte sur bouton primaire (fond clair)', () => {
    expect(contrastRatio(light.primaryInk, light.primary)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('bouton destructeur outline sur surface (fond clair)', () => {
    expect(contrastRatio(light.danger, light.surface)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('bouton "Facile" (success) outline sur surface (fond clair)', () => {
    // Paire la plus tendue de la palette (~4.5) — si ce test casse après un
    // ajustement de --sh-success, resserrer la couleur (assombrir de ~10/canal).
    expect(contrastRatio(light.success, light.surface)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte principal sur fond sombre', () => {
    expect(contrastRatio(dark.ink, dark.app)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte secondaire (muted) sur fond sombre', () => {
    expect(contrastRatio(dark.inkMuted, dark.app)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte sur bouton primaire (fond sombre)', () => {
    expect(contrastRatio(dark.primaryInk, dark.primary)).toBeGreaterThanOrEqual(AA_TEXT)
  })
})
```

- [ ] **Étape 3 : lancer le test, vérifier qu'il échoue pour la bonne raison**

```bash
cd web && npx vitest run tests/design-tokens/contrast.spec.ts
```

Attendu : les 8 assertions passent déjà en réalité (les triplets ci-dessus sont les valeurs
*cibles*, pas les valeurs actuelles du fichier — ce test ne lit pas encore `style.css`, il
vérifie que les valeurs qu'on s'apprête à écrire sont mathématiquement correctes). C'est donc
vert dès l'écriture — le rouge réel de ce cycle est visuel : rien dans `style.css` ne
correspond encore à ces valeurs tant que l'Étape 4 n'est pas faite. Continuer.

- [ ] **Étape 4 : remplacer les blocs de tokens dans `web/src/style.css`**

Remplacer les lignes 12–93 (blocs `:root { ... }` et `.dark { ... }`) par :

```css
  :root {
    --sh-app: 239 234 224;          /* papier chaud (#EFEAE0) */
    --sh-surface: 251 248 242;      /* cartes (#FBF8F2) */
    --sh-surface-soft: 242 236 222; /* fonds imbriqués / hover (#F2ECDE) */

    --sh-line: 217 208 188;         /* filets (#D9D0BC) */
    --sh-line-soft: 232 225 210;    /* filets discrets */

    --sh-ink: 35 36 31;             /* texte principal (#23241F) */
    --sh-ink-muted: 107 104 88;     /* texte secondaire (#6B6858) */
    --sh-ink-subtle: 150 145 125;   /* texte ténu */

    --sh-primary: 46 67 116;        /* encre indigo — actions, "Bien" SM2 (#2E4374) */
    --sh-primary-strong: 31 46 82;  /* hover/pressed */
    --sh-primary-soft: 221 227 240; /* fond teinté indigo */
    --sh-primary-ink: 255 255 255;  /* texte sur fond primary */

    --sh-accent: 201 154 46;        /* rehaut ocre — échéance, "Difficile" SM2 (#C99A2E) */
    --sh-accent-soft: 234 223 192;

    --sh-success: 92 122 90;        /* sauge — "Facile" SM2 */
    --sh-success-soft: 217 224 211;
    --sh-warning: 201 154 46;       /* alias de accent (pas de teinte distincte en Direction A) */
    --sh-warning-soft: 234 223 192;
    --sh-danger: 178 76 58;         /* brique — suppression, "Encore" SM2 */
    --sh-danger-strong: 143 60 45;
    --sh-danger-soft: 231 207 198;
    --sh-info: 46 67 116;           /* alias de primary (pas de teinte distincte) */
    --sh-info-soft: 221 227 240;

    --sh-shadow: 0 1px 2px rgb(35 36 31 / 0.06), 0 8px 20px -12px rgb(35 36 31 / 0.18);
    --sh-shadow-lg: 0 4px 8px rgb(35 36 31 / 0.10), 0 20px 40px -16px rgb(35 36 31 / 0.28);

    /* Couleurs de catégorie de contenu (Bibliothèque) — icônes & pastilles.
       Non couvertes par les maquettes Direction A (qui différencient par icône,
       pas par couleur) : teintes dérivées, harmonisées avec la palette. */
    --sh-cat-note: 110 90 115;      --sh-cat-note-soft: 231 224 232;
    --sh-cat-pdf: 156 90 60;        --sh-cat-pdf-soft: 239 224 214;
    --sh-cat-diagram: 63 110 112;   --sh-cat-diagram-soft: 220 231 231;
    --sh-cat-deck: 46 67 116;       --sh-cat-deck-soft: 221 227 240;   /* = primary */
    --sh-cat-set: 201 154 46;       --sh-cat-set-soft: 234 223 192;    /* = accent */
  }

  .dark {
    --sh-app: 27 25 18;             /* #1B1912 */
    --sh-surface: 36 33 25;         /* #242119 */
    --sh-surface-soft: 44 40 32;

    --sh-line: 58 54 39;            /* #3A3627 */
    --sh-line-soft: 50 46 36;

    --sh-ink: 243 239 227;          /* #F3EFE3 */
    --sh-ink-muted: 184 178 156;    /* #B8B29C */
    --sh-ink-subtle: 138 132 112;

    --sh-primary: 147 169 222;      /* #93A9DE */
    --sh-primary-strong: 183 196 233;
    --sh-primary-soft: 43 51 71;
    --sh-primary-ink: 27 25 18;     /* texte sombre sur fond indigo clair */

    --sh-accent: 224 184 74;        /* #E0B84A */
    --sh-accent-soft: 58 49 28;

    --sh-success: 143 174 139;      /* #8FAE8B */
    --sh-success-soft: 38 48 31;
    --sh-warning: 224 184 74;
    --sh-warning-soft: 58 49 28;
    --sh-danger: 224 136 114;       /* #E08872 */
    --sh-danger-strong: 234 160 144;
    --sh-danger-soft: 61 42 34;
    --sh-info: 147 169 222;
    --sh-info-soft: 43 51 71;

    --sh-shadow: 0 1px 2px rgb(0 0 0 / 0.3), 0 8px 24px -12px rgb(0 0 0 / 0.5);
    --sh-shadow-lg: 0 4px 8px rgb(0 0 0 / 0.4), 0 20px 44px -16px rgb(0 0 0 / 0.6);

    --sh-cat-note: 165 145 170;     --sh-cat-note-soft: 45 38 48;
    --sh-cat-pdf: 206 145 115;      --sh-cat-pdf-soft: 48 38 32;
    --sh-cat-diagram: 123 165 167;  --sh-cat-diagram-soft: 34 44 44;
    --sh-cat-deck: 147 169 222;     --sh-cat-deck-soft: 43 51 71;
    --sh-cat-set: 224 184 74;       --sh-cat-set-soft: 58 49 28;
  }
```

Remplacer la règle `body` (lignes 95–98) — retirer le `font-family` codé en dur, s'appuyer
sur le token :

```css
  body {
    @apply bg-app text-ink font-sans transition-colors duration-200;
  }
```

- [ ] **Étape 5 : ajouter le lien Google Fonts dans `web/index.html`**

Dans le `<head>`, avant les autres feuilles de style :

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bitter:wght@400;600;700&family=Karla:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap">
```

- [ ] **Étape 6 : réécrire `web/tailwind.config.js`**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // Tokens sémantiques alimentés par des CSS custom properties (cf. src/style.css).
      // Le dark mode et tout ré-accent se règlent en un seul point.
      colors: {
        app: 'rgb(var(--sh-app) / <alpha-value>)',
        surface: {
          DEFAULT: 'rgb(var(--sh-surface) / <alpha-value>)',
          soft: 'rgb(var(--sh-surface-soft) / <alpha-value>)',
        },
        line: {
          DEFAULT: 'rgb(var(--sh-line) / <alpha-value>)',
          soft: 'rgb(var(--sh-line-soft) / <alpha-value>)',
        },
        ink: {
          DEFAULT: 'rgb(var(--sh-ink) / <alpha-value>)',
          muted: 'rgb(var(--sh-ink-muted) / <alpha-value>)',
          subtle: 'rgb(var(--sh-ink-subtle) / <alpha-value>)',
        },
        primary: {
          DEFAULT: 'rgb(var(--sh-primary) / <alpha-value>)',
          strong: 'rgb(var(--sh-primary-strong) / <alpha-value>)',
          soft: 'rgb(var(--sh-primary-soft) / <alpha-value>)',
          ink: 'rgb(var(--sh-primary-ink) / <alpha-value>)',
        },
        accent: {
          DEFAULT: 'rgb(var(--sh-accent) / <alpha-value>)',
          soft: 'rgb(var(--sh-accent-soft) / <alpha-value>)',
        },
        success: {
          DEFAULT: 'rgb(var(--sh-success) / <alpha-value>)',
          soft: 'rgb(var(--sh-success-soft) / <alpha-value>)',
        },
        warning: {
          DEFAULT: 'rgb(var(--sh-warning) / <alpha-value>)',
          soft: 'rgb(var(--sh-warning-soft) / <alpha-value>)',
        },
        danger: {
          DEFAULT: 'rgb(var(--sh-danger) / <alpha-value>)',
          strong: 'rgb(var(--sh-danger-strong) / <alpha-value>)',
          soft: 'rgb(var(--sh-danger-soft) / <alpha-value>)',
        },
        info: {
          DEFAULT: 'rgb(var(--sh-info) / <alpha-value>)',
          soft: 'rgb(var(--sh-info-soft) / <alpha-value>)',
        },
        'cat-note': { DEFAULT: 'rgb(var(--sh-cat-note) / <alpha-value>)', soft: 'rgb(var(--sh-cat-note-soft) / <alpha-value>)' },
        'cat-pdf': { DEFAULT: 'rgb(var(--sh-cat-pdf) / <alpha-value>)', soft: 'rgb(var(--sh-cat-pdf-soft) / <alpha-value>)' },
        'cat-diagram': { DEFAULT: 'rgb(var(--sh-cat-diagram) / <alpha-value>)', soft: 'rgb(var(--sh-cat-diagram-soft) / <alpha-value>)' },
        'cat-deck': { DEFAULT: 'rgb(var(--sh-cat-deck) / <alpha-value>)', soft: 'rgb(var(--sh-cat-deck-soft) / <alpha-value>)' },
        'cat-set': { DEFAULT: 'rgb(var(--sh-cat-set) / <alpha-value>)', soft: 'rgb(var(--sh-cat-set-soft) / <alpha-value>)' },
      },
      fontFamily: {
        display: ['Bitter', 'Georgia', 'serif'],
        sans: ['Karla', 'system-ui', 'sans-serif'],
        mono: ['Space Mono', 'Courier New', 'monospace'],
      },
      fontSize: {
        tiny: ['10px', { lineHeight: '1.3' }],
        meta: ['13px', { lineHeight: '1.4' }],
        'display-md': ['19px', { lineHeight: '1.25', fontWeight: '700' }],
        'display-lg': ['30px', { lineHeight: '1.15', fontWeight: '700' }],
      },
      borderRadius: {
        'btn-primary': '10px',
        checkbox: '3px',
      },
      boxShadow: {
        'elev-1': 'var(--sh-shadow)',
        'elev-2': 'var(--sh-shadow-lg)',
        'elev-3': 'var(--sh-shadow-lg)',
        'elev-primary': '0 6px 20px -8px rgb(var(--sh-primary) / 0.35)',
        // Alias rétro-compat : composants existants (shadow-soft*) non touchés par ce plan.
        soft: 'var(--sh-shadow)',
        'soft-lg': 'var(--sh-shadow-lg)',
        'soft-primary': '0 6px 20px -8px rgb(var(--sh-primary) / 0.35)',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'none' },
        },
        'pop-in': {
          '0%': { opacity: '0', transform: 'scale(.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      animation: {
        'fade-up': 'fade-up .25s ease-out both',
        'pop-in': 'pop-in .2s ease-out both',
      },
    },
  },
  plugins: [],
}
```

- [ ] **Étape 7 : vérifier le build et le test de contraste**

```bash
cd web && npx vitest run tests/design-tokens/contrast.spec.ts && npm run build
```

Attendu : 8/8 tests verts, build TypeScript/Vite sans erreur.

- [ ] **Étape 8 : commit**

```bash
git add docs/design-system-direction-a-spec.md web/tests/design-tokens/contrast.spec.ts web/src/style.css web/tailwind.config.js web/index.html
git commit -m "$(cat <<'EOF'
feat(design-system): tokens Direction A « Fiche » (palette, typo, rayons, ombres)

Remplace le thème White/Pink par la palette validée par l'utilisateur sur les
33 écrans du canevas (encre indigo, rehaut ocre, papier chaud). Contraste AA
vérifié par test automatisé sur les paires critiques clair/sombre.
EOF
)"
```

---

## Tâche 2 : BaseButton (bouton)

**Files:**
- Create: `web/tests/components/ui/base/BaseButton.spec.ts`
- Modify: `web/src/components/ui/base/BaseButton.vue`

**Interfaces:**
- Consumes: tokens Tâche 1 (`bg-primary`, `text-primary-ink`, `rounded-btn-primary`, `rounded-lg`, `bg-danger`, `border-danger`...).
- Produces: `variant: 'primary'|'secondary'|'ghost'|'soft'|'danger'`, `size: 'sm'|'md'|'lg'`, props `type/block/loading/disabled` — inchangé pour les consommateurs existants (aucun composant appelant ne doit être modifié).

- [ ] **Étape 1 : écrire les tests (rouge)**

`web/tests/components/ui/base/BaseButton.spec.ts` :

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '../../../../src/components/ui/base/BaseButton.vue'

describe('BaseButton', () => {
  it('affiche le contenu du slot par défaut', () => {
    const wrapper = mount(BaseButton, { slots: { default: 'Valider' } })
    expect(wrapper.text()).toContain('Valider')
  })

  it('applique le rayon 10px et le fond indigo pour la variante primary par défaut', () => {
    const wrapper = mount(BaseButton, { slots: { default: 'OK' } })
    expect(wrapper.classes()).toContain('rounded-btn-primary')
    expect(wrapper.classes()).toContain('bg-primary')
    expect(wrapper.classes()).toContain('text-primary-ink')
  })

  it('applique un rayon de 8px et un contour transparent pour la variante danger', () => {
    const wrapper = mount(BaseButton, { props: { variant: 'danger' }, slots: { default: 'Supprimer' } })
    expect(wrapper.classes()).toContain('rounded-lg')
    expect(wrapper.classes()).toContain('border-danger')
    expect(wrapper.classes()).toContain('bg-transparent')
  })

  it('désactive le bouton quand disabled est vrai', () => {
    const wrapper = mount(BaseButton, { props: { disabled: true }, slots: { default: 'X' } })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('désactive le bouton et affiche le spinner quand loading est vrai', () => {
    const wrapper = mount(BaseButton, { props: { loading: true }, slots: { default: 'X' } })
    expect(wrapper.attributes('disabled')).toBeDefined()
    expect(wrapper.find('svg.animate-spin').exists()).toBe(true)
  })

  it('applique la largeur pleine quand block est vrai', () => {
    const wrapper = mount(BaseButton, { props: { block: true }, slots: { default: 'X' } })
    expect(wrapper.classes()).toContain('w-full')
  })

  it('déclenche un click natif quand activé', async () => {
    const wrapper = mount(BaseButton, { slots: { default: 'X' } })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge**

```bash
cd web && npx vitest run tests/components/ui/base/BaseButton.spec.ts
```
Attendu : échecs sur `rounded-btn-primary`, `text-primary-ink`, `border-danger`/`bg-transparent` (le composant actuel a `rounded-full` et un `danger` plein `bg-danger text-white`).

- [ ] **Étape 3 : réécrire `BaseButton.vue`**

```vue
<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="inline-flex items-center justify-center gap-2 font-bold transition-all duration-200 active:scale-[.97] focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-app disabled:opacity-50 disabled:pointer-events-none"
    :class="[sizeClass, variantClass, radiusClass, block ? 'w-full' : '']"
  >
    <svg v-if="loading" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
    <slot name="icon" />
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Variant = 'primary' | 'secondary' | 'ghost' | 'soft' | 'danger'
type Size = 'sm' | 'md' | 'lg'

const props = withDefaults(defineProps<{
  variant?: Variant
  size?: Size
  type?: 'button' | 'submit' | 'reset'
  block?: boolean
  loading?: boolean
  disabled?: boolean
}>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
  block: false,
  loading: false,
  disabled: false,
})

const sizeClass = computed(() => ({
  sm: 'text-xs px-3 py-1.5',
  md: 'text-sm px-4 py-2.5',
  lg: 'text-base px-5 py-3',
}[props.size]))

const variantClass = computed(() => ({
  primary: 'bg-primary text-primary-ink hover:bg-primary-strong',
  secondary: 'bg-surface text-ink border border-line hover:bg-surface-soft',
  ghost: 'text-ink-muted hover:bg-surface-soft hover:text-ink',
  soft: 'bg-primary-soft text-primary hover:brightness-95 dark:hover:brightness-125',
  danger: 'bg-transparent text-danger border border-danger hover:bg-danger-soft',
}[props.variant]))

const radiusClass = computed(() => (props.variant === 'primary' ? 'rounded-btn-primary' : 'rounded-lg'))
</script>
```

- [ ] **Étape 4 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/BaseButton.spec.ts
```
Attendu : 7/7 verts.

- [ ] **Étape 5 : commit**

```bash
git add web/tests/components/ui/base/BaseButton.spec.ts web/src/components/ui/base/BaseButton.vue
git commit -m "$(cat <<'EOF'
feat(design-system): BaseButton en Direction A (rayons, danger en outline)

EOF
)"
```

---

## Tâche 3 : BaseCard (carte)

**Files:**
- Create: `web/tests/components/ui/base/BaseCard.spec.ts`
- Modify: `web/src/components/ui/base/BaseCard.vue`

- [ ] **Étape 1 : tests (rouge)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseCard from '../../../../src/components/ui/base/BaseCard.vue'

describe('BaseCard', () => {
  it('rend le contenu du slot', () => {
    const wrapper = mount(BaseCard, { slots: { default: 'Contenu' } })
    expect(wrapper.text()).toContain('Contenu')
  })

  it('applique le rayon 8px et l\'ombre de carte par défaut', () => {
    const wrapper = mount(BaseCard)
    expect(wrapper.classes()).toContain('rounded-lg')
    expect(wrapper.classes()).toContain('shadow-elev-1')
  })

  it('applique le padding md par défaut', () => {
    const wrapper = mount(BaseCard)
    expect(wrapper.classes()).toContain('p-6')
  })

  it('applique le tag HTML donné via la prop as', () => {
    const wrapper = mount(BaseCard, { props: { as: 'article' } })
    expect(wrapper.element.tagName).toBe('ARTICLE')
  })

  it('ajoute les classes d\'interactivité seulement quand interactive est vrai', () => {
    const wrapper = mount(BaseCard, { props: { interactive: true } })
    expect(wrapper.classes()).toContain('hover:shadow-elev-2')
    const flat = mount(BaseCard)
    expect(flat.classes()).not.toContain('hover:shadow-elev-2')
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge** (`rounded-2xl` actuel ≠ `rounded-lg`)

```bash
cd web && npx vitest run tests/components/ui/base/BaseCard.spec.ts
```

- [ ] **Étape 3 : modifier `BaseCard.vue`**

Ligne 4, remplacer `rounded-2xl` par `rounded-lg` :

```vue
<template>
  <component
    :is="as"
    class="rounded-lg bg-surface border border-line shadow-elev-1"
    :class="[paddingClass, interactive ? 'transition-all duration-200 hover:-translate-y-0.5 hover:shadow-elev-2' : '']"
  >
    <slot />
  </component>
</template>
```
(le `<script>` ne change pas)

- [ ] **Étape 4 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/BaseCard.spec.ts
```

- [ ] **Étape 5 : commit**

```bash
git add web/tests/components/ui/base/BaseCard.spec.ts web/src/components/ui/base/BaseCard.vue
git commit -m "feat(design-system): BaseCard en Direction A (rayon 8px)"
```

---

## Tâche 4 : BaseBadge (badge)

**Files:**
- Create: `web/tests/components/ui/base/BaseBadge.spec.ts`
- Modify: `web/src/components/ui/base/BaseBadge.vue:25` (retrait de la valeur Tailwind arbitraire)

- [ ] **Étape 1 : tests (rouge)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseBadge from '../../../../src/components/ui/base/BaseBadge.vue'

describe('BaseBadge', () => {
  it('rend le contenu du slot', () => {
    const wrapper = mount(BaseBadge, { slots: { default: 'Nouveau' } })
    expect(wrapper.text()).toContain('Nouveau')
  })

  it('est une pilule (rayon 999px)', () => {
    const wrapper = mount(BaseBadge)
    expect(wrapper.classes()).toContain('rounded-full')
  })

  it('utilise le token text-tiny (pas de classe Tailwind arbitraire) pour la taille sm', () => {
    const wrapper = mount(BaseBadge, { props: { size: 'sm' } })
    expect(wrapper.classes()).toContain('text-tiny')
    expect(wrapper.classes().some(c => c.includes('['))).toBe(false)
  })

  it.each([
    ['neutral', 'bg-surface-soft'],
    ['primary', 'bg-primary-soft'],
    ['accent', 'bg-accent-soft'],
    ['success', 'bg-success-soft'],
    ['warning', 'bg-warning-soft'],
    ['danger', 'bg-danger-soft'],
    ['info', 'bg-info-soft'],
  ])('applique la classe de fond pour la variante %s', (variant, expectedClass) => {
    const wrapper = mount(BaseBadge, { props: { variant: variant as any } })
    expect(wrapper.classes()).toContain(expectedClass)
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge** (`text-[10px]` actuel casse le test « pas de classe arbitraire »)

```bash
cd web && npx vitest run tests/components/ui/base/BaseBadge.spec.ts
```

- [ ] **Étape 3 : modifier `BaseBadge.vue`** — ligne 25, remplacer `sm: 'text-[10px] px-2 py-0.5'` par :

```ts
const sizeClass = computed(() => ({
  sm: 'text-tiny px-2 py-0.5',
  md: 'text-xs px-2.5 py-1',
}[props.size]))
```
(reste du fichier inchangé)

- [ ] **Étape 4 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/BaseBadge.spec.ts
```

- [ ] **Étape 5 : commit**

```bash
git add web/tests/components/ui/base/BaseBadge.spec.ts web/src/components/ui/base/BaseBadge.vue
git commit -m "feat(design-system): BaseBadge — retrait de la classe Tailwind arbitraire text-[10px]"
```

---

## Tâche 5 : BaseField + BaseInput (champ)

**Files:**
- Create: `web/tests/components/ui/base/BaseField.spec.ts`, `web/tests/components/ui/base/BaseInput.spec.ts`
- Modify: `web/src/components/ui/base/BaseField.vue`, `web/src/components/ui/base/BaseInput.vue`

- [ ] **Étape 1 : tests BaseField (rouge)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseField from '../../../../src/components/ui/base/BaseField.vue'

describe('BaseField', () => {
  it('affiche le label en majuscules (fiche bristol) quand fourni', () => {
    const wrapper = mount(BaseField, { props: { label: 'Adresse email' } })
    const label = wrapper.find('label')
    expect(label.text()).toContain('Adresse email')
    expect(label.classes()).toContain('uppercase')
    expect(label.classes()).toContain('text-ink-muted')
  })

  it("n'affiche pas de label quand non fourni", () => {
    const wrapper = mount(BaseField)
    expect(wrapper.find('label').exists()).toBe(false)
  })

  it('affiche l\'astérisque quand required est vrai', () => {
    const wrapper = mount(BaseField, { props: { label: 'Nom', required: true } })
    expect(wrapper.find('label').text()).toContain('*')
  })

  it("affiche le message d'erreur en priorité sur l'indice", () => {
    const wrapper = mount(BaseField, { props: { error: 'Champ requis', hint: 'Indice' } })
    expect(wrapper.text()).toContain('Champ requis')
    expect(wrapper.text()).not.toContain('Indice')
  })

  it('affiche l\'indice quand seul hint est fourni', () => {
    const wrapper = mount(BaseField, { props: { hint: 'Format attendu : jj/mm/aaaa' } })
    expect(wrapper.text()).toContain('Format attendu')
  })

  it('rend le contenu du slot par défaut', () => {
    const wrapper = mount(BaseField, {
      slots: { default: '<input data-test="champ" />' },
    })
    expect(wrapper.find('[data-test="champ"]').exists()).toBe(true)
  })
})
```

- [ ] **Étape 2 : tests BaseInput (rouge)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseInput from '../../../../src/components/ui/base/BaseInput.vue'

describe('BaseInput', () => {
  it('applique la valeur modelValue', () => {
    const wrapper = mount(BaseInput, { props: { modelValue: 'Chimie' } })
    expect((wrapper.find('input').element as HTMLInputElement).value).toBe('Chimie')
  })

  it('émet update:modelValue à la saisie', async () => {
    const wrapper = mount(BaseInput)
    await wrapper.find('input').setValue('Droit constitutionnel')
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['Droit constitutionnel'])
  })

  it('applique le rayon 8px et le fond surface (pas surface-soft)', () => {
    const wrapper = mount(BaseInput)
    const input = wrapper.find('input')
    expect(input.classes()).toContain('rounded-lg')
    expect(input.classes()).toContain('bg-surface')
  })

  it('décale le padding et affiche l\'icône quand le slot icon est fourni', () => {
    const wrapper = mount(BaseInput, { slots: { icon: '<svg data-test="icone" />' } })
    expect(wrapper.find('[data-test="icone"]').exists()).toBe(true)
    expect(wrapper.find('input').classes()).toContain('pl-11')
  })

  it('désactive l\'input quand disabled est vrai', () => {
    const wrapper = mount(BaseInput, { props: { disabled: true } })
    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })

  it('utilise "text" comme type par défaut', () => {
    const wrapper = mount(BaseInput)
    expect(wrapper.find('input').attributes('type')).toBe('text')
  })
})
```

- [ ] **Étape 3 : lancer, vérifier le rouge**

```bash
cd web && npx vitest run tests/components/ui/base/BaseField.spec.ts tests/components/ui/base/BaseInput.spec.ts
```
Attendu : échec sur les classes du label (`text-sm font-semibold text-ink` actuel, pas
`uppercase text-ink-muted`) et sur `rounded-lg`/`bg-surface` de l'input (`rounded-xl`/
`bg-surface-soft` actuels).

- [ ] **Étape 4 : modifier `BaseField.vue`**

```vue
<template>
  <div class="space-y-1.5">
    <label v-if="label" :for="forId" class="block text-xs font-semibold uppercase tracking-wide text-ink-muted">
      {{ label }}
      <span v-if="required" class="text-danger normal-case">*</span>
    </label>
    <slot />
    <p v-if="error" class="text-xs font-medium text-danger">{{ error }}</p>
    <p v-else-if="hint" class="text-xs text-ink-muted">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label?: string
  error?: string
  hint?: string
  required?: boolean
  forId?: string
}>()
</script>
```

- [ ] **Étape 5 : modifier `BaseInput.vue`**

```vue
<template>
  <div class="relative">
    <span v-if="$slots.icon" class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-ink-subtle pointer-events-none">
      <slot name="icon" />
    </span>
    <input
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      class="w-full rounded-lg bg-surface border border-line text-sm text-ink placeholder:text-ink-subtle transition focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary/40 disabled:opacity-50"
      :class="$slots.icon ? 'pl-11 pr-4 py-2.5' : 'px-4 py-2.5'"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  modelValue?: string | number
  type?: string
  placeholder?: string
  disabled?: boolean
}>(), {
  modelValue: '',
  type: 'text',
  placeholder: '',
  disabled: false,
})

defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
```

- [ ] **Étape 6 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/BaseField.spec.ts tests/components/ui/base/BaseInput.spec.ts
```

- [ ] **Étape 7 : commit**

```bash
git add web/tests/components/ui/base/BaseField.spec.ts web/tests/components/ui/base/BaseInput.spec.ts web/src/components/ui/base/BaseField.vue web/src/components/ui/base/BaseInput.vue
git commit -m "feat(design-system): BaseField/BaseInput en Direction A (label majuscule, rayon 8px)"
```

---

## Tâche 6 : BaseModal (modale)

**Files:**
- Create: `web/tests/components/ui/base/BaseModal.spec.ts`
- Modify: `web/src/components/ui/base/BaseModal.vue`

- [ ] **Étape 1 : tests (rouge)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseModal from '../../../../src/components/ui/base/BaseModal.vue'

describe('BaseModal', () => {
  it("n'affiche pas le dialogue quand open est faux", () => {
    const wrapper = mount(BaseModal, { props: { open: false } })
    expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
  })

  it('affiche le dialogue et le titre en police display quand open est vrai', async () => {
    const wrapper = mount(BaseModal, { props: { open: true, title: 'Confirmer la suppression' } })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[role="dialog"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Confirmer la suppression')
    expect(wrapper.html()).toContain('font-display')
  })

  it('émet close au clic sur le bouton de fermeture', async () => {
    const wrapper = mount(BaseModal, { props: { open: true, title: 'X' } })
    await wrapper.vm.$nextTick()
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('applique la classe de taille correspondant à la prop size', async () => {
    const wrapper = mount(BaseModal, { props: { open: true, size: 'lg' } })
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('max-w-lg')
  })

  it('affiche le pied de page quand le slot footer est fourni', async () => {
    const wrapper = mount(BaseModal, {
      props: { open: true },
      slots: { footer: '<button>OK</button>' },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('OK')
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge** (pas de `font-display` sur le titre actuellement)

```bash
cd web && npx vitest run tests/components/ui/base/BaseModal.spec.ts
```

- [ ] **Étape 3 : modifier `BaseModal.vue`** — ligne 20 (`rounded-3xl` → `rounded-xl`) et ligne 24 (ajout `font-display`) :

```vue
<template>
  <TransitionRoot :show="open" as="template">
    <Dialog as="div" class="relative z-50" @close="$emit('close')">
      <TransitionChild
        as="template"
        enter="duration-200 ease-out" enter-from="opacity-0" enter-to="opacity-100"
        leave="duration-150 ease-in" leave-from="opacity-100" leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-ink/40 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="duration-200 ease-out" enter-from="opacity-0 scale-96" enter-to="opacity-100 scale-100"
            leave="duration-150 ease-in" leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-96"
          >
            <DialogPanel
              class="w-full rounded-xl bg-surface border border-line shadow-elev-3 p-6 text-left align-middle"
              :class="sizeClass"
            >
              <div v-if="title || $slots.title" class="flex items-start justify-between gap-4 mb-4">
                <DialogTitle class="text-lg font-display font-bold text-ink">
                  <slot name="title">{{ title }}</slot>
                </DialogTitle>
                <button
                  type="button"
                  class="p-1.5 -mr-1 -mt-1 rounded-lg text-ink-subtle hover:text-ink hover:bg-surface-soft transition-colors"
                  @click="$emit('close')"
                >
                  <X class="w-5 h-5" />
                </button>
              </div>

              <slot />

              <div v-if="$slots.footer" class="mt-6 flex items-center justify-end gap-2">
                <slot name="footer" />
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { X } from '@lucide/vue'

type Size = 'sm' | 'md' | 'lg' | 'xl'

const props = withDefaults(defineProps<{
  open: boolean
  title?: string
  size?: Size
}>(), {
  size: 'md',
})

defineEmits<{ close: [] }>()

const sizeClass = computed(() => ({
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-2xl',
}[props.size]))
</script>

<style scoped>
.scale-96 { transform: scale(0.96); }
</style>
```

- [ ] **Étape 4 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/BaseModal.spec.ts
```

- [ ] **Étape 5 : commit**

```bash
git add web/tests/components/ui/base/BaseModal.spec.ts web/src/components/ui/base/BaseModal.vue
git commit -m "feat(design-system): BaseModal en Direction A (rayon 12px, titre en Bitter)"
```

---

## Tâche 7 : Tabs (onglet)

**Files:**
- Create: `web/tests/components/ui/base/Tabs.spec.ts`
- Modify: `web/src/components/ui/base/Tabs.vue`

- [ ] **Étape 1 : tests (rouge)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Tabs from '../../../../src/components/ui/base/Tabs.vue'

const tabs = [
  { key: 'teacher', label: 'Enseignant' },
  { key: 'groups', label: 'Groupes', badge: 3 },
]

describe('Tabs', () => {
  it('affiche tous les onglets fournis', () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs } })
    expect(wrapper.text()).toContain('Enseignant')
    expect(wrapper.text()).toContain('Groupes')
  })

  it('marque l\'onglet actif en pilule pleine indigo (fond primary, texte primary-ink)', () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs } })
    const buttons = wrapper.findAll('button')
    expect(buttons[0].classes()).toContain('bg-primary')
    expect(buttons[0].classes()).toContain('text-primary-ink')
    expect(buttons[0].classes()).toContain('rounded-full')
    expect(buttons[1].classes()).not.toContain('bg-primary')
  })

  it('émet update:modelValue avec la clé au clic', async () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs } })
    await wrapper.findAll('button')[1].trigger('click')
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['groups'])
  })

  it('affiche le badge avec le token text-tiny quand fourni et non vide', () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs } })
    const badge = wrapper.findAll('button')[1].find('span')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toBe('3')
    expect(badge.classes()).toContain('text-tiny')
  })

  it('masque le badge quand il vaut null/undefined/chaîne vide', () => {
    const wrapper = mount(Tabs, { props: { modelValue: 'teacher', tabs: [{ key: 'a', label: 'A' }] } })
    expect(wrapper.find('button span').exists()).toBe(false)
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge**

```bash
cd web && npx vitest run tests/components/ui/base/Tabs.spec.ts
```

- [ ] **Étape 3 : modifier `Tabs.vue`**

```vue
<template>
  <div class="inline-flex items-center gap-1 flex-wrap max-w-full">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      class="inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-semibold whitespace-nowrap transition-all duration-200"
      :class="tab.key === modelValue
        ? 'bg-primary text-primary-ink'
        : 'text-ink-muted hover:text-ink hover:bg-surface-soft'"
      @click="$emit('update:modelValue', tab.key)"
    >
      <component :is="tab.icon" v-if="tab.icon" class="w-4 h-4" />
      {{ tab.label }}
      <span
        v-if="tab.badge !== undefined && tab.badge !== null && tab.badge !== ''"
        class="ml-0.5 rounded-full px-1.5 py-0.5 text-tiny font-bold"
        :class="tab.key === modelValue ? 'bg-primary-ink/20 text-primary-ink' : 'bg-surface-soft text-ink-muted'"
      >{{ tab.badge }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

export interface TabItem {
  key: string
  label: string
  icon?: Component
  badge?: string | number | null
}

defineProps<{
  modelValue: string
  tabs: TabItem[]
}>()

defineEmits<{ 'update:modelValue': [key: string] }>()
</script>
```

- [ ] **Étape 4 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/Tabs.spec.ts
```

- [ ] **Étape 5 : commit**

```bash
git add web/tests/components/ui/base/Tabs.spec.ts web/src/components/ui/base/Tabs.vue
git commit -m "feat(design-system): Tabs en Direction A (pilules pleines, cohérent avec la nav)"
```

---

## Tâche 8 : BaseTooltip — nouveau (info-bulle)

**Files:**
- Create: `web/tests/components/ui/base/BaseTooltip.spec.ts`
- Create: `web/src/components/ui/base/BaseTooltip.vue`
- Modify: `web/src/components/ui/base/index.ts` (export)

**Interfaces:**
- Produces: `<BaseTooltip content="..." placement="top|bottom|left|right">` avec slot par défaut = élément déclencheur. Pas de dépendance externe ajoutée (pas de floating-ui/tippy — positionnement CSS pur, cohérent avec le reste des primitives qui n'ajoutent pas de lib de positionnement).

- [ ] **Étape 1 : tests (rouge — le composant n'existe pas)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseTooltip from '../../../../src/components/ui/base/BaseTooltip.vue'

describe('BaseTooltip', () => {
  it('ne montre pas la bulle par défaut', () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'Facteur de facilité' }, slots: { default: '<span>i</span>' } })
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(false)
  })

  it('montre la bulle avec son contenu au survol', async () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'Facteur de facilité' }, slots: { default: '<span>i</span>' } })
    await wrapper.trigger('mouseenter')
    const tooltip = wrapper.find('[role="tooltip"]')
    expect(tooltip.exists()).toBe(true)
    expect(tooltip.text()).toBe('Facteur de facilité')
  })

  it('masque la bulle quand la souris quitte', async () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'X' }, slots: { default: '<span>i</span>' } })
    await wrapper.trigger('mouseenter')
    await wrapper.trigger('mouseleave')
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(false)
  })

  it('montre la bulle au focus clavier et la masque au blur', async () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'X' }, slots: { default: '<span tabindex="0">i</span>' } })
    await wrapper.trigger('focusin')
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(true)
    await wrapper.trigger('focusout')
    expect(wrapper.find('[role="tooltip"]').exists()).toBe(false)
  })

  it('applique la classe de positionnement correspondant à placement="bottom"', async () => {
    const wrapper = mount(BaseTooltip, { props: { content: 'X', placement: 'bottom' }, slots: { default: '<span>i</span>' } })
    await wrapper.trigger('mouseenter')
    expect(wrapper.find('[role="tooltip"]').classes()).toContain('top-full')
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge** (`Failed to resolve import` — fichier absent)

```bash
cd web && npx vitest run tests/components/ui/base/BaseTooltip.spec.ts
```

- [ ] **Étape 3 : créer `BaseTooltip.vue`**

```vue
<template>
  <span class="relative inline-flex" @mouseenter="show" @mouseleave="hide" @focusin="show" @focusout="hide">
    <span :aria-describedby="tooltipId">
      <slot />
    </span>
    <span
      v-if="visible"
      :id="tooltipId"
      role="tooltip"
      class="absolute z-50 whitespace-nowrap rounded bg-ink text-app text-xs font-medium px-2.5 py-1.5 pointer-events-none"
      :class="placementClass"
    >
      {{ content }}
    </span>
  </span>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

type Placement = 'top' | 'bottom' | 'left' | 'right'

const props = withDefaults(defineProps<{
  content: string
  placement?: Placement
}>(), {
  placement: 'top',
})

const visible = ref(false)
const tooltipId = `tooltip-${Math.random().toString(36).slice(2, 9)}`

function show() { visible.value = true }
function hide() { visible.value = false }

const placementClass = computed(() => ({
  top: 'bottom-full left-1/2 -translate-x-1/2 mb-1.5',
  bottom: 'top-full left-1/2 -translate-x-1/2 mt-1.5',
  left: 'right-full top-1/2 -translate-y-1/2 mr-1.5',
  right: 'left-full top-1/2 -translate-y-1/2 ml-1.5',
}[props.placement]))
</script>
```

- [ ] **Étape 4 : exporter dans `index.ts`** — ajouter après la ligne `BaseToggle` :

```ts
export { default as BaseTooltip } from './BaseTooltip.vue'
```

- [ ] **Étape 5 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/BaseTooltip.spec.ts
```

- [ ] **Étape 6 : commit**

```bash
git add web/tests/components/ui/base/BaseTooltip.spec.ts web/src/components/ui/base/BaseTooltip.vue web/src/components/ui/base/index.ts
git commit -m "feat(design-system): ajout de BaseTooltip (info-bulle, primitive manquante phase 3)"
```

---

## Tâche 9 : BaseEmptyState (état vide)

**Files:**
- Create: `web/tests/components/ui/base/BaseEmptyState.spec.ts`
- Modify: `web/src/components/ui/base/BaseEmptyState.vue`

- [ ] **Étape 1 : tests (rouge)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseEmptyState from '../../../../src/components/ui/base/BaseEmptyState.vue'

describe('BaseEmptyState', () => {
  it('affiche le titre en police display', () => {
    const wrapper = mount(BaseEmptyState, { props: { title: 'Aucune fiche à réviser' } })
    expect(wrapper.text()).toContain('Aucune fiche à réviser')
    expect(wrapper.html()).toContain('font-display')
  })

  it('affiche la description quand fournie', () => {
    const wrapper = mount(BaseEmptyState, { props: { title: 'X', description: 'Ajoutez votre premier deck.' } })
    expect(wrapper.text()).toContain('Ajoutez votre premier deck.')
  })

  it('affiche l\'icône dans un cercle en pointillés quand le slot icon est fourni', () => {
    const wrapper = mount(BaseEmptyState, {
      props: { title: 'X' },
      slots: { icon: '<svg data-test="icone" />' },
    })
    const holder = wrapper.find('[data-test="icone"]').element.parentElement
    expect(holder?.className).toContain('rounded-full')
    expect(holder?.className).toContain('border-dashed')
  })

  it('masque le conteneur d\'icône quand le slot icon est absent', () => {
    const wrapper = mount(BaseEmptyState, { props: { title: 'X' } })
    expect(wrapper.find('.border-dashed').exists()).toBe(false)
  })

  it('affiche les actions quand le slot actions est fourni', () => {
    const wrapper = mount(BaseEmptyState, {
      props: { title: 'X' },
      slots: { actions: '<button>Créer un deck</button>' },
    })
    expect(wrapper.text()).toContain('Créer un deck')
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge** (structure actuelle = rectangle en pointillés `rounded-3xl`, pas de cercle, pas de `font-display`)

```bash
cd web && npx vitest run tests/components/ui/base/BaseEmptyState.spec.ts
```

- [ ] **Étape 3 : réécrire `BaseEmptyState.vue`**

```vue
<template>
  <div class="flex flex-col items-center text-center gap-3.5 py-14 px-6">
    <div v-if="$slots.icon" class="flex items-center justify-center w-14 h-14 rounded-full border-2 border-dashed border-line text-ink-subtle">
      <slot name="icon" />
    </div>
    <div>
      <p class="font-display font-bold text-base text-ink mb-1">{{ title }}</p>
      <p v-if="description" class="text-meta text-ink-muted max-w-xs mx-auto">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="mt-2 flex items-center gap-2">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>
```

- [ ] **Étape 4 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/BaseEmptyState.spec.ts
```

- [ ] **Étape 5 : commit**

```bash
git add web/tests/components/ui/base/BaseEmptyState.spec.ts web/src/components/ui/base/BaseEmptyState.vue
git commit -m "feat(design-system): BaseEmptyState en Direction A (icône en cercle pointillé, titre Bitter)"
```

---

## Tâche 10 : BaseSkeleton (squelette de chargement)

**Files:**
- Create: `web/tests/components/ui/base/BaseSkeleton.spec.ts`
- Modify: `web/src/components/ui/base/BaseSkeleton.vue`

- [ ] **Étape 1 : tests (rouge)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseSkeleton from '../../../../src/components/ui/base/BaseSkeleton.vue'

describe('BaseSkeleton', () => {
  it('applique le rayon 8px par défaut (cohérent avec les cartes)', () => {
    const wrapper = mount(BaseSkeleton)
    expect(wrapper.classes()).toContain('rounded-lg')
  })

  it('applique le rayon fourni via la prop rounded', () => {
    const wrapper = mount(BaseSkeleton, { props: { rounded: 'rounded-full' } })
    expect(wrapper.classes()).toContain('rounded-full')
    expect(wrapper.classes()).not.toContain('rounded-lg')
  })

  it('applique la classe de taille par défaut', () => {
    const wrapper = mount(BaseSkeleton)
    expect(wrapper.classes()).toContain('h-4')
    expect(wrapper.classes()).toContain('w-full')
  })

  it('applique la classe de taille fournie via customClass', () => {
    const wrapper = mount(BaseSkeleton, { props: { customClass: 'h-10 w-10' } })
    expect(wrapper.classes()).toContain('h-10')
    expect(wrapper.classes()).toContain('w-10')
  })

  it('porte l\'animation de pulsation', () => {
    const wrapper = mount(BaseSkeleton)
    expect(wrapper.classes()).toContain('animate-pulse')
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge** (défaut actuel `rounded-xl` = 12px)

```bash
cd web && npx vitest run tests/components/ui/base/BaseSkeleton.spec.ts
```

- [ ] **Étape 3 : modifier `BaseSkeleton.vue`** — changer la valeur par défaut de `rounded` :

```vue
<template>
  <div class="animate-pulse bg-surface-soft" :class="[rounded, customClass]" />
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  rounded?: string
  customClass?: string
}>(), {
  rounded: 'rounded-lg',
  customClass: 'h-4 w-full',
})
</script>
```

- [ ] **Étape 4 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/BaseSkeleton.spec.ts
```

- [ ] **Étape 5 : commit**

```bash
git add web/tests/components/ui/base/BaseSkeleton.spec.ts web/src/components/ui/base/BaseSkeleton.vue
git commit -m "feat(design-system): BaseSkeleton en Direction A (rayon 8px par défaut)"
```

---

## Tâche 11 : BaseToast — nouveau (toast)

**Files:**
- Create: `web/tests/components/ui/base/BaseToast.spec.ts`
- Create: `web/src/components/ui/base/BaseToast.vue`
- Modify: `web/src/components/ui/base/index.ts` (export)

**Interfaces:**
- Produces: `<BaseToast variant="info|success|warning|danger" title? message? closable @close>`.
  Primitive présentationnelle uniquement — la file d'attente/l'orchestration globale
  (`useToast()` composable + conteneur monté dans `App.vue`) n'est **pas** dans ce plan :
  elle sera câblée en phase 4 quand un premier écran migré en aura réellement besoin
  (cohérent avec `components/ui/` = présentationnel pur, aucun état applicatif).

- [ ] **Étape 1 : tests (rouge — le composant n'existe pas)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseToast from '../../../../src/components/ui/base/BaseToast.vue'

describe('BaseToast', () => {
  it('affiche le message fourni en prop', () => {
    const wrapper = mount(BaseToast, { props: { message: 'Deck enregistré.' } })
    expect(wrapper.text()).toContain('Deck enregistré.')
  })

  it('affiche le titre quand fourni', () => {
    const wrapper = mount(BaseToast, { props: { title: 'Enregistré', message: 'Deck mis à jour.' } })
    expect(wrapper.text()).toContain('Enregistré')
  })

  it('applique la classe de fond correspondant à variant="danger"', () => {
    const wrapper = mount(BaseToast, { props: { variant: 'danger', message: 'Échec de la synchronisation.' } })
    expect(wrapper.classes()).toContain('bg-danger-soft')
  })

  it('utilise info comme variante par défaut', () => {
    const wrapper = mount(BaseToast, { props: { message: 'X' } })
    expect(wrapper.classes()).toContain('bg-primary-soft')
  })

  it('affiche le bouton de fermeture par défaut et émet close au clic', async () => {
    const wrapper = mount(BaseToast, { props: { message: 'X' } })
    const closeBtn = wrapper.find('button[aria-label="Fermer"]')
    expect(closeBtn.exists()).toBe(true)
    await closeBtn.trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('masque le bouton de fermeture quand closable est faux', () => {
    const wrapper = mount(BaseToast, { props: { message: 'X', closable: false } })
    expect(wrapper.find('button[aria-label="Fermer"]').exists()).toBe(false)
  })

  it('expose role="status" pour l\'accessibilité', () => {
    const wrapper = mount(BaseToast, { props: { message: 'X' } })
    expect(wrapper.attributes('role')).toBe('status')
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge**

```bash
cd web && npx vitest run tests/components/ui/base/BaseToast.spec.ts
```

- [ ] **Étape 3 : créer `BaseToast.vue`**

```vue
<template>
  <div role="status" aria-live="polite" class="flex items-start gap-3 rounded-lg border p-4 shadow-elev-2" :class="variantClass">
    <component :is="icon" class="w-5 h-5 flex-shrink-0 mt-0.5" />
    <div class="flex-1 min-w-0">
      <p v-if="title" class="text-sm font-bold">{{ title }}</p>
      <p class="text-sm" :class="title ? 'mt-0.5' : ''"><slot>{{ message }}</slot></p>
    </div>
    <button
      v-if="closable"
      type="button"
      class="flex-shrink-0 -mr-1 -mt-1 p-1 rounded hover:bg-black/5 dark:hover:bg-white/5"
      aria-label="Fermer"
      @click="$emit('close')"
    >
      <X class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from '@lucide/vue'

type Variant = 'info' | 'success' | 'warning' | 'danger'

const props = withDefaults(defineProps<{
  variant?: Variant
  title?: string
  message?: string
  closable?: boolean
}>(), {
  variant: 'info',
  closable: true,
})

defineEmits<{ close: [] }>()

const variantClass = computed(() => ({
  info: 'bg-primary-soft border-primary/30 text-primary',
  success: 'bg-success-soft border-success/30 text-success',
  warning: 'bg-accent-soft border-accent/30 text-accent',
  danger: 'bg-danger-soft border-danger/30 text-danger',
}[props.variant]))

const icon = computed(() => ({
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  danger: XCircle,
}[props.variant]))
</script>
```

Si un des noms d'icône `@lucide/vue` (`CheckCircle2`, `AlertTriangle`, `XCircle`, `Info`, `X`)
n'existe pas dans la version installée, l'échec de build TypeScript le signale immédiatement
— remplacer par l'équivalent disponible dans `node_modules/@lucide/vue/dist/...` sans changer
le comportement testé (le test ne dépend pas du nom d'icône, seulement de sa présence).

- [ ] **Étape 4 : exporter dans `index.ts`**

```ts
export { default as BaseToast } from './BaseToast.vue'
```

- [ ] **Étape 5 : vérifier le vert**

```bash
cd web && npx vitest run tests/components/ui/base/BaseToast.spec.ts
```

- [ ] **Étape 6 : commit**

```bash
git add web/tests/components/ui/base/BaseToast.spec.ts web/src/components/ui/base/BaseToast.vue web/src/components/ui/base/index.ts
git commit -m "feat(design-system): ajout de BaseToast (primitive manquante phase 3)"
```

---

## Tâche 12 : Page de démonstration + vérification visuelle

**Files:**
- Create: `web/tests/views/DesignSystemDemo.spec.ts`
- Create: `web/src/views/Dev/DesignSystemDemo.vue`
- Modify: `web/src/router/index.ts` (nouvelle route, dans le bloc `AppLayout` children — après la route `Accueil`)

**Interfaces:**
- Consumes: les 10 primitives (Tâches 2–11) via `@/components/ui/base`.

- [ ] **Étape 1 : test (rouge — le composant n'existe pas)**

```ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DesignSystemDemo from '../../src/views/Dev/DesignSystemDemo.vue'

describe('DesignSystemDemo', () => {
  it('bascule la classe "dark" sur <html> au clic sur le bouton de thème', async () => {
    document.documentElement.classList.remove('dark')
    const wrapper = mount(DesignSystemDemo)
    const toggle = wrapper.find('[data-test="toggle-theme"]')
    expect(toggle.exists()).toBe(true)

    await toggle.trigger('click')
    expect(document.documentElement.classList.contains('dark')).toBe(true)

    await toggle.trigger('click')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('affiche au moins un exemple de chacune des 10 primitives de la checklist phase 3', () => {
    const wrapper = mount(DesignSystemDemo)
    const html = wrapper.html()
    // Un marqueur data-demo par section suffit à garantir qu'aucune n'a été oubliée.
    for (const name of ['bouton', 'champ', 'carte', 'modale', 'onglet', 'badge', 'info-bulle', 'etat-vide', 'squelette', 'toast']) {
      expect(wrapper.find(`[data-demo="${name}"]`).exists()).toBe(true)
    }
  })
})
```

- [ ] **Étape 2 : lancer, vérifier le rouge**

```bash
cd web && npx vitest run tests/views/DesignSystemDemo.spec.ts
```

- [ ] **Étape 3 : créer `web/src/views/Dev/DesignSystemDemo.vue`**

```vue
<template>
  <PageContainer>
    <PageHeader title="Design System — Direction A « Fiche »">
      <template #actions>
        <BaseButton data-test="toggle-theme" variant="secondary" size="sm" @click="toggleDark">
          {{ isDark ? 'Thème clair' : 'Thème sombre' }}
        </BaseButton>
      </template>
    </PageHeader>

    <section data-demo="bouton" class="space-y-3">
      <h2 class="font-display text-display-md">Boutons</h2>
      <div class="flex flex-wrap items-center gap-3">
        <BaseButton variant="primary">Primaire</BaseButton>
        <BaseButton variant="secondary">Secondaire</BaseButton>
        <BaseButton variant="ghost">Discret</BaseButton>
        <BaseButton variant="soft">Doux</BaseButton>
        <BaseButton variant="danger">Supprimer</BaseButton>
        <BaseButton variant="primary" loading>Chargement</BaseButton>
        <BaseButton variant="primary" disabled>Désactivé</BaseButton>
      </div>
    </section>

    <section data-demo="champ" class="space-y-3 max-w-sm">
      <h2 class="font-display text-display-md">Champs</h2>
      <BaseField label="Matière" hint="Ex. Chimie organique">
        <BaseInput v-model="demoInput" placeholder="Chimie organique" />
      </BaseField>
      <BaseField label="Email" required error="Adresse invalide">
        <BaseInput v-model="demoInput" type="email" />
      </BaseField>
    </section>

    <section data-demo="carte" class="space-y-3">
      <h2 class="font-display text-display-md">Cartes</h2>
      <div class="grid grid-cols-2 gap-4 max-w-lg">
        <BaseCard>Carte statique</BaseCard>
        <BaseCard interactive>Carte interactive (survol)</BaseCard>
      </div>
    </section>

    <section data-demo="badge" class="space-y-3">
      <h2 class="font-display text-display-md">Badges</h2>
      <div class="flex flex-wrap gap-2">
        <BaseBadge variant="neutral">Neutre</BaseBadge>
        <BaseBadge variant="primary">Primaire</BaseBadge>
        <BaseBadge variant="accent">Accent</BaseBadge>
        <BaseBadge variant="success">Succès</BaseBadge>
        <BaseBadge variant="danger">Danger</BaseBadge>
        <BaseBadge size="sm" variant="info">Petit</BaseBadge>
      </div>
    </section>

    <section data-demo="onglet" class="space-y-3">
      <h2 class="font-display text-display-md">Onglets</h2>
      <Tabs v-model="activeTab" :tabs="[{ key: 'a', label: 'Enseignant' }, { key: 'b', label: 'Groupes', badge: 3 }]" />
    </section>

    <section data-demo="info-bulle" class="space-y-3">
      <h2 class="font-display text-display-md">Info-bulle</h2>
      <BaseTooltip content="Facteur de facilité SM2 : 2.5 par défaut">
        <span class="underline decoration-dotted cursor-help text-sm">Survoler ce texte</span>
      </BaseTooltip>
    </section>

    <section data-demo="etat-vide" class="space-y-3">
      <h2 class="font-display text-display-md">État vide</h2>
      <BaseCard>
        <BaseEmptyState title="Aucune fiche à réviser" description="Revenez demain, ou ajoutez un nouveau deck.">
          <template #actions>
            <BaseButton size="sm">Créer un deck</BaseButton>
          </template>
        </BaseEmptyState>
      </BaseCard>
    </section>

    <section data-demo="squelette" class="space-y-3 max-w-sm">
      <h2 class="font-display text-display-md">Squelette de chargement</h2>
      <div class="space-y-2">
        <BaseSkeleton custom-class="h-4 w-3/4" />
        <BaseSkeleton custom-class="h-4 w-full" />
        <BaseSkeleton rounded="rounded-full" custom-class="h-10 w-10" />
      </div>
    </section>

    <section data-demo="toast" class="space-y-3 max-w-sm">
      <h2 class="font-display text-display-md">Toasts</h2>
      <div class="space-y-2">
        <BaseToast variant="success" title="Enregistré" message="Le deck a été mis à jour." />
        <BaseToast variant="danger" title="Échec" message="La synchronisation a échoué." />
      </div>
    </section>

    <section data-demo="modale" class="space-y-3">
      <h2 class="font-display text-display-md">Modale</h2>
      <BaseButton @click="modalOpen = true">Ouvrir la modale</BaseButton>
      <BaseModal :open="modalOpen" title="Supprimer ce deck ?" @close="modalOpen = false">
        <p class="text-sm text-ink-muted">Cette action est irréversible.</p>
        <template #footer>
          <BaseButton variant="secondary" @click="modalOpen = false">Annuler</BaseButton>
          <BaseButton variant="danger" @click="modalOpen = false">Supprimer</BaseButton>
        </template>
      </BaseModal>
    </section>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  BaseButton, BaseCard, BaseBadge, BaseField, BaseInput, BaseModal,
  BaseEmptyState, BaseSkeleton, BaseToast, BaseTooltip, Tabs,
  PageContainer, PageHeader,
} from '@/components/ui/base'

const isDark = ref(document.documentElement.classList.contains('dark'))
const demoInput = ref('')
const activeTab = ref('a')
const modalOpen = ref(false)

function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}
</script>
```

- [ ] **Étape 4 : ajouter la route** — dans `web/src/router/index.ts`, dans le tableau `children`
du bloc `AppLayout` (après la route `Accueil`, ligne 55) :

```ts
      {
        path: 'dev/design-system',
        name: 'DevDesignSystem',
        component: () => import('../views/Dev/DesignSystemDemo.vue'),
        meta: { requiresAuth: true }
      },
```

- [ ] **Étape 5 : vérifier le vert, le build, et visuellement**

```bash
cd web && npx vitest run tests/views/DesignSystemDemo.spec.ts && npm run build
npm run dev -- --port 3000
```

Naviguer vers `http://localhost:3000/dev/design-system`, se connecter, basculer clair/sombre,
comparer visuellement aux 33 écrans du canevas (palette, rayons, typo Bitter/Karla/Space Mono
bien chargées). Capturer une capture d'écran clair + sombre (n'importe quel outil, ex.
`mcp__claude-in-chrome__computer` `screenshot`) pour trace dans la passation.

- [ ] **Étape 6 : commit**

```bash
git add web/tests/views/DesignSystemDemo.spec.ts web/src/views/Dev/DesignSystemDemo.vue web/src/router/index.ts
git commit -m "feat(design-system): page de démonstration interne des 10 primitives"
```

---

## Tâche 13 : Hook de détection de valeurs brutes sur les primitives

**Files:**
- Create: `.claude/hooks/raw_value_guard.py`
- Modify: `.claude/settings.json:130-151` (bloc `PostToolUse`)

**Interfaces:**
- Produces: hook `PostToolUse` non bloquant (même contrat que `no_debug.py` : lit
  `tool_name`/`tool_input.{content,new_string,edits[].new_string}` sur stdin JSON, imprime
  `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": ...}}` s'il
  trouve une valeur brute, silencieux sinon).

- [ ] **Étape 1 : créer `.claude/hooks/raw_value_guard.py`**

```python
#!/usr/bin/env python3
"""PostToolUse hook — signale les valeurs de style brutes dans les primitives UI
(CLAUDE.md : #rrggbb / rgb(...) / px hors 0-1px / classe Tailwind arbitraire [...] interdits).

Non bloquant : injecte un avertissement dans le contexte de Claude via additionalContext.
Cible uniquement web/src/components/ui/ (primitives) — le reste de l'app n'est pas encore
migre vers Direction A (phase 4, skill migration-ecran) et peut legitimement contenir des
valeurs non tokenisees jusqu'a sa migration ecran par ecran.
"""
import json
import re
import sys

HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
RGB_FUNC = re.compile(r"\brgba?\(\s*\d")
ARBITRARY_TAILWIND = re.compile(
    r"\b(?:bg|text|border|shadow|rounded|w|h|p|m|gap|top|left|right|bottom|inset)-\[[^\]]+\]"
)
RAW_PX = re.compile(r"\b(?:[2-9]|\d{2,})px\b")


def is_ui_primitive(path: str) -> bool:
    norm = path.replace("\\", "/")
    return "/web/src/components/ui/" in norm and norm.endswith(".vue")


def new_text(tool_input: dict) -> str:
    parts = []
    if "content" in tool_input:
        parts.append(tool_input["content"])
    if "new_string" in tool_input:
        parts.append(tool_input["new_string"])
    for edit in tool_input.get("edits", []) or []:
        if isinstance(edit, dict) and "new_string" in edit:
            parts.append(edit["new_string"])
    return "\n".join(p for p in parts if isinstance(p, str))


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    tool_input = payload.get("tool_input", {}) or {}
    path = tool_input.get("file_path", "") or ""
    if not is_ui_primitive(path):
        sys.exit(0)

    text = new_text(tool_input)
    if not text:
        sys.exit(0)

    hits = []
    for line in text.splitlines():
        stripped = line.strip()
        if (HEX_COLOR.search(stripped) or RGB_FUNC.search(stripped)
                or ARBITRARY_TAILWIND.search(stripped) or RAW_PX.search(stripped)):
            hits.append(stripped)

    if not hits:
        sys.exit(0)

    preview = "\n".join(f"  • {h}" for h in hits[:5])
    msg = (
        f"⚠️ Valeur de style brute détectée dans {path} — interdit sur une primitive "
        f"(CLAUDE.md : #rrggbb / rgb(...) / px hors 0-1px / classe Tailwind arbitraire).\n"
        f"{preview}\n"
        "Remplace par un token (couleur sémantique, rounded-*, text-*, espacement standard)."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": msg,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [ ] **Étape 2 : câbler dans `.claude/settings.json`** — ajouter dans le tableau `hooks` du
bloc `PostToolUse` (après l'entrée `no_debug.py`, avant `no_secrets.py`) :

```json
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/raw_value_guard.py\""
          },
```

- [ ] **Étape 3 : vérifier manuellement (pas de suite pytest dédiée aux hooks dans ce dépôt — vérification directe comme en phase 1)**

```bash
cd "C:\Users\denoe\Documents\Projets\StudyHub"
echo '{"tool_name":"Edit","tool_input":{"file_path":"web/src/components/ui/base/BaseButton.vue","new_string":"background:#F06292;"}}' | python .claude/hooks/raw_value_guard.py
```
Attendu : une ligne JSON avec `additionalContext` mentionnant `#F06292`.

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"web/src/views/Home/Accueil.vue","new_string":"background:#F06292;"}}' | python .claude/hooks/raw_value_guard.py
```
Attendu : aucune sortie (hors périmètre `components/ui/`, silence normal en phase 3).

```bash
cat web/src/components/ui/base/*.vue | python -c "
import sys, json
sys.path.insert(0, '.claude/hooks')
from raw_value_guard import HEX_COLOR, RGB_FUNC, ARBITRARY_TAILWIND, RAW_PX
text = sys.stdin.read()
hits = [l.strip() for l in text.splitlines() if HEX_COLOR.search(l) or RGB_FUNC.search(l) or ARBITRARY_TAILWIND.search(l) or RAW_PX.search(l)]
print(f'{len(hits)} valeur(s) brute(s) restante(s) sur les primitives déjà migrées')
for h in hits: print(' ', h)
"
```
Attendu (critère d'acceptation checklist ETAT.md) : **0 valeur brute** sur les 10 primitives
traitées par les Tâches 2–11 (`BaseToggle`/`ListRow`/`PageContainer`/`PageHeader`/`SplitView`/
`StatCard`, non retouchées par ce plan, peuvent encore en contenir — attendu, hors périmètre).

- [ ] **Étape 4 : commit**

```bash
git add .claude/hooks/raw_value_guard.py .claude/settings.json
git commit -m "$(cat <<'EOF'
feat(hooks): garde de détection de valeurs de style brutes sur les primitives UI

Avertit (non bloquant) si une couleur hex/rgb(), un px hors 0-1px, ou une classe
Tailwind arbitraire apparaît dans web/src/components/ui/ — cible uniquement les
primitives, le reste de l'app se migre écran par écran en phase 4.
EOF
)"
```

---

## Tâche 14 : Skill `design-system` + mise à jour de la documentation

**Files:**
- Create: `.claude/skills/design-system/SKILL.md`
- Modify: `.claude/skills/frontend-patterns/SKILL.md` (section « Design system »)
- Modify: `web/CLAUDE.md`, `web/src/components/CLAUDE.md` (pointeurs vers la nouvelle skill)
- Modify: `ETAT.md` (cocher la checklist phase 3, section « Round de direction »)
- Modify: `docs/development_journal.md` (entrée de session)

- [ ] **Étape 1 : créer `.claude/skills/design-system/SKILL.md`**

```markdown
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
```

- [ ] **Étape 2 : mettre à jour `.claude/skills/frontend-patterns/SKILL.md`** — remplacer
la section « Design system — « White/Pink × Material épuré » » (et sa note « ⚠️ danger =
rouge... ») par :

```markdown
## Design system — Direction A « Fiche »

Détail complet (palette, typo, rayons, ombres, primitives) : skill `design-system`
(`.claude/skills/design-system/SKILL.md`), à charger avant de toucher un token ou une
primitive. Résumé : couleurs = tokens sémantiques (`bg-app`, `bg-surface`, `border-line`,
`text-ink/-muted`, `bg-primary` encre indigo, `bg-accent` rehaut ocre) — jamais de couleur
brute dans une vue nouvellement écrite. `danger` = brique = erreur/destruction uniquement.
Formes : cartes/inputs `rounded-lg` (8px), boutons primaires `rounded-btn-primary` (10px),
pilules/badges/onglets `rounded-full`. Élévation `shadow-elev-1/2/3`, CTA
`shadow-elev-primary`. Police display (titres) = Bitter, corps = Karla, données = Space Mono.
```

- [ ] **Étape 3 : mettre à jour les pointeurs**

Dans `web/CLAUDE.md` et `web/src/components/CLAUDE.md`, remplacer la mention « sera
complétée par la skill `design-system` à partir de la phase 3 » par « voir skill
`design-system` » (la skill existe désormais).

- [ ] **Étape 4 : cocher la checklist phase 3 dans `ETAT.md`**

Cocher les items « Tokens Tailwind », « Primitives développées en TDD », « Page de
démonstration interne... », « Skill `.claude/skills/design-system/SKILL.md` rédigée »,
« Hook de détection de valeurs brutes » et ajouter une entrée sous « Round de direction »
résumant l'exécution de ce plan (date, tâches, commits).

- [ ] **Étape 5 : entrée de journal**

Ajouter une entrée datée dans `docs/development_journal.md` résumant le passage White/Pink
→ Direction A « Fiche » (tokens, 10 primitives, démo, hook, skill).

- [ ] **Étape 6 : vérification finale globale**

```bash
cd web && npm run test:run && npm run build
```
Attendu : suite complète verte (y compris les nouveaux tests), build sans erreur TypeScript.

- [ ] **Étape 7 : commit**

```bash
git add .claude/skills/design-system/SKILL.md .claude/skills/frontend-patterns/SKILL.md web/CLAUDE.md web/src/components/CLAUDE.md ETAT.md docs/development_journal.md
git commit -m "$(cat <<'EOF'
docs(design-system): skill design-system, checklist phase 3 complétée

Documente le résultat des tâches 1-13 (tokens, 10 primitives, démo, hook) et
met à jour les pointeurs frontend-patterns/CLAUDE.md vers la nouvelle skill.
EOF
)"
```

---

## Self-Review

**Couverture de la spec (checklist phase 3, `ETAT.md`) :**
- Tokens Tailwind (couleur/espacement/rayon/ombre/typo/transitions) → Tâche 1 (transitions :
  déjà conformes, documenté sans modification nécessaire).
- Arbitrage utilisateur reçu, une direction retenue → déjà acquis avant ce plan (Direction A).
- Primitives TDD (bouton/champ/carte/modale/onglet/badge/info-bulle/état vide/squelette/
  toast) → Tâches 2–11, une par un, chacune avec test rouge→vert.
- Page de démonstration + contraste AA → Tâche 12 (page) + Tâche 1 Étape 2 (test de
  contraste automatisé, plus rigoureux qu'une vérification visuelle seule).
- Skill `design-system` → Tâche 14.
- Hook de détection de valeurs brutes → Tâche 13.

**Placeholders :** aucun — chaque étape de code contient le fichier complet ou le diff exact
(numéro de ligne + contenu de remplacement), chaque test contient des assertions concrètes
sur des valeurs réelles (classes Tailwind, contenu textuel, événements émis).

**Cohérence des types/noms :** `BaseButton`/`BaseCard`/`BaseBadge`/`BaseField`/`BaseInput`/
`BaseModal`/`Tabs`/`BaseTooltip`/`BaseEmptyState`/`BaseSkeleton`/`BaseToast` — signatures de
props inchangées par rapport à l'existant sauf ajouts explicites (`BaseButton.variantClass`
danger désormais outline — même prop `variant="danger"`, comportement visuel différent,
documenté). `text-primary-ink` (nouveau token) utilisé de façon cohérente dans `BaseButton`
(Tâche 2), `Tabs` (Tâche 7) et le test de contraste (Tâche 1) avec la même paire de valeurs
RGB. `font-display`/`text-display-md`/`text-display-lg`/`text-meta`/`text-tiny` définis en
Tâche 1, consommés en Tâches 4, 6, 7, 9, 12 sans redéfinition divergente.

**Écart connu, non bloquant :** les valeurs RGB des catégories Bibliothèque
(`cat-note/pdf/diagram/deck/set`) et les valeurs `surface-soft`/`line-soft`/`ink-subtle`/
`primary-strong`/`primary-soft`/`danger-strong` sont des extrapolations de l'auteur du plan
(non présentes dans les 33 écrans validés, qui ne montrent pas ces états). Documenté comme
tel dans la skill (Tâche 14) — ajustable sans repasser par une revalidation utilisateur
complète si besoin, contrairement aux tokens centraux (`primary`/`accent`/`success`/`danger`/
`ink`/`app`/`surface`) qui eux reproduisent exactement `_DIRECTION_A_SPEC.md`.
