<template>
  <PageContainer>
    <PageHeader
      title="Réviser"
      subtitle="Vue d'ensemble de tout ce qui est dû, tous decks et séries confondus."
    />

    <!-- Bandeau résumé : file unifiée (focusStore) -->
    <BaseCard
      class="border-l-4 border-l-accent flex flex-col sm:flex-row sm:items-center justify-between gap-6"
    >
      <div class="flex items-center gap-4 min-w-0">
        <div
          class="w-12 h-12 shrink-0 rounded-full bg-accent-soft text-accent flex items-center justify-center"
        >
          <Flame class="w-6 h-6" />
        </div>
        <div class="min-w-0">
          <p class="text-base font-bold text-ink">{{ summarySentence }}</p>
          <p class="text-meta text-ink-muted mt-1">{{ summarySubSentence }}</p>
        </div>
      </div>
      <div class="flex items-center gap-2 shrink-0 flex-wrap">
        <router-link
          to="/exam/setup"
          class="inline-flex items-center gap-2 px-4 py-2.5 text-xs font-bold rounded-lg bg-surface text-ink border border-line hover:bg-surface-soft transition-colors"
        >
          <ShieldAlert class="w-4 h-4" />
          Examen blanc
        </router-link>
        <BaseButton
          data-test="review-all"
          :disabled="focusStore.totalDue === 0"
          @click="continueReview"
        >
          <template #icon><Play class="w-4 h-4" /></template>
          {{ focusStore.totalDue > 0 ? 'Tout réviser' : 'Rien à réviser' }}
        </BaseButton>
      </div>
    </BaseCard>

    <!-- Erreur de chargement -->
    <p
      v-if="focusStore.error"
      class="rounded-lg border border-danger bg-danger-soft px-4 py-3 text-sm font-semibold text-danger"
    >
      {{ focusStore.error }}
    </p>

    <!-- Chargement -->
    <div v-if="focusStore.loading" class="space-y-4">
      <BaseSkeleton v-for="n in 3" :key="n" custom-class="h-28 w-full" />
    </div>

    <template v-else>
      <!-- En retard / Aujourd'hui : même forme de ligne, une source par ligne -->
      <BaseCard v-for="section in dueSections" :key="section.key" :data-test="section.testId">
        <div class="flex items-center gap-2.5 mb-4">
          <h3 class="font-display text-base font-bold" :class="section.titleClass">
            {{ section.title }}
          </h3>
          <span class="font-mono text-xs px-2 py-0.5 rounded-full" :class="section.countClass">{{
            section.items.length
          }}</span>
        </div>

        <div class="flex flex-col">
          <div
            v-for="item in section.items"
            :key="`${item.type}-${item.id}`"
            :data-test="`due-row-${item.type}-${item.id}`"
            class="flex items-center gap-3 sm:gap-4 py-3.5 border-b border-dashed border-line last:border-b-0"
          >
            <div class="w-1 self-stretch rounded-sm shrink-0" :class="section.railClass" />
            <span
              :data-test="`badge-${item.type}-${item.id}`"
              class="font-mono text-tiny font-bold uppercase tracking-wide px-2 py-0.5 rounded-full shrink-0"
              :class="badgeClass(item)"
            >
              {{ badgeLabel(item) }}
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-ink truncate">{{ item.title }}</p>
              <p class="font-mono text-xs text-ink-muted mt-0.5 truncate">{{ metaLine(item) }}</p>
            </div>
            <button
              :data-test="`review-${item.type}-${item.id}`"
              class="shrink-0 inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-line bg-surface text-ink text-xs font-bold hover:bg-surface-soft transition-colors"
              @click="studyItem(item)"
            >
              <Play class="w-3.5 h-3.5" />
              Réviser
            </button>
          </div>
        </div>
      </BaseCard>

      <!-- À venir : /focus/forecast ne renvoie qu'une charge agrégée par jour
           (flashcards uniquement), pas des sources nommées — on liste donc les
           jours à charge non nulle plutôt que d'inventer des lignes par source. -->
      <BaseCard v-if="upcomingDays.length > 0" data-test="section-upcoming">
        <div class="flex items-center gap-2.5 mb-4 flex-wrap">
          <h3 class="font-display text-base font-bold text-ink-muted">À venir</h3>
          <span class="font-mono text-xs px-2 py-0.5 rounded-full bg-app text-ink-muted">{{
            upcomingDays.length
          }}</span>
          <span class="font-mono text-tiny text-ink-subtle uppercase tracking-wide"
            >Charge prévue · flashcards</span
          >
        </div>

        <div class="flex flex-col">
          <div
            v-for="day in upcomingDays"
            :key="day.date"
            :data-test="`upcoming-row-${day.date}`"
            class="flex items-center gap-3 sm:gap-4 py-3.5 border-b border-dashed border-line last:border-b-0"
          >
            <div class="w-1 self-stretch rounded-sm shrink-0 bg-line" />
            <span
              class="font-mono text-tiny font-bold uppercase tracking-wide px-2 py-0.5 rounded-full shrink-0 bg-cat-deck text-primary-ink"
            >
              Cartes
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-ink truncate">{{ day.title }}</p>
              <p class="font-mono text-xs text-ink-muted mt-0.5">{{ day.meta }}</p>
            </div>
            <span
              class="shrink-0 font-mono text-tiny font-bold uppercase tracking-wide text-ink-muted px-2.5 py-1 rounded-full bg-surface-soft"
              >{{ day.label }}</span
            >
          </div>
        </div>
      </BaseCard>

      <!-- Rien à réviser -->
      <BaseCard v-if="dueSections.length === 0 && upcomingDays.length === 0" padding="none">
        <BaseEmptyState
          title="Tout est à jour 🎉"
          description="Aucun deck, aucune série et aucune feuille blanche n'attend votre révision aujourd'hui."
        >
          <template #icon><Flame class="w-6 h-6" /></template>
        </BaseEmptyState>
      </BaseCard>
    </template>
  </PageContainer>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Flame, Play, ShieldAlert } from 'lucide-vue-next'
import {
  PageContainer,
  PageHeader,
  BaseButton,
  BaseCard,
  BaseEmptyState,
  BaseSkeleton,
} from '../../components/ui/base'
import { useFocusStore } from '../../stores/focus'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionType } from '../../stores/revision'
import type { FocusItem } from '../../services/focusService'

const router = useRouter()
const focusStore = useFocusStore()
const revisionStore = useRevisionStore()

// ─── Navigation ─────────────────────────────────────────────────────────────

/** Type propre de l'ensemble de révision (null = hétérogène, undefined = inconnu). */
function setType(item: FocusItem): RevisionType | null | undefined {
  const set = revisionStore.sets.find((s) => String(s.id) === String(item.id))
  return set ? set.type : undefined
}

function studyItem(item: FocusItem) {
  if (item.type === 'deck') router.push(`/decks/${item.id}/study?focus=true`)
  else if (item.type === 'note') router.push(`/notes/${item.id}/blurting?focus=true&from=focus`)
  else if (item.type === 'assignment') router.push(`/bibliotheque/${item.id}`)
  else if (item.type === 'revision_set') {
    // Un ensemble homogène QCM se joue en mode « run » (série notée) ; tout le
    // reste — y compris un ensemble inconnu du store — passe par /study.
    const mode = setType(item) === 'qcm' ? 'run' : 'study'
    router.push(`/revision/sets/${item.id}/${mode}`)
  }
}

function continueReview() {
  const first = focusStore.startUnifiedReview()
  if (first) studyItem(first)
}

// ─── Badges de type ─────────────────────────────────────────────────────────

const SET_TYPE_BADGES: Record<RevisionType, string> = {
  qcm: 'Série QCM',
  vf: 'Vrai-Faux',
  association: 'Association',
  definition: 'Définition',
  ordre: 'Ordre',
}

function badgeLabel(item: FocusItem): string {
  if (item.type === 'deck') return 'Deck'
  if (item.type === 'note') return 'Feuille blanche'
  if (item.type === 'assignment') return 'Devoir'
  const type = setType(item)
  if (type === undefined) return 'Série'
  return type === null ? 'Série mixte' : SET_TYPE_BADGES[type]
}

function badgeClass(item: FocusItem): string {
  if (item.type === 'deck') return 'bg-cat-deck text-primary-ink'
  if (item.type === 'note') return 'bg-success text-primary-ink'
  if (item.type === 'assignment') return 'bg-ink-muted text-app'
  return 'bg-cat-set text-primary-ink'
}

// ─── Lignes ─────────────────────────────────────────────────────────────────

function plural(n: number): string {
  return n > 1 ? 's' : ''
}

function lastPassage(days: number): string {
  if (days <= 0) return "dernier passage aujourd'hui"
  if (days === 1) return 'dernier passage hier'
  return `dernier passage il y a ${days} jours`
}

function metaLine(item: FocusItem): string {
  const parts: string[] = []

  if (item.type === 'deck') {
    parts.push(`${item.count} carte${plural(item.count)}${item.is_late ? ' en retard' : ''}`)
  } else if (item.type === 'revision_set') {
    parts.push(`${item.count} élément${plural(item.count)} à revoir`)
  } else if (item.type === 'note') {
    parts.push('Feuille blanche sur 1 note')
  } else {
    parts.push(item.due_date ? `à rendre le ${item.due_date}` : 'devoir à rendre')
    return parts.join(' · ')
  }

  if (item.last_session_ago_days !== null && item.last_session_ago_days !== undefined) {
    parts.push(lastPassage(item.last_session_ago_days))
  } else {
    parts.push('jamais révisé')
  }
  return parts.join(' · ')
}

// ─── Sections « En retard » / « Aujourd'hui » ───────────────────────────────

interface DueSection {
  key: string
  testId: string
  title: string
  titleClass: string
  countClass: string
  railClass: string
  items: FocusItem[]
}

const dueSections = computed<DueSection[]>(() =>
  [
    {
      key: 'late',
      testId: 'section-late',
      title: 'En retard',
      titleClass: 'text-danger',
      countClass: 'bg-danger-soft text-danger',
      railClass: 'bg-danger',
      items: focusStore.items.filter((i) => i.is_late),
    },
    {
      key: 'today',
      testId: 'section-today',
      title: "Aujourd'hui",
      titleClass: 'text-ink',
      countClass: 'bg-accent-soft text-ink-muted',
      railClass: 'bg-accent',
      items: focusStore.items.filter((i) => !i.is_late),
    },
  ].filter((s) => s.items.length > 0),
)

// ─── Section « À venir » ────────────────────────────────────────────────────

/** Écart en jours pleins entre aujourd'hui (local) et une date ISO `YYYY-MM-DD`. */
function daysFromToday(dateStr: string): number {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const target = new Date(`${dateStr}T00:00:00`)
  return Math.round((target.getTime() - today.getTime()) / 86400000)
}

const upcomingDateFormat = new Intl.DateTimeFormat('fr-FR', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
})

interface UpcomingDay {
  date: string
  title: string
  meta: string
  label: string
}

const upcomingDays = computed<UpcomingDay[]>(() =>
  focusStore.forecast
    .map((f) => ({ ...f, days: daysFromToday(f.date) }))
    .filter((f) => f.days >= 1 && f.count > 0)
    .sort((a, b) => a.days - b.days)
    .map((f) => {
      const formatted = upcomingDateFormat.format(new Date(`${f.date}T00:00:00`))
      return {
        date: f.date,
        title: formatted.charAt(0).toUpperCase() + formatted.slice(1),
        meta: `${f.count} carte${plural(f.count)} prévue${plural(f.count)}`,
        label: f.days === 1 ? 'DEMAIN' : `${f.days} JOURS`,
      }
    }),
)

// ─── Bandeau résumé ─────────────────────────────────────────────────────────

const revisionSetDue = computed(() =>
  focusStore.items.filter((i) => i.type === 'revision_set').reduce((acc, i) => acc + i.count, 0),
)

const summarySentence = computed(() => {
  if (focusStore.totalDue === 0) return 'Tout est à jour 🎉'

  const parts: string[] = []
  if (focusStore.flashcardCount > 0)
    parts.push(`${focusStore.flashcardCount} carte${plural(focusStore.flashcardCount)}`)
  if (revisionSetDue.value > 0)
    parts.push(`${revisionSetDue.value} série${plural(revisionSetDue.value)}`)
  if (focusStore.blurtingCount > 0)
    parts.push(
      `${focusStore.blurtingCount} feuille${plural(focusStore.blurtingCount)} blanche${plural(focusStore.blurtingCount)}`,
    )
  if (focusStore.assignmentCount > 0)
    parts.push(`${focusStore.assignmentCount} devoir${plural(focusStore.assignmentCount)}`)

  const listed =
    parts.length > 1 ? `${parts.slice(0, -1).join(', ')} et ${parts[parts.length - 1]}` : parts[0]
  const verb = focusStore.totalDue > 1 ? 'vous attendent' : 'vous attend'
  return `${listed} ${verb} aujourd'hui`
})

const summarySubSentence = computed(() => {
  if (focusStore.totalDue === 0)
    return 'File unifiée : flashcards, séries typées et feuilles blanches.'

  const lateItems = focusStore.items.filter((i) => i.is_late)
  if (focusStore.lateCount === 0 || lateItems.length === 0)
    return 'Aucun retard : vous êtes à jour sur vos échéances.'
  if (lateItems.length === 1)
    return `Dont ${focusStore.lateCount} en retard sur « ${lateItems[0].title} ».`
  return `Dont ${focusStore.lateCount} en retard, répartis sur ${lateItems.length} sources.`
})

// ─── Chargement ─────────────────────────────────────────────────────────────

onMounted(async () => {
  // `revisionStore.sets` sert uniquement à connaître le type propre d'un
  // ensemble dû (badge + /run vs /study) : son échec ne doit pas vider le flux.
  await Promise.all([
    focusStore.loadFocusData(),
    revisionStore.fetchSets().catch((err) => {
      console.error('Erreur de chargement des ensembles de révision', err)
    }),
  ])
})
</script>
