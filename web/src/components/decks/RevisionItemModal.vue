<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center px-4">
    <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="$emit('close')"></div>

    <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl w-full max-w-lg p-6 relative z-10 shadow-2xl max-h-[88vh] overflow-y-auto">
      <h3 class="text-lg font-bold mb-1 text-ink dark:text-white">Ajouter un élément de révision</h3>
      <p class="text-xs text-ink-subtle mb-4">Choisissez un type, il sera révisé en répétition espacée (SM-2).</p>

      <!-- Type selector -->
      <div class="flex flex-wrap gap-2 mb-5">
        <button
          v-for="t in TYPES"
          :key="t.value"
          type="button"
          @click="itemType = t.value"
          class="px-3 py-1.5 rounded-xl text-xs font-bold border transition-all"
          :class="itemType === t.value
            ? 'bg-primary text-white border-transparent'
            : 'bg-surface-soft dark:bg-surface-soft text-ink-muted dark:text-ink-subtle border-line dark:border-line'"
        >
          {{ t.label }}
        </button>
      </div>

      <form @submit.prevent="submit" class="space-y-4">
        <!-- Target : deck (basic) OR revision set (typed) -->
        <div>
          <label :class="labelCls">{{ itemType === 'basic' ? 'Jeu de révision (flashcards)' : 'Ensemble de révision' }}</label>
          <select v-model="targetChoice" :class="inputCls">
            <option :value="NEW_TARGET">➕ Nouvel ensemble…</option>
            <option v-for="t in targets" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
          <input
            v-if="targetChoice === NEW_TARGET"
            v-model="newTargetName"
            type="text"
            placeholder="Nom de l'ensemble"
            :class="['mt-2', inputCls]"
          />
        </div>

        <!-- BASIC -->
        <template v-if="itemType === 'basic'">
          <div><label :class="labelCls">Recto (question)</label><textarea v-model="basicFront" rows="2" :class="inputCls" placeholder="Ex: Capitale de l'Italie ?"></textarea></div>
          <div><label :class="labelCls">Verso (réponse)</label><textarea v-model="basicBack" rows="2" :class="inputCls" placeholder="Ex: Rome"></textarea></div>
        </template>

        <!-- QCM -->
        <template v-else-if="itemType === 'qcm'">
          <div><label :class="labelCls">Question</label><textarea v-model="qcmQuestion" rows="2" :class="inputCls" placeholder="Ex: Quelle est la capitale de la France ?"></textarea></div>
          <div>
            <label :class="labelCls">Options (cochez la/les bonne(s))</label>
            <div v-for="(opt, i) in qcmOptions" :key="i" class="flex items-center gap-2 mb-2">
              <input type="checkbox" v-model="opt.correct" class="accent-success shrink-0" />
              <input v-model="opt.text" type="text" :class="inputCls" :placeholder="`Option ${i + 1}`" />
              <button type="button" @click="qcmOptions.splice(i, 1)" :disabled="qcmOptions.length <= 2" class="text-ink-subtle hover:text-danger disabled:opacity-30 shrink-0 px-1">✕</button>
            </div>
            <button type="button" @click="qcmOptions.push({ text: '', correct: false })" class="text-xs font-bold text-primary hover:text-primary">+ Ajouter une option</button>
            <p class="text-[10px] text-ink-subtle mt-1">Cochez plusieurs cases pour une question à réponses multiples (correction tout-ou-rien).</p>
          </div>
          <div>
            <label :class="labelCls">Barème (points)</label>
            <input v-model.number="qcmPoints" type="number" min="1" step="1" :class="inputCls" />
          </div>
        </template>

        <!-- VF -->
        <template v-else-if="itemType === 'vf'">
          <div><label :class="labelCls">Affirmation</label><textarea v-model="vfAssertion" rows="2" :class="inputCls" placeholder="Ex: La Terre est plate."></textarea></div>
          <div>
            <label :class="labelCls">Verdict</label>
            <div class="flex gap-2">
              <button type="button" @click="vfCorrect = true" class="flex-1 py-2 rounded-xl text-xs font-bold border" :class="vfCorrect ? 'bg-success text-white border-transparent' : 'bg-surface-soft dark:bg-surface-soft text-ink-muted border-line dark:border-line'">Vrai</button>
              <button type="button" @click="vfCorrect = false" class="flex-1 py-2 rounded-xl text-xs font-bold border" :class="!vfCorrect ? 'bg-danger text-white border-transparent' : 'bg-surface-soft dark:bg-surface-soft text-ink-muted border-line dark:border-line'">Faux</button>
            </div>
          </div>
          <div><label :class="labelCls">Justification (optionnel)</label><textarea v-model="vfJustification" rows="2" :class="inputCls" placeholder="Ex: Elle a la forme d'un géoïde."></textarea></div>
        </template>

        <!-- DEFINITION -->
        <template v-else-if="itemType === 'definition'">
          <div><label :class="labelCls">Terme</label><input v-model="defTerm" type="text" :class="inputCls" placeholder="Ex: Photosynthèse" /></div>
          <div><label :class="labelCls">Définition</label><textarea v-model="defDefinition" rows="3" :class="inputCls" placeholder="Ex: Conversion de la lumière en énergie chimique."></textarea></div>
        </template>

        <!-- ORDRE -->
        <template v-else-if="itemType === 'ordre'">
          <div><label :class="labelCls">Titre / consigne</label><input v-model="ordreTitle" type="text" :class="inputCls" placeholder="Ex: Cycle de l'eau" /></div>
          <div>
            <label :class="labelCls">Étapes (dans le bon ordre)</label>
            <div v-for="(step, i) in ordreSteps" :key="i" class="flex items-center gap-2 mb-2">
              <span class="text-xs font-bold text-ink-subtle w-4 shrink-0">{{ i + 1 }}</span>
              <input v-model="step.value" type="text" :class="inputCls" :placeholder="`Étape ${i + 1}`" />
              <button type="button" @click="ordreSteps.splice(i, 1)" :disabled="ordreSteps.length <= 2" class="text-ink-subtle hover:text-danger disabled:opacity-30 shrink-0 px-1">✕</button>
            </div>
            <button type="button" @click="ordreSteps.push({ value: '' })" class="text-xs font-bold text-primary hover:text-primary">+ Ajouter une étape</button>
          </div>
        </template>

        <!-- ASSOCIATION -->
        <template v-else-if="itemType === 'association'">
          <div><label :class="labelCls">Titre / consigne</label><input v-model="assocTitle" type="text" :class="inputCls" placeholder="Ex: Pays et capitales" /></div>
          <div>
            <label :class="labelCls">Associations</label>
            <div v-for="(p, i) in assocPairs" :key="i" class="flex items-center gap-2 mb-2">
              <input v-model="p.left" type="text" :class="inputCls" placeholder="Élément" />
              <span class="text-ink-subtle shrink-0">→</span>
              <input v-model="p.right" type="text" :class="inputCls" placeholder="Correspondance" />
              <button type="button" @click="assocPairs.splice(i, 1)" :disabled="assocPairs.length <= 2" class="text-ink-subtle hover:text-danger disabled:opacity-30 shrink-0 px-1">✕</button>
            </div>
            <button type="button" @click="assocPairs.push({ left: '', right: '' })" class="text-xs font-bold text-primary hover:text-primary">+ Ajouter une paire</button>
          </div>
        </template>

        <p v-if="error" class="text-xs text-danger">{{ error }}</p>

        <div class="flex items-center justify-end gap-3 pt-2">
          <button type="button" @click="$emit('close')" class="px-4 py-2 text-sm font-semibold rounded-xl text-ink-muted hover:bg-surface-soft dark:hover:bg-surface-soft">Annuler</button>
          <button type="submit" :disabled="!canSubmit || saving" class="px-4 py-2 text-sm font-bold rounded-xl text-white bg-primary hover:bg-primary-strong disabled:opacity-50 disabled:cursor-not-allowed">
            {{ saving ? 'Ajout…' : 'Ajouter' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useDecksStore } from '../../stores/decks'
import type { Deck } from '../../stores/decks'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionType, RevisionItemPayload } from '../../stores/revision'

// 'basic' = flashcard recto/verso (Deck) ; les autres = ensembles de révision.
type ItemType = 'basic' | RevisionType

const props = defineProps<{
  binderId: string | null
  decks: Deck[]
  initialType?: ItemType
  initialDeckId?: number
}>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'created'): void }>()

const decksStore = useDecksStore()
const revisionStore = useRevisionStore()

const labelCls = 'block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1'
const inputCls = 'w-full px-3 py-2.5 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200'

const TYPES: { value: ItemType; label: string }[] = [
  { value: 'basic', label: 'Carte' },
  { value: 'qcm', label: 'QCM' },
  { value: 'vf', label: 'Vrai / Faux' },
  { value: 'definition', label: 'Définition' },
  { value: 'ordre', label: 'Ordre' },
  { value: 'association', label: 'Association' },
]

const NEW_TARGET = '__new__' as const
const itemType = ref<ItemType>(props.initialType || 'basic')
const targetChoice = ref<number | typeof NEW_TARGET>(NEW_TARGET)
const newTargetName = ref('')
const saving = ref(false)
const error = ref('')

// Cibles disponibles selon le type : decks (basic) ou ensembles du même type.
const targets = computed(() => {
  if (itemType.value === 'basic') return props.decks.map(d => ({ id: d.id, name: d.name }))
  return revisionStore.sets
    .filter(s => s.type === itemType.value)
    .map(s => ({ id: s.id, name: s.name }))
})

function resetTargetChoice() {
  if (itemType.value === 'basic' && props.initialDeckId) {
    targetChoice.value = props.initialDeckId
    return
  }
  targetChoice.value = targets.value.length ? targets.value[0].id : NEW_TARGET
}

watch(itemType, resetTargetChoice)
onMounted(async () => {
  await revisionStore.fetchSets()
  resetTargetChoice()
})

// BASIC
const basicFront = ref('')
const basicBack = ref('')
// QCM
const qcmQuestion = ref('')
const qcmPoints = ref(1)
const qcmOptions = ref<{ text: string; correct: boolean }[]>([
  { text: '', correct: false },
  { text: '', correct: false },
])
// VF
const vfAssertion = ref('')
const vfCorrect = ref(true)
const vfJustification = ref('')
// DEFINITION
const defTerm = ref('')
const defDefinition = ref('')
// ORDRE
const ordreTitle = ref('')
const ordreSteps = ref<{ value: string }[]>([{ value: '' }, { value: '' }])
// ASSOCIATION
const assocTitle = ref('')
const assocPairs = ref<{ left: string; right: string }[]>([
  { left: '', right: '' },
  { left: '', right: '' },
])

const canSubmit = computed(() => {
  if (targetChoice.value === NEW_TARGET && !newTargetName.value.trim()) return false
  if (itemType.value === 'basic') return !!basicFront.value.trim() && !!basicBack.value.trim()
  if (itemType.value === 'qcm') {
    const opts = qcmOptions.value.filter((o) => o.text.trim())
    return !!qcmQuestion.value.trim() && opts.length >= 2 && opts.some((o) => o.correct)
  }
  if (itemType.value === 'vf') return !!vfAssertion.value.trim()
  if (itemType.value === 'definition') return !!defTerm.value.trim() && !!defDefinition.value.trim()
  if (itemType.value === 'ordre') return !!ordreTitle.value.trim() && ordreSteps.value.filter((s) => s.value.trim()).length >= 2
  if (itemType.value === 'association') return !!assocTitle.value.trim() && assocPairs.value.filter((p) => p.left.trim() && p.right.trim()).length >= 2
  return false
})

const OPTION_IDS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

function buildPayload(): RevisionItemPayload {
  if (itemType.value === 'qcm') {
    const options = qcmOptions.value
      .filter((o) => o.text.trim())
      .map((o, i) => ({ id: OPTION_IDS[i] || String(i), text: o.text.trim(), correct: o.correct }))
    return { question: qcmQuestion.value.trim(), options, points: Math.max(1, qcmPoints.value || 1) }
  }
  if (itemType.value === 'vf') {
    return {
      assertion: vfAssertion.value.trim(),
      correct: vfCorrect.value,
      justification: vfJustification.value.trim() || undefined,
    }
  }
  if (itemType.value === 'definition') {
    return { term: defTerm.value.trim(), definition: defDefinition.value.trim() }
  }
  if (itemType.value === 'ordre') {
    return { title: ordreTitle.value.trim(), steps: ordreSteps.value.map((s) => s.value.trim()).filter(Boolean) }
  }
  // association
  return {
    title: assocTitle.value.trim(),
    pairs: assocPairs.value
      .map((p) => ({ left: p.left.trim(), right: p.right.trim() }))
      .filter((p) => p.left && p.right),
  }
}

async function submit() {
  if (!canSubmit.value || saving.value) return
  saving.value = true
  error.value = ''
  try {
    if (itemType.value === 'basic') {
      let deckId: number
      if (targetChoice.value === NEW_TARGET) {
        const deck = await decksStore.createDeck(newTargetName.value.trim(), '', props.binderId)
        deckId = deck.id
      } else {
        deckId = targetChoice.value
      }
      await decksStore.createCard(deckId, basicFront.value.trim(), basicBack.value.trim())
    } else {
      let setId: number
      if (targetChoice.value === NEW_TARGET) {
        const set = await revisionStore.createSet(newTargetName.value.trim(), itemType.value, props.binderId)
        setId = set.id
      } else {
        setId = targetChoice.value
      }
      await revisionStore.createItem(setId, buildPayload())
    }
    emit('created')
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Impossible d'ajouter l'élément."
  } finally {
    saving.value = false
  }
}
</script>
