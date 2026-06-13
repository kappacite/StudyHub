import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// L'instance Axios centralisée est mockée : aucun appel réseau réel.
const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))
vi.mock('../../src/services/api', () => ({ default: api }))

import { useNotesStore, type Note } from '../../src/stores/notes'

function makeNote(overrides: Partial<Note> = {}): Note {
  return {
    id: 'note-uuid-1',
    binder_id: null,
    title: 'Titre',
    content: '',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
    tags: [],
    ...overrides,
  }
}

describe('notes store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('createNote poste et ajoute la note retournée (id UUID string)', async () => {
    const note = makeNote({ id: 'a1b2c3d4-uuid', title: 'Nouvelle' })
    api.post.mockResolvedValue({ data: note })

    const store = useNotesStore()
    const result = await store.createNote('Nouvelle')

    expect(api.post).toHaveBeenCalledWith('/notes', {
      title: 'Nouvelle',
      content: '',
      binder_id: null,
    })
    // Garde-fou du refactor UUID : l'id reste une string.
    expect(typeof result.id).toBe('string')
    expect(result.id).toBe('a1b2c3d4-uuid')
    expect(store.notes).toContainEqual(note)
  })

  it('fetchNoteById met à jour une note déjà présente, en place', async () => {
    const existing = makeNote({ id: 'x-uuid', title: 'Ancien' })
    const refreshed = makeNote({ id: 'x-uuid', title: 'Rafraîchi' })
    api.get.mockResolvedValue({ data: refreshed })

    const store = useNotesStore()
    store.notes.push(existing)

    const result = await store.fetchNoteById('x-uuid')

    expect(api.get).toHaveBeenCalledWith('/notes/x-uuid')
    expect(result?.title).toBe('Rafraîchi')
    expect(store.notes).toHaveLength(1)
    expect(store.notes[0].title).toBe('Rafraîchi')
  })

  it('fetchNoteById ajoute la note si absente du cache', async () => {
    const note = makeNote({ id: 'y-uuid' })
    api.get.mockResolvedValue({ data: note })

    const store = useNotesStore()
    const result = await store.fetchNoteById('y-uuid')

    expect(result?.id).toBe('y-uuid')
    expect(store.notes).toHaveLength(1)
  })

  it('updateNote conserve le binder_id existant et met à jour le cache', async () => {
    const existing = makeNote({ id: 'z-uuid', binder_id: 'binder-uuid', title: 'V1' })
    const updated = makeNote({ id: 'z-uuid', binder_id: 'binder-uuid', title: 'V2' })
    api.put.mockResolvedValue({ data: updated })

    const store = useNotesStore()
    store.notes.push(existing)

    await store.updateNote('z-uuid', 'V2', 'contenu')

    expect(api.put).toHaveBeenCalledWith('/notes/z-uuid', {
      title: 'V2',
      content: 'contenu',
      binder_id: 'binder-uuid',
    })
    expect(store.notes[0].title).toBe('V2')
  })

  it('updateNote envoie le NOUVEAU binder_id quand il est fourni (changement de classeur)', async () => {
    const existing = makeNote({ id: 'm-uuid', binder_id: 'ancien-binder' })
    api.put.mockResolvedValue({ data: makeNote({ id: 'm-uuid', binder_id: 'nouveau-binder' }) })
    const store = useNotesStore()
    store.notes.push(existing)

    await store.updateNote('m-uuid', 'T', 'c', 'nouveau-binder')

    // Régression : le classeur fourni doit être envoyé, pas l'ancien du cache.
    expect(api.put).toHaveBeenCalledWith('/notes/m-uuid', {
      title: 'T',
      content: 'c',
      binder_id: 'nouveau-binder',
    })
  })

  it('updateNote envoie binder_id=null (déplacement vers « Général »)', async () => {
    const existing = makeNote({ id: 'n-uuid', binder_id: 'un-binder' })
    api.put.mockResolvedValue({ data: makeNote({ id: 'n-uuid', binder_id: null }) })
    const store = useNotesStore()
    store.notes.push(existing)

    await store.updateNote('n-uuid', 'T', 'c', null)

    expect(api.put).toHaveBeenCalledWith('/notes/n-uuid', {
      title: 'T',
      content: 'c',
      binder_id: null,
    })
  })

  it('deleteNote retire la note du cache par son id', async () => {
    api.delete.mockResolvedValue({})
    const store = useNotesStore()
    store.notes.push(makeNote({ id: 'del-uuid' }), makeNote({ id: 'keep-uuid' }))

    await store.deleteNote('del-uuid')

    expect(api.delete).toHaveBeenCalledWith('/notes/del-uuid')
    expect(store.notes.map(n => n.id)).toEqual(['keep-uuid'])
  })
})
