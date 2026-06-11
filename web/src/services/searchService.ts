import api from './api'

export interface SearchTag {
  id: number
  name: string
  color: string
}

export interface SearchNoteResult {
  id: number
  title: string
  excerpt: string
  binder_id: number | null
  tags: SearchTag[]
  score: number
}

export interface SearchDeckResult {
  id: number
  name: string
  excerpt: string
  binder_id: number | null
  tags: SearchTag[]
  score: number
}

export interface SearchFlashcardResult {
  id: number
  front: string
  deck_id: number
  deck_name: string
  score: number
}

export interface SearchDiagramResult {
  id: number
  title: string
  binder_id: number | null
  score: number
}

export interface SearchResults {
  notes: SearchNoteResult[]
  decks: SearchDeckResult[]
  flashcards: SearchFlashcardResult[]
  diagrams: SearchDiagramResult[]
}

export interface SearchResponse {
  query: string
  results: SearchResults
  total: number
}

const searchService = {
  async search(query: string, types?: string[], limit?: number, signal?: AbortSignal): Promise<SearchResponse> {
    const params: Record<string, string | number> = { q: query }
    if (types && types.length > 0) {
      params.types = types.join(',')
    }
    if (limit) {
      params.limit = limit
    }
    const response = await api.get<SearchResponse>('/search', {
      params,
      signal
    })
    return response.data
  }
}

export default searchService
