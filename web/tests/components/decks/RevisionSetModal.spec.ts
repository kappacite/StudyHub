import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

const api = vi.hoisted(() => ({ post: vi.fn(), put: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import RevisionSetModal from '../../../src/components/decks/RevisionSetModal.vue'
import type { RevisionSet } from '../../../src/stores/revision'

const EXISTING: RevisionSet = {
  id: 7, name: 'Mécanismes SN1 / SN2', description: 'Flashcards, QCM et vrai/faux.',
  type: null, binder_id: 'b1', tuning_default: 1, is_public: false, item_count: 3,
}

describe('RevisionSetModal', () => {
  let wrapper: VueWrapper | undefined

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  it('mode creation : champs vides, cree un ensemble heterogene (type: null)', async () => {
    api.post.mockResolvedValue({ data: { ...EXISTING, id: 9, name: 'Nouveau', description: null } })
    wrapper = mount(RevisionSetModal, { props: { mode: 'create', binderId: 'b1' }, attachTo: document.body })
    await wrapper.vm.$nextTick()

    const input = document.body.querySelector('input[type="text"]') as HTMLInputElement
    expect(input?.value).toBe('')
    input!.value = 'Nouveau'
    input!.dispatchEvent(new Event('input', { bubbles: true }))
    const form = document.body.querySelector('form') as HTMLFormElement
    form!.dispatchEvent(new Event('submit', { bubbles: true }))
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/revision/sets', {
      name: 'Nouveau', type: null, description: null, binder_id: 'b1', tuning_default: 1.0,
    })
    expect(wrapper.emitted('created')?.[0]).toEqual([{ ...EXISTING, id: 9, name: 'Nouveau', description: null }])
  })

  it('mode edition : champs prerempli, appelle updateSet', async () => {
    api.put.mockResolvedValue({ data: { ...EXISTING, name: 'Renommé' } })
    wrapper = mount(RevisionSetModal, { props: { mode: 'edit', binderId: 'b1', set: EXISTING }, attachTo: document.body })
    await wrapper.vm.$nextTick()

    const input = document.body.querySelector('input[type="text"]') as HTMLInputElement
    const textarea = document.body.querySelector('textarea') as HTMLTextAreaElement
    expect(input?.value).toBe('Mécanismes SN1 / SN2')
    expect(textarea?.value).toBe('Flashcards, QCM et vrai/faux.')
    input!.value = 'Renommé'
    input!.dispatchEvent(new Event('input', { bubbles: true }))
    const form = document.body.querySelector('form') as HTMLFormElement
    form!.dispatchEvent(new Event('submit', { bubbles: true }))
    await flushPromises()

    expect(api.put).toHaveBeenCalledWith('/revision/sets/7', { name: 'Renommé', description: 'Flashcards, QCM et vrai/faux.' })
    expect(wrapper.emitted('updated')).toBeTruthy()
  })

  it('emet close au clic sur Annuler', async () => {
    wrapper = mount(RevisionSetModal, { props: { mode: 'create', binderId: null }, attachTo: document.body })
    await wrapper.vm.$nextTick()
    const buttons = Array.from(document.body.querySelectorAll('button'))
    const cancelButton = buttons.find((b) => b.textContent === 'Annuler')
    cancelButton?.click()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
