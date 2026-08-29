import type { Component } from 'vue'
import { Layers, HelpCircle, Rows3, BookOpen, ListOrdered, Shuffle } from 'lucide-vue-next'
import type { RevisionItemType } from '../stores/revision'

export interface RevisionItemTypeMeta {
  label: string
  icon: Component
}

export const REVISION_ITEM_TYPE_META: Record<RevisionItemType, RevisionItemTypeMeta> = {
  flashcard: { label: 'Flashcards', icon: Layers },
  qcm: { label: 'QCM', icon: HelpCircle },
  vf: { label: 'Vrai / Faux', icon: Rows3 },
  definition: { label: 'Définition', icon: BookOpen },
  ordre: { label: 'Ordre', icon: ListOrdered },
  association: { label: 'Association', icon: Shuffle },
}
