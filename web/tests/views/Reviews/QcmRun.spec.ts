import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

import QcmRun from '../../../src/views/Reviews/QcmRun.vue'

const SET = {
  id: 7,
  name: 'QCM Histoire',
  description: null,
  type: 'qcm',
  binder_id: null,
  tuning_default: 1,
  is_public: false,
  item_count: 1,
}

function question(id: number, overrides: Record<string, unknown> = {}) {
  return {
    id,
    set_id: 7,
    type: 'qcm',
    payload: {
      question: 'Capitale de la France ?',
      options: [
        { id: 'a', text: 'Lyon', correct: false },
        { id: 'b', text: 'Paris', correct: true },
      ],
    },
    tuning: 1,
    position: 0,
    interval: 0,
    ease_factor: 2.5,
    repetitions: 0,
    next_review: '',
    created_at: '',
    updated_at: '',
    ...overrides,
  }
}

const stub = { template: '<div />' }
function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/revision/sets/:id/run', name: 'QcmRun', component: stub }],
  })
}

async function mountQcmRun(items: unknown[]) {
  const pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/\/revision\/sets\/\d+$/.test(url)) return Promise.resolve({ data: SET })
    if (/\/revision\/sets\/\d+\/study$/.test(url)) return Promise.resolve({ data: items })
    return Promise.reject(new Error(`non mocké: ${url}`))
  })
  const router = createTestRouter()
  await router.push('/revision/sets/7/run')
  await router.isReady()
  const wrapper = mount(QcmRun, { global: { plugins: [pinia, router] } })
  await flushPromises()
  return wrapper
}

describe('QcmRun — duree de revision reelle (Task 9)', () => {
  beforeEach(() => vi.clearAllMocks())

  it('inclut la duree reelle ecoulee (Date.now) dans le payload de /run', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-01-01T00:00:00.000Z'))
    try {
      api.post.mockResolvedValue({
        data: { score: 1, max_score: 1, percentage: 100, results: [] },
      })
      const wrapper = await mountQcmRun([question(1)])

      // Le chrono demarre a onMounted -- on avance le temps de 12s avant de
      // repondre et valider.
      vi.setSystemTime(new Date('2026-01-01T00:00:12.000Z'))
      const checkboxes = wrapper.findAll('input[type="checkbox"]')
      await checkboxes[1].setValue(true) // option "b", correcte
      const submitButton = wrapper.findAll('button').find((b) => b.text().includes('Valider'))
      await submitButton?.trigger('click')
      await flushPromises()

      expect(api.post).toHaveBeenCalledWith('/revision/sets/7/run', {
        answers: [{ item_id: 1, selected_option_ids: ['b'] }],
        duration_seconds: 12,
      })
    } finally {
      vi.useRealTimers()
    }
  })
})
