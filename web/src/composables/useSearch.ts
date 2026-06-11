import { ref, watch, onUnmounted } from 'vue'
import searchService from '../services/searchService'
import type { SearchResults } from '../services/searchService'

export function useSearch(types?: string[], limit?: number) {
  const query = ref('')
  const isLoading = ref(false)
  const results = ref<SearchResults>({
    notes: [],
    decks: [],
    flashcards: [],
    diagrams: []
  })
  const total = ref(0)
  const error = ref<string | null>(null)

  let abortController: AbortController | null = null
  let debounceTimeout: ReturnType<typeof setTimeout> | null = null

  const performSearch = async (q: string) => {
    // Abort in-flight request
    if (abortController) {
      abortController.abort()
    }

    const trimmed = q.trim()
    if (trimmed.length < 2) {
      results.value = {
        notes: [],
        decks: [],
        flashcards: [],
        diagrams: []
      }
      total.value = 0
      isLoading.value = false
      error.value = null
      return
    }

    isLoading.value = true
    error.value = null
    abortController = new AbortController()

    try {
      const response = await searchService.search(trimmed, types, limit, abortController.signal)
      results.value = response.results
      total.value = response.total
    } catch (err: any) {
      // Axios error/abort check
      if (err.name === 'CanceledError' || err.name === 'AbortError' || err.message === 'canceled') {
        return
      }
      error.value = err.response?.data?.error?.message || err.message || "Une erreur est survenue lors de la recherche."
      results.value = {
        notes: [],
        decks: [],
        flashcards: [],
        diagrams: []
      }
      total.value = 0
    } finally {
      if (abortController && !abortController.signal.aborted) {
        isLoading.value = false
      }
    }
  }

  watch(query, (newQuery) => {
    if (debounceTimeout) {
      clearTimeout(debounceTimeout)
    }

    const trimmed = newQuery.trim()
    if (trimmed.length < 2) {
      performSearch(newQuery)
      return
    }

    debounceTimeout = setTimeout(() => {
      performSearch(newQuery)
    }, 300)
  })

  onUnmounted(() => {
    if (debounceTimeout) {
      clearTimeout(debounceTimeout)
    }
    if (abortController) {
      abortController.abort()
    }
  })

  return {
    query,
    isLoading,
    results,
    total,
    error,
    search: performSearch
  }
}
