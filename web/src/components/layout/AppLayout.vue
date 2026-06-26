<template>
  <!-- h-screen + overflow-hidden : l'app occupe exactement le viewport ; seul
       <main> défile en interne. La sidebar (lg:static) reste ainsi fixe et son
       pied (compte) ne descend plus avec le contenu de la page. -->
  <div class="h-screen overflow-hidden flex bg-app text-ink transition-colors duration-300 print:h-auto print:overflow-visible print:block">

    <!-- Sidebar -->
    <aside
      v-if="!$route.meta.immersive"
      class="fixed inset-y-0 left-0 z-50 flex flex-col w-64 bg-surface border-r border-line transition-all duration-300"
      :class="[
        isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
        isZenMode ? 'lg:fixed lg:shadow-2xl' : 'lg:static',
        isZenMode 
          ? (isZenSidebarOpen ? 'lg:translate-x-0' : 'lg:-translate-x-full') 
          : 'lg:translate-x-0'
      ]"
    >
      <!-- Logo (cliquable → /) -->
      <router-link to="/" class="flex items-center gap-3 px-6 py-5 border-b border-line hover:bg-surface-soft transition-colors cursor-pointer" @click="isMobileMenuOpen = false">
        <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-accent text-white shadow-lg shadow-elev-primary">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.62 48.62 0 0112 20.9c.38 0 .758-.004 1.136-.011a60.9 60.9 0 00-.5-6.32 48.56 48.56 0 01-8.376-4.422z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 10.5V18M15 10.5V18M3 10.5h18M12 3v7.5M21 10.5a60.47 60.47 0 00-.491 6.347M3 10.5a60.47 60.47 0 01.491 6.347M12 21a48.58 48.58 0 008.377-4.153" />
          </svg>
        </div>
        <div>
          <h1 class="font-bold text-lg leading-none bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">StudyHub</h1>
          <span class="text-[10px] font-semibold text-ink-subtle uppercase tracking-widest">Tout-en-un</span>
        </div>
      </router-link>

      <!-- Navigation Links -->
      <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 group"
          :class="[
            isNavActive(item)
              ? 'bg-primary-soft text-primary'
              : 'text-ink-muted hover:bg-surface-soft hover:text-ink'
          ]"
          @click="isMobileMenuOpen = false"
          @click.capture="isZenSidebarOpen = false"
        >
          <component
            :is="item.icon"
            class="w-5 h-5 transition-transform duration-200 group-hover:scale-110"
            :class="[isNavActive(item) ? 'text-primary' : 'text-ink-subtle group-hover:text-ink-muted']"
          />
          {{ item.name }}
        </router-link>
      </nav>

      <!-- Sidebar Footer (User Profile & Dark Mode) -->
      <div class="p-4 border-t border-line space-y-4">
        <!-- Quick Settings / Theme toggler -->
        <div class="flex items-center justify-between px-2">
          <span class="text-xs font-semibold text-ink-subtle uppercase tracking-wider">Mode Sombre</span>
          <BaseToggle :model-value="isDarkMode" @update:model-value="toggleDarkMode">
            <template #default="{ checked }">
              <Sun v-if="!checked" class="w-3 h-3 text-accent" />
              <Moon v-else class="w-3 h-3 text-primary" />
            </template>
          </BaseToggle>
        </div>

        <!-- User profile snippet -->
        <div v-if="authStore.isAuthenticated" class="flex items-center gap-3 p-2 rounded-xl bg-surface-soft">
          <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-primary-soft text-primary font-semibold">
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold truncate text-ink">{{ authStore.user?.username }}</p>
            <p class="text-[11px] text-ink-subtle truncate">{{ authStore.user?.email }}</p>
          </div>
          <button
            @click="handleLogout"
            class="p-1.5 text-ink-subtle hover:text-danger hover:bg-danger-soft rounded-lg transition-colors"
            title="Se déconnecter"
          >
            <LogOut class="w-4 h-4" />
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
      class="fixed inset-0 z-40 bg-ink/40 backdrop-blur-sm lg:hidden"
      @click="isMobileMenuOpen = false"
    ></div>

    <div
      v-if="isZenSidebarOpen && !$route.meta.immersive"
      class="fixed inset-0 z-40 hidden bg-ink/20 backdrop-blur-[1px] lg:block"
      @click="isZenSidebarOpen = false"
    ></div>

    <!-- Main Content Area : colonne bornée au viewport, scroll délégué à <main> -->
    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden print:h-auto print:overflow-visible">
      
      <!-- Invisible Header Hover Trigger (Zen mode only) -->
      <div 
        v-if="isZenMode && !$route.meta.immersive" 
        class="fixed top-0 left-0 right-0 h-3 z-29 no-print"
        @mouseenter="isHeaderHovered = true"
      ></div>

      <!-- Navbar / Top Header -->
      <header
        v-if="!$route.meta.immersive"
        class="flex items-center justify-between px-6 py-4 bg-surface/85 backdrop-blur border-b border-line z-30 transition-all duration-300"
        :class="[
          isZenMode 
            ? 'fixed top-0 left-0 right-0 shadow-lg' 
            : 'sticky top-0',
          isZenMode 
            ? (isHeaderHovered ? 'translate-y-0' : '-translate-y-full') 
            : ''
        ]"
        @mouseenter="isZenMode ? isHeaderHovered = true : null"
        @mouseleave="isZenMode ? isHeaderHovered = false : null"
      >
        <div class="flex items-center gap-4">
          <button
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="p-2 -ml-2 text-ink-muted hover:text-ink hover:bg-surface-soft rounded-lg lg:hidden"
          >
            <Menu class="w-6 h-6" />
          </button>
          <h2 class="text-lg font-bold text-ink capitalize">
            {{ currentRouteName }}
          </h2>
        </div>

        <div class="flex items-center gap-4">
          <!-- Global Search Button -->
          <button
            @click="isSearchOpen = true"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-soft border border-line hover:bg-surface text-xs font-semibold text-ink-muted cursor-pointer transition-colors"
            title="Recherche globale (Ctrl+K)"
          >
            <Search class="w-4 h-4 text-primary" />
            <span class="hidden md:inline">Rechercher...</span>
            <kbd class="hidden sm:inline-block px-1.5 py-0.5 ml-1 text-[10px] font-bold text-ink-subtle bg-line/50 rounded">⌘K</kbd>
          </button>

          <!-- Notifications -->
          <NotificationBell v-if="authStore.isAuthenticated" />

          <!-- Calendar shortcut or current date -->
          <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-soft border border-line text-xs font-semibold text-ink-muted">
            <Calendar class="w-4 h-4 text-primary" />
            {{ currentDate }}
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
              ? (isEditMode ? 'p-0 bg-surface overflow-hidden' : 'p-4 md:p-8 lg:p-12 bg-app overflow-y-auto')
              : 'p-6 overflow-y-auto'
        ]"
      >
        <router-view v-slot="{ Component }">
          <transition 
            name="fade" 
            mode="out-in"
          >
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- Universal Search Modal -->
    <SearchModal :is-open="isSearchOpen" @close="isSearchOpen = false" />

    <!-- Pomodoro Timer Floating Widget -->
    <PomodoroTimer v-if="!$route.meta.immersive" />
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
import {
  Home,
  FolderClosed,
  LogOut,
  LogIn,
  Sun,
  Moon,
  Menu,
  Calendar,
  Brain,
  Search,
  Compass,
  GraduationCap
} from '@lucide/vue'


const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isMobileMenuOpen = ref(false)
const isZenSidebarOpen = ref(false)
const isDarkMode = ref(false)
const isSearchOpen = ref(false)

const isHeaderHovered = ref(false)

const isZenMode = computed(() => {
  return route.name === 'NoteEdit'
})

const isEditMode = computed(() => {
  return route.name === 'NoteEdit' && route.query.edit === 'true'
})

// Refonte 5 sections par intention + lien Communauté. L'état actif se calcule par
// PRÉFIXE (match[]) pour que les routes feuilles (ex. /notes/123, /decks/5/study)
// allument la bonne section.
const navItems = [
  { name: 'Accueil', path: '/accueil', icon: Home, match: ['/accueil', '/focus'] },
  { name: 'Bibliothèque', path: '/bibliotheque', icon: FolderClosed, match: ['/bibliotheque', '/notes', '/pdfs', '/diagrams'] },
  { name: 'Réviser', path: '/reviser', icon: Brain, match: ['/reviser', '/decks', '/revision', '/exam'] },
  { name: 'Planning', path: '/planning', icon: Calendar, match: ['/planning'] },
  { name: 'Classes', path: '/classes', icon: GraduationCap, match: ['/classes', '/groups'] },
  { name: 'Communauté', path: '/explore', icon: Compass, match: ['/explore', '/package'] },
]

function isNavActive(item: { match: string[] }) {
  return item.match.some(m => route.path === m || route.path.startsWith(m + '/'))
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
  if (name === 'ExamSession') return 'Session d\'Examen'
  if (name === 'ExamResults') return 'Résultats d\'Examen'
  if (name === 'AssignmentDetail') return 'Détails du devoir'
  return name
})

const userInitials = computed(() => {
  const username = authStore.user?.username || ''
  if (!username) return 'U'
  return username.substring(0, 2).toUpperCase()
})

const currentDate = computed(() => {
  const options: Intl.DateTimeFormatOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
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

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('studyhub:toggle-sidebar', handleToggleSidebar)

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
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
