<template>
  <div class="min-h-screen flex flex-col bg-app text-ink transition-colors duration-300">
    <!-- Top Navigation Header -->
    <header class="sticky top-0 z-50 w-full bg-surface/80 backdrop-blur-md border-b border-line transition-all duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">

        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2.5 group">
          <div class="flex items-center justify-center w-9 h-9 rounded-xl bg-primary text-white shadow-elev-primary">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.62 48.62 0 0112 20.9c.38 0 .758-.004 1.136-.011a60.9 60.9 0 00-.5-6.32 48.56 48.56 0 01-8.376-4.422z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 10.5V18M15 10.5V18M3 10.5h18M12 3v7.5M21 10.5a60.47 60.47 0 00-.491 6.347M3 10.5a60.47 60.47 0 01.491 6.347M12 21a48.58 48.58 0 008.377-4.153" />
            </svg>
          </div>
          <div>
            <h1 class="font-bold text-base text-primary">StudyHub</h1>
          </div>
        </router-link>

        <!-- Desktop Menu Links -->
        <nav class="hidden md:flex items-center gap-1">
          <router-link
            to="/"
            class="px-4 py-2 rounded-xl text-sm font-semibold transition-colors"
            :class="$route.path === '/' ? 'bg-surface-soft text-ink' : 'text-ink-muted hover:text-ink hover:bg-surface-soft'"
          >
            Accueil
          </router-link>
          <router-link
            to="/explore"
            class="px-4 py-2 rounded-xl text-sm font-semibold transition-colors"
            :class="$route.path === '/explore' ? 'bg-surface-soft text-ink' : 'text-ink-muted hover:text-ink hover:bg-surface-soft'"
          >
            Cours Publics
          </router-link>
        </nav>

        <!-- Right Side: Dark Mode & Personal Space -->
        <div class="hidden md:flex items-center gap-4">
          <button
            @click="toggleDarkMode"
            class="p-2 text-ink-muted hover:text-ink rounded-xl hover:bg-surface-soft transition-colors"
            aria-label="Changer de thème"
          >
            <Sun v-if="isDarkMode" class="w-5 h-5 text-accent" />
            <Moon v-else class="w-5 h-5" />
          </button>

          <BaseButton @click="goToPersonalSpace">
            {{ authStore.isAuthenticated ? 'Espace Personnel' : 'Se Connecter' }}
            <ArrowRight class="w-3.5 h-3.5" />
          </BaseButton>
        </div>

        <!-- Mobile Menu Toggler -->
        <div class="flex items-center gap-2 md:hidden">
          <button
            @click="toggleDarkMode"
            class="p-2 text-ink-muted hover:text-ink rounded-xl hover:bg-surface-soft transition-colors"
          >
            <Sun v-if="isDarkMode" class="w-4.5 h-4.5 text-accent" />
            <Moon v-else class="w-4.5 h-4.5" />
          </button>

          <button
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="p-2 text-ink-muted hover:text-ink rounded-xl hover:bg-surface-soft transition-colors"
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
        <div v-if="isMobileMenuOpen" class="md:hidden border-b border-line bg-surface px-4 py-4 space-y-3 shadow-elev-2">
          <router-link
            to="/"
            class="block px-4 py-2.5 rounded-xl text-sm font-semibold transition-colors"
            :class="$route.path === '/' ? 'bg-surface-soft text-ink' : 'text-ink-muted hover:text-ink'"
            @click="isMobileMenuOpen = false"
          >
            Accueil
          </router-link>
          <router-link
            to="/explore"
            class="block px-4 py-2.5 rounded-xl text-sm font-semibold transition-colors"
            :class="$route.path === '/explore' ? 'bg-surface-soft text-ink' : 'text-ink-muted hover:text-ink'"
            @click="isMobileMenuOpen = false"
          >
            Cours Publics
          </router-link>

          <div class="border-t border-line pt-3">
            <BaseButton block @click="goToPersonalSpaceMobile">
              {{ authStore.isAuthenticated ? 'Espace Personnel' : 'Se Connecter' }}
              <ArrowRight class="w-4 h-4" />
            </BaseButton>
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
    <footer class="border-t border-line bg-surface py-8 text-center text-xs text-ink-subtle">
      <p>&copy; 2026 StudyHub. Tous droits réservés. Optimisé pour la réussite étudiante.</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { BaseButton } from '../ui/base'
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
