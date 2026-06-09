<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Hero / Header Section -->
    <div class="p-8 bg-gradient-to-r from-indigo-500/10 via-purple-500/5 to-transparent border border-indigo-500/10 rounded-3xl dark:from-indigo-950/20 dark:border-indigo-900/30 text-center md:text-left">
      <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight">Marketplace d'Étude Communautaire 🌍</h1>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-2 max-w-2xl">
        Découvrez, importez et étudiez des classeurs complets partagés par d'autres étudiants. Cloner un pack réinitialise vos intervalles de révision (SM-2) pour démarrer à votre rythme.
      </p>
    </div>

    <!-- Search and Filter Bar -->
    <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-5 shadow-sm flex flex-col md:flex-row items-center gap-4 justify-between">
      <div class="relative w-full md:w-96">
        <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-450" />
        <input 
          type="text" 
          v-model="searchQuery"
          @input="onSearchInput"
          placeholder="Rechercher par matière, mot-clé, étiquette..."
          class="w-full pl-10 pr-4 py-2.5 text-xs bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 font-semibold"
        />
      </div>
      
      <div class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
        {{ pagination.total }} pack(s) disponible(s)
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <svg class="animate-spin h-6 w-6 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-xs font-semibold text-slate-400 uppercase tracking-widest">Recherche des packs...</span>
    </div>

    <!-- Packages Grid -->
    <div v-else>
      <div v-if="packages.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="pkg in packages" 
          :key="pkg.id"
          class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm flex flex-col justify-between hover:shadow-md hover:-translate-y-1 transition-all duration-200 group"
        >
          <div class="space-y-4">
            <!-- Header of card -->
            <div class="flex items-start justify-between gap-2">
              <div class="p-3 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-2xl">
                <Folder class="w-5 h-5" />
              </div>
              
              <!-- Fork count badge -->
              <div class="flex items-center gap-1 px-2.5 py-1 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700/50 text-[10px] font-bold text-slate-500">
                <GitFork class="w-3.5 h-3.5 text-indigo-500" />
                <span>{{ pkg.fork_count }}</span>
              </div>
            </div>

            <!-- Title & Description -->
            <div>
              <h3 class="font-bold text-base text-slate-850 dark:text-white line-clamp-1 group-hover:text-indigo-600 transition-colors">
                {{ pkg.name }}
              </h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                {{ pkg.description || 'Aucune description fournie.' }}
              </p>
            </div>

            <!-- Tags -->
            <div v-if="pkg.tags && pkg.tags.length > 0" class="flex flex-wrap gap-1.5 pt-1">
              <span 
                v-for="tag in pkg.tags" 
                :key="tag"
                class="px-2 py-0.5 text-[9px] font-extrabold rounded-lg bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 border border-indigo-100/50 dark:border-indigo-900/40 uppercase tracking-wider"
              >
                {{ tag }}
              </span>
            </div>
          </div>

          <!-- Card Footer & Actions -->
          <div class="border-t border-slate-50 dark:border-slate-800/60 mt-5 pt-4 flex items-center justify-between gap-4">
            <span class="text-[10px] text-slate-400 dark:text-slate-500 font-semibold uppercase tracking-wider">
              Partagé le {{ formatDate(pkg.created_at) }}
            </span>
            
            <button 
              @click="router.push(`/package/${pkg.id}`)"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all active:scale-95 shadow-md shadow-indigo-600/10 flex items-center gap-1"
            >
              Voir l'Aperçu
              <ChevronRight class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="border-2 border-dashed border-slate-200 dark:border-slate-850 rounded-3xl p-16 flex flex-col items-center justify-center text-center text-slate-400 bg-white dark:bg-slate-900">
        <FolderOpen class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
        <h4 class="font-bold text-slate-800 dark:text-slate-200">Aucun package trouvé</h4>
        <p class="text-xs mt-1">Essayez une autre recherche ou modifiez vos filtres.</p>
      </div>

      <!-- Pagination -->
      <div v-if="pagination.pages > 1" class="flex items-center justify-center gap-2 mt-8">
        <button 
          @click="changePage(pagination.page - 1)"
          :disabled="pagination.page === 1"
          class="p-2 border border-slate-200 dark:border-slate-800 rounded-xl disabled:opacity-50 hover:bg-slate-50 dark:hover:bg-slate-850 transition-colors"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        <span class="text-xs font-semibold text-slate-500">
          Page {{ pagination.page }} sur {{ pagination.pages }}
        </span>
        <button 
          @click="changePage(pagination.page + 1)"
          :disabled="pagination.page === pagination.pages"
          class="p-2 border border-slate-200 dark:border-slate-800 rounded-xl disabled:opacity-50 hover:bg-slate-50 dark:hover:bg-slate-850 transition-colors"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import { 
  Search, 
  Folder, 
  FolderOpen, 
  GitFork, 
  ChevronRight, 
  ChevronLeft 
} from '@lucide/vue'

const router = useRouter()
const searchQuery = ref('')
const loading = ref(false)
const packages = ref<any[]>([])

const pagination = ref({
  page: 1,
  per_page: 9,
  total: 0,
  pages: 0
})

let debounceTimer: any = null

function onSearchInput() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    pagination.value.page = 1
    fetchPackages()
  }, 300)
}

async function fetchPackages() {
  loading.value = true
  try {
    const res = await api.get('/packages', {
      params: {
        search: searchQuery.value || undefined,
        page: pagination.value.page,
        per_page: pagination.value.per_page
      }
    })
    packages.value = res.data.data
    pagination.value = res.data.pagination
  } catch (err) {
    console.error('Erreur de chargement des packages', err)
  } finally {
    loading.value = false
  }
}

function changePage(newPage: number) {
  pagination.value.page = newPage
  fetchPackages()
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(() => {
  fetchPackages()
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
