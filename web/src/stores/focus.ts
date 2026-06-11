import { defineStore } from 'pinia'
import { ref } from 'vue'
import focusService from '../services/focusService'
import type { FocusItem, ForecastItem, RetentionSubject } from '../services/focusService'

export const useFocusStore = defineStore('focus', () => {
  const totalDue = ref(0)
  const lateCount = ref(0)
  const flashcardCount = ref(0)
  const blurtingCount = ref(0)
  const items = ref<FocusItem[]>([])
  
  const forecast = ref<ForecastItem[]>([])
  const retention = ref<RetentionSubject[]>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Unified review queue
  const reviewQueue = ref<FocusItem[]>([])
  const currentQueueIndex = ref(-1)

  async function loadFocusData() {
    loading.value = true
    error.value = null
    try {
      const [todayRes, forecastRes, retentionRes] = await Promise.all([
        focusService.getFocusToday(),
        focusService.getFocusForecast(),
        focusService.getFocusRetention()
      ])
      
      totalDue.value = todayRes.total_due
      lateCount.value = todayRes.late_count
      flashcardCount.value = todayRes.flashcard_count
      blurtingCount.value = todayRes.blurting_count
      items.value = todayRes.items
      
      forecast.value = forecastRes.forecast
      retention.value = retentionRes.by_subject
    } catch (err: any) {
      console.error('Erreur lors du chargement des donnees Focus', err)
      error.value = err.message || 'Impossible de charger les donnees Focus.'
    } finally {
      loading.value = false
    }
  }

  function startUnifiedReview(customItems?: FocusItem[]) {
    // If customItems is provided, review only those. Otherwise, review all today items.
    const itemsToReview = customItems || [...items.value]
    
    // Sort queue: late items first
    itemsToReview.sort((a, b) => {
      if (a.is_late && !b.is_late) return -1
      if (!a.is_late && b.is_late) return 1
      return 0
    })

    reviewQueue.value = itemsToReview
    currentQueueIndex.value = itemsToReview.length > 0 ? 0 : -1
    return reviewQueue.value[0] || null
  }

  function getActiveItem() {
    if (currentQueueIndex.value >= 0 && currentQueueIndex.value < reviewQueue.value.length) {
      return reviewQueue.value[currentQueueIndex.value]
    }
    return null
  }

  function nextQueueItem() {
    if (currentQueueIndex.value < reviewQueue.value.length - 1) {
      currentQueueIndex.value++
      return reviewQueue.value[currentQueueIndex.value]
    }
    // Finished review
    currentQueueIndex.value = -1
    reviewQueue.value = []
    return null
  }

  return {
    totalDue,
    lateCount,
    flashcardCount,
    blurtingCount,
    items,
    forecast,
    retention,
    loading,
    error,
    reviewQueue,
    currentQueueIndex,
    loadFocusData,
    startUnifiedReview,
    getActiveItem,
    nextQueueItem
  }
})
