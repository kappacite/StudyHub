<template>
  <div class="space-y-6 max-w-xl mx-auto animate-fade-in">
    <div class="flex items-center justify-between text-sm font-semibold">
      <button
        class="text-ink-muted hover:text-primary dark:text-ink-subtle flex items-center gap-1"
        @click="goBack"
      >
        <ChevronLeft class="w-4 h-4" /> Retour
      </button>
      <span
        class="text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary px-2.5 py-1 rounded-lg uppercase tracking-wider"
      >
        {{ filterType ? TYPE_LABELS[filterType] || 'Révision' : 'Révision' }} · {{ setName }}
      </span>
    </div>

    <div
      v-if="loading"
      class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest"
    >
      Chargement…
    </div>

    <div
      v-else-if="items.length === 0"
      class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-10 text-center space-y-3"
    >
      <p class="text-sm text-ink-muted dark:text-ink-subtle">Rien à réviser pour l'instant. 🎉</p>
      <div class="flex items-center justify-center gap-3">
        <button
          class="px-4 py-2 text-sm font-bold text-white bg-primary hover:bg-primary-strong rounded-xl"
          @click="goBack"
        >
          Retour
        </button>
        <button
          class="px-4 py-2 text-sm font-bold text-primary border border-primary hover:bg-primary-soft dark:hover:bg-primary-soft rounded-xl"
          @click="reviewAnyway"
        >
          Réviser quand même
        </button>
      </div>
    </div>

    <template v-else>
      <!-- Progress -->
      <div class="space-y-2">
        <div
          class="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-ink-subtle"
        >
          <span>{{ index + 1 }} / {{ items.length }}</span>
          <span>{{ correctCount }} bonne(s)</span>
        </div>
        <div class="w-full bg-surface-soft dark:bg-surface-soft rounded-full h-2 overflow-hidden">
          <div
            class="bg-primary h-full rounded-full transition-all"
            :style="{ width: `${(index / items.length) * 100}%` }"
          ></div>
        </div>
      </div>

      <div
        class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm space-y-5"
      >
        <!-- VRAI / FAUX -->
        <template v-if="current.type === 'vf'">
          <p class="text-lg font-bold text-ink dark:text-ink-subtle">
            {{ current.payload.assertion }}
          </p>
          <div v-if="phase === 'answer'" class="grid grid-cols-2 gap-3">
            <button
              class="py-3 rounded-xl text-sm font-bold border border-line dark:border-line hover:bg-success-soft dark:hover:bg-success-soft disabled:opacity-50"
              :disabled="busy"
              @click="submitVf(true)"
            >
              Vrai
            </button>
            <button
              class="py-3 rounded-xl text-sm font-bold border border-line dark:border-line hover:bg-danger-soft dark:hover:bg-danger-soft disabled:opacity-50"
              :disabled="busy"
              @click="submitVf(false)"
            >
              Faux
            </button>
          </div>
          <div v-else class="space-y-2">
            <p class="text-sm font-bold" :class="lastCorrect ? 'text-success' : 'text-danger'">
              {{ lastCorrect ? 'Correct !' : 'Incorrect.' }} Réponse :
              {{ current.payload.correct ? 'Vrai' : 'Faux' }}
            </p>
            <p
              v-if="current.payload.justification"
              class="text-sm text-ink-muted dark:text-ink-subtle"
            >
              {{ current.payload.justification }}
            </p>
            <template v-if="phase === 'self-eval'">
              <p
                class="text-center text-[10px] font-bold text-ink-subtle uppercase tracking-widest"
              >
                Votre auto-évaluation
              </p>
              <SelfEvalButtons :disabled="busy" @select="selfEvalGraded" />
            </template>
          </div>
        </template>

        <!-- FLASHCARD (auto-évaluation, meme famille que DEFINITION) -->
        <template v-else-if="current.type === 'flashcard'">
          <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest">Recto</p>
          <p class="text-lg font-bold text-ink dark:text-ink-subtle">
            {{ current.payload.front }}
          </p>
          <button
            v-if="phase === 'answer'"
            data-test="reveal-flashcard-button"
            class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong"
            @click="phase = 'reveal'"
          >
            Révéler le verso
          </button>
          <template v-else>
            <p
              class="text-sm text-ink dark:text-ink-subtle border-t border-line dark:border-line pt-3"
            >
              {{ current.payload.back }}
            </p>
            <template v-if="phase === 'reveal'">
              <p
                class="text-center text-[10px] font-bold text-ink-subtle uppercase tracking-widest"
              >
                Votre auto-évaluation
              </p>
              <SelfEvalButtons :disabled="busy" @select="selfEval" />
            </template>
          </template>
        </template>

        <!-- DEFINITION (auto-évaluation) -->
        <template v-else-if="current.type === 'definition'">
          <p class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest">Terme</p>
          <p class="text-lg font-bold text-ink dark:text-ink-subtle">{{ current.payload.term }}</p>
          <button
            v-if="phase === 'answer'"
            class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong"
            @click="phase = 'reveal'"
          >
            Révéler la définition
          </button>
          <template v-else>
            <p
              class="text-sm text-ink dark:text-ink-subtle border-t border-line dark:border-line pt-3"
            >
              {{ current.payload.definition }}
            </p>
            <template v-if="phase === 'reveal'">
              <p
                class="text-center text-[10px] font-bold text-ink-subtle uppercase tracking-widest"
              >
                Votre auto-évaluation
              </p>
              <SelfEvalButtons :disabled="busy" @select="selfEval" />
            </template>
          </template>
        </template>

        <!-- ASSOCIATION -->
        <template v-else-if="current.type === 'association'">
          <p class="text-sm font-bold text-ink dark:text-ink-subtle">
            {{ current.payload.title || 'Associez chaque élément' }}
          </p>
          <div class="space-y-2">
            <div v-for="(left, i) in leftItems" :key="i" class="flex items-center gap-2">
              <span class="flex-1 text-sm font-medium text-ink dark:text-ink-subtle truncate">{{
                left
              }}</span>
              <span class="text-ink-subtle">→</span>
              <select
                v-model="matches[left]"
                :disabled="phase !== 'answer'"
                class="flex-1 px-3 py-2 text-sm rounded-xl border border-line dark:border-line bg-surface dark:bg-surface-soft"
              >
                <option value="">—</option>
                <option v-for="r in rightOptions" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
          </div>
          <button
            v-if="phase === 'answer'"
            :disabled="!allMatched || busy"
            class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong disabled:opacity-50"
            @click="submitAssoc"
          >
            {{ busy ? 'Correction…' : 'Valider' }}
          </button>
          <template v-else>
            <p class="text-sm font-bold" :class="lastCorrect ? 'text-success' : 'text-danger'">
              {{ lastCorrect ? 'Tout est correct !' : 'Des associations sont erronées.' }}
            </p>
            <template v-if="phase === 'self-eval'">
              <p
                class="text-center text-[10px] font-bold text-ink-subtle uppercase tracking-widest"
              >
                Votre auto-évaluation
              </p>
              <SelfEvalButtons :disabled="busy" @select="selfEvalGraded" />
            </template>
          </template>
        </template>

        <!-- ORDRE -->
        <template v-else-if="current.type === 'ordre'">
          <p class="text-sm font-bold text-ink dark:text-ink-subtle">
            {{ current.payload.title || 'Remettez dans le bon ordre' }}
          </p>
          <ul class="space-y-2">
            <li
              v-for="(step, i) in ordering"
              :key="step"
              class="flex items-center gap-2 p-2.5 rounded-xl border border-line dark:border-line"
            >
              <span class="text-xs font-bold text-ink-subtle w-5">{{ i + 1 }}</span>
              <span class="flex-1 text-sm text-ink dark:text-ink-subtle">{{ step }}</span>
              <div v-if="phase === 'answer'" class="flex flex-col">
                <button
                  :disabled="i === 0"
                  class="text-ink-subtle hover:text-primary disabled:opacity-30 leading-none"
                  @click="move(i, -1)"
                >
                  ▲
                </button>
                <button
                  :disabled="i === ordering.length - 1"
                  class="text-ink-subtle hover:text-primary disabled:opacity-30 leading-none"
                  @click="move(i, 1)"
                >
                  ▼
                </button>
              </div>
              <span
                v-else
                class="w-4 text-center"
                :class="step === (current.payload.steps || [])[i] ? 'text-success' : 'text-danger'"
              >
                {{ step === (current.payload.steps || [])[i] ? '✓' : '✕' }}
              </span>
            </li>
          </ul>
          <button
            v-if="phase === 'answer'"
            :disabled="busy"
            class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong disabled:opacity-50"
            @click="submitOrdre"
          >
            {{ busy ? 'Correction…' : 'Valider' }}
          </button>
          <template v-else>
            <p class="text-sm font-bold" :class="lastCorrect ? 'text-success' : 'text-danger'">
              {{ lastCorrect ? 'Ordre correct !' : 'Ordre incorrect.' }}
            </p>
            <template v-if="phase === 'self-eval'">
              <p
                class="text-center text-[10px] font-bold text-ink-subtle uppercase tracking-widest"
              >
                Votre auto-évaluation
              </p>
              <SelfEvalButtons :disabled="busy" @select="selfEvalGraded" />
            </template>
          </template>
        </template>

        <!-- QCM -->
        <template v-else-if="current.type === 'qcm'">
          <p class="text-sm font-bold text-ink dark:text-ink-subtle">
            {{ current.payload.question }}
          </p>
          <div v-if="phase === 'answer'" class="space-y-2">
            <label
              v-for="opt in current.payload.options || []"
              :key="opt.id"
              class="flex items-center gap-3 p-2.5 rounded-xl border cursor-pointer transition-colors"
              :class="
                qcmSelected.includes(opt.id)
                  ? 'border-primary bg-primary-soft dark:bg-primary-soft'
                  : 'border-line dark:border-line'
              "
            >
              <input
                v-model="qcmSelected"
                type="checkbox"
                :value="opt.id"
                class="accent-primary shrink-0"
              />
              <span class="text-sm text-ink dark:text-ink-subtle">{{ opt.text }}</span>
            </label>
          </div>
          <button
            v-if="phase === 'answer'"
            :disabled="busy"
            class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong disabled:opacity-50"
            @click="submitQcm"
          >
            {{ busy ? 'Correction…' : 'Valider' }}
          </button>
          <template v-else>
            <p class="text-sm font-bold" :class="lastCorrect ? 'text-success' : 'text-danger'">
              {{ lastCorrect ? 'Correct !' : 'Incorrect.' }}
            </p>
            <ul class="space-y-1.5">
              <li
                v-for="opt in current.payload.options || []"
                :key="opt.id"
                class="flex items-center gap-2 text-sm"
              >
                <span class="w-4 shrink-0 text-center">
                  <span v-if="opt.correct" class="text-success">✓</span>
                  <span v-else-if="qcmSelected.includes(opt.id)" class="text-danger">✕</span>
                </span>
                <span
                  :class="
                    opt.correct
                      ? 'text-success dark:text-success font-semibold'
                      : 'text-ink-muted dark:text-ink-subtle'
                  "
                  >{{ opt.text }}</span
                >
              </li>
            </ul>
            <template v-if="phase === 'self-eval'">
              <p
                class="text-center text-[10px] font-bold text-ink-subtle uppercase tracking-widest"
              >
                Votre auto-évaluation
              </p>
              <SelfEvalButtons :disabled="busy" @select="selfEvalGraded" />
            </template>
          </template>
        </template>

        <!-- Bouton suivant (après correction / révélation auto-corrigée) -->
        <button
          v-if="phase === 'feedback'"
          class="w-full py-3 rounded-xl text-sm font-bold text-white bg-primary hover:bg-primary-strong"
          @click="next"
        >
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
import type { RevisionItem, RevisionItemType } from '../../stores/revision'
import { ChevronLeft } from 'lucide-vue-next'
import SelfEvalButtons from '../../components/revision/SelfEvalButtons.vue'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()

const setId = Number(route.params.id)
const setName = ref('')
const filterType = ref<RevisionItemType | null>(null)
const loading = ref(true)
const items = ref<RevisionItem[]>([])
const index = ref(0)
const correctCount = ref(0)
const phase = ref<'answer' | 'reveal' | 'self-eval' | 'feedback'>('answer')
const lastCorrect = ref(false)
// Reponse soumise au check (Task 5) : reutilisee telle quelle au moment du
// grade (l'auto-evaluation ne fait que choisir le score, pas re-saisir une
// reponse), reassignee a chaque soumission vf/association/ordre.
const lastAnswer = ref<Record<string, unknown>>({})
// Garde anti double-soumission (regression finale) : empeche un double-clic
// pendant l'appel reseau en cours d'appliquer SM-2 deux fois ou d'ecrire deux
// StudySession -- desactive aussi les boutons "Valider"/Vrai/Faux et
// SelfEvalButtons a chaque emplacement ou ils sont montes.
const busy = ref(false)

const TYPE_LABELS: Record<string, string> = {
  vf: 'Vrai / Faux',
  definition: 'Définition',
  association: 'Association',
  ordre: 'Ordre',
  qcm: 'QCM',
  flashcard: 'Flashcards',
}

const current = computed(
  () => items.value[index.value] || ({ type: 'vf', payload: {} } as RevisionItem),
)

// Association
const matches = reactive<Record<string, string>>({})
const leftItems = ref<string[]>([])
const rightOptions = ref<string[]>([])
const allMatched = computed(
  () => leftItems.value.length > 0 && leftItems.value.every((l) => matches[l]),
)

// Ordre
const ordering = ref<string[]>([])

// QCM
const qcmSelected = ref<string[]>([])

function shuffle<T>(arr: T[]): T[] {
  return [...arr].sort(() => Math.random() - 0.5)
}

// Duree de revision reelle (Task 9) : chrono redemarre a chaque setupItem()
// (premier item comme suivants, cf. onMounted/next()) -- elapsedSeconds()
// donne la duree ecoulee sur l'item courant au moment de la soumission.
const itemStartedAt = ref(Date.now())

function elapsedSeconds(): number {
  return Math.max(0, Math.round((Date.now() - itemStartedAt.value) / 1000))
}

function setupItem() {
  itemStartedAt.value = Date.now()
  phase.value = 'answer'
  lastCorrect.value = false
  const payload = current.value.payload || {}
  if (current.value.type === 'association') {
    const pairs = payload.pairs || []
    leftItems.value = pairs.map((p) => p.left)
    rightOptions.value = shuffle(pairs.map((p) => p.right))
    Object.keys(matches).forEach((k) => delete matches[k])
    leftItems.value.forEach((l) => {
      matches[l] = ''
    })
  } else if (current.value.type === 'ordre') {
    ordering.value = shuffle(payload.steps || [])
  } else if (current.value.type === 'qcm') {
    qcmSelected.value = []
  }
}

// Filtrage commun a l'onMounted et a reviewAnyway (Task 7) : applique le
// filtre ?type= eventuel -- plus d'exclusion qcm (revision-qcm-heterogene,
// Task 2), le qcm est revisable comme tout autre type gradable.
function applyItemFilter(studyItems: RevisionItem[]) {
  return filterType.value ? studyItems.filter((i) => i.type === filterType.value) : studyItems
}

onMounted(async () => {
  filterType.value = (route.query.type as RevisionItemType) || null
  try {
    const [set, studyItems] = await Promise.all([
      revisionStore.fetchSet(setId),
      revisionStore.fetchStudyItems(setId),
    ])
    // Les QCM ont leur passage scoré dédié : on y redirige, sauf si on ne
    // revise qu'un sous-ensemble filtré (un ensemble heterogene ne peut de
    // toute facon jamais avoir set.type === 'qcm', donc ce garde reste
    // correct sans condition supplementaire sur filterType).
    if (set.type === 'qcm') {
      router.replace(`/revision/sets/${setId}/run`)
      return
    }
    setName.value = set.name
    items.value = applyItemFilter(studyItems)
    if (items.value.length) setupItem()
  } catch (e) {
    console.error('Erreur de chargement de la session', e)
  } finally {
    loading.value = false
  }
})

// Revision libre (Task 7, meme principe que QcmRun.vue en Task 6) : sur
// l'etat vide generique, relance le chargement en incluant les items non dus.
async function reviewAnyway() {
  try {
    const studyItems = await revisionStore.fetchStudyItems(setId, true)
    items.value = applyItemFilter(studyItems)
    if (items.value.length) setupItem()
  } catch (e) {
    console.error('Erreur de chargement de la session', e)
  }
}

async function submitVf(value: boolean) {
  await checkAndAwaitSelfEval({ value })
}

async function submitAssoc() {
  await checkAndAwaitSelfEval({ matches: { ...matches } })
}

async function submitOrdre() {
  await checkAndAwaitSelfEval({ order: [...ordering.value] })
}

async function submitQcm() {
  await checkAndAwaitSelfEval({ selected_option_ids: [...qcmSelected.value] })
}

// vf/association/ordre (Task 5) : la reponse a une correction objective, mais
// n'applique plus directement la note SM-2 -- on verifie d'abord (sans effet
// de bord) puis on affiche la correction et on attend une auto-evaluation
// manuelle (phase 'self-eval'), comme flashcard/definition.
async function checkAndAwaitSelfEval(answer: Record<string, unknown>) {
  if (busy.value) return
  busy.value = true
  try {
    lastAnswer.value = answer
    const res = await revisionStore.checkItemAnswer(setId, current.value.id, answer)
    lastCorrect.value = res.correct
    phase.value = 'self-eval'
  } catch (e) {
    console.error('Erreur de correction de la reponse', e)
  } finally {
    busy.value = false
  }
}

// flashcard/definition (inchange) : pas de correction objective, l'auto-
// evaluation applique directement la note SM-2 via answerItem().
async function selfEval(score: number) {
  if (busy.value) return
  busy.value = true
  try {
    await revisionStore.answerItem(setId, current.value.id, score, elapsedSeconds())
    applyResult(score >= 3)
  } catch (e) {
    console.error("Erreur d'enregistrement de l'auto-evaluation", e)
  } finally {
    busy.value = false
  }
}

// vf/association/ordre en phase 'self-eval' (Task 5) : applique la note SM-2
// choisie manuellement, avec la reponse deja verifiee par checkItemAnswer.
// correctCount reste base sur la correction reelle (lastCorrect, issue du
// check) et non sur le score choisi ensuite -- les deux sont volontairement
// independants (le score reflete la confiance/memorisation, pas l'exactitude).
async function selfEvalGraded(score: number) {
  if (busy.value) return
  busy.value = true
  try {
    await revisionStore.gradeItem(
      setId,
      current.value.id,
      lastAnswer.value,
      score,
      elapsedSeconds(),
    )
    if (lastCorrect.value) correctCount.value++
    phase.value = 'feedback'
  } catch (e) {
    console.error("Erreur d'enregistrement de la notation", e)
  } finally {
    busy.value = false
  }
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
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
