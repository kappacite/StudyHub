import { describe, it, expect, afterEach } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'

import NoteSidebar from '../../../src/components/notes/NoteSidebar.vue'
import type { Tag } from '../../../src/stores/tags'

const TAGS: Tag[] = [
  { id: 1, name: 'Chimie', color: '#4F46E5', created_at: '2026-01-01T00:00:00Z' },
  { id: 2, name: 'Organique', color: null, created_at: '2026-01-01T00:00:00Z' },
]

describe('NoteSidebar', () => {
  let wrapper: VueWrapper | undefined

  afterEach(() => {
    wrapper?.unmount()
    wrapper = undefined
  })

  function mountSidebar(overrides: Partial<{ binderName: string; tags: Tag[]; updatedAt: string }> = {}) {
    return mount(NoteSidebar, {
      props: {
        binderName: 'Chimie organique',
        tags: TAGS,
        updatedAt: '2026-08-30T10:00:00Z',
        ...overrides,
      },
    })
  }

  it("affiche exactement les 3 méthodes d'entraînement du canevas, dans l'ordre, sans le quiz", () => {
    wrapper = mountSidebar()

    const buttons = wrapper.findAll('button').map((b) => b.text())
    expect(buttons).toEqual([
      'Évaluation mixte',
      'Méthode de la feuille blanche',
      'Méthode Feynman',
    ])
    expect(wrapper.text()).not.toContain('Générer un quiz')
    expect(wrapper.text()).not.toContain('QCM')
  })

  it('affiche le sous-titre de la carte Assistant IA', () => {
    wrapper = mountSidebar()

    expect(wrapper.text()).toContain('S\'entraîner sur cette note, à partir de son contenu.')
  })

  it("émet start-activity avec le type 'evaluation' au clic sur Évaluation mixte", async () => {
    wrapper = mountSidebar()

    await wrapper.findAll('button')[0].trigger('click')

    expect(wrapper.emitted('start-activity')).toEqual([['evaluation']])
  })

  it("émet start-activity avec le type 'blurting' au clic sur Méthode de la feuille blanche", async () => {
    wrapper = mountSidebar()

    await wrapper.findAll('button')[1].trigger('click')

    expect(wrapper.emitted('start-activity')).toEqual([['blurting']])
  })

  it("émet start-activity avec le type 'feynman' au clic sur Méthode Feynman", async () => {
    wrapper = mountSidebar()

    await wrapper.findAll('button')[2].trigger('click')

    expect(wrapper.emitted('start-activity')).toEqual([['feynman']])
  })

  it('affiche le classeur, les tags (via TagBadge) et la date de modification formatée', () => {
    wrapper = mountSidebar()

    expect(wrapper.text()).toContain('Chimie organique')
    expect(wrapper.text()).toContain('Chimie')
    expect(wrapper.text()).toContain('Organique')
    expect(wrapper.text()).toContain('30 août 2026')
  })

  it("affiche un repli quand la date de modification est absente/invalide", () => {
    wrapper = mountSidebar({ updatedAt: '' })

    expect(wrapper.text()).toContain('—')
  })
})
