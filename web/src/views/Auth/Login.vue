<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-[#0B0F19] px-4 py-12 sm:px-6 lg:px-8 transition-colors duration-300 relative overflow-hidden">
    <!-- Visual background decoration -->
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl dark:bg-indigo-500/5"></div>
    <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl dark:bg-purple-500/5"></div>

    <div class="max-w-md w-full space-y-8 relative z-10">
      <!-- Header -->
      <div class="text-center">
        <div class="mx-auto flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow-xl shadow-indigo-500/25">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-8 h-8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.62 48.62 0 0112 20.9c.38 0 .758-.004 1.136-.011a60.9 60.9 0 00-.5-6.32 48.56 48.56 0 01-8.376-4.422z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 10.5V18M15 10.5V18M3 10.5h18M12 3v7.5M21 10.5a60.47 60.47 0 00-.491 6.347M3 10.5a60.47 60.47 0 01.491 6.347M12 21a48.58 48.58 0 008.377-4.153" />
          </svg>
        </div>
        <h2 class="mt-6 text-3xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-600 to-purple-500 bg-clip-text text-transparent dark:from-indigo-400 dark:to-purple-400">
          Bienvenue sur StudyHub
        </h2>
        <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Entrez vos identifiants pour accéder à votre espace
        </p>
      </div>

      <!-- Card container with glass effect -->
      <div class="bg-white/80 dark:bg-slate-900/60 backdrop-blur-md border border-slate-100 dark:border-slate-800 rounded-3xl p-8 shadow-xl shadow-slate-100/50 dark:shadow-none">
        <form class="space-y-6" @submit.prevent="onSubmit">
          <!-- Error alert -->
          <div v-if="error" class="p-4 rounded-xl bg-rose-50 border border-rose-100 text-rose-600 dark:bg-rose-950/20 dark:border-rose-950/30 dark:text-rose-400 text-sm flex items-start gap-2.5 animate-shake">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5 shrink-0 mt-0.5">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-5a.75.75 0 01.75.75v4.5a.75.75 0 01-1.5 0v-4.5A.75.75 0 0110 5zm0 10a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
            </svg>
            <span>{{ error }}</span>
          </div>

          <div class="space-y-4">
            <!-- Email -->
            <div>
              <label for="email" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">Adresse email</label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25H4.5a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                  </svg>
                </div>
                <input 
                  id="email" 
                  type="email" 
                  required 
                  v-model="email"
                  placeholder="nom@exemple.com"
                  class="block w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm font-medium transition-all"
                />
              </div>
            </div>

            <!-- Password -->
            <div>
              <div class="flex justify-between items-center mb-2">
                <label for="password" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">Mot de passe</label>
                <a href="#" class="text-xs font-medium text-indigo-500 hover:text-indigo-600 dark:text-indigo-400">Mot de passe oublié ?</a>
              </div>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                  </svg>
                </div>
                <input 
                  id="password" 
                  type="password" 
                  required 
                  v-model="password"
                  placeholder="••••••••"
                  class="block w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm font-medium transition-all"
                />
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <button 
            type="submit" 
            :disabled="loading"
            class="w-full flex items-center justify-center gap-2.5 px-4 py-3 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150 active:scale-95 shadow-lg shadow-indigo-600/10 dark:shadow-none"
          >
            <!-- Loading spinner -->
            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Se connecter
          </button>
        </form>

        <!-- Redirect to register -->
        <div class="mt-6 text-center">
          <p class="text-sm text-slate-500 dark:text-slate-400">
            Nouveau sur StudyHub ?
            <router-link to="/register" class="font-semibold text-indigo-500 hover:text-indigo-600 dark:text-indigo-400 transition-colors">
              Créer un compte
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function onSubmit() {
  error.value = ''
  loading.value = true
  
  try {
    await authStore.login(email.value, password.value)
    router.push('/dashboard')
  } catch (err: any) {
    error.value = err.message || 'Une erreur s\'est produite.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}
.animate-shake {
  animation: shake 0.2s ease-in-out 0s 2;
}
</style>
