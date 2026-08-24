# web/ — StudyHub frontend Vue 3

> Portée : tout `web/src`. Skill `frontend-patterns` pour le détail complet (charge-la avant
> d'éditer) — voir skill `design-system` pour les tokens/primitives. `AGENTS.md` fait
> autorité en cas de doute.

- `<script setup lang="ts">` exclusivement. TypeScript strict — jamais `any`.
- Appels API **uniquement** dans `stores/` et `services/` — jamais de `fetch`/Axios direct dans
  un composant ou une vue.
- État partagé → Pinia. État local d'un composant → `ref`/`reactive` local, pas un store.
- Aucune valeur brute de style (`#rrggbb`, `rgb(...)`, `px` hors `0px`/`1px`, classe Tailwind
  arbitraire `[...]`) — toujours un token.
- `usePlatform()` pour tout conditionnel natif/web, jamais de détection ad hoc.
- Responsive vérifié 375px **et** 1440px, mode sombre systématique, états
  loading/error/empty sur chaque vue.
