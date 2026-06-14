<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center px-4">
    <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="$emit('close')"></div>

    <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl w-full max-w-lg p-6 relative z-10 shadow-2xl max-h-[88vh] overflow-y-auto">
      <h3 class="text-lg font-bold mb-1 text-slate-800 dark:text-white">Ajouter un item de révision</h3>
      <p class="text-xs text-slate-400 mb-4">Choisissez un type, il sera révisé en répétition espacée (SM-2).</p>

      <!-- Type selector -->
      <div class="flex flex-wrap gap-2 mb-5">
        <button
          v-for="t in TYPES"
          :key="t.value"
          type="button"
          @click="cardType = t.value"
          class="px-3 py-1.5 rounded-xl text-xs font-bold border transition-all"
          :class="cardType === t.value
            ? 'bg-indigo-600 text-white border-transparent'
            : 'bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-300 border-slate-200 dark:border-slate-700'"
        >
          {{ t.label }}
        </button>
      </div>

      <form @submit.prevent="submit" class="space-y-4">
        <!-- Target deck -->
        <div>
          <label :class="labelCls">Jeu de révision</label>
          <select v-model="deckChoice" :class="inputCls">
            <option :value="NEW_DECK">➕ Nouveau jeu de révision…</option>
            <option v-for="d in decks" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
          <input
            v-if="deckChoice === NEW_DECK"
            v-model="newDeckName"
            type="text"
            placeholder="Nom du jeu de révision"
            :class="['mt-2', inputCls]"
          />
        </div>

        <!-- BASIC -->
        <template v-if="cardType === 'basic'">
          <div><label :class="labelCls">Recto (question)</label><textarea v-model="basicFront" rows="2" :class="inputCls" placeholder="Ex: Capitale de l'Italie ?"></textarea></div>
          <div><label :class="labelCls">Verso (réponse)</label><textarea v-model="basicBack" rows="2" :class="inputCls" placeholder="Ex: Rome"></textarea></div>
        </template>

        <!-- QCM -->
        <template v-else-if="cardType === 'qcm'">
          <div><label :class="labelCls">Question</label><textarea v-model="qcmQuestion" rows="2" :class="inputCls" placeholder="Ex: Quelle est la capitale de la France ?"></textarea></div>
          <div>
            <label :class="labelCls">Options (cochez la/les bonne(s))</label>
            <div v-for="(opt, i) in qcmOptions" :key="i" class="flex items-center gap-2 mb-2">
              <input type="checkbox" v-model="opt.correct" class="accent-emerald-600 shrink-0" />
              <input v-model="opt.text" type="text" :class="inputCls" :placeholder="`Option ${i + 1}`" />
              <button type="button" @click="qcmOptions.splice(i, 1)" :disabled="qcmOptions.length <= 2" class="text-slate-400 hover:text-rose-500 disabled:opacity-30 shrink-0 px-1">✕</button>
            </div>
            <button type="button" @click="qcmOptions.push({ text: '', correct: false })" class="text-xs font-bold text-indigo-600 hover:text-indigo-700">+ Ajouter une option</button>
          </div>
        </template>

        <!-- VF -->
        <template v-else-if="cardType === 'vf'">
          <div><label :class="labelCls">Affirmation</label><textarea v-model="vfAssertion" rows="2" :class="inputCls" placeholder="Ex: La Terre est plate."></textarea></div>
          <div>
            <label :class="labelCls">Verdict</label>
            <div class="flex gap-2">
              <button type="button" @click="vfCorrect = true" class="flex-1 py-2 rounded-xl text-xs font-bold border" :class="vfCorrect ? 'bg-emerald-600 text-white border-transparent' : 'bg-slate-50 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700'">Vrai</button>
              <button type="button" @click="vfCorrect = false" class="flex-1 py-2 rounded-xl text-xs font-bold border" :class="!vfCorrect ? 'bg-rose-600 text-white border-transparent' : 'bg-slate-50 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700'">Faux</button>
            </div>
          </div>
          <div><label :class="labelCls">Justification (optionnel)</label><textarea v-model="vfJustification" rows="2" :class="inputCls" placeholder="Ex: Elle a la forme d'un géoïde."></textarea></div>
        </template>

        <!-- ORDRE -->
        <template v-else-if="cardType === 'ordre'">
          <div><label :class="labelCls">Titre / consigne</label><input v-model="ordreTitle" type="text" :class="inputCls" placeholder="Ex: Cycle de l'eau" /></div>
          <div>
            <label :class="labelCls">Étapes (dans le bon ordre)</label>
            <div v-for="(step, i) in ordreSteps" :key="i" class="flex items-center gap-2 mb-2">
              <span class="text-xs font-bold text-slate-400 w-4 shrink-0">{{ i + 1 }}</span>
              <input v-model="step.value" type="text" :class="inputCls" :placeholder="`Étape ${i + 1}`" />
              <button type="button" @click="ordreSteps.splice(i, 1)" :disabled="ordreSteps.length <= 2" class="text-slate-400 hover:text-rose-500 disabled:opacity-30 shrink-0 px-1">✕</button>
            </div>
            <button type="button" @click="ordreSteps.push({ value: '' })" class="text-xs font-bold text-indigo-600 hover:text-indigo-700">+ Ajouter une étape</button>
          </div>
        </template>

        <!-- ASSOC -->
        <template v-else-if="cardType === 'assoc'">
          <div><label :class="labelCls">Titre / consigne</label><input v-model="assocTitle" type="text" :class="inputCls" placeholder="Ex: Pays et capitales" /></div>
          <div>
            <label :class="labelCls">Associations</label>
            <div v-for="(p, i) in assocPairs" :key="i" class="flex items-center gap-2 mb-2">
              <input v-model="p.left" type="text" :class="inputCls" placeholder="Élément" />
              <span class="text-slate-400 shrink-0">→</span>
              <input v-model="p.right" type="text" :class="inputCls" placeholder="Correspondance" />
              <button type="button" @click="assocPairs.splice(i, 1)" :disabled="assocPairs.length <= 2" class="text-slate-400 hover:text-rose-500 disabled:opacity-30 shrink-0 px-1">✕</button>
            </div>
            <button type="button" @click="assocPairs.push({ left: '', right: '' })" class="text-xs font-bold text-indigo-600 hover:text-indigo-700">+ Ajouter une paire</button>
          </div>
        </template>

        <p v-if="error" class="text-xs text-rose-500">{{ error }}</p>

        <div class="flex items-center justify-end gap-3 pt-2">
          <button type="button" @click="$emit('close')" class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800">Annuler</button>
          <button type="submit" :disabled="!canSubmit || saving" class="px-4 py-2 text-sm font-bold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed">
            {{ saving ? 'Ajout…' : 'Ajouter' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDecksStore } from '../../stores/decks'
import type { CardType, CardPayload, Deck } from '../../stores/decks'

const props = defineProps<{
  binderId: string | null
  decks: Deck[]
  initialType?: CardType
  initialDeckId?: number
}>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'created', deckId: number): void }>()

const decksStore = useDecksStore()

const labelCls = 'block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1'
const inputCls = 'w-full px-3 py-2.5 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200'

const TYPES: { value: CardType; label: string }[] = [
  { value: 'basic', label: 'Carte' },
  { value: 'qcm', label: 'QCM' },
  { value: 'vf', label: 'Vrai / Faux' },
  { value: 'ordre', label: 'Ordre' },
  { value: 'assoc', label: 'Association' },
]

const NEW_DECK = '__new__' as const
const cardType = ref<CardType>(props.initialType || 'basic')
const deckChoice = ref<number | typeof NEW_DECK>(
  props.initialDeckId ?? (props.decks.length ? props.decks[0].id : NEW_DECK),
)
const newDeckName = ref('')
const saving = ref(false)
const error = ref('')

// BASIC
const basicFront = ref('')
const basicBack = ref('')
// QCM
const qcmQuestion = ref('')
const qcmOptions = ref<{ text: string; correct: boolean }[]>([
  { text: '', correct: false },
  { text: '', correct: false },
])
// VF
const vfAssertion = ref('')
const vfCorrect = ref(true)
const vfJustification = ref('')
// ORDRE (objets pour permettre le v-model sur primitive)
const ordreTitle = ref('')
const ordreSteps = ref<{ value: string }[]>([{ value: '' }, { value: '' }])
// ASSOC
const assocTitle = ref('')
const assocPairs = ref<{ left: string; right: string }[]>([
  { left: '', right: '' },
  { left: '', right: '' },
])

const canSubmit = computed(() => {
  if (deckChoice.value === NEW_DECK && !newDeckName.value.trim()) return false
  if (cardType.value === 'basic') return !!basicFront.value.trim() && !!basicBack.value.trim()
  if (cardType.value === 'qcm') {
    const opts = qcmOptions.value.filter((o) => o.text.trim())
    return !!qcmQuestion.value.trim() && opts.length >= 2 && opts.some((o) => o.correct)
  }
  if (cardType.value === 'vf') return !!vfAssertion.value.trim()
  if (cardType.value === 'ordre') return !!ordreTitle.value.trim() && ordreSteps.value.filter((s) => s.value.trim()).length >= 2
  if (cardType.value === 'assoc') return !!assocTitle.value.trim() && assocPairs.value.filter((p) => p.left.trim() && p.right.trim()).length >= 2
  return false
})

const OPTION_IDS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

function build(): { front: string; back: string; payload: CardPayload | null } {
  if (cardType.value === 'qcm') {
    const opts = qcmOptions.value
      .filter((o) => o.text.trim())
      .map((o, i) => ({ id: OPTION_IDS[i] || String(i), text: o.text.trim(), correct: o.correct }))
    const back = opts.filter((o) => o.correct).map((o) => o.text).join(', ')
    return { front: qcmQuestion.value.trim(), back, payload: { question: qcmQuestion.value.trim(), options: opts } }
  }
  if (cardType.value === 'vf') {
    const verdict = vfCorrect.value ? 'Vrai' : 'Faux'
    const just = vfJustification.value.trim()
    return {
      front: vfAssertion.value.trim(),
      back: just ? `${verdict} — ${just}` : verdict,
      payload: { assertion: vfAssertion.value.trim(), correct: vfCorrect.value, justification: just },
    }
  }
  if (cardType.value === 'ordre') {
    const steps = ordreSteps.value.map((s) => s.value.trim()).filter(Boolean)
    return { front: ordreTitle.value.trim(), back: steps.join(' → '), payload: { title: ordreTitle.value.trim(), steps } }
  }
  if (cardType.value === 'assoc') {
    const pairs = assocPairs.value
      .map((p) => ({ left: p.left.trim(), right: p.right.trim() }))
      .filter((p) => p.left && p.right)
    return {
      front: assocTitle.value.trim(),
      back: pairs.map((p) => `${p.left} → ${p.right}`).join(' ; '),
      payload: { title: assocTitle.value.trim(), pairs },
    }
  }
  return { front: basicFront.value.trim(), back: basicBack.value.trim(), payload: null }
}

async function submit() {
  if (!canSubmit.value || saving.value) return
  saving.value = true
  error.value = ''
  try {
    let deckId: number
    if (deckChoice.value === NEW_DECK) {
      const deck = await decksStore.createDeck(newDeckName.value.trim(), '', props.binderId)
      deckId = deck.id
    } else {
      deckId = deckChoice.value
    }
    const { front, back, payload } = build()
    await decksStore.createCard(deckId, front, back, cardType.value, payload)
    emit('created', deckId)
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Impossible d'ajouter l'item."
  } finally {
    saving.value = false
  }
}
</script>
