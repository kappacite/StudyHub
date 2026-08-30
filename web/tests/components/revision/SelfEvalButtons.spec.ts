import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SelfEvalButtons from '../../../src/components/revision/SelfEvalButtons.vue'

describe('SelfEvalButtons', () => {
  it('emet select avec le score correspondant pour chaque bouton', async () => {
    const wrapper = mount(SelfEvalButtons)
    await wrapper.find('[data-test="self-eval-a-revoir"]').trigger('click')
    await wrapper.find('[data-test="self-eval-moyen"]').trigger('click')
    await wrapper.find('[data-test="self-eval-acquis"]').trigger('click')
    expect(wrapper.emitted('select')).toEqual([[1], [3], [5]])
  })

  it('desactive les 3 boutons quand disabled=true', () => {
    const wrapper = mount(SelfEvalButtons, { props: { disabled: true } })
    wrapper.findAll('button').forEach((b) => {
      expect(b.attributes('disabled')).toBeDefined()
    })
  })

  // Revue finale de branche (defaut Minor #5) : cible tactile >= 44px --
  // jsdom ne mesure pas de layout reel, on verifie donc la presence de la
  // classe Tailwind (token de l'echelle par defaut, pas de valeur arbitraire
  // [...]) qui garantit min-height: 2.75rem (44px) sur chaque bouton.
  it('utilise min-h-11 (44px, token Tailwind standard) sur les 3 boutons', () => {
    const wrapper = mount(SelfEvalButtons)
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(3)
    buttons.forEach((b) => {
      expect(b.classes()).toContain('min-h-11')
      expect(b.classes().some((c) => c.includes('['))).toBe(false)
    })
  })
})
