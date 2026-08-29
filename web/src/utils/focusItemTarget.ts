import type { Component } from 'vue'
import { FileQuestion } from 'lucide-vue-next'
import type { FocusItem } from '../services/focusService'
import type { RevisionSet, RevisionType } from '../stores/revision'

// Extrait de la logique de routage validée dans Reviews.vue (référence) afin que
// les 6 consommateurs de FocusItem/focusStore.items (Reviews.vue, Accueil.vue,
// FocusPage.vue, FocusWidget.vue, StudyDeck.vue, Blurting.vue) traitent tous le
// type `revision_set` de la même façon — voir revue de branche « reviser-hub »,
// finding #1 : ce type n'était jusque-là câblé que dans Reviews.vue.

/**
 * Type "propre" (homogène) d'un ensemble de révision dû, résolu depuis
 * `revisionStore.sets`. `undefined` = ensemble inconnu du store (pas encore
 * chargé, supprimé, ou partagé hors page) ; `null` = ensemble hétérogène.
 */
export function getRevisionSetType(
  item: Pick<FocusItem, 'id'>,
  sets: RevisionSet[],
): RevisionType | null | undefined {
  const set = sets.find((s) => String(s.id) === String(item.id))
  return set ? set.type : undefined
}

/**
 * Route de révision d'un ensemble déjà identifié par son id et son type propre.
 * Un ensemble homogène QCM se joue en mode "run" (série notée) ; tout le
 * reste — y compris un ensemble inconnu (`undefined`) ou hétérogène (`null`)
 * — passe par /study.
 */
export function getRevisionSetRoute(
  id: number | string,
  type: RevisionType | null | undefined,
): string {
  const mode = type === 'qcm' ? 'run' : 'study'
  return `/revision/sets/${id}/${mode}`
}

/**
 * Route de destination pour "réviser" un FocusItem, tous types confondus
 * (deck, note, devoir, ensemble de révision). Référence : Reviews.vue.
 */
export function getFocusItemTarget(item: FocusItem, sets: RevisionSet[]): string {
  if (item.type === 'deck') return `/decks/${item.id}/study?focus=true`
  if (item.type === 'note') return `/notes/${item.id}/blurting?focus=true&from=focus`
  if (item.type === 'assignment') return `/bibliotheque/${item.id}`
  return getRevisionSetRoute(item.id, getRevisionSetType(item, sets))
}

/**
 * Icône générique d'un ensemble de révision — même pictogramme que celui déjà
 * utilisé pour une ligne "ensemble de révision" dans Binders.vue, afin de
 * rester cohérent visuellement dans toute l'application.
 */
export const REVISION_SET_ICON: Component = FileQuestion

/** Libellé générique d'un ensemble de révision dû, pour les résumés courts. */
export const REVISION_SET_LABEL = 'Série de révision'
