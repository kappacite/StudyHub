<template>
  <!-- h-screen + overflow-hidden : l'app occupe exactement le viewport ; seul
       <main> défile en interne. La nav principale vit désormais dans l'en-tête
       (desktop : pastilles ; mobile : barre basse + icônes de mini-en-tête) — le
       tiroir latéral (<aside>) ne sert plus que de drawer mobile et d'overlay
       Zen (édition de note), jamais de colonne statique en desktop. -->
  <div
    class="h-screen overflow-hidden flex flex-col bg-app text-ink transition-colors duration-300 print:h-auto print:overflow-visible print:block"
  >
    <!-- Tiroir (drawer mobile toujours ; overlay Zen en desktop uniquement) -->
    <aside
      v-if="!$route.meta.immersive"
      class="fixed inset-y-0 left-0 z-50 flex flex-col w-64 bg-surface border-r border-line transition-all duration-300"
      :class="[
        isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
        isZenMode ? 'lg:fixed lg:shadow-2xl' : 'lg:hidden',
        isZenMode ? (isZenSidebarOpen ? 'lg:translate-x-0' : 'lg:-translate-x-full') : '',
      ]"
    >
      <!-- Logo (cliquable → /) -->
      <router-link
        to="/"
        class="flex items-center gap-3 px-6 py-5 border-b border-line hover:bg-surface-soft transition-colors cursor-pointer"
        @click="isMobileMenuOpen = false"
      >
        <div
          class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-accent text-white shadow-lg shadow-elev-primary"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2.5"
            stroke="currentColor"
            class="w-6 h-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.62 48.62 0 0112 20.9c.38 0 .758-.004 1.136-.011a60.9 60.9 0 00-.5-6.32 48.56 48.56 0 01-8.376-4.422z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M9 10.5V18M15 10.5V18M3 10.5h18M12 3v7.5M21 10.5a60.47 60.47 0 00-.491 6.347M3 10.5a60.47 60.47 0 01.491 6.347M12 21a48.58 48.58 0 008.377-4.153"
            />
          </svg>
        </div>
        <div>
          <h1 class="font-display font-bold text-lg leading-none text-ink">StudyHub</h1>
          <span class="text-[10px] font-semibold text-ink-subtle uppercase tracking-widest"
            >Tout-en-un</span
          >
        </div>
      </router-link>

      <!-- Navigation Links (liste complète des 6 destinations, préservée telle quelle) -->
      <nav aria-label="Navigation du tiroir" class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 group"
          :class="[
            isNavActive(item)
              ? 'bg-primary-soft text-primary'
              : 'text-ink-muted hover:bg-surface-soft hover:text-ink',
          ]"
          @click="isMobileMenuOpen = false"
          @click.capture="isZenSidebarOpen = false"
        >
          <component
            :is="item.icon"
            class="w-5 h-5 transition-transform duration-200 group-hover:scale-110"
            :class="[
              isNavActive(item) ? 'text-primary' : 'text-ink-subtle group-hover:text-ink-muted',
            ]"
          />
          {{ item.name }}
        </router-link>
      </nav>

      <!-- Sidebar Footer (User Profile & Dark Mode) -->
      <div class="p-4 border-t border-line space-y-4">
        <!-- Quick Settings / Theme toggler -->
        <div class="flex items-center justify-between px-2">
          <span class="text-xs font-semibold text-ink-subtle uppercase tracking-wider"
            >Mode sombre</span
          >
          <BaseToggle :model-value="isDarkMode" @update:model-value="toggleDarkMode">
            <template #default="{ checked }">
              <Sun v-if="!checked" class="w-3 h-3 text-accent" />
              <Moon v-else class="w-3 h-3 text-primary" />
            </template>
          </BaseToggle>
        </div>

        <!-- User profile snippet -->
        <div
          v-if="authStore.isAuthenticated"
          class="flex items-center gap-3 p-2 rounded-xl bg-surface-soft"
        >
          <div
            class="flex items-center justify-center w-10 h-10 rounded-lg bg-primary-soft text-primary font-semibold"
          >
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold truncate text-ink">{{ authStore.user?.username }}</p>
            <p class="text-[11px] text-ink-subtle truncate">{{ authStore.user?.email }}</p>
          </div>
          <!-- p-3 + w-5 (44px) : sur mobile, ce bouton est désormais le SEUL recours
               pour se déconnecter (le cluster compte de l'en-tête est desktop-only,
               cf. plus bas) — il devient load-bearing, donc dimensionné en conséquence. -->
          <button
            class="flex items-center justify-center p-3 text-ink-subtle hover:text-danger hover:bg-danger-soft rounded-lg transition-colors"
            title="Se déconnecter"
            aria-label="Se déconnecter"
            @click="handleLogout"
          >
            <LogOut class="w-5 h-5" />
          </button>
        </div>
        <div v-else class="p-1">
          <BaseButton variant="primary" block @click="router.push('/login')">
            <template #icon><LogIn class="w-4 h-4" /></template>
            Se connecter
          </BaseButton>
        </div>
      </div>
    </aside>

    <!-- Mobile menu backdrop -->
    <div
      v-if="isMobileMenuOpen"
      data-test="mobile-menu-backdrop"
      class="fixed inset-0 z-40 bg-ink/40 backdrop-blur-sm lg:hidden"
      @click="isMobileMenuOpen = false"
    ></div>

    <div
      v-if="isZenSidebarOpen && !$route.meta.immersive"
      data-test="zen-sidebar-backdrop"
      class="fixed inset-0 z-40 hidden bg-ink/20 backdrop-blur-[1px] lg:block"
      @click="isZenSidebarOpen = false"
    ></div>

    <!-- Invisible Header Hover Trigger (Zen mode only) -->
    <div
      v-if="isZenMode && !$route.meta.immersive"
      data-test="header-hover-trigger"
      class="fixed top-0 left-0 right-0 h-3 z-20 no-print"
      @mouseenter="isHeaderHovered = true"
    ></div>

    <!-- En-tête : logo + nav desktop (5 pastilles) à gauche, actions à droite.
         En mobile, la nav principale se retrouve dans la barre basse ; Planning
         et Communauté restent accessibles ici en icônes (miroir du traitement
         desktop de Communauté, qui est toujours une icône, jamais une pastille).
         Fix round 1 : le contenu de l'en-tête était trop dense entre 1024-1279px
         (lg, avant xl) — recherche/date repoussées à xl, gaps et paddings des
         pastilles resserrés jusqu'à xl, padding horizontal du header lui-même
         resserré jusqu'à xl. -->
    <header
      v-if="!$route.meta.immersive"
      class="flex items-center justify-between gap-3 px-4 xl:px-6 py-3 lg:py-4 bg-surface/85 backdrop-blur border-b border-line z-30 transition-all duration-300 flex-shrink-0"
      :class="[
        isZenMode ? 'fixed top-0 left-0 right-0 shadow-elev-3' : 'sticky top-0',
        isZenMode ? (isHeaderHovered ? 'translate-y-0' : '-translate-y-full') : '',
      ]"
      @mouseenter="isZenMode ? (isHeaderHovered = true) : null"
      @mouseleave="isZenMode ? (isHeaderHovered = false) : null"
    >
      <div class="flex items-center gap-2 lg:gap-4 xl:gap-8 min-w-0">
        <button
          data-test="hamburger-button"
          class="flex items-center justify-center p-3 -ml-1 text-ink-muted hover:text-ink hover:bg-surface-soft rounded-lg lg:hidden"
          aria-label="Ouvrir le menu"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
        >
          <Menu class="w-5 h-5" />
        </button>

        <router-link
          to="/"
          data-test="header-logo-link"
          class="hidden lg:flex items-center gap-2 shrink-0"
        >
          <div
            class="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-accent text-white"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="2.5"
              stroke="currentColor"
              class="w-4 h-4"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.62 48.62 0 0112 20.9c.38 0 .758-.004 1.136-.011a60.9 60.9 0 00-.5-6.32 48.56 48.56 0 01-8.376-4.422z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M9 10.5V18M15 10.5V18M3 10.5h18M12 3v7.5M21 10.5a60.47 60.47 0 00-.491 6.347M3 10.5a60.47 60.47 0 01.491 6.347M12 21a48.58 48.58 0 008.377-4.153"
              />
            </svg>
          </div>
          <span class="font-display font-bold text-base text-ink">StudyHub</span>
        </router-link>

        <!-- Nav desktop : 5 destinations primaires (Communauté = icône séparée, cluster de droite).
             Gap/padding resserrés jusqu'à xl (fix round 1, item 1) : au-delà, l'espacement
             généreux d'origine revient. -->
        <nav
          data-test="desktop-nav"
          aria-label="Navigation principale"
          class="hidden lg:flex items-center gap-0.5 xl:gap-1 min-w-0"
        >
          <router-link
            v-for="item in desktopNavItems"
            :key="item.path"
            :to="item.path"
            class="inline-flex items-center gap-1.5 xl:gap-2 rounded-full px-2.5 xl:px-4 py-3 text-sm font-semibold whitespace-nowrap transition-all duration-200"
            :class="
              isNavActive(item)
                ? 'bg-primary text-primary-ink'
                : 'text-ink-muted hover:text-ink hover:bg-surface-soft'
            "
          >
            <component :is="item.icon" class="w-4 h-4" />
            {{ item.name }}
          </router-link>
        </nav>

        <!-- Titre de la route courante : seulement pertinent en mobile (le desktop
             indique déjà la section active via la pastille de nav). min-w-0 est
             nécessaire pour que `truncate` fonctionne réellement dans ce conteneur
             flex (sinon min-width:auto empêche l'élément de rétrécir sous son
             contenu, et le header pourrait déborder plutôt que tronquer). -->
        <h2
          data-test="mobile-route-title"
          class="lg:hidden min-w-0 text-base font-bold text-ink capitalize truncate"
        >
          {{ currentRouteName }}
        </h2>
      </div>

      <div
        data-test="header-actions-cluster"
        class="flex items-center gap-1.5 lg:gap-2 flex-shrink-0"
      >
        <!-- Indicateur hors ligne : discret, non bloquant, jamais de modale. Le
             libellé visuel se réduit à une icône sous sm (fix round 1, item 5) pour
             ne jamais pousser l'en-tête mobile en débordement ; aria-label porte
             l'information même quand le texte est masqué. -->
        <BaseBadge
          v-if="!isOnline"
          data-test="offline-indicator"
          variant="neutral"
          aria-label="Hors ligne"
          class="gap-1.5"
        >
          <WifiOff class="w-3 h-3" />
          <span class="hidden sm:inline">Hors ligne</span>
        </BaseBadge>

        <!-- Recherche globale : libellé + raccourci repoussés à xl (fix round 1, item 1) —
             icône seule jusque-là. Icône remontée à w-5 (44px avec le padding du bouton,
             fix round 1, item 4). -->
        <button
          data-test="global-search-button"
          class="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-surface-soft border border-line hover:bg-surface text-xs font-semibold text-ink-muted cursor-pointer transition-colors"
          title="Recherche globale (Ctrl+K)"
          aria-label="Recherche globale"
          @click="isSearchOpen = true"
        >
          <Search class="w-5 h-5 text-primary" />
          <span class="hidden xl:inline">Rechercher...</span>
          <kbd
            class="hidden xl:inline-block px-1.5 py-0.5 ml-1 text-[10px] font-bold text-ink-subtle bg-line/50 rounded"
            >⌘K</kbd
          >
        </button>

        <!-- Communauté : icône secondaire, desktop uniquement (fix round 2, item 5).
             En mobile, l'en-tête n'a plus la place pour Planning + Communauté sans
             écraser le titre de route sous l'indicateur hors ligne (mesuré : le titre
             tombait à 1px de large) — les deux restent accessibles via le tiroir
             hamburger, qui liste déjà les 6 destinations. Aucune destination perdue. -->
        <router-link
          to="/explore"
          data-test="header-communaute-link"
          class="hidden lg:flex items-center justify-center p-3 rounded-lg transition-colors"
          :class="
            isNavActive(communauteItem)
              ? 'text-primary bg-primary-soft'
              : 'text-ink-muted hover:text-ink hover:bg-surface-soft'
          "
          aria-label="Communauté"
          title="Communauté"
        >
          <Compass class="w-5 h-5" />
        </router-link>

        <!-- Notifications -->
        <NotificationBell v-if="authStore.isAuthenticated" />

        <!-- Date du jour : repoussée à xl (fix round 1, item 1) — c'était le poste le
             moins essentiel du cluster et l'un des plus larges (texte complet
             "lundi 24 août 2026"). -->
        <div
          data-test="current-date"
          class="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-soft border border-line text-xs font-semibold text-ink-muted"
        >
          <Calendar class="w-4 h-4 text-primary" />
          {{ currentDate }}
        </div>

        <!-- Bascule thème : icône remontée à w-5 (44px avec le padding du bouton,
             fix round 1, item 4). -->
        <button
          data-test="header-theme-toggle"
          type="button"
          class="flex items-center justify-center p-3 rounded-lg border border-line bg-surface hover:bg-surface-soft text-ink-muted transition-colors"
          :aria-label="isDarkMode ? 'Activer le mode clair' : 'Activer le mode sombre'"
          @click="toggleDarkMode"
        >
          <Sun v-if="!isDarkMode" class="w-5 h-5 text-accent" />
          <Moon v-else class="w-5 h-5 text-primary" />
        </button>

        <!-- Compte : avatar + déconnexion, ou CTA connexion — desktop uniquement.
             En mobile, le tiroir (hamburger) reste l'unique porte d'entrée du
             profil/déconnexion/connexion, préservé tel quel ci-dessus. Icône de
             déconnexion remontée à w-5 (fix round 1, item 4). -->
        <div class="hidden lg:flex items-center gap-2">
          <template v-if="authStore.isAuthenticated">
            <div
              data-test="header-avatar"
              class="flex items-center justify-center w-11 h-11 rounded-full bg-primary-soft text-primary font-semibold"
              :title="`${authStore.user?.username} — ${authStore.user?.email}`"
            >
              {{ userInitials }}
            </div>
            <button
              data-test="header-logout-button"
              class="flex items-center justify-center p-3 text-ink-subtle hover:text-danger hover:bg-danger-soft rounded-lg transition-colors"
              title="Se déconnecter"
              aria-label="Se déconnecter"
              @click="handleLogout"
            >
              <LogOut class="w-5 h-5" />
            </button>
          </template>
          <BaseButton
            v-else
            data-test="header-account-cta"
            variant="primary"
            size="lg"
            @click="router.push('/login')"
          >
            <template #icon><LogIn class="w-4 h-4" /></template>
            Se connecter
          </BaseButton>
        </div>
      </div>
    </header>

    <!-- Main Router View with padding -->
    <main
      class="flex-1 min-h-0 transition-all duration-300 print:overflow-visible print:h-auto"
      :class="[
        $route.meta.immersive
          ? 'p-0 bg-app overflow-y-auto'
          : isZenMode
            ? isEditMode
              ? 'p-0 bg-surface overflow-hidden'
              : 'p-4 md:p-8 lg:p-12 bg-app overflow-y-auto'
            : 'p-6 overflow-y-auto',
      ]"
    >
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Barre de navigation mobile : 4 onglets primaires (conforme à la maquette
         Direction A). Accueil/Bibliothèque/Réviser/Classes inchangés ; Planning
         et Communauté restent accessibles via les icônes du mini-en-tête ci-dessus.
         min-h (pas h) + no-print (fix round 1, items 2 et 7) : `h-16` combiné à
         `pb-safe` aurait comprimé les onglets sous l'encoche iOS au lieu de laisser
         la barre grandir ; `no-print` évite qu'elle apparaisse dans un export PDF,
         comme le FAB Pomodoro et la bande de survol Zen. -->
    <nav
      v-if="!$route.meta.immersive"
      data-test="mobile-bottom-nav"
      aria-label="Navigation mobile"
      class="lg:hidden no-print flex-shrink-0 flex items-center justify-around min-h-16 pb-safe bg-surface border-t border-line"
    >
      <router-link
        v-for="item in mobileTabItems"
        :key="item.path"
        :to="item.path"
        class="flex flex-col items-center justify-center gap-1 min-w-11 min-h-11 px-2 rounded-lg"
        :class="isNavActive(item) ? 'text-primary' : 'text-ink-muted'"
      >
        <component :is="item.icon" class="w-5 h-5" />
        <span class="text-tiny font-semibold">{{ item.name }}</span>
      </router-link>
    </nav>

    <!-- Universal Search Modal -->
    <SearchModal :is-open="isSearchOpen" @close="isSearchOpen = false" />

    <!-- Pomodoro Timer Floating Widget : masqué pendant une session de
         révision de flashcards — sa position fixe (bottom-28 right-6, cf.
         PomodoroTimer.vue) chevauche et intercepte les clics du 4e bouton de
         notation (« Facile ») sur mobile, mesuré à 375px avec une seule
         carte affichée (hauteur de contenu quasi constante quelle que soit
         la taille du deck, donc collision systématique, pas un cas limite). -->
    <PomodoroTimer v-if="!$route.meta.immersive && route.name !== 'StudyDeck'" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import SearchModal from '../ui/SearchModal.vue'
import PomodoroTimer from '../ui/PomodoroTimer.vue'
import NotificationBell from '../ui/NotificationBell.vue'
import BaseToggle from '../ui/base/BaseToggle.vue'
import BaseButton from '../ui/base/BaseButton.vue'
import BaseBadge from '../ui/base/BaseBadge.vue'
import {
  Home,
  BookOpen,
  LogOut,
  LogIn,
  Sun,
  Moon,
  Menu,
  Calendar,
  Brain,
  Search,
  Compass,
  Users,
  WifiOff,
} from '@lucide/vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isMobileMenuOpen = ref(false)
const isZenSidebarOpen = ref(false)
const isDarkMode = ref(false)
const isSearchOpen = ref(false)
const isOnline = ref(navigator.onLine)

const isHeaderHovered = ref(false)

const isZenMode = computed(() => {
  return route.name === 'NoteEdit'
})

const isEditMode = computed(() => {
  return route.name === 'NoteEdit' && route.query.edit === 'true'
})

// Refonte 5 sections par intention + lien Communauté. L'état actif se calcule par
// PRÉFIXE (match[]) pour que les routes feuilles (ex. /notes/123, /decks/5/study)
// allument la bonne section. Cette liste complète (6) reste utilisée telle quelle
// dans le tiroir (drawer mobile / overlay Zen) ; le sous-ensemble utilisé par la
// nav desktop et la barre mobile est dérivé ci-dessous, sans rien dupliquer.
const navItems = [
  { name: 'Accueil', path: '/accueil', icon: Home, match: ['/accueil', '/focus'] },
  {
    name: 'Bibliothèque',
    path: '/bibliotheque',
    icon: BookOpen,
    match: ['/bibliotheque', '/notes', '/pdfs', '/diagrams'],
  },
  {
    name: 'Réviser',
    path: '/reviser',
    icon: Brain,
    match: ['/reviser', '/decks', '/revision', '/exam'],
  },
  { name: 'Planning', path: '/planning', icon: Calendar, match: ['/planning'] },
  { name: 'Classes', path: '/classes', icon: Users, match: ['/classes', '/groups'] },
  { name: 'Communauté', path: '/explore', icon: Compass, match: ['/explore', '/package'] },
]

// Nav desktop (en-tête) : 5 pastilles primaires — Communauté en est exclue, elle
// vit en icône séparée dans le cluster d'actions (cf. ETAT.md, ruling explicite).
const desktopNavItems = computed(() => navItems.filter((item) => item.path !== '/explore'))

// Barre basse mobile : 4 onglets conformes à la maquette Direction A.
const mobileTabPaths = ['/accueil', '/bibliotheque', '/reviser', '/classes']
const mobileTabItems = computed(() => navItems.filter((item) => mobileTabPaths.includes(item.path)))

const communauteItem = navItems.find((item) => item.path === '/explore')!

function isNavActive(item: { match: string[] }) {
  return item.match.some((m) => route.path === m || route.path.startsWith(m + '/'))
}

const currentRouteName = computed(() => {
  const name = route.name as string
  if (!name) return ''
  if (name === 'Accueil') return 'Accueil'
  if (name === 'Bibliotheque') return 'Bibliothèque'
  if (name === 'StudyDeck') return 'Flashcards (Étude)'
  if (name === 'NoteEdit') return 'Édition de Note'
  if (name === 'Reviser') return 'Espace Révisions'
  if (name === 'Classes') return 'Classes'
  if (name === 'Planning') return 'Planning des révisions'
  if (name === 'ExamSetup') return 'Configuration Examen'
  if (name === 'ExamSession') return "Session d'Examen"
  if (name === 'ExamResults') return "Résultats d'Examen"
  if (name === 'AssignmentDetail') return 'Détails du devoir'
  if (name === 'RevisionSetDetail') return 'Ensemble de révision'
  if (name === 'RevisionSetTypeItems') return 'Éléments par type'
  if (name === 'RevisionStudy') return 'Session de révision'
  return name
})

const userInitials = computed(() => {
  const username = authStore.user?.username || ''
  if (!username) return 'U'
  return username.substring(0, 2).toUpperCase()
})

const currentDate = computed(() => {
  const options: Intl.DateTimeFormatOptions = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }
  return new Date().toLocaleDateString('fr-FR', options)
})

function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('sh_theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('sh_theme', 'light')
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function handleKeyDown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    isSearchOpen.value = !isSearchOpen.value
  }
}

function handleToggleSidebar() {
  if (isZenMode.value) {
    isZenSidebarOpen.value = !isZenSidebarOpen.value
  } else {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
  }
}

// Indicateur hors ligne : purement additif, basé sur les événements standard
// online/offline de window (identiques web/mobile/desktop, cf. usePlatform() —
// aucun conditionnel natif nécessaire ici, navigator.onLine est universel).
function handleOnline() {
  isOnline.value = true
}
function handleOffline() {
  isOnline.value = false
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('studyhub:toggle-sidebar', handleToggleSidebar)
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)

  const savedTheme = localStorage.getItem('sh_theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    isDarkMode.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDarkMode.value = false
    document.documentElement.classList.remove('dark')
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('studyhub:toggle-sidebar', handleToggleSidebar)
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* env() n'est pas un token de couleur/rayon/typo — c'est une métrique matérielle
   (encoche iOS) sans équivalent Tailwind dans ce projet. Isolée ici plutôt que
   comme valeur brute inline. */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>
