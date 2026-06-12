<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 text-xs font-semibold text-slate-400">
      <router-link to="/explore" class="hover:text-indigo-600 transition-colors">Marketplace</router-link>
      <ChevronRight class="w-3 h-3" />
      <span class="text-slate-650 truncate max-w-[200px]">{{ packageData?.binder?.name || 'Aperçu du package' }}</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-40 gap-3">
      <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Chargement de l'aperçu...</span>
    </div>

    <!-- Main Content -->
    <div v-else-if="packageData" class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- 1. LEFT SIDEBAR: PACK METADATA & IMPORT ACTION (4 cols) -->
      <div class="lg:col-span-4 space-y-6">
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-5">
          <div class="p-4 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-2xl w-fit">
            <Folder class="w-8 h-8" />
          </div>
          
          <div>
            <h1 class="text-xl font-bold text-slate-850 dark:text-white">{{ packageData.binder.name }}</h1>
            <p class="text-xs text-slate-450 mt-1 uppercase font-bold tracking-wider">
              Partagé par l'auteur #{{ packageData.binder.user_id }}
            </p>
          </div>

          <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            {{ packageData.binder.description || 'Aucune description disponible pour ce pack.' }}
          </p>

          <!-- Tags -->
          <div v-if="packageData.binder.tags && packageData.binder.tags.length > 0" class="flex flex-wrap gap-1.5 pt-1">
            <span 
              v-for="tag in packageData.binder.tags" 
              :key="tag"
              class="px-2.5 py-0.5 text-[9px] font-extrabold rounded-lg bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 border border-indigo-100/50 dark:border-indigo-900/40 uppercase tracking-wider"
            >
              {{ tag }}
            </span>
          </div>

          <!-- Stats list -->
          <div class="border-t border-b border-slate-50 dark:border-slate-800/80 py-4 my-2 space-y-2.5 text-xs">
            <div class="flex justify-between font-semibold">
              <span class="text-slate-450 uppercase tracking-wider text-[10px]">Importations</span>
              <span class="flex items-center gap-1">
                <GitFork class="w-3.5 h-3.5 text-indigo-500" />
                {{ packageData.binder.fork_count }}
              </span>
            </div>
            <div class="flex justify-between font-semibold">
              <span class="text-slate-450 uppercase tracking-wider text-[10px]">Date de partage</span>
              <span>{{ formatDate(packageData.binder.created_at) }}</span>
            </div>
          </div>

          <!-- Import / Clone Button -->
          <div class="space-y-3 pt-2">
            <button 
              @click="handleImport"
              :disabled="importing"
              class="w-full flex items-center justify-center gap-2 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-xs font-bold transition-all active:scale-95 shadow-md shadow-indigo-600/10 disabled:opacity-50"
            >
              <Download v-if="!importing" class="w-4 h-4" />
              <svg v-else class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ importing ? 'Importation en cours...' : (authStore.isAuthenticated ? 'Importer dans mes classeurs' : 'Se connecter pour importer') }}
            </button>
            
            <p v-if="!authStore.isAuthenticated" class="text-[10px] text-center text-rose-500 font-bold uppercase tracking-wider">
              Compte requis pour importer.
            </p>
          </div>
        </div>
      </div>

      <!-- 2. RIGHT SIDEBAR: DETAILED TABLE OF CONTENTS (8 cols) -->
      <div class="lg:col-span-8 space-y-6">
        <!-- Read-only locked preview banner -->
        <div class="p-5 bg-amber-500/10 border border-amber-500/20 rounded-3xl dark:bg-amber-950/20 dark:border-amber-900/30 flex items-start gap-4">
          <div class="p-2 bg-amber-500/10 text-amber-600 dark:text-amber-400 rounded-xl mt-0.5">
            <Lock class="w-5 h-5 animate-bounce" />
          </div>
          <div>
            <h4 class="font-bold text-slate-800 dark:text-amber-300 text-sm">Mode Aperçu (Lecture Seule)</h4>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
              Vous explorez le contenu de ce pack. Pour modifier les notes de cours, dessiner sur les diagrammes ou lancer des sessions de flashcards actives (SM-2), importez ce pack dans votre espace personnel.
            </p>
          </div>
        </div>

        <!-- Contents list -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-6">
          <h3 class="font-bold text-slate-800 dark:text-white flex items-center gap-2 border-b border-slate-50 dark:border-slate-800/60 pb-4">
            <Layers class="w-5 h-5 text-indigo-500" />
            Contenu détaillé du pack
          </h3>

          <!-- Table of contents list -->
          <div class="space-y-6">
            <!-- 1. Notes section -->
            <div v-if="packageData.notes.length > 0" class="space-y-3">
              <h4 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <FileText class="w-4 h-4 text-indigo-500" />
                Notes de cours ({{ packageData.notes.length }})
              </h4>
              <ul class="pl-6 space-y-2 border-l border-indigo-100 dark:border-slate-800">
                <li 
                  v-for="note in packageData.notes" 
                  :key="note"
                  class="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2 hover:text-indigo-500 transition-colors"
                >
                  <div class="w-1.5 h-1.5 rounded-full bg-indigo-500"></div>
                  {{ note }}
                </li>
              </ul>
            </div>

            <!-- 2. Decks section -->
            <div v-if="packageData.decks.length > 0" class="space-y-3">
              <h4 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Layers class="w-4 h-4 text-indigo-500" />
                Decks de cartes ({{ packageData.decks.length }})
              </h4>
              <ul class="pl-6 space-y-2 border-l border-indigo-100 dark:border-slate-800">
                <li 
                  v-for="deck in packageData.decks" 
                  :key="deck"
                  class="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2 hover:text-indigo-500 transition-colors"
                >
                  <div class="w-1.5 h-1.5 rounded-full bg-indigo-500"></div>
                  {{ deck }}
                </li>
              </ul>
            </div>

            <!-- 3. Diagrams section -->
            <div v-if="packageData.diagrams.length > 0" class="space-y-3">
              <h4 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Activity class="w-4 h-4 text-indigo-500" />
                Schémas & Cartes Mentales ({{ packageData.diagrams.length }})
              </h4>
              <ul class="pl-6 space-y-2 border-l border-indigo-100 dark:border-slate-800">
                <li 
                  v-for="diag in packageData.diagrams" 
                  :key="diag"
                  class="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2 hover:text-indigo-500 transition-colors"
                >
                  <div class="w-1.5 h-1.5 rounded-full bg-indigo-500"></div>
                  {{ diag }}
                </li>
              </ul>
            </div>

            <!-- 4. PDFs section -->
            <div v-if="packageData.pdfs.length > 0" class="space-y-3">
              <h4 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <FileDown class="w-4 h-4 text-indigo-500" />
                Documents PDF ({{ packageData.pdfs.length }})
              </h4>
              <ul class="pl-6 space-y-2 border-l border-indigo-100 dark:border-slate-800">
                <li 
                  v-for="pdf in packageData.pdfs" 
                  :key="pdf"
                  class="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2 hover:text-indigo-500 transition-colors"
                >
                  <div class="w-1.5 h-1.5 rounded-full bg-indigo-500"></div>
                  {{ pdf }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../services/api'
import { 
  ChevronRight, 
  Folder, 
  GitFork, 
  Download, 
  Lock, 
  Layers, 
  FileText, 
  Activity, 
  FileDown 
} from '@lucide/vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const importing = ref(false)
const packageData = ref<any>(null)

const packageId = route.params.id as string

async function fetchPackagePreview() {
  loading.value = true
  try {
    const res = await api.get(`/packages/${packageId}`)
    packageData.value = res.data
  } catch (err) {
    console.error('Impossible de charger la preview', err)
    alert("Ce package n'existe pas ou n'est plus disponible.")
    router.push('/explore')
  } finally {
    loading.value = false
  }
}

async function handleImport() {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }

  importing.value = true
  try {
    await api.post(`/packages/${packageId}/clone`)
    alert('Pack d\'étude cloné avec succès dans vos classeurs !')
    router.push('/binders')
  } catch (err) {
    console.error('Erreur lors du clonage', err)
    alert('Impossible d\'importer le pack d\'études.')
  } finally {
    importing.value = false
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(() => {
  fetchPackagePreview()
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
