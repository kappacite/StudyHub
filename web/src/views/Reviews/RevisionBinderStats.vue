<template>
  <PageContainer>
    <div
      v-if="loading"
      class="py-20 text-center text-sm font-semibold text-ink-subtle uppercase tracking-widest"
    >
      Chargement des statistiques…
    </div>

    <!-- Erreur de chargement -->
    <p
      v-else-if="error"
      data-test="stats-error"
      class="rounded-lg border border-danger bg-danger-soft px-4 py-3 text-sm font-semibold text-danger"
    >
      {{ error }}
    </p>

    <template v-else-if="stats">
      <!-- En-tête -->
      <div class="flex items-end justify-between gap-5 flex-wrap">
        <div class="min-w-0">
          <p class="font-mono text-tiny tracking-wide text-ink-subtle uppercase mb-1.5">
            Bibliothèque · Classeur
          </p>
          <h1 class="font-display text-display-lg text-ink truncate">{{ stats.name }}</h1>
          <p class="text-sm text-ink-muted mt-1.5">{{ subtitleText }}</p>
        </div>
        <div class="flex items-center gap-4 shrink-0">
          <label
            class="flex items-center gap-2 text-xs font-semibold text-ink-muted cursor-pointer"
          >
            <BaseToggle
              data-test="include-descendants-toggle"
              :model-value="includeDescendants"
              @update:model-value="onToggleDescendants"
            />
            Inclure les sous-classeurs
          </label>
          <BaseButton data-test="revise-binder-button" @click="reviseBinder">
            <template #icon><Play class="w-4 h-4" /></template>
            Réviser le classeur
          </BaseButton>
        </div>
      </div>

      <!-- Vue d'ensemble : 5 blocs stat (Task 9 : ajout du temps total d'etude,
           les 4 cartes existantes -- deja revues/approuvees en tache 6 -- sont
           conservees telles quelles). -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        <BaseCard padding="lg">
          <p class="text-xs font-bold uppercase tracking-wide text-ink-subtle mb-2.5">
            Cartes totales
          </p>
          <p class="font-display font-mono text-3xl font-bold text-ink">{{ totalCardsCount }}</p>
          <p class="text-xs text-ink-muted mt-2">
            Réparties sur {{ mergedCount }} deck(s) et série(s)
          </p>
        </BaseCard>
        <BaseCard padding="lg">
          <p class="text-xs font-bold uppercase tracking-wide text-ink-subtle mb-2.5">
            Cartes maîtrisées
          </p>
          <p class="font-display font-mono text-3xl font-bold text-primary">
            {{ stats.mastered_count }}
          </p>
          <p class="text-xs text-ink-muted mt-2">
            {{ stats.mastery_rate }}% des ensembles de révision
          </p>
        </BaseCard>
        <BaseCard padding="lg">
          <p class="text-xs font-bold uppercase tracking-wide text-ink-subtle mb-2.5">
            Taux de réussite moyen
          </p>
          <p class="font-display font-mono text-3xl font-bold text-ink">
            {{ stats.avg_success_rate }}%
          </p>
          <p class="text-xs text-ink-muted mt-2">
            Rétention actuelle : {{ stats.avg_retrievability }}%
          </p>
        </BaseCard>
        <BaseCard padding="lg">
          <p class="text-xs font-bold uppercase tracking-wide text-ink-subtle mb-2.5">À réviser</p>
          <p
            class="font-display font-mono text-3xl font-bold"
            :class="stats.due_count ? 'text-accent' : 'text-ink'"
          >
            {{ stats.due_count }}
          </p>
          <p class="text-xs text-ink-muted mt-2">{{ leechesHint }}</p>
        </BaseCard>
        <BaseCard padding="lg" data-test="total-duration-card">
          <p class="text-xs font-bold uppercase tracking-wide text-ink-subtle mb-2.5">
            Temps total d'étude
          </p>
          <p class="font-display font-mono text-3xl font-bold text-ink">
            {{ formatDuration(stats.total_duration_seconds) }}
          </p>
          <p class="text-xs text-ink-muted mt-2">Depuis la création</p>
        </BaseCard>
      </div>

      <!-- Verdicts actionnables -->
      <BaseCard v-if="stats.verdicts.length" padding="lg" class="space-y-2">
        <p class="text-tiny font-bold text-ink-subtle uppercase tracking-widest">À retenir</p>
        <ul class="space-y-1.5">
          <li
            v-for="(v, i) in stats.verdicts"
            :key="i"
            class="flex items-start gap-2 text-sm text-ink dark:text-ink-subtle"
          >
            <span class="text-primary mt-0.5">›</span>{{ v }}
          </li>
        </ul>
      </BaseCard>

      <!-- Répartition par deck et série : fusion frontend des decks classiques
           (SM2, /stats/decks/:id) et des ensembles de révision (/stats/binders/:id) --
           pas de nouvel endpoint, cf. brief tache 6. -->
      <BaseCard padding="lg">
        <h3 class="font-display text-base font-bold text-ink mb-1">
          Répartition par deck et série
        </h3>
        <p class="text-xs text-ink-subtle mb-4">
          Maîtrise pour les ensembles de révision · rétention (cartes non dues) pour les decks
          classiques.
        </p>
        <div class="flex flex-col">
          <button
            v-for="row in mergedRows"
            :key="row.key"
            data-test="merged-row"
            class="w-full flex items-center gap-4 py-3.5 border-b border-dashed border-line last:border-0 text-left hover:bg-surface-soft transition-colors -mx-2 px-2 rounded-lg"
            @click="openRow(row)"
          >
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-ink truncate">{{ row.name }}</p>
              <p class="font-mono text-tiny text-ink-subtle mt-0.5">
                {{ row.typeLabel }} · {{ row.itemsLabel }} · {{ row.dueLabel }}
              </p>
            </div>
            <div class="w-32 sm:w-56 shrink-0 h-2 rounded-full bg-line overflow-hidden">
              <div
                class="h-full rounded-full"
                :class="row.hasMastery ? successRateBgClass(row.masteryRate) : 'bg-line'"
                :style="{ width: `${row.hasMastery ? row.masteryRate : 0}%` }"
              ></div>
            </div>
            <span
              class="w-11 shrink-0 text-right font-mono text-xs font-bold"
              :class="row.hasMastery ? successRateTextClass(row.masteryRate) : 'text-ink-subtle'"
              >{{ row.hasMastery ? `${row.masteryRate}%` : '—' }}</span
            >
          </button>
          <p
            v-if="mergedRows.length === 0"
            class="text-center py-6 text-xs text-ink-subtle uppercase tracking-wider"
          >
            Aucun deck ni ensemble de révision dans ce classeur.
          </p>
        </div>
      </BaseCard>

      <!-- Répartition par type : widget existant (deja corrige pour les ensembles
           heterogenes), conserve tel quel en section secondaire additive -- pas un
           remplacement de la liste ci-dessus (decision explicite du brief). -->
      <BaseCard v-if="stats.by_type.length" padding="lg">
        <p class="text-tiny font-bold text-ink-subtle uppercase tracking-widest mb-3">
          Répartition par type
        </p>
        <div class="space-y-2">
          <div v-for="bt in stats.by_type" :key="bt.type" class="flex items-center gap-3">
            <span class="w-24 shrink-0 text-xs font-semibold text-ink-muted dark:text-ink-subtle">{{
              typeLabel(bt.type)
            }}</span>
            <div
              class="flex-1 h-2 rounded-full bg-surface-soft dark:bg-surface-soft overflow-hidden"
            >
              <div
                class="h-full bg-primary rounded-full"
                :style="{ width: `${bt.mastery_rate}%` }"
              ></div>
            </div>
            <span class="shrink-0 text-[11px] text-ink-subtle w-28 text-right"
              >{{ bt.mastered_count }}/{{ bt.items_count }} mûrs · {{ bt.sets_count }} ens.</span
            >
          </div>
        </div>
      </BaseCard>
    </template>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRevisionStore } from '../../stores/revision'
import type { BinderStats, RevisionType, RevisionItemType } from '../../stores/revision'
import { useDecksStore } from '../../stores/decks'
import type { Deck, DeckStatsResponse } from '../../stores/decks'
import { REVISION_ITEM_TYPE_META } from '../../utils/revisionItemTypeMeta'
import { successRateTextClass, successRateBgClass } from '../../utils/successRate'
import { formatDuration } from '../../utils/duration'
import { PageContainer, BaseCard, BaseButton, BaseToggle } from '../../components/ui/base'
import { Play } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const revisionStore = useRevisionStore()
const decksStore = useDecksStore()

const binderId = String(route.params.id)
const loading = ref(true)
const stats = ref<BinderStats | null>(null)
const error = ref<string | null>(null)
const includeDescendants = ref(true)

// DeckStatsResponse (retention_rate uniquement, pas de "mastered_count" cote
// deck classique) importe depuis stores/decks.ts -- utilise comme proxy de
// "maitrise" pour la ligne fusionnee d'un deck (pas invente : c'est le seul
// pourcentage expose par decksStore.fetchDeckStats/GET /stats/decks/:id).
interface DeckWithStats {
  deck: Deck
  deckStats: DeckStatsResponse
}

const binderDecksWithStats = ref<DeckWithStats[]>([])

function typeLabel(t: RevisionType | RevisionItemType | null): string {
  return t ? REVISION_ITEM_TYPE_META[t].label : 'Mixte'
}

// Reprend le pattern de Binders.vue (decksStore.fetchDecks() puis filtre par
// binder_id -- pas de nouvel endpoint "decks d'un classeur"). L'appel
// /stats/decks/:id (meme forme que Reviews.vue::fetchDecksStats) passe par
// decksStore.fetchDeckStats -- pas d'appel api direct dans cette vue.
//
// `scopeBinderIds` : classeur courant + sous-arbre SI include_descendants (le
// meme perimetre que celui deja utilise pour les ensembles de revision via
// revisionStore.fetchBinderStats) -- expose par le backend (BinderStats.binder_ids,
// cf. revue de branche finding #3) plutot que re-marche cote frontend, pour ne
// pas melanger un cote "descendants inclus" et un cote "enfants directs
// seulement" quand le classeur a des sous-classeurs.
async function fetchDecksWithStats(
  decks: Deck[],
  scopeBinderIds: string[],
): Promise<DeckWithStats[]> {
  const scopeSet = new Set(scopeBinderIds)
  const scoped = decks.filter((d) => d.binder_id !== null && scopeSet.has(d.binder_id))
  const withStats = await Promise.all(
    scoped.map(async (deck): Promise<DeckWithStats> => {
      try {
        const deckStats = await decksStore.fetchDeckStats(deck.id)
        return { deck, deckStats }
      } catch (e) {
        console.error(`Erreur stats deck ${deck.id}`, e)
        return {
          deck,
          deckStats: {
            deck_id: deck.id,
            retention_rate: 0,
            next_review: null,
            cards_to_review: 0,
            total_cards: deck.card_count,
          },
        }
      }
    }),
  )
  return withStats
}

async function reload() {
  loading.value = true
  error.value = null
  try {
    const [binderStats, decks] = await Promise.all([
      revisionStore.fetchBinderStats(binderId, includeDescendants.value),
      decksStore.fetchDecks(),
    ])
    stats.value = binderStats
    binderDecksWithStats.value = await fetchDecksWithStats(decks, binderStats.binder_ids)
  } catch (e) {
    console.error('Erreur de chargement des stats du classeur', e)
    error.value = 'Impossible de charger les statistiques.'
  } finally {
    loading.value = false
  }
}

function onToggleDescendants(value: boolean) {
  includeDescendants.value = value
  reload()
}

onMounted(reload)

const mergedCount = computed(
  () => binderDecksWithStats.value.length + (stats.value?.sets_count ?? 0),
)

const totalCardsCount = computed(() => {
  const s = stats.value
  if (!s) return 0
  const deckCards = binderDecksWithStats.value.reduce((sum, d) => sum + d.deckStats.total_cards, 0)
  return deckCards + s.items_count
})

const leechesHint = computed(() => {
  const n = stats.value?.leeches_count ?? 0
  return n > 0 ? `${n} sangsue(s) à traiter` : 'Aucune sangsue détectée'
})

const subtitleText = computed(
  () =>
    `${mergedCount.value} deck(s) et série(s) · statistiques agrégées sur l'ensemble du classeur`,
)

interface MergedRevisionRow {
  key: string
  kind: 'deck' | 'set'
  id: number
  name: string
  typeLabel: string
  itemsLabel: string
  dueLabel: string
  masteryRate: number
  hasMastery: boolean
}

// Fusion cote frontend, triee par maitrise decroissante (brique explicite du
// brief -- pas de tri secondaire, les egalites gardent l'ordre deck-puis-set).
const mergedRows = computed<MergedRevisionRow[]>(() => {
  const s = stats.value
  if (!s) return []

  const deckRows: MergedRevisionRow[] = binderDecksWithStats.value.map(({ deck, deckStats }) => ({
    key: `deck:${deck.id}`,
    kind: 'deck',
    id: deck.id,
    name: deck.name,
    typeLabel: 'Deck SM-2',
    itemsLabel: `${deckStats.total_cards} carte(s)`,
    dueLabel: `${deckStats.cards_to_review} à réviser`,
    masteryRate: deckStats.retention_rate,
    hasMastery: true,
  }))

  const setRows: MergedRevisionRow[] = s.sets.map((set) => ({
    key: `set:${set.set_id}`,
    kind: 'set',
    id: set.set_id,
    name: set.name,
    typeLabel: typeLabel(set.type),
    itemsLabel: `${set.items_count} élément(s)`,
    dueLabel: `${set.due_count} à réviser`,
    masteryRate: set.mastery_rate,
    hasMastery: set.reviewed_items > 0,
  }))

  return [...deckRows, ...setRows].sort((a, b) => b.masteryRate - a.masteryRate)
})

function openRow(row: MergedRevisionRow) {
  if (row.kind === 'set') {
    router.push(`/revision/sets/${row.id}/stats`)
  } else {
    router.push(`/decks/${row.id}/study`)
  }
}

function reviseBinder() {
  const name = stats.value?.name || 'Classeur'
  router.push(`/bibliotheque/${binderId}/reviser?name=${encodeURIComponent(name)}`)
}
</script>
