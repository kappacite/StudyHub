<template>
  <div class="space-y-6 max-w-xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button @click="goBack" class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 flex items-center gap-1">
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span class="text-xs font-bold text-indigo-500 bg-indigo-50 dark:bg-indigo-950/40 dark:text-indigo-400 px-2.5 py-1 rounded-lg uppercase tracking-wider">
        {{ TYPE_LABELS[setType] || 'Révision' }} · {{ setName }}
      </span>
    </div>

    <div v-if="loading" class="py-20 text-center text-sm font-semibold text-slate-400 uppercase tracking-widest">Chargement…</div>

    <div v-else-if="items.length === 0" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-10 text-center space-y-3">
      <p class="text-sm text-slate-500 dark:text-slate-400">Rien à réviser pour l'instant. 🎉</p>
      <button @click="goBack" class="px-4 py-2 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl">Retour</button>
    </div>

    <template v-else>
      <!-- Progress -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
          <span>{{ index + 1 }} / {{ items.length }}</span>
          <span>{{ correctCount }} bonne(s)</span>
        </div>
        <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
          <div class="bg-indigo-600 h-full rounded-full transition-all" :style="{ width: `${(index / items.length) * 100}%` }"></div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-5">
        <!-- VRAI / FAUX -->
        <template v-if="setType === 'vf'">
          <p class="text-lg font-bold text-slate-800 dark:text-slate-100">{{ current.payload.assertion }}</p>
          <div v-if="phase === 'answer'" class="grid grid-cols-2 gap-3">
            <button @click="submitVf(true)" class="py-3 rounded-xl text-sm font-bold border border-slate-200 dark:border-slate-700 hover:bg-emerald-50 dark:hover:bg-emerald-950/20">Vrai</button>
            <button @click="submitVf(false)" class="py-3 rounded-xl text-sm font-bold border border-slate-200 dark:border-slate-700 hover:bg-rose-50 dark:hover:bg-rose-950/20">Faux</button>
          </div>
          <div v-else class="space-y-2">
            <p class="text-sm font-bold" :class="lastCorrect ? 'text-emerald-600' : 'text-rose-500'">
              {{ lastCorrect ? 'Correct !' : 'Incorrect.' }} Réponse : {{ current.payload.correct ? 'Vrai' : 'Faux' }}
            </p>
            <p v-if="current.payload.justification" class="text-sm text-slate-600 dark:text-slate-400">{{ current.payload.justification }}</p>
          </div>
        </template>

        <!-- DEFINITION (auto-évaluation) -->
        <template v-else-if="setType === 'definition'">
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Terme</p>
          <p class="text-lg font-bold text-slate-800 dark:text-slate-100">{{ current.payload.term }}</p>
          <button v-if="phase === 'answer'" @click="phase = 'reveal'" class="w-full py-3 rounded-xl text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700">Révéler la définition</button>
          <template v-else>
            <p class="text-sm text-slate-700 dark:text-slate-300 border-t border-slate-100 dark:border-slate-800 pt-3">{{ current.payload.definition }}</p>
            <p class="text-center text-[10px] font-bold text-slate-400 uppercase tracking-widest">Votre auto-évaluation</p>
            <div class="grid grid-cols-3 gap-2">
              <button @click="selfEval(1)" class="py-2.5 rounded-xl text-xs font-bold border border-rose-100 text-rose-600 hover:bg-rose-50 dark:border-rose-900/30 dark:bg-rose-950/10">À revoir</button>
              <button @click="selfEval(3)" class="py-2.5 rounded-xl text-xs font-bold border border-amber-100 text-amber-600 hover:bg-amber-50 dark:border-amber-900/30 dark:bg-amber-950/10">Moyen</button>
              <button @click="selfEval(5)" class="py-2.5 rounded-xl text-xs font-bold border border-emerald-100 text-emerald-600 hover:bg-emerald-50 dark:border-emerald-900/30 dark:bg-emerald-950/10">Acquis</button>
            </div>
          </template>
        </template>

        <!-- ASSOCIATION -->
        <template v-else-if="setType === 'association'">
          <p class="text-sm font-bold text-slate-800 dark:text-slate-200">{{ current.payload.title || 'Associez chaque élément' }}</p>
          <div class="space-y-2">
            <div v-for="(left, i) in leftItems" :key="i" class="flex items-center gap-2">
              <span class="flex-1 text-sm font-medium text-slate-700 dark:text-slate-300 truncate">{{ left }}</span>
              <span class="text-slate-400">→</span>
              <select v-model="matches[left]" :disabled="phase === 'feedback'" class="flex-1 px-3 py-2 text-sm rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
                <option value="">—</option>
                <option v-for="r in rightOptions" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
          </div>
          <button v-if="phase === 'answer'" @click="submitAssoc" :disabled="!allMatched" class="w-full py-3 rounded-xl text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50">Valider</button>
          <p v-else class="text-sm font-bold" :class="lastCorrect ? 'text-emerald-600' : 'text-rose-500'">
            {{ lastCorrect ? 'Tout est correct !' : 'Des associations sont erronées.' }}
          </p>
        </template>

        <!-- ORDRE -->
        <template v-else-if="setType === 'ordre'">
          <p class="text-sm font-bold text-slate-800 dark:text-slate-200">{{ current.payload.title || 'Remettez dans le bon ordre' }}</p>
          <ul class="space-y-2">
            <li v-for="(step, i) in ordering" :key="step" class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700">
              <span class="text-xs font-bold text-slate-400 w-5">{{ i + 1 }}</span>
              <span class="flex-1 text-sm text-slate-700 dark:text-slate-300">{{ step }}</span>
              <div v-if="phase === 'answer'" class="flex flex-col">
                <button @click="move(i, -1)" :disabled="i === 0" class="text-slate-400 hover:text-indigo-600 disabled:opacity-30 leading-none">▲</button>
                <button @click="move(i, 1)" :disabled="i === ordering.length - 1" class="text-slate-400 hover:text-indigo-600 disabled:opacity-30 leading-none">▼</button>
              </div>
              <span v-else class="w-4 text-center" :class="step === (current.payload.steps || [])[i] ? 'text-emerald-500' : 'text-rose-500'">
                {{ step === (current.payload.steps || [])[i] ? '✓' : '✕' }}
              </span>
            </li>
          </ul>
          <button v-if="phase === 'answer'" @click="submitOrdre" class="w-full py-3 rounded-xl text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700">Valider</button>
          <p v-else class="text-sm font-bold" :class="lastCorrect ? 'text-emerald-600' : 'text-rose-500'">
            {{ lastCorrect ? 'Ordre correct !' : 'Ordre incorrect.' }}
          </p>
        </template>

        <!-- Bouton suivant (après correction / révélation auto-corrigée) -->
        <button v-if="phase === 'feedback'" @click="next" class="w-full py-3 rounded-xl text-sm font-bold text-white bg-slate-800 dark:bg-slate-700 hover:bg-slate-900">
          {{ index + 1 < items.length ? 'Suivant' : 'Terminer' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionItem, RevisionType } from '../../stores/revision'
import { ChevronLeft } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const setName = ref('')
const setType = ref<RevisionType>('vf')
const loading = ref(true)
const items = ref<RevisionItem[]>([])
const index = ref(0)
const correctCount = ref(0)
const phase = ref<'answer' | 'reveal' | 'feedback'>('answer')
const lastCorrect = ref(false)

const TYPE_LABELS: Record<string, string> = {
  vf: 'Vrai / Faux', definition: 'Définition', association: 'Association', ordre: 'Ordre', qcm: 'QCM',
}

const current = computed(() => items.value[index.value] || ({ payload: {} } as RevisionItem))

// Association
const matches = reactive<Record<string, string>>({})
const leftItems = ref<string[]>([])
const rightOptions = ref<string[]>([])
const allMatched = computed(() => leftItems.value.length > 0 && leftItems.value.every((l) => matches[l]))

// Ordre
const ordering = ref<string[]>([])

function shuffle<T>(arr: T[]): T[] {
  return [...arr].sort(() => Math.random() - 0.5)
}

function setupItem() {
  phase.value = 'answer'
  lastCorrect.value = false
  const payload = current.value.payload || {}
  if (setType.value === 'association') {
    const pairs = payload.pairs || []
    leftItems.value = pairs.map((p) => p.left)
    rightOptions.value = shuffle(pairs.map((p) => p.right))
    Object.keys(matches).forEach((k) => delete matches[k])
    leftItems.value.forEach((l) => { matches[l] = '' })
  } else if (setType.value === 'ordre') {
    ordering.value = shuffle(payload.steps || [])
  }
}

onMounted(async () => {
  try {
    const [set, studyItems] = await Promise.all([
      revisionStore.fetchSet(setId),
      revisionStore.fetchStudyItems(setId),
    ])
    setName.value = set.name
    setType.value = set.type
    items.value = studyItems
    if (items.value.length) setupItem()
  } catch (e) {
    console.error('Erreur de chargement de la session', e)
  } finally {
    loading.value = false
  }
})

async function submitVf(value: boolean) {
  const res = await revisionStore.gradeItem(setId, current.value.id, { value })
  applyResult(res.correct)
}

async function submitAssoc() {
  const res = await revisionStore.gradeItem(setId, current.value.id, { matches: { ...matches } })
  applyResult(res.correct)
}

async function submitOrdre() {
  const res = await revisionStore.gradeItem(setId, current.value.id, { order: [...ordering.value] })
  applyResult(res.correct)
}

async function selfEval(score: number) {
  await revisionStore.answerItem(setId, current.value.id, score)
  applyResult(score >= 3)
}

function applyResult(correct: boolean) {
  lastCorrect.value = correct
  if (correct) correctCount.value++
  phase.value = 'feedback'
}

function move(i: number, dir: number) {
  const j = i + dir
  if (j < 0 || j >= ordering.value.length) return
  const arr = ordering.value
  ;[arr[i], arr[j]] = [arr[j], arr[i]]
  ordering.value = [...arr]
}

function next() {
  if (index.value + 1 >= items.value.length) {
    goBack()
    return
  }
  index.value++
  setupItem()
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
