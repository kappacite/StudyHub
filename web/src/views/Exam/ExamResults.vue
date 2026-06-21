<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '../../services/examService'
import type { ExamSession } from '../../services/examService'
import { Trophy, Clock, RotateCcw, CheckCircle2, XCircle, FileText, HelpCircle, ChevronLeft } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const sessionId = Number(route.params.id)

const session = ref<ExamSession | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await examService.getExamSession(sessionId)
    if (!data.completed_at) {
      router.push(`/exam/${sessionId}`)
      return
    }
    session.value = data
  } catch (err) {
    console.error("Erreur lors du chargement des résultats", err)
    router.push('/exam/setup')
  } finally {
    loading.value = false
  }
})

const formattedTimeTaken = computed(() => {
  if (!session.value || session.value.time_taken_seconds === null) return ''
  const secs = session.value.time_taken_seconds
  const mins = Math.floor(secs / 60)
  const remainingSecs = secs % 60
  if (mins === 0) return `${remainingSecs} seconde(s)`
  return `${mins} min et ${remainingSecs} sec`
})

function getOptionClass(opt: any, item: any) {
  const isSelected = item.user_answer === opt.id
  
  if (opt.correct) {
    return 'bg-success-soft dark:bg-success-soft border-success text-success dark:text-success font-medium'
  }
  if (isSelected && !opt.correct) {
    return 'bg-danger-soft dark:bg-danger-soft border-danger text-danger dark:text-danger font-medium'
  }
  return 'bg-surface-soft dark:bg-surface-soft border-line dark:border-line text-ink-muted dark:text-ink-subtle'
}

function handleRestart() {
  router.push('/exam/setup')
}
</script>

<template>
  <div class="max-w-4xl mx-auto py-8 px-4 space-y-8">
    
    <!-- Header de Retour -->
    <div class="flex items-center gap-3">
      <button 
        @click="handleRestart"
        class="p-2 text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle rounded-xl hover:bg-surface-soft dark:hover:bg-surface-soft transition-all"
        title="Retour au configurateur"
      >
        <ChevronLeft class="w-5 h-5" />
      </button>
      <div>
        <h1 class="text-xl font-black text-ink dark:text-white">Résultats de l'examen</h1>
        <p class="text-xs text-ink-muted dark:text-ink-subtle">Simulation complétée avec succès</p>
      </div>
    </div>

    <div v-if="!loading && session" class="space-y-8 animate-fade-in">
      
      <!-- Bilan & Scores Card -->
      <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-8 shadow-sm grid grid-cols-1 md:grid-cols-3 gap-6 relative overflow-hidden items-center">
        <!-- Background decorative blurs -->
        <div class="absolute -top-12 -left-12 w-36 h-36 bg-primary dark:bg-primary rounded-full blur-2xl pointer-events-none"></div>
        
        <!-- Score global -->
        <div class="text-center md:border-r border-line dark:border-line py-4 space-y-2 relative z-10">
          <div class="inline-flex p-3 bg-primary-soft dark:bg-primary-soft rounded-2xl text-primary dark:text-primary mb-1">
            <Trophy class="w-8 h-8 animate-bounce" />
          </div>
          <div>
            <span class="text-4xl font-black font-mono text-primary dark:text-primary block">
              {{ Math.round(session.score_pct || 0) }}%
            </span>
            <span class="text-xs font-bold text-ink-subtle dark:text-ink-muted uppercase tracking-widest block mt-1">Score Global</span>
          </div>
        </div>

        <!-- Détail modules -->
        <div class="md:border-r border-line dark:border-line px-6 py-2 space-y-3.5 relative z-10 text-xs font-semibold">
          <div>
            <div class="flex justify-between items-center text-ink-muted mb-1">
              <span>Section QCM (IA)</span>
              <span class="font-mono font-bold text-ink dark:text-ink-subtle" v-if="session.qcm_score !== null">
                {{ Math.round(session.qcm_score) }}%
              </span>
              <span class="text-ink-subtle font-medium" v-else>Non inclus</span>
            </div>
            <div class="w-full bg-surface-soft dark:bg-surface-soft h-2 rounded-full overflow-hidden">
              <div 
                class="bg-primary h-full transition-all duration-300"
                :style="{ width: `${session.qcm_score || 0}%` }"
              ></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between items-center text-ink-muted mb-1">
              <span>Section Cartes Flash</span>
              <span class="font-mono font-bold text-ink dark:text-ink-subtle" v-if="session.flashcard_score !== null">
                {{ Math.round(session.flashcard_score) }}%
              </span>
              <span class="text-ink-subtle font-medium" v-else>Non incluse</span>
            </div>
            <div class="w-full bg-surface-soft dark:bg-surface-soft h-2 rounded-full overflow-hidden">
              <div 
                class="bg-accent h-full transition-all duration-300"
                :style="{ width: `${session.flashcard_score || 0}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Temps & Action -->
        <div class="text-center py-4 space-y-4 relative z-10">
          <div class="flex flex-col items-center justify-center">
            <Clock class="w-7 h-7 text-primary mb-1" />
            <span class="text-sm font-black text-ink dark:text-ink-subtle">
              {{ formattedTimeTaken }}
            </span>
            <span class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest mt-1">Temps écoulé</span>
          </div>

          <button
            @click="handleRestart"
            class="inline-flex items-center gap-1.5 px-4 py-2 border border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft text-xs font-bold rounded-xl transition-all"
          >
            <RotateCcw class="w-3.5 h-3.5" />
            Nouvelle simulation
          </button>
        </div>

      </div>

      <!-- Correction Détaillée -->
      <div class="space-y-4">
        <h2 class="text-base font-black text-ink dark:text-white flex items-center gap-2">
          Correction Détaillée
        </h2>

        <div class="space-y-4">
          <div 
            v-for="item in session.items" 
            :key="item.id"
            class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-6 shadow-xs space-y-4"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 text-xs font-bold text-ink-subtle">
                <span>N° {{ item.id }}</span>
                <span>•</span>
                <span class="flex items-center gap-1">
                  <HelpCircle v-if="item.item_type === 'qcm'" class="w-3.5 h-3.5 text-primary" />
                  <FileText v-else class="w-3.5 h-3.5 text-primary" />
                  {{ item.item_type === 'qcm' ? 'QCM' : 'Flashcard' }}
                </span>
              </div>

              <!-- Badge correct / incorrect -->
              <span 
                v-if="item.is_correct" 
                class="inline-flex items-center gap-1 text-success dark:text-success font-bold text-xs"
              >
                <CheckCircle2 class="w-3.5 h-3.5" />
                Correct
              </span>
              <span 
                v-else 
                class="inline-flex items-center gap-1 text-danger dark:text-danger font-bold text-xs"
              >
                <XCircle class="w-3.5 h-3.5" />
                Incorrect
              </span>
            </div>

            <!-- Front (Question / Recto) -->
            <p class="text-sm font-black text-ink dark:text-white leading-relaxed">
              {{ item.front }}
            </p>

            <!-- OPTIONS (QCM) -->
            <div v-if="item.item_type === 'qcm' && item.options" class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div 
                v-for="opt in item.options" 
                :key="opt.id"
                class="p-3.5 border rounded-xl flex items-center gap-2.5"
                :class="getOptionClass(opt, item)"
              >
                <span class="w-5 h-5 rounded-md bg-surface-soft dark:bg-surface-soft text-[10px] uppercase font-black text-ink-subtle flex items-center justify-center shrink-0">
                  {{ opt.id }}
                </span>
                <span>{{ opt.text }}</span>
              </div>
            </div>

            <!-- BACK (Flashcard) -->
            <div v-else-if="item.item_type === 'flashcard'" class="space-y-3">
              <div class="flex items-center justify-between text-xs font-semibold">
                <span class="text-ink-subtle">
                  Auto-évaluation : 
                  <span :class="[item.is_correct ? 'text-success dark:text-success' : 'text-danger dark:text-danger']">
                    {{ item.is_correct ? 'Sûr de soi' : 'Oublié / Faux' }}
                  </span>
                </span>
              </div>
              <div class="p-4 bg-surface-soft dark:bg-surface-soft rounded-xl border border-line dark:border-line text-xs leading-relaxed">
                <span class="block text-[10px] font-bold text-primary uppercase tracking-widest mb-1">Réponse attendue</span>
                <p class="text-ink dark:text-ink-subtle whitespace-pre-line font-medium">{{ item.back }}</p>
              </div>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>
