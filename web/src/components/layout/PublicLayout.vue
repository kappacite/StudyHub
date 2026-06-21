<template>
  <div class="min-h-screen flex flex-col bg-slate-50 text-slate-900 transition-colors duration-300 dark:bg-[#0B0F19] dark:text-slate-100">
    <!-- Top Navigation Header -->
    <header class="sticky top-0 z-50 w-full bg-white/80 dark:bg-[#0B0F19]/80 backdrop-blur-md border-b border-slate-100 dark:border-slate-800/80 transition-all duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2.5 group">
          <div class="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-500/10">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.62 48.62 0 0112 20.9c.38 0 .758-.004 1.136-.011a60.9 60.9 0 00-.5-6.32 48.56 48.56 0 01-8.376-4.422z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 10.5V18M15 10.5V18M3 10.5h18M12 3v7.5M21 10.5a60.47 60.47 0 00-.491 6.347M3 10.5a60.47 60.47 0 01.491 6.347M12 21a48.58 48.58 0 008.377-4.153" />
            </svg>
          </div>
          <div>
            <h1 class="font-bold text-base bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">StudyHub</h1>
          </div>
        </router-link>

        <!-- Desktop Menu Links -->
        <nav class="hidden md:flex items-center gap-1">
          <router-link 
            to="/" 
            class="px-4 py-2 rounded-xl text-sm font-semibold transition-all"
            :class="[
              $route.path === '/' 
                ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-white' 
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800/40'
            ]"
          >
            Accueil
          </router-link>
          <router-link 
            to="/explore" 
            class="px-4 py-2 rounded-xl text-sm font-semibold transition-all"
            :class="[
              $route.path === '/explore' 
                ? 'bg-slate-100 text-slate-900 dark:bg-slate-800 dark:text-white' 
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800/40'
            ]"
          >
            Cours Publics
          </router-link>
        </nav>

        <!-- Right Side: Dark Mode & Personal Space -->
        <div class="hidden md:flex items-center gap-4">
          <!-- Dark mode switch -->
          <button 
            @click="toggleDarkMode" 
            class="p-2 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
            aria-label="Changer de thème"
          >
            <Sun v-if="isDarkMode" class="w-5 h-5 text-amber-400" />
            <Moon v-else class="w-5 h-5 text-slate-600" />
          </button>

          <!-- Personal Space Button -->
          <button 
            @click="goToPersonalSpace"
            class="inline-flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl text-sm font-bold shadow-md shadow-indigo-500/10 hover:shadow-lg hover:shadow-indigo-500/20 active:scale-95 transition-all"
          >
            {{ authStore.isAuthenticated ? 'Espace Personnel' : 'Se Connecter' }}
            <ArrowRight class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Mobile Menu Toggler -->
        <div class="flex items-center gap-2 md:hidden">
          <!-- Theme Switch -->
          <button 
            @click="toggleDarkMode" 
            class="p-2 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
          >
            <Sun v-if="isDarkMode" class="w-4.5 h-4.5 text-amber-400" />
            <Moon v-else class="w-4.5 h-4.5 text-slate-600" />
          </button>

          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen" 
            class="p-2 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-all"
          >
            <Menu v-if="!isMobileMenuOpen" class="w-5.5 h-5.5" />
            <X v-else class="w-5.5 h-5.5" />
          </button>
        </div>
      </div>

      <!-- Mobile Dropdown Navigation -->
      <transition 
        enter-active-class="transition duration-150 ease-out" 
        enter-from-class="transform scale-95 opacity-0" 
        enter-to-class="transform scale-100 opacity-100" 
        leave-active-class="transition duration-100 ease-in" 
        leave-from-class="transform scale-100 opacity-100" 
        leave-to-class="transform scale-95 opacity-0"
      >
        <div v-if="isMobileMenuOpen" class="md:hidden border-b border-slate-100 dark:border-slate-800 bg-white dark:bg-[#0B0F19] px-4 py-4 space-y-3 shadow-lg">
          <router-link 
            to="/" 
            class="block px-4 py-2.5 rounded-xl text-sm font-semibold transition-all"
            :class="[
              $route.path === '/' 
                ? 'bg-slate-100 text-slate-950 dark:bg-slate-800 dark:text-white' 
                : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
            ]"
            @click="isMobileMenuOpen = false"
          >
            Accueil
          </router-link>
          <router-link 
            to="/explore" 
            class="block px-4 py-2.5 rounded-xl text-sm font-semibold transition-all"
            :class="[
              $route.path === '/explore' 
                ? 'bg-slate-100 text-slate-950 dark:bg-slate-800 dark:text-white' 
                : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
            ]"
            @click="isMobileMenuOpen = false"
          >
            Cours Publics
          </router-link>
          
          <div class="border-t border-slate-100 dark:border-slate-800/50 pt-3">
            <button 
              @click="goToPersonalSpaceMobile"
              class="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl text-xs font-bold transition-all active:scale-95"
            >
              {{ authStore.isAuthenticated ? 'Espace Personnel' : 'Se Connecter' }}
              <ArrowRight class="w-4 h-4" />
            </button>
          </div>
        </div>
      </transition>
    </header>

    <!-- Main Viewport Content -->
    <main class="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-100 dark:border-slate-800/80 bg-white dark:bg-[#070913] py-8 text-center text-xs text-slate-400 dark:text-slate-500">
      <p>&copy; 2026 StudyHub. Tous droits réservés. Optimisé pour la réussite étudiante.</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { Sun, Moon, Menu, X, ArrowRight } from '@lucide/vue'

const authStore = useAuthStore()
const router = useRouter()

const isMobileMenuOpen = ref(false)
const isDarkMode = ref(false)

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

function goToPersonalSpace() {
  router.push('/accueil')
}

function goToPersonalSpaceMobile() {
  isMobileMenuOpen.value = false
  goToPersonalSpace()
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
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
