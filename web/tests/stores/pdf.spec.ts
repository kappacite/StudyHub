import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../src/services/api', () => ({ default: api }))

import { usePdfStore } from '../../src/stores/pdf'

const PDF = {
  id: 'uuid-1', name: 'Cours.pdf', filename: 'x.pdf', binder_id: null,
  tags: [], read_only: false, created_at: '', updated_at: '',
}

describe('pdf store — upload PDF réel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    // jsdom n'implémente pas les object URLs.
    globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock')
    globalThis.URL.revokeObjectURL = vi.fn()
  })

  it('fetchPdfs charge la liste réelle (per_page=100)', async () => {
    api.get.mockResolvedValue({ data: { data: [PDF] } })
    const store = usePdfStore()
    await store.fetchPdfs()
    expect(api.get).toHaveBeenCalledWith('/pdfs', { params: { per_page: 100 } })
    expect(store.pdfs).toHaveLength(1)
  })

  it('uploadPdf envoie un multipart et préfixe la liste', async () => {
    api.post.mockResolvedValue({ data: PDF })
    const store = usePdfStore()
    const file = new File([new Uint8Array([1, 2, 3])], 'Cours.pdf', { type: 'application/pdf' })
    await store.uploadPdf(file, 'Cours.pdf')
    expect(api.post).toHaveBeenCalledWith('/pdfs', expect.any(FormData), {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    expect(store.pdfs[0].id).toBe('uuid-1')
  })

  it('renamePdf appelle PUT et met à jour la liste', async () => {
    api.post.mockResolvedValue({ data: PDF })
    api.put.mockResolvedValue({ data: { ...PDF, name: 'Renommé' } })
    const store = usePdfStore()
    const file = new File([new Uint8Array([1])], 'Cours.pdf', { type: 'application/pdf' })
    await store.uploadPdf(file)
    await store.renamePdf('uuid-1', 'Renommé')
    expect(api.put).toHaveBeenCalledWith('/pdfs/uuid-1', { name: 'Renommé' })
    expect(store.pdfs[0].name).toBe('Renommé')
  })

  it('openPdf charge le fichier en blob (responseType blob) et crée une URL', async () => {
    api.post.mockResolvedValue({ data: PDF })
    api.get.mockResolvedValue({ data: new Blob([new Uint8Array([1])]) })
    const store = usePdfStore()
    const file = new File([new Uint8Array([1])], 'Cours.pdf', { type: 'application/pdf' })
    await store.uploadPdf(file)
    await store.openPdf('uuid-1')
    expect(api.get).toHaveBeenCalledWith('/pdfs/uuid-1/file', { responseType: 'blob' })
    expect(store.activePdfUrl).toBe('blob:mock')
    expect(store.activePdf?.id).toBe('uuid-1')
  })

  it('removePdf appelle DELETE et retire de la liste', async () => {
    api.post.mockResolvedValue({ data: PDF })
    api.delete.mockResolvedValue({})
    const store = usePdfStore()
    const file = new File([new Uint8Array([1])], 'Cours.pdf', { type: 'application/pdf' })
    await store.uploadPdf(file)
    await store.removePdf('uuid-1')
    expect(api.delete).toHaveBeenCalledWith('/pdfs/uuid-1')
    expect(store.pdfs).toHaveLength(0)
  })
})
