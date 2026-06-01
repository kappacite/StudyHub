<template>
  <div class="min-h-screen flex bg-slate-50 text-slate-900 transition-colors duration-300 dark:bg-[#0B0F19] dark:text-slate-100">
    
    <!-- Invisible Sidebar Hover Trigger (Zen mode only) -->
    <div 
      v-if="isZenMode" 
      class="fixed left-0 top-0 bottom-0 w-3 z-45 no-print"
      @mouseenter="isSidebarHovered = true"
    ></div>

    <!-- Sidebar -->
    <aside 
      class="fixed inset-y-0 left-0 z-50 flex flex-col w-64 bg-white border-r border-slate-100 transition-all duration-300 dark:bg-[#111827] dark:border-slate-800 lg:translate-x-0"
      :class="[
        isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full',
        isZenMode 
          ? 'lg:fixed lg:-translate-x-full lg:shadow-2xl' 
          : 'lg:static lg:translate-x-0',
        (isZenMode && isSidebarHovered) ? 'lg:translate-x-0' : ''
      ]"
      @mouseenter="isZenMode ? isSidebarHovered = true : null"
      @mouseleave="isZenMode ? isSidebarHovered = false : null"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-6 py-5 border-b border-slate-100 dark:border-slate-800">
        <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/20">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.62 48.62 0 0112 20.9c.38 0 .758-.004 1.136-.011a60.9 60.9 0 00-.5-6.32 48.56 48.56 0 01-8.376-4.422z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 10.5V18M15 10.5V18M3 10.5h18M12 3v7.5M21 10.5a60.47 60.47 0 00-.491 6.347M3 10.5a60.47 60.47 0 01.491 6.347M12 21a48.58 48.58 0 008.377-4.153" />
          </svg>
        </div>
        <div>
          <h1 class="font-bold text-lg leading-none bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">StudyHub</h1>
          <span class="text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Tout-en-un</span>
        </div>
      </div>

      <!-- Navigation Links -->
      <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 group"
          :class="[
            $route.path === item.path 
              ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-950/40 dark:text-indigo-400' 
              : 'text-slate-600 hover:bg-slate-100/70 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/50 dark:hover:text-slate-200'
          ]"
          @click="isMobileMenuOpen = false"
        >
          <component 
            :is="item.icon" 
            class="w-5 h-5 transition-transform duration-200 group-hover:scale-110"
            :class="[$route.path === item.path ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300']"
          />
          {{ item.name }}
        </router-link>
      </nav>

      <!-- Sidebar Footer (User Profile & Dark Mode) -->
      <div class="p-4 border-t border-slate-100 dark:border-slate-800 space-y-4">
        <!-- Quick Settings / Theme toggler -->
        <div class="flex items-center justify-between px-2">
          <span class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Mode Sombre</span>
          <button 
            @click="toggleDarkMode" 
            class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none bg-slate-200 dark:bg-indigo-600"
          >
            <span 
              class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out flex items-center justify-center"
              :class="[isDarkMode ? 'translate-x-5' : 'translate-x-0']"
            >
              <Sun v-if="!isDarkMode" class="w-3 h-3 text-amber-500" />
              <Moon v-else class="w-3 h-3 text-indigo-600" />
            </span>
          </button>
        </div>

        <!-- User profile snippet -->
        <div class="flex items-center gap-3 p-2 rounded-xl bg-slate-50 dark:bg-slate-800/40">
          <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-100 text-indigo-600 font-semibold dark:bg-indigo-950/60 dark:text-indigo-400">
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold truncate">{{ authStore.user?.username }}</p>
            <p class="text-[11px] text-slate-400 truncate dark:text-slate-500">{{ authStore.user?.email }}</p>
          </div>
          <button 
            @click="handleLogout" 
            class="p-1.5 text-slate-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-lg transition-colors"
            title="Se déconnecter"
          >
            <LogOut class="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Mobile menu backdrop -->
    <div 
      v-if="isMobileMenuOpen" 
      class="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm lg:hidden"
      @click="isMobileMenuOpen = false"
    ></div>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-w-0 min-h-screen">
      
      <!-- Invisible Header Hover Trigger (Zen mode only) -->
      <div 
        v-if="isZenMode" 
        class="fixed top-0 left-0 right-0 h-3 z-29 no-print"
        @mouseenter="isHeaderHovered = true"
      ></div>

      <!-- Navbar / Top Header -->
      <header 
        class="flex items-center justify-between px-6 py-4 bg-white/85 backdrop-blur border-b border-slate-100 z-30 transition-all duration-300 dark:bg-[#111827]/85 dark:border-slate-800"
        :class="[
          isZenMode 
            ? 'fixed top-0 left-0 right-0 shadow-lg -translate-y-full' 
            : 'sticky top-0',
          (isZenMode && isHeaderHovered) ? 'translate-y-0' : ''
        ]"
        @mouseenter="isZenMode ? isHeaderHovered = true : null"
        @mouseleave="isZenMode ? isHeaderHovered = false : null"
      >
        <div class="flex items-center gap-4">
          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen" 
            class="p-2 -ml-2 text-slate-500 hover:text-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 dark:hover:text-slate-100 rounded-lg lg:hidden"
          >
            <Menu class="w-6 h-6" />
          </button>
          <h2 class="text-lg font-bold text-slate-800 dark:text-white capitalize">
            {{ currentRouteName }}
          </h2>
        </div>

        <div class="flex items-center gap-4">
          <!-- Calendar shortcut or current date -->
          <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-100 text-xs font-semibold text-slate-500 dark:bg-slate-800/40 dark:border-slate-800 dark:text-slate-400">
            <Calendar class="w-4 h-4 text-indigo-500" />
            {{ currentDate }}
          </div>
        </div>
      </header>

      <!-- Main Router View with padding -->
      <main 
        class="flex-1 transition-all duration-300"
        :class="[
          isZenMode 
            ? (isEditMode ? 'p-0 bg-white dark:bg-slate-900 overflow-hidden' : 'p-4 md:p-8 lg:p-12 bg-slate-100 dark:bg-[#070913] overflow-y-auto') 
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { 
  LayoutDashboard, 
  FolderClosed, 
  Layers, 
  FileText, 
  Activity, 
  FileDown, 
  LogOut, 
  Sun, 
  Moon, 
  Menu, 
  Calendar 
} from '@lucide/vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isMobileMenuOpen = ref(false)
const isDarkMode = ref(false)

const isSidebarHovered = ref(false)
const isHeaderHovered = ref(false)

const isZenMode = computed(() => {
  return route.name === 'NoteEdit'
})

const isEditMode = computed(() => {
  return route.name === 'NoteEdit' && route.query.edit === 'true'
})

const navItems = [
  { name: 'Tableau de bord', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Classeurs', path: '/binders', icon: FolderClosed },
  { name: 'Flashcards', path: '/decks', icon: Layers },
  { name: 'Notes', path: '/notes', icon: FileText },
  { name: 'Diagrammes', path: '/diagrams', icon: Activity },
  { name: 'PDFs', path: '/pdfs', icon: FileDown }
]

const currentRouteName = computed(() => {
  const name = route.name as string
  if (!name) return ''
  if (name === 'StudyDeck') return 'Flashcards (Étude)'
  if (name === 'NoteEdit') return 'Édition de Note'
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

onMounted(() => {
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
