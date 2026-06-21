/**
 * Presets d'animation partagés — « subtiles & rapides » (Soft & Friendly).
 *
 * À utiliser avec la directive `v-motion` de @vueuse/motion :
 *   <div v-motion="fadeUp" />
 *   <li v-for="(it, i) in items" v-motion="listItem(i)" />
 *
 * Durées courtes (≈200-250 ms), ease-out, pas de rebond marqué.
 * `prefers-reduced-motion` est neutralisé globalement via src/style.css.
 */

type MotionVariants = {
  initial: Record<string, number>
  [key: string]: Record<string, unknown>
}

const EASE = [0.22, 1, 0.36, 1] as const // ease-out doux

/** Apparition standard : léger fondu + montée de 8px. */
export const fadeUp: MotionVariants = {
  initial: { opacity: 0, y: 8 },
  enter: { opacity: 1, y: 0, transition: { duration: 250, ease: EASE } },
}

/** Apparition au scroll (une seule fois), même rendu que fadeUp. */
export const fadeUpOnce: MotionVariants = {
  initial: { opacity: 0, y: 12 },
  visibleOnce: { opacity: 1, y: 0, transition: { duration: 300, ease: EASE } },
}

/** Pop discret pour modales / badges / petits éléments. */
export const pop: MotionVariants = {
  initial: { opacity: 0, scale: 0.96 },
  enter: { opacity: 1, scale: 1, transition: { duration: 200, ease: EASE } },
}

/** Entrée en cascade pour les listes/grilles (décalage léger par index). */
export function listItem(index: number, step = 40): MotionVariants {
  return {
    initial: { opacity: 0, y: 8 },
    enter: {
      opacity: 1,
      y: 0,
      transition: { duration: 220, ease: EASE, delay: index * step },
    },
  }
}

export function useMotionPresets() {
  return { fadeUp, fadeUpOnce, pop, listItem }
}
