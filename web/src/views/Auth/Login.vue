<template>
  <div class="min-h-screen flex items-center justify-center bg-app text-ink px-4 py-12 sm:px-6 lg:px-8 transition-colors duration-300 relative overflow-hidden">
    <!-- Visual background decoration -->
    <div class="absolute top-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl"></div>
    <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl"></div>

    <div v-motion="fadeUp" class="max-w-md w-full space-y-8 relative z-10">
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
        <p class="mt-2 text-sm text-ink-muted">
          Entrez vos identifiants pour accéder à votre espace
        </p>
      </div>

      <!-- Card container -->
      <BaseCard padding="lg" class="backdrop-blur-md">
        <form class="space-y-6" @submit.prevent="onSubmit">
          <!-- Error alert -->
          <div v-if="error" class="p-4 rounded-xl bg-danger-soft border border-danger/20 text-danger text-sm flex items-start gap-2.5 animate-shake">
            <AlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
            <span>{{ error }}</span>
          </div>

          <div class="space-y-4">
            <!-- Email -->
            <BaseField label="Adresse email" for-id="email">
              <BaseInput id="email" type="email" v-model="email" placeholder="nom@exemple.com">
                <template #icon><Mail class="w-5 h-5" /></template>
              </BaseInput>
            </BaseField>

            <!-- Password -->
            <BaseField label="Mot de passe" for-id="password">
              <BaseInput id="password" type="password" v-model="password" placeholder="••••••••">
                <template #icon><Lock class="w-5 h-5" /></template>
              </BaseInput>
            </BaseField>
          </div>

          <!-- Submit Button -->
          <BaseButton type="submit" block size="lg" :loading="loading">Se connecter</BaseButton>
        </form>

        <!-- Redirect to register -->
        <div class="mt-6 text-center">
          <p class="text-sm text-ink-muted">
            Nouveau sur StudyHub ?
            <router-link to="/register" class="font-semibold text-primary hover:text-primary-strong transition-colors">
              Créer un compte
            </router-link>
          </p>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { BaseCard, BaseButton, BaseField, BaseInput } from '../../components/ui/base'
import { fadeUp } from '../../composables/useMotionPresets'
import { Mail, Lock, AlertCircle } from '@lucide/vue'

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
