# Design System StudyHub

Le design system a basculé vers la direction esthétique **Direction A « Fiche »** (papier
chaud, encre indigo, rehaut ocre, typographie Bitter/Karla/Space Mono). L'ancien thème
« White/Pink × Material épuré » que ce document décrivait auparavant est abandonné et n'existe
plus dans le code (tokens, primitives) — cette page n'est donc plus la référence canonique.

Les deux sources de vérité réelles sont désormais :

- **`.claude/skills/design-system/SKILL.md`** — référence canonique : palette de tokens,
  typographie, rayons, ombres, primitives `web/src/components/ui/base/`, garde-fous. À charger
  avant de toucher un token ou une primitive.
- **`docs/design-system-direction-a-spec.md`** — spec source, avec les patterns HTML de
  référence ayant servi à construire les tokens et primitives.

Pour l'architecture frontend générale (hors design system), voir `docs/frontend.md`.
