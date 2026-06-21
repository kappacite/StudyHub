<template>
  <div class="space-y-6 max-w-xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button @click="goBack" class="text-ink-muted hover:text-primary dark:text-ink-subtle flex items-center gap-1">
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span class="text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary px-2.5 py-1 rounded-lg uppercase tracking-wider">
        {{ TYPE_LABELS[setType] || 'Révision' }} · {{ setName }}
      </span>
    </div>

    <div v-if="loading" class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest">Chargement…</div>

    <div v-else-if="items.length === 0" class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-10 text-center space-y-3">
      <p class="text-sm text-ink-muted dark:text-ink-subtle">Rien à réviser pour l'instant. 🎉</p>
      <button @click="goBack" class="px-4 py-2 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl">Retour</button>
    </div>

    <template v-else>
      <!-- Progress -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-ink-subtle">
          <span>{{ index + 1 }} / {{ items.length }}</span>
          <span>{{ correctCount }} bonne(s)</span>
        </div>
        <div class="w-full bg-surface-soft dark:bg-surface-soft rounded-full h-2 overflow-hidden">
          <div class="bg-primary h-full rounded-full transition-all" :style="{ width: `${(index / items.length) * 100}%` }"></div>
        </div>
      </div>

      <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm space-y-5">
        <!-- VRAI / FAUX -->
        <template v-if="setType === 'vf'">
          <p class="text-lg font-bold text-ink dark:text-ink-subtle">{{ current.payload.assertion }}</p>
          <div v-if="phase === 'answer'" class="grid grid-cols-2 gap-3">
            <button @click="submitVf(true)" class="py-3 rounded-xl text-sm font-bold border border-line dark:border-line hover:bg-success-soft dark:hover:bg-success-soft">Vrai</button>
            <button @click="submitVf(false)" class="py-3 rounded-xl text-sm font-bold border border-line dark:border-line hover:bg-danger-soft dark:hover:bg-danger-soft">Faux</button>
          </div>
          <div v-else class="space-y-2">
            <p class="text-sm font-bold" :class="lastCorrect ? 'text-success' : 'text-danger'">
              {{ lastCorrect ? 'Correct !' : 'Incorrect.' }} Réponse : {{ current.payload.correct ? 'Vrai' : 'Faux' }}
            </p>
            <p v-if="current.payload.justification" class="text-sm text-ink-muted dark:text-ink-subtle">{{ current.payload.justification }}</p>
          </div>
        </template>

        <!-- DEFINITION (auto-évaluation) -->
        <template v-else-if="setType === 'definition'">
          <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest">Terme</p>
          <p class="text-lg font-bold text-ink dark:text-ink-subtle">{{ current.payload.term }}</p>
          <button v-if="phase === 'answer'" @click="phase = 'reveal'" class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong">Révéler la définition</button>
          <template v-else>
            <p class="text-sm text-ink dark:text-ink-subtle border-t border-line dark:border-line pt-3">{{ current.payload.definition }}</p>
            <p class="text-center text-[10px] font-bold text-ink-subtle uppercase tracking-widest">Votre auto-évaluation</p>
            <div class="grid grid-cols-3 gap-2">
              <button @click="selfEval(1)" class="py-2.5 rounded-xl text-xs font-bold border border-danger text-danger hover:bg-danger-soft dark:border-danger dark:bg-danger-soft">À revoir</button>
              <button @click="selfEval(3)" class="py-2.5 rounded-xl text-xs font-bold border border-warning text-warning hover:bg-warning-soft dark:border-warning dark:bg-warning-soft">Moyen</button>
              <button @click="selfEval(5)" class="py-2.5 rounded-xl text-xs font-bold border border-success text-success hover:bg-success-soft dark:border-success dark:bg-success-soft">Acquis</button>
            </div>
          </template>
        </template>

        <!-- ASSOCIATION -->
        <template v-else-if="setType === 'association'">
          <p class="text-sm font-bold text-ink dark:text-ink-subtle">{{ current.payload.title || 'Associez chaque élément' }}</p>
          <div class="space-y-2">
            <div v-for="(left, i) in leftItems" :key="i" class="flex items-center gap-2">
              <span class="flex-1 text-sm font-medium text-ink dark:text-ink-subtle truncate">{{ left }}</span>
              <span class="text-ink-subtle">→</span>
              <select v-model="matches[left]" :disabled="phase === 'feedback'" class="flex-1 px-3 py-2 text-sm rounded-xl border border-line dark:border-line bg-surface dark:bg-surface-soft">
                <option value="">—</option>
                <option v-for="r in rightOptions" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
          </div>
          <button v-if="phase === 'answer'" @click="submitAssoc" :disabled="!allMatched" class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong disabled:opacity-50">Valider</button>
          <p v-else class="text-sm font-bold" :class="lastCorrect ? 'text-success' : 'text-danger'">
            {{ lastCorrect ? 'Tout est correct !' : 'Des associations sont erronées.' }}
          </p>
        </template>

        <!-- ORDRE -->
        <template v-else-if="setType === 'ordre'">
          <p class="text-sm font-bold text-ink dark:text-ink-subtle">{{ current.payload.title || 'Remettez dans le bon ordre' }}</p>
          <ul class="space-y-2">
            <li v-for="(step, i) in ordering" :key="step" class="flex items-center gap-2 p-2.5 rounded-xl border border-line dark:border-line">
              <span class="text-xs font-bold text-ink-subtle w-5">{{ i + 1 }}</span>
              <span class="flex-1 text-sm text-ink dark:text-ink-subtle">{{ step }}</span>
              <div v-if="phase === 'answer'" class="flex flex-col">
                <button @click="move(i, -1)" :disabled="i === 0" class="text-ink-subtle hover:text-primary disabled:opacity-30 leading-none">▲</button>
                <button @click="move(i, 1)" :disabled="i === ordering.length - 1" class="text-ink-subtle hover:text-primary disabled:opacity-30 leading-none">▼</button>
              </div>
              <span v-else class="w-4 text-center" :class="step === (current.payload.steps || [])[i] ? 'text-success' : 'text-danger'">
                {{ step === (current.payload.steps || [])[i] ? '✓' : '✕' }}
              </span>
            </li>
          </ul>
          <button v-if="phase === 'answer'" @click="submitOrdre" class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong">Valider</button>
          <p v-else class="text-sm font-bold" :class="lastCorrect ? 'text-success' : 'text-danger'">
            {{ lastCorrect ? 'Ordre correct !' : 'Ordre incorrect.' }}
          </p>
        </template>

        <!-- Bouton suivant (après correction / révélation auto-corrigée) -->
        <button v-if="phase === 'feedback'" @click="next" class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong">
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
    // Les QCM ont leur passage scoré dédié : on y redirige (ex. lancement d'une tâche de devoir).
    if (set.type === 'qcm') {
      router.replace(`/revision/sets/${setId}/run`)
      return
    }
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
