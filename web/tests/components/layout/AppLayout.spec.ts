import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createPinia, setActivePinia, type Pinia } from 'pinia'
import { createRouter, createMemoryHistory, type Router } from 'vue-router'

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn().mockResolvedValue({}),
  patch: vi.fn(),
}))
vi.mock('../../../src/services/api', () => ({ default: api }))

import { BookOpen, Users } from '@lucide/vue'
import AppLayout from '../../../src/components/layout/AppLayout.vue'
import SearchModal from '../../../src/components/ui/SearchModal.vue'
import PomodoroTimer from '../../../src/components/ui/PomodoroTimer.vue'
import NotificationBell from '../../../src/components/ui/NotificationBell.vue'
import BaseToggle from '../../../src/components/ui/base/BaseToggle.vue'
import { useAuthStore, type User } from '../../../src/stores/auth'

const stub = { template: '<div><router-view /></div>' }

function createTestRouter(initialPath: string): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'Home', component: stub },
      { path: '/login', name: 'Login', component: stub },
      { path: '/accueil', name: 'Accueil', component: stub },
      { path: '/bibliotheque/:id?', name: 'Bibliotheque', component: stub },
      { path: '/reviser', name: 'Reviser', component: stub },
      { path: '/planning', name: 'Planning', component: stub },
      { path: '/classes', name: 'Classes', component: stub },
      { path: '/explore', name: 'Explore', component: stub },
      { path: '/notes/:id', name: 'NoteEdit', component: stub },
      { path: '/decks/:id/study', name: 'StudyDeck', component: stub },
      { path: '/exam/:id', name: 'ExamSession', component: stub, meta: { immersive: true } },
    ],
  })
}

const longUser: User = {
  id: 1,
  email: 'utilisateur-avec-une-adresse-tres-longue-pour-tester-la-troncature@universite-exemple.fr',
  username: 'un-nom-utilisateur-vraiment-tres-long-pour-tester-la-troncature',
  created_at: '2026-01-01T00:00:00Z',
}

const shortUser: User = {
  id: 2,
  email: 'alice@studyhub.fr',
  username: 'alice',
  created_at: '2026-01-01T00:00:00Z',
}

async function mountLayout(
  opts: { path?: string; authenticated?: boolean; user?: User; online?: boolean } = {},
) {
  const { path = '/accueil', authenticated = false, user = shortUser, online = true } = opts

  Object.defineProperty(window.navigator, 'onLine', {
    configurable: true,
    value: online,
  })

  const pinia: Pinia = createPinia()
  setActivePinia(pinia)
  const authStore = useAuthStore()
  if (authenticated) {
    authStore.token = 'tok'
    authStore.refreshToken = 'refresh'
    authStore.user = user
  }

  const router = createTestRouter(path)
  router.push(path)
  await router.isReady()

  const wrapper = mount(AppLayout, {
    global: {
      plugins: [pinia, router],
      stubs: {
        NotificationBell: true,
        SearchModal: true,
        PomodoroTimer: true,
      },
    },
  })
  await flushPromises()

  return { wrapper, authStore, router }
}

describe('AppLayout', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'matchMedia',
      vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    )
    localStorage.clear()
    document.documentElement.classList.remove('dark')
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  // ── Logo / marque ──────────────────────────────────────────────────
  it('affiche le logo StudyHub et un lien vers l\'accueil dans le tiroir', async () => {
    const { wrapper } = await mountLayout()
    const logo = wrapper.get('aside a[href="/"]')
    expect(logo.text()).toContain('StudyHub')
  })

  it('affiche le logo StudyHub dans l\'en-tête desktop', async () => {
    const { wrapper } = await mountLayout()
    const logo = wrapper.get('[data-test="header-logo-link"]')
    expect(logo.text()).toContain('StudyHub')
    expect(logo.attributes('href')).toBe('/')
  })

  // ── Nav desktop : 5 pastilles + Communauté en icône séparée ────────
  it('affiche les 5 destinations principales en pastilles dans la nav desktop', async () => {
    const { wrapper } = await mountLayout()
    const nav = wrapper.get('[data-test="desktop-nav"]')
    const links = nav.findAll('a')
    const labels = links.map((l) => l.text())
    expect(labels).toEqual(['Accueil', 'Bibliothèque', 'Réviser', 'Planning', 'Classes'])
  })

  it("ne place pas Communauté parmi les pastilles desktop, mais en icône séparée", async () => {
    const { wrapper } = await mountLayout()
    const nav = wrapper.get('[data-test="desktop-nav"]')
    expect(nav.text()).not.toContain('Communauté')
    const communaute = wrapper.get('[data-test="header-communaute-link"]')
    expect(communaute.attributes('href')).toBe('/explore')
  })

  it('marque la pastille active par préfixe de route', async () => {
    const { wrapper } = await mountLayout({ path: '/bibliotheque/42' })
    const nav = wrapper.get('[data-test="desktop-nav"]')
    const active = nav.findAll('a').find((a) => a.text() === 'Bibliothèque')!
    expect(active.classes()).toContain('bg-primary')
    const inactive = nav.findAll('a').find((a) => a.text() === 'Accueil')!
    expect(inactive.classes()).not.toContain('bg-primary')
  })

  // ── Nav mobile : barre basse à 4 onglets + icônes mini-en-tête ─────
  it('affiche exactement 4 onglets dans la barre de navigation mobile', async () => {
    const { wrapper } = await mountLayout()
    const bar = wrapper.get('[data-test="mobile-bottom-nav"]')
    const labels = bar.findAll('a').map((a) => a.text())
    expect(labels).toEqual(['Accueil', 'Bibliothèque', 'Réviser', 'Classes'])
  })

  it("n'expose plus Planning en icône dans le mini-en-tête mobile (accessible via le tiroir)", async () => {
    const { wrapper } = await mountLayout()
    expect(wrapper.find('[data-test="header-planning-link"]').exists()).toBe(false)
  })

  it('expose Communauté en icône desktop uniquement (accessible via le tiroir en mobile)', async () => {
    const { wrapper } = await mountLayout()
    const communaute = wrapper.get('[data-test="header-communaute-link"]')
    expect(communaute.classes()).toContain('hidden')
    expect(communaute.classes()).toContain('lg:flex')
  })

  // ── Icônes de nav conformes à la maquette AppShell.dc.html ─────────
  it('utilise l\'icône livre ouvert (BookOpen) pour Bibliothèque, pas un dossier', async () => {
    const { wrapper } = await mountLayout()
    const nav = wrapper.get('[data-test="desktop-nav"]')
    const link = nav.findAll('a').find((a) => a.text() === 'Bibliothèque')!
    expect(link.findComponent(BookOpen).exists()).toBe(true)
  })

  it("utilise l'icône deux-personnes (Users) pour Classes, pas un chapeau de diplômé", async () => {
    const { wrapper } = await mountLayout()
    const nav = wrapper.get('[data-test="desktop-nav"]')
    const link = nav.findAll('a').find((a) => a.text() === 'Classes')!
    expect(link.findComponent(Users).exists()).toBe(true)
  })

  it('reprend les mêmes icônes BookOpen/Users dans la barre de navigation mobile', async () => {
    const { wrapper } = await mountLayout()
    const bar = wrapper.get('[data-test="mobile-bottom-nav"]')
    const biblio = bar.findAll('a').find((a) => a.text() === 'Bibliothèque')!
    const classes = bar.findAll('a').find((a) => a.text() === 'Classes')!
    expect(biblio.findComponent(BookOpen).exists()).toBe(true)
    expect(classes.findComponent(Users).exists()).toBe(true)
  })

  // ── Titre de route courant (mobile) ─────────────────────────────────
  it('affiche le titre de la route courante', async () => {
    const { wrapper } = await mountLayout({ path: '/reviser' })
    expect(wrapper.get('[data-test="mobile-route-title"]').text()).toBe('Espace Révisions')
  })

  // ── Date du jour ──────────────────────────────────────────────────────
  // Fix round 1 (item 1) : repoussée de sm à xl pour désserrer l'en-tête entre
  // 1024-1279px — c'était le poste le moins essentiel du cluster d'actions.
  it('affiche la date du jour, masquée avant xl', async () => {
    const { wrapper } = await mountLayout()
    const dateEl = wrapper.get('[data-test="current-date"]')
    expect(dateEl.text().length).toBeGreaterThan(0)
    expect(dateEl.classes()).toContain('hidden')
    expect(dateEl.classes()).toContain('xl:flex')
  })

  // ── Recherche globale ────────────────────────────────────────────────
  it('ouvre la recherche globale au clic sur le bouton de recherche', async () => {
    const { wrapper } = await mountLayout()
    expect(wrapper.findComponent(SearchModal).props('isOpen')).toBe(false)
    await wrapper.get('[data-test="global-search-button"]').trigger('click')
    expect(wrapper.findComponent(SearchModal).props('isOpen')).toBe(true)
  })

  it('bascule la recherche globale avec Ctrl+K', async () => {
    const { wrapper } = await mountLayout()
    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true }))
    await nextTick()
    expect(wrapper.findComponent(SearchModal).props('isOpen')).toBe(true)

    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true }))
    await nextTick()
    expect(wrapper.findComponent(SearchModal).props('isOpen')).toBe(false)
  })

  it('ferme la recherche globale quand SearchModal émet "close"', async () => {
    const { wrapper } = await mountLayout()
    await wrapper.get('[data-test="global-search-button"]').trigger('click')
    expect(wrapper.findComponent(SearchModal).props('isOpen')).toBe(true)

    await wrapper.findComponent(SearchModal).vm.$emit('close')
    await nextTick()
    expect(wrapper.findComponent(SearchModal).props('isOpen')).toBe(false)
  })

  // ── Widgets globaux ──────────────────────────────────────────────────
  it('rend PomodoroTimer hors mode immersif', async () => {
    const { wrapper } = await mountLayout()
    expect(wrapper.findComponent(PomodoroTimer).exists()).toBe(true)
  })

  it('masque PomodoroTimer mais garde SearchModal en mode immersif', async () => {
    const { wrapper } = await mountLayout({ path: '/exam/1' })
    expect(wrapper.findComponent(PomodoroTimer).exists()).toBe(false)
    expect(wrapper.findComponent(SearchModal).exists()).toBe(true)
  })

  it('masque PomodoroTimer pendant une session de révision (chevauchement mesuré avec le bouton de notation « Facile » à 375px)', async () => {
    const { wrapper } = await mountLayout({ path: '/decks/1/study' })
    expect(wrapper.findComponent(PomodoroTimer).exists()).toBe(false)
  })

  // ── Mode immersif : coquille masquée ────────────────────────────────
  it('masque en-tête, tiroir et barre mobile en mode immersif', async () => {
    const { wrapper } = await mountLayout({ path: '/exam/1' })
    expect(wrapper.find('aside').exists()).toBe(false)
    expect(wrapper.find('header').exists()).toBe(false)
    expect(wrapper.find('[data-test="mobile-bottom-nav"]').exists()).toBe(false)
  })

  // ── Tiroir mobile (drawer) ───────────────────────────────────────────
  it('ouvre le tiroir mobile au clic sur le bouton hamburger', async () => {
    const { wrapper } = await mountLayout()
    const aside = wrapper.get('aside')
    expect(aside.classes()).toContain('-translate-x-full')

    await wrapper.get('[data-test="hamburger-button"]').trigger('click')
    expect(aside.classes()).toContain('translate-x-0')
    expect(wrapper.find('[data-test="mobile-menu-backdrop"]').exists()).toBe(true)
  })

  it('ferme le tiroir mobile au clic sur le fond (backdrop-click-to-close)', async () => {
    const { wrapper } = await mountLayout()
    await wrapper.get('[data-test="hamburger-button"]').trigger('click')
    await wrapper.get('[data-test="mobile-menu-backdrop"]').trigger('click')
    expect(wrapper.get('aside').classes()).toContain('-translate-x-full')
  })

  it('ferme le tiroir mobile au clic sur un lien de nav ou le logo', async () => {
    const { wrapper } = await mountLayout()
    await wrapper.get('[data-test="hamburger-button"]').trigger('click')
    expect(wrapper.get('aside').classes()).toContain('translate-x-0')

    await wrapper.get('aside a[href="/"]').trigger('click')
    expect(wrapper.get('aside').classes()).toContain('-translate-x-full')
  })

  // ── Mode Zen (édition de note) ───────────────────────────────────────
  it('bascule la sidebar en overlay et masque le header par défaut en mode Zen', async () => {
    const { wrapper } = await mountLayout({ path: '/notes/5' })
    const aside = wrapper.get('aside')
    expect(aside.classes()).toContain('lg:fixed')
    expect(aside.classes()).not.toContain('lg:hidden')
    expect(aside.classes()).toContain('lg:-translate-x-full')

    const header = wrapper.get('header')
    expect(header.classes()).toContain('-translate-y-full')
  })

  it('révèle le header en mode Zen au survol de la bande invisible', async () => {
    const { wrapper } = await mountLayout({ path: '/notes/5' })
    await wrapper.get('[data-test="header-hover-trigger"]').trigger('mouseenter')
    expect(wrapper.get('header').classes()).not.toContain('-translate-y-full')
  })

  it("masque la nav desktop hors mode Zen (remplacée par la nav du header)", async () => {
    const { wrapper } = await mountLayout({ path: '/accueil' })
    expect(wrapper.get('aside').classes()).toContain('lg:hidden')
  })

  it("l'événement studyhub:toggle-sidebar bascule la sidebar Zen en mode Zen", async () => {
    const { wrapper } = await mountLayout({ path: '/notes/5' })
    const aside = wrapper.get('aside')
    expect(aside.classes()).toContain('lg:-translate-x-full')

    window.dispatchEvent(new CustomEvent('studyhub:toggle-sidebar'))
    await nextTick()
    expect(aside.classes()).toContain('lg:translate-x-0')
  })

  it("l'événement studyhub:toggle-sidebar bascule le tiroir mobile hors mode Zen", async () => {
    const { wrapper } = await mountLayout({ path: '/accueil' })
    const aside = wrapper.get('aside')
    expect(aside.classes()).toContain('-translate-x-full')

    window.dispatchEvent(new CustomEvent('studyhub:toggle-sidebar'))
    await nextTick()
    expect(aside.classes()).toContain('translate-x-0')
  })

  it('ferme la sidebar Zen au clic sur le fond dédié', async () => {
    const { wrapper } = await mountLayout({ path: '/notes/5' })
    window.dispatchEvent(new CustomEvent('studyhub:toggle-sidebar'))
    await nextTick()
    expect(wrapper.get('aside').classes()).toContain('lg:translate-x-0')

    await wrapper.get('[data-test="zen-sidebar-backdrop"]').trigger('click')
    expect(wrapper.get('aside').classes()).toContain('lg:-translate-x-full')
  })

  // ── Thème sombre/clair ───────────────────────────────────────────────
  it('résout le thème initial depuis localStorage', async () => {
    localStorage.setItem('sh_theme', 'dark')
    await mountLayout()
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it("résout le thème initial depuis prefers-color-scheme si rien n'est sauvegardé", async () => {
    vi.stubGlobal(
      'matchMedia',
      vi.fn().mockImplementation((query: string) => ({
        matches: true,
        media: query,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    )
    await mountLayout()
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('bascule et persiste le thème au clic sur le toggle du tiroir', async () => {
    const { wrapper } = await mountLayout()
    const toggle = wrapper.findComponent(BaseToggle)
    await toggle.vm.$emit('update:modelValue', true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('sh_theme')).toBe('dark')
  })

  it("bascule le thème au clic sur l'icône de thème de l'en-tête", async () => {
    const { wrapper } = await mountLayout()
    await wrapper.get('[data-test="header-theme-toggle"]').trigger('click')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('sh_theme')).toBe('dark')
  })

  // ── États d'authentification ─────────────────────────────────────────
  describe('état vide (non authentifié)', () => {
    it('affiche le CTA "Se connecter" au lieu du bloc profil dans le tiroir', async () => {
      const { wrapper } = await mountLayout({ authenticated: false })
      const aside = wrapper.get('aside')
      expect(aside.text()).toContain('Se connecter')
      expect(aside.text()).not.toContain('alice')
    })

    it('affiche le CTA "Se connecter" dans l\'en-tête desktop', async () => {
      const { wrapper } = await mountLayout({ authenticated: false })
      expect(wrapper.get('[data-test="header-account-cta"]').text()).toContain('Se connecter')
    })

    it("n'affiche pas NotificationBell", async () => {
      const { wrapper } = await mountLayout({ authenticated: false })
      expect(wrapper.findComponent(NotificationBell).exists()).toBe(false)
    })

    it('navigue vers /login au clic sur "Se connecter"', async () => {
      const { wrapper, router } = await mountLayout({ authenticated: false })
      await wrapper.get('[data-test="header-account-cta"]').trigger('click')
      await flushPromises()
      expect(router.currentRoute.value.path).toBe('/login')
    })
  })

  describe('authentifié', () => {
    it('affiche le bloc profil (initiales, nom, email) et NotificationBell', async () => {
      const { wrapper } = await mountLayout({ authenticated: true, user: shortUser })
      expect(wrapper.get('aside').text()).toContain('alice')
      expect(wrapper.get('aside').text()).toContain('alice@studyhub.fr')
      expect(wrapper.findComponent(NotificationBell).exists()).toBe(true)
    })
  })

  describe('état erreur (déconnexion malgré échec API)', () => {
    it('redirige vers /login même si authStore.logout() échoue côté API', async () => {
      api.post.mockRejectedValueOnce(new Error('network down'))
      const { wrapper, router, authStore } = await mountLayout({ authenticated: true })

      await wrapper.get('[data-test="header-logout-button"]').trigger('click')
      await flushPromises()

      expect(router.currentRoute.value.path).toBe('/login')
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('état dense (identifiants longs)', () => {
    it("tronque visuellement le nom d'utilisateur et l'email sans perdre l'information", async () => {
      const { wrapper } = await mountLayout({ authenticated: true, user: longUser })
      const aside = wrapper.get('aside')
      const usernameEl = aside.findAll('p').find((p) => p.text() === longUser.username)!
      const emailEl = aside.findAll('p').find((p) => p.text() === longUser.email)!
      expect(usernameEl.classes()).toContain('truncate')
      expect(emailEl.classes()).toContain('truncate')
    })

    it("garde le cluster d'actions de l'en-tête non compressible (flex-shrink-0)", async () => {
      const { wrapper } = await mountLayout({ authenticated: true, user: longUser })
      expect(wrapper.get('[data-test="header-actions-cluster"]').classes()).toContain('flex-shrink-0')
    })
  })

  // ── État hors ligne ───────────────────────────────────────────────────
  describe('état hors ligne', () => {
    it("affiche l'indicateur hors ligne quand navigator.onLine est déjà false au montage", async () => {
      const { wrapper } = await mountLayout({ online: false })
      expect(wrapper.find('[data-test="offline-indicator"]').exists()).toBe(true)
      expect(wrapper.get('[data-test="offline-indicator"]').text()).toContain('Hors ligne')
    })

    it("n'affiche pas l'indicateur hors ligne quand la connexion est disponible", async () => {
      const { wrapper } = await mountLayout({ online: true })
      expect(wrapper.find('[data-test="offline-indicator"]').exists()).toBe(false)
    })

    it("affiche l'indicateur à l'événement 'offline' et le masque à l'événement 'online'", async () => {
      const { wrapper } = await mountLayout({ online: true })
      expect(wrapper.find('[data-test="offline-indicator"]').exists()).toBe(false)

      window.dispatchEvent(new Event('offline'))
      await nextTick()
      expect(wrapper.find('[data-test="offline-indicator"]').exists()).toBe(true)

      window.dispatchEvent(new Event('online'))
      await nextTick()
      expect(wrapper.find('[data-test="offline-indicator"]').exists()).toBe(false)
    })
  })

  // ── Fix round 1 (revue post-migration) ──────────────────────────────
  describe('fix round 1 : pression horizontale de l\'en-tête (item 1)', () => {
    it("replie le libellé et le raccourci de recherche à xl (pas lg) pour desserrer l'en-tête", async () => {
      const { wrapper } = await mountLayout()
      const button = wrapper.get('[data-test="global-search-button"]')
      const label = button.findAll('span').find((s) => s.text().includes('Rechercher'))!
      expect(label.classes()).toContain('xl:inline')
      expect(label.classes()).not.toContain('md:inline')
      const kbd = button.get('kbd')
      expect(kbd.classes()).toContain('xl:inline-block')
      expect(kbd.classes()).not.toContain('sm:inline-block')
    })

    it('repousse la date du jour à xl pour desserrer l\'en-tête (au lieu de sm)', async () => {
      const { wrapper } = await mountLayout()
      const dateEl = wrapper.get('[data-test="current-date"]')
      expect(dateEl.classes()).toContain('xl:flex')
      expect(dateEl.classes()).not.toContain('sm:flex')
    })
  })

  describe('fix round 1 : cibles tactiles 44px manquantes (item 4)', () => {
    it('dimensionne les icônes de recherche, thème et déconnexion en-tête à 44px (w-5 h-5)', async () => {
      const { wrapper } = await mountLayout({ authenticated: true })
      expect(wrapper.get('[data-test="global-search-button"] svg').classes()).toContain('w-5')
      expect(wrapper.get('[data-test="header-theme-toggle"] svg').classes()).toContain('w-5')
      expect(wrapper.get('[data-test="header-logout-button"] svg').classes()).toContain('w-5')
    })
  })

  describe('fix round 1 : bouton de déconnexion du tiroir mobile, devenu load-bearing (item 8)', () => {
    it('dimensionne le bouton de déconnexion du tiroir mobile à 44px', async () => {
      const { wrapper } = await mountLayout({ authenticated: true })
      const drawerLogout = wrapper.get('aside button[title="Se déconnecter"]')
      expect(drawerLogout.classes()).toContain('p-3')
      expect(drawerLogout.get('svg').classes()).toContain('w-5')
    })
  })

  describe('fix round 1 : safe-area de la barre mobile ne comprime plus le contenu (item 2)', () => {
    it('utilise min-h (pas h) pour laisser la barre grandir avec l\'encoche au lieu de la comprimer', async () => {
      const { wrapper } = await mountLayout()
      const bar = wrapper.get('[data-test="mobile-bottom-nav"]')
      expect(bar.classes()).toContain('min-h-16')
      expect(bar.classes()).not.toContain('h-16')
    })

    it("exclut la barre de navigation mobile de l'impression (no-print)", async () => {
      const { wrapper } = await mountLayout()
      expect(wrapper.get('[data-test="mobile-bottom-nav"]').classes()).toContain('no-print')
    })
  })

  describe('fix round 1 : titre de route et indicateur hors ligne ne forcent jamais le débordement (item 5)', () => {
    it("le titre de route peut se réduire sous sa largeur naturelle (min-w-0 + truncate)", async () => {
      const { wrapper } = await mountLayout({ path: '/reviser' })
      const title = wrapper.get('[data-test="mobile-route-title"]')
      expect(title.classes()).toContain('truncate')
      expect(title.classes()).toContain('min-w-0')
    })

    it("l'indicateur hors ligne se réduit à une icône sous sm pour ne pas déborder l'en-tête mobile", async () => {
      const { wrapper } = await mountLayout({ online: false })
      const badge = wrapper.get('[data-test="offline-indicator"]')
      const label = badge.findAll('span').find((s) => s.text() === 'Hors ligne')!
      expect(label.classes()).toContain('hidden')
      expect(label.classes()).toContain('sm:inline')
      // Le libellé visuel peut disparaître à l'écran le plus étroit : l'information
      // reste portée par aria-label (pas seulement par le texte visuel).
      expect(badge.attributes('aria-label')).toBe('Hors ligne')
    })
  })

  // ── Fix round 2 (re-vérification visuelle post fix round 1) ─────────
  describe('fix round 2 : titre mobile écrasé à 1px avec indicateur hors ligne (item 5)', () => {
    it("ne compte plus que hamburger + titre + [hors ligne] + recherche + cloche + thème dans le groupe gauche/droite mobile, Planning et Communauté retirés du mini-en-tête", async () => {
      const { wrapper } = await mountLayout({ authenticated: true, online: false })
      expect(wrapper.find('[data-test="header-planning-link"]').exists()).toBe(false)
      const communaute = wrapper.get('[data-test="header-communaute-link"]')
      expect(communaute.classes()).toContain('hidden')
    })

    it('garde Planning et Communauté joignables via le tiroir hamburger en mobile', async () => {
      const { wrapper } = await mountLayout()
      const drawerNav = wrapper.get('aside nav')
      const labels = drawerNav.findAll('a').map((a) => a.text())
      expect(labels).toContain('Planning')
      expect(labels).toContain('Communauté')
    })
  })

  describe('fix round 1 : landmarks de navigation identifiables (item 6)', () => {
    it('donne un aria-label distinct à chacune des 3 landmarks de navigation', async () => {
      const { wrapper } = await mountLayout()
      const drawerNav = wrapper.get('aside nav')
      const desktopNav = wrapper.get('[data-test="desktop-nav"]')
      const mobileNav = wrapper.get('[data-test="mobile-bottom-nav"]')
      const labels = [drawerNav, desktopNav, mobileNav].map((n) => n.attributes('aria-label'))
      expect(labels.every((l) => !!l)).toBe(true)
      expect(new Set(labels).size).toBe(3)
    })
  })

  // ── Nettoyage des écouteurs ───────────────────────────────────────────
  it('retire les écouteurs globaux au démontage', async () => {
    const { wrapper } = await mountLayout()
    const removeSpy = vi.spyOn(window, 'removeEventListener')
    wrapper.unmount()
    const events = removeSpy.mock.calls.map((c) => c[0])
    expect(events).toContain('keydown')
    expect(events).toContain('studyhub:toggle-sidebar')
    expect(events).toContain('online')
    expect(events).toContain('offline')
  })
})
