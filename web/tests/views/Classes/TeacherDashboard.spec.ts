import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia, type Pinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('../../../src/services/api', () => ({ default: api }))

const classService = vi.hoisted(() => ({
  getMyClasses: vi.fn(),
  listAssignments: vi.fn(),
  getClassDetails: vi.fn(),
  listRoster: vi.fn(),
  getAnalytics: vi.fn(),
  getLeaderboard: vi.fn(),
  listQuestions: vi.fn(),
}))
vi.mock('../../../src/services/classService', () => ({ default: classService }))

const groupService = vi.hoisted(() => ({
  getGroupBinders: vi.fn(),
  getGroupProgress: vi.fn(),
}))
vi.mock('../../../src/services/groupService', () => ({ default: groupService }))

import TeacherDashboard from '../../../src/views/Classes/TeacherDashboard.vue'
import AssignmentBuilder from '../../../src/components/classes/AssignmentBuilder.vue'
import { useRevisionStore } from '../../../src/stores/revision'

const HETEROGENEOUS_SET = { id: 7, name: 'Mixte', description: null, type: null, binder_id: null, tuning_default: 1, is_public: false, item_count: 2 }
const TYPED_SET = { id: 8, name: 'QCM Histoire', description: null, type: 'qcm', binder_id: null, tuning_default: 1, is_public: false, item_count: 4 }

const stub = { template: '<div />' }

function createTestRouter(): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/classes', name: 'Classes', component: stub },
      { path: '/decks/:id/study', name: 'StudyDeck', component: stub },
    ],
  })
}

async function mountDashboard() {
  const pinia: Pinia = createPinia()
  setActivePinia(pinia)
  api.get.mockImplementation((url: string) => {
    if (/^\/revision\/sets\?/.test(url)) return Promise.resolve({ data: { data: [HETEROGENEOUS_SET, TYPED_SET] } })
    return Promise.resolve({ data: { data: [] } })
  })
  classService.getMyClasses.mockResolvedValue([{ id: 1, name: 'Ma classe', description: null, invite_code: 'ABC', type: 'class', is_class: true, is_public: false, created_by: 1, members_count: 3, created_at: '', my_role: 'owner' }])
  classService.listAssignments.mockResolvedValue([])
  classService.getClassDetails.mockResolvedValue(null)
  classService.listRoster.mockResolvedValue([])
  classService.getAnalytics.mockResolvedValue(null)
  classService.getLeaderboard.mockResolvedValue([])
  classService.listQuestions.mockResolvedValue([])
  groupService.getGroupBinders.mockResolvedValue([])
  groupService.getGroupProgress.mockResolvedValue([])

  const router = createTestRouter()
  router.push('/classes')
  await router.isReady()

  // AssignmentBuilder (comme les modales du tableau de bord) rend son contenu dans un
  // <Teleport to="body"> : sans ce stub, rien de ce qu'il affiche n'est visible depuis
  // wrapper.text() et l'assertion sur le rendu reel serait vide de sens.
  const wrapper = mount(TeacherDashboard, {
    global: { plugins: [pinia, router], stubs: { teleport: true } },
  })
  await flushPromises()
  return wrapper
}

describe('TeacherDashboard — selecteur d\'ensemble dans le createur de devoir', () => {
  beforeEach(() => vi.clearAllMocks())

  it('ne plante pas sur un ensemble heterogene et rend un libelle de repli dans le selecteur', async () => {
    const wrapper = await mountDashboard()
    const revisionStore = useRevisionStore()
    expect(revisionStore.sets).toHaveLength(2) // confirme que le seed a bien pris

    await wrapper.find('[data-test="open-create-assignment"]').trigger('click')
    await flushPromises()

    // Le selecteur d'ensembles n'est peuple que si la tache cible un ensemble de
    // revision : on bascule le type de la premiere tache sur « revision ».
    const builder = wrapper.findComponent(AssignmentBuilder)
    expect(builder.exists()).toBe(true)
    await builder.findAll('select')[0].setValue('revision')
    await flushPromises()

    // Assertion sur le DOM reellement rendu (et non sur le computed) : c'est le rendu
    // du selecteur qui plantait sur un ensemble heterogene (type: null).
    expect(wrapper.text()).toContain('Mixte (MIXTE)')
    expect(wrapper.text()).toContain('QCM Histoire (QCM)')
  })
})
