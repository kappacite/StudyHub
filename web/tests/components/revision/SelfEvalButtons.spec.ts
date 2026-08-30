import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SelfEvalButtons from '../../../src/components/revision/SelfEvalButtons.vue'

describe('SelfEvalButtons', () => {
  it('emet select avec le score correspondant pour chacun des 4 paliers SM-2', async () => {
    const wrapper = mount(SelfEvalButtons)
    await wrapper.find('[data-test="self-eval-encore"]').trigger('click')
    await wrapper.find('[data-test="self-eval-difficile"]').trigger('click')
    await wrapper.find('[data-test="self-eval-bien"]').trigger('click')
    await wrapper.find('[data-test="self-eval-facile"]').trigger('click')
    expect(wrapper.emitted('select')).toEqual([[1], [2], [4], [5]])
  })

  it('desactive les 4 boutons quand disabled=true', () => {
    const wrapper = mount(SelfEvalButtons, { props: { disabled: true } })
    wrapper.findAll('button').forEach((b) => {
      expect(b.attributes('disabled')).toBeDefined()
    })
  })

  // Revue finale de branche (defaut Minor #5) : cible tactile >= 44px --
  // jsdom ne mesure pas de layout reel, on verifie donc la presence de la
  // classe Tailwind (token de l'echelle par defaut, pas de valeur arbitraire
  // [...]) qui garantit min-height: 2.75rem (44px) sur chaque bouton.
  it('utilise min-h-11 (44px, token Tailwind standard) sur les 4 boutons', () => {
    const wrapper = mount(SelfEvalButtons)
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(4)
    buttons.forEach((b) => {
      expect(b.classes()).toContain('min-h-11')
      expect(b.classes().some((c) => c.includes('['))).toBe(false)
    })
  })

  // Alignement avec le graphique "PAR NOTATION SM2" de RevisionSetStats.vue
  // (RevisionSetStats.vue: GRADE_BARS "Enc./Diff./Bien/Fac.") -- les 4
  // paliers pedagogiques du backend (GradeDistribution: again/hard/good/easy)
  // sont desormais les 4 options de notation manuelle, pas 3 valeurs
  // arbitraires (1/3/5) sans lien visible avec les stats.
  it('affiche les 4 libelles des paliers du graphique de stats', () => {
    const wrapper = mount(SelfEvalButtons)
    const text = wrapper.text()
    expect(text).toContain('Encore')
    expect(text).toContain('Difficile')
    expect(text).toContain('Bien')
    expect(text).toContain('Facile')
  })
})
