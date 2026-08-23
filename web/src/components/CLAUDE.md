# web/src/components/ — primitives & composants UI

> Portée : `web/src/components/`. Skill `frontend-patterns` (primitives actuelles) — sera
> complétée par la skill `design-system` à partir de la phase 3.

- `components/ui/` : primitives présentationnelles pures — **aucun appel API**, aucune logique
  métier. Elles consomment des props/slots, pas des stores directement.
- Réutiliser une primitive existante (`BaseButton`, `BaseCard`, `BaseModal`, `BaseInput`,
  `BaseBadge`, `BaseSkeleton`, `BaseEmptyState`, …) avant d'en écrire une nouvelle.
- Cibles tactiles ≥ 44px, contraste AA, `prefers-reduced-motion` respecté (chemin dégradé
  fonctionnel, pas juste "moins d'animation").
- Un composant = une responsabilité visuelle. Au-delà de ~300 lignes, c'est un signal qu'il
  doit être découpé (plusieurs composants sont déjà dans ce cas — voir cartographie §3.3).
