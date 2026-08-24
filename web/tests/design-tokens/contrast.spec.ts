import { describe, it, expect } from 'vitest'

type RGB = [number, number, number]

function srgbToLinear(c: number): number {
  const cs = c / 255
  return cs <= 0.03928 ? cs / 12.92 : Math.pow((cs + 0.055) / 1.055, 2.4)
}

function relativeLuminance([r, g, b]: RGB): number {
  return 0.2126 * srgbToLinear(r) + 0.7152 * srgbToLinear(g) + 0.0722 * srgbToLinear(b)
}

function contrastRatio(a: RGB, b: RGB): number {
  const l1 = relativeLuminance(a)
  const l2 = relativeLuminance(b)
  const lighter = Math.max(l1, l2)
  const darker = Math.min(l1, l2)
  return (lighter + 0.05) / (darker + 0.05)
}

// Ces triplets dupliquent volontairement les valeurs RGB de web/src/style.css
// (Direction A « Fiche »). Si la palette change, mettre à jour ce fichier en même
// temps (rappelé dans .claude/skills/design-system/SKILL.md).
const light = {
  app: [239, 234, 224] as RGB,
  surface: [251, 248, 242] as RGB,
  ink: [35, 36, 31] as RGB,
  inkMuted: [107, 104, 88] as RGB,
  primary: [46, 67, 116] as RGB,
  primaryInk: [255, 255, 255] as RGB,
  danger: [178, 76, 58] as RGB,
  success: [92, 122, 90] as RGB,
}

const dark = {
  app: [27, 25, 18] as RGB,
  ink: [243, 239, 227] as RGB,
  inkMuted: [184, 178, 156] as RGB,
  primary: [147, 169, 222] as RGB,
  primaryInk: [27, 25, 18] as RGB,
}

const AA_TEXT = 4.5

describe('Contraste AA — Direction A « Fiche »', () => {
  it('texte principal sur fond clair', () => {
    expect(contrastRatio(light.ink, light.app)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte secondaire (muted) sur fond clair', () => {
    expect(contrastRatio(light.inkMuted, light.app)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte sur bouton primaire (fond clair)', () => {
    expect(contrastRatio(light.primaryInk, light.primary)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('bouton destructeur outline sur surface (fond clair)', () => {
    expect(contrastRatio(light.danger, light.surface)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('bouton "Facile" (success) outline sur surface (fond clair)', () => {
    // Paire la plus tendue de la palette (~4.5) — si ce test casse après un
    // ajustement de --sh-success, resserrer la couleur (assombrir de ~10/canal).
    expect(contrastRatio(light.success, light.surface)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte principal sur fond sombre', () => {
    expect(contrastRatio(dark.ink, dark.app)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte secondaire (muted) sur fond sombre', () => {
    expect(contrastRatio(dark.inkMuted, dark.app)).toBeGreaterThanOrEqual(AA_TEXT)
  })

  it('texte sur bouton primaire (fond sombre)', () => {
    expect(contrastRatio(dark.primaryInk, dark.primary)).toBeGreaterThanOrEqual(AA_TEXT)
  })
})
