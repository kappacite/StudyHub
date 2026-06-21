<template>
  <div class="space-y-6 max-w-2xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button @click="goBack" class="text-ink-muted hover:text-primary dark:text-ink-subtle flex items-center gap-1">
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span class="text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary px-2.5 py-1 rounded-lg uppercase tracking-wider">
        QCM · {{ setName }}
      </span>
    </div>

    <div v-if="loading" class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest">
      Chargement du QCM…
    </div>

    <!-- Empty -->
    <div v-else-if="questions.length === 0" class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-10 text-center space-y-3">
      <p class="text-sm text-ink-muted dark:text-ink-subtle">Aucune question à réviser pour l'instant.</p>
      <button @click="goBack" class="px-4 py-2 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl">Retour</button>
    </div>

    <!-- Result -->
    <div v-else-if="result" class="space-y-6">
      <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 text-center space-y-3">
        <h2 class="text-2xl font-bold text-ink dark:text-white">{{ result.score }} / {{ result.max_score }} points</h2>
        <div class="w-full bg-surface-soft dark:bg-surface-soft rounded-full h-3 overflow-hidden">
          <div class="h-full rounded-full transition-all" :class="result.percentage >= 50 ? 'bg-success' : 'bg-danger'" :style="{ width: `${result.percentage}%` }"></div>
        </div>
        <p class="text-sm font-bold" :class="result.percentage >= 50 ? 'text-success' : 'text-danger'">{{ result.percentage }} %</p>
      </div>

      <div v-for="(q, i) in questions" :key="q.id" class="bg-surface dark:bg-surface-soft border rounded-2xl p-5"
        :class="resultFor(q.id)?.correct ? 'border-success dark:border-success' : 'border-danger dark:border-danger'">
        <div class="flex items-start justify-between gap-3">
          <p class="text-sm font-bold text-ink dark:text-ink-subtle">{{ i + 1 }}. {{ q.payload.question }}</p>
          <span class="text-xs font-bold shrink-0" :class="resultFor(q.id)?.correct ? 'text-success' : 'text-danger'">
            {{ resultFor(q.id)?.earned }}/{{ resultFor(q.id)?.points }}
          </span>
        </div>
        <ul class="mt-3 space-y-1.5">
          <li v-for="opt in q.payload.options || []" :key="opt.id" class="flex items-center gap-2 text-sm">
            <span class="w-4 shrink-0 text-center">
              <span v-if="opt.correct" class="text-success">✓</span>
              <span v-else-if="answers[q.id]?.includes(opt.id)" class="text-danger">✕</span>
            </span>
            <span :class="opt.correct ? 'text-success dark:text-success font-semibold' : 'text-ink-muted dark:text-ink-subtle'">{{ opt.text }}</span>
          </li>
        </ul>
      </div>

      <button @click="goBack" class="w-full px-4 py-3 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl">Terminer</button>
    </div>

    <!-- Quiz -->
    <div v-else class="space-y-5">
      <div v-for="(q, i) in questions" :key="q.id" class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5">
        <p class="text-sm font-bold text-ink dark:text-ink-subtle mb-1">{{ i + 1 }}. {{ q.payload.question }}</p>
        <p class="text-[10px] text-ink-subtle mb-3">{{ q.payload.points || 1 }} point{{ (q.payload.points || 1) > 1 ? 's' : '' }} · cochez la/les bonne(s) réponse(s)</p>
        <div class="space-y-2">
          <label v-for="opt in q.payload.options || []" :key="opt.id"
            class="flex items-center gap-3 p-2.5 rounded-xl border cursor-pointer transition-colors"
            :class="answers[q.id]?.includes(opt.id) ? 'border-primary bg-primary-soft dark:bg-primary-soft' : 'border-line dark:border-line'">
            <input type="checkbox" :value="opt.id" v-model="answers[q.id]" class="accent-primary shrink-0" />
            <span class="text-sm text-ink dark:text-ink-subtle">{{ opt.text }}</span>
          </label>
        </div>
      </div>

      <button @click="submit" :disabled="submitting" class="w-full px-4 py-3 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl disabled:opacity-50">
        {{ submitting ? 'Correction…' : 'Valider mes réponses' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionItem, RunResult } from '../../stores/revision'
import { ChevronLeft } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const setName = ref('')
const loading = ref(true)
const submitting = ref(false)
const questions = ref<RevisionItem[]>([])
const answers = reactive<Record<number, string[]>>({})
const result = ref<RunResult | null>(null)

onMounted(async () => {
  try {
    const [set, items] = await Promise.all([
      revisionStore.fetchSet(setId),
      revisionStore.fetchStudyItems(setId),
    ])
    setName.value = set.name
    questions.value = items
    items.forEach((q) => { answers[q.id] = [] })
  } catch (e) {
    console.error('Erreur de chargement du QCM', e)
  } finally {
    loading.value = false
  }
})

function resultFor(itemId: number) {
  return result.value?.results.find((r) => r.item_id === itemId)
}

async function submit() {
  if (submitting.value) return
  submitting.value = true
  try {
    result.value = await revisionStore.runQcm(
      setId,
      questions.value.map((q) => ({ item_id: q.id, selected_option_ids: answers[q.id] || [] })),
    )
  } catch (e) {
    console.error('Erreur de correction', e)
  } finally {
    submitting.value = false
  }
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
