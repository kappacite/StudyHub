<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50/30 dark:from-[#0B0F19] dark:to-indigo-950/10">
    
    <!-- Header public -->
    <header class="sticky top-0 z-10 bg-white/80 dark:bg-slate-900/80 backdrop-blur border-b border-slate-100 dark:border-slate-800">
      <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.62 48.62 0 0112 20.9c.38 0 .758-.004 1.136-.011a60.9 60.9 0 00-.5-6.32 48.56 48.56 0 01-8.376-4.422z" />
            </svg>
          </div>
          <span class="font-bold text-sm bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">StudyHub</span>
        </div>
        <router-link
          to="/login"
          class="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-all shadow active:scale-95"
        >
          Rejoindre StudyHub
          <ArrowRight class="w-4 h-4" />
        </router-link>
      </div>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-32 gap-4">
      <div class="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
      <span class="text-sm text-slate-400 font-medium">Chargement de la note...</span>
    </div>

    <!-- Erreur -->
    <div v-else-if="error" class="flex flex-col items-center justify-center py-32 gap-4 text-center px-6">
      <div class="w-16 h-16 rounded-2xl bg-rose-100 dark:bg-rose-950/30 flex items-center justify-center">
        <Lock class="w-8 h-8 text-rose-500" />
      </div>
      <h1 class="text-xl font-bold text-slate-800 dark:text-white">Note introuvable</h1>
      <p class="text-slate-500 dark:text-slate-400 max-w-sm">Cette note n'existe pas ou n'est plus partagée publiquement.</p>
      <router-link to="/" class="mt-2 text-indigo-600 hover:text-indigo-700 font-semibold text-sm">← Retour à l'accueil</router-link>
    </div>

    <!-- Note content -->
    <div v-else-if="note" class="max-w-4xl mx-auto px-6 py-10">
      
      <!-- Meta -->
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-4">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-full">
            <Globe class="w-3 h-3" />
            Note publique
          </span>
          <span class="text-xs text-slate-400 dark:text-slate-500">
            Modifiée le {{ formatDate(note.updated_at) }}
          </span>
        </div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white leading-tight">{{ note.title }}</h1>
      </div>

      <!-- Copy link -->
      <div class="mb-8 p-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl flex items-center gap-3 shadow-sm">
        <Link2 class="w-4 h-4 text-slate-400 shrink-0" />
        <span class="text-xs text-slate-500 dark:text-slate-400 font-mono flex-1 truncate">{{ shareUrl }}</span>
        <button
          @click="copyLink"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg transition-all active:scale-95"
        >
          <Check v-if="copied" class="w-3.5 h-3.5" />
          <Copy v-else class="w-3.5 h-3.5" />
          {{ copied ? 'Copié !' : 'Copier' }}
        </button>
      </div>

      <!-- Note body rendered as markdown -->
      <article 
        class="prose prose-slate dark:prose-invert max-w-none bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl p-8 shadow-sm"
        v-html="renderedContent"
      ></article>

      <!-- CTA footer -->
      <div class="mt-12 p-8 bg-gradient-to-br from-indigo-600 to-purple-700 rounded-3xl text-center text-white shadow-xl shadow-indigo-500/20">
        <h2 class="text-xl font-bold mb-2">Envie de créer tes propres notes ?</h2>
        <p class="text-indigo-200 text-sm mb-6">StudyHub est gratuit et tout-en-un : notes, flashcards, diagrammes, PDF...</p>
        <router-link
          to="/register"
          class="inline-flex items-center gap-2 px-6 py-3 bg-white text-indigo-700 hover:bg-indigo-50 font-bold rounded-xl transition-all shadow active:scale-95"
        >
          Créer un compte gratuitement
          <ArrowRight class="w-4 h-4" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowRight, Globe, Lock, Link2, Copy, Check } from '@lucide/vue'
import api from '@/services/api'
import { marked } from 'marked'

const route = useRoute()

const note = ref<any>(null)
const loading = ref(true)
const error = ref(false)
const copied = ref(false)

const shareUrl = computed(() => window.location.href)

const renderedContent = computed(() => {
  if (!note.value?.content) return ''
  try {
    return marked(note.value.content)
  } catch {
    return note.value.content
  }
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric'
  })
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {}
}

onMounted(async () => {
  const token = route.params.token as string
  try {
    const { data } = await api.get(`/notes/public/${token}`)
    note.value = data
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>
