<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Hero / Header Section -->
    <div class="p-8 bg-gradient-to-r from-indigo-500/10 via-purple-500/5 to-transparent border border-indigo-500/10 rounded-3xl dark:from-indigo-950/20 dark:border-indigo-900/30 text-center md:text-left">
      <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight">Marketplace & Espace Communautaire 🌍</h1>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-2 max-w-2xl">
        Découvrez, importez des packs d'étude ou suivez en direct les cours publics des professeurs. En suivant un cours public, les mises à jour s'ajoutent automatiquement à vos révisions !
      </p>
    </div>

    <!-- Search and Filter Bar -->
    <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-5 shadow-sm flex flex-col md:flex-row items-center gap-4 justify-between">
      <div class="flex gap-2 w-full md:w-auto">
        <button 
          @click="switchCategory('packages')"
          :class="[
            'px-4 py-2.5 rounded-xl text-xs font-bold transition-all',
            activeCategory === 'packages'
              ? 'bg-indigo-650 text-white shadow-md shadow-indigo-650/15'
              : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-350 hover:bg-slate-100 dark:hover:bg-slate-750'
          ]"
        >
          Packs d'Étude 📚
        </button>
        <button 
          @click="switchCategory('classes')"
          :class="[
            'px-4 py-2.5 rounded-xl text-xs font-bold transition-all',
            activeCategory === 'classes'
              ? 'bg-indigo-650 text-white shadow-md shadow-indigo-650/15'
              : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-350 hover:bg-slate-100 dark:hover:bg-slate-750'
          ]"
        >
          Cours Publics (Professeurs) 🎓
        </button>
      </div>

      <div class="relative w-full md:w-72">
        <Search class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input 
          type="text" 
          v-model="searchQuery"
          @input="onSearchInput"
          :placeholder="activeCategory === 'packages' ? 'Rechercher un pack...' : 'Rechercher un cours public...'"
          class="w-full pl-10 pr-4 py-2.5 text-xs bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 font-semibold"
        />
      </div>
      
      <div class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
        {{ pagination.total }} {{ activeCategory === 'packages' ? 'pack(s)' : 'cours' }} disponible(s)
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <Loader2 class="animate-spin h-6 w-6 text-indigo-600" />
      <span class="text-xs font-semibold text-slate-400 uppercase tracking-widest">Recherche en cours...</span>
    </div>

    <!-- Packages / Classes Grid -->
    <div v-else>
      <!-- Mode Packages -->
      <div v-if="activeCategory === 'packages'">
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
                  <span>{{ pkg.fork_count }} clones</span>
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

        <!-- Empty State Binders -->
        <div v-else class="border-2 border-dashed border-slate-200 dark:border-slate-850 rounded-3xl p-16 flex flex-col items-center justify-center text-center text-slate-400 bg-white dark:bg-slate-900">
          <FolderOpen class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
          <h4 class="font-bold text-slate-800 dark:text-slate-200">Aucun package trouvé</h4>
          <p class="text-xs mt-1">Essayez une autre recherche ou modifiez vos filtres.</p>
        </div>
      </div>

      <!-- Mode Classes -->
      <div v-else-if="activeCategory === 'classes'">
        <div v-if="publicClasses.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="cls in publicClasses" 
            :key="cls.id"
            class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm flex flex-col justify-between hover:shadow-md hover:-translate-y-1 transition-all duration-200 group"
          >
            <div class="space-y-4">
              <!-- Header of class card -->
              <div class="flex items-start justify-between gap-2">
                <div class="p-3 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-2xl">
                  <GraduationCap class="w-5 h-5" />
                </div>
                
                <!-- Student / Follower count -->
                <div class="flex items-center gap-1 px-2.5 py-1 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-100 dark:border-slate-700/50 text-[10px] font-bold text-slate-500">
                  <Users class="w-3.5 h-3.5 text-indigo-500" />
                  <span>{{ cls.members_count }} abonnés</span>
                </div>
              </div>

              <!-- Title & Description -->
              <div>
                <h3 class="font-bold text-base text-slate-850 dark:text-white line-clamp-1 group-hover:text-indigo-600 transition-colors">
                  {{ cls.name }}
                </h3>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                  {{ cls.description || 'Aucune description fournie.' }}
                </p>
              </div>
            </div>

            <!-- Card Footer & Actions -->
            <div class="border-t border-slate-50 dark:border-slate-800/60 mt-5 pt-4 flex items-center justify-between gap-4">
              <span class="text-[10px] text-slate-400 dark:text-slate-500 font-semibold uppercase tracking-wider">
                Créé le {{ formatDate(cls.created_at) }}
              </span>
              
              <button 
                @click="followClass(cls.id)"
                :disabled="followingStates[cls.id] === 'loading' || followingStates[cls.id] === 'done'"
                :class="[
                  'px-4 py-2 text-white rounded-xl text-xs font-bold transition-all active:scale-95 shadow-md flex items-center gap-1',
                  followingStates[cls.id] === 'done'
                    ? 'bg-emerald-600 shadow-emerald-600/10'
                    : 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-600/10'
                ]"
              >
                <Loader2 v-if="followingStates[cls.id] === 'loading'" class="w-3.5 h-3.5 animate-spin" />
                <Check v-else-if="followingStates[cls.id] === 'done'" class="w-3.5 h-3.5" />
                <Plus v-else class="w-3.5 h-3.5" />
                
                <span>{{ followingStates[cls.id] === 'done' ? 'Suivi' : (followingStates[cls.id] === 'loading' ? 'En cours...' : 'Suivre le cours') }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State Classes -->
        <div v-else class="border-2 border-dashed border-slate-200 dark:border-slate-850 rounded-3xl p-16 flex flex-col items-center justify-center text-center text-slate-400 bg-white dark:bg-slate-900">
          <GraduationCap class="w-12 h-12 text-slate-300 dark:text-slate-700 mb-3" />
          <h4 class="font-bold text-slate-800 dark:text-slate-200">Aucun cours public trouvé</h4>
          <p class="text-xs mt-1">Revenez plus tard ou recherchez d'autres matières.</p>
        </div>
      </div>

      <!-- Pagination (Packages mode only) -->
      <div v-if="activeCategory === 'packages' && pagination.pages > 1" class="flex items-center justify-center gap-2 mt-8">
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
import classService from '../../services/classService'
import type { ClassInfo } from '../../services/classService'
import { 
  Search, 
  Folder, 
  FolderOpen, 
  GitFork, 
  ChevronRight, 
  ChevronLeft,
  GraduationCap,
  Users,
  Check,
  Plus,
  Loader2
} from 'lucide-vue-next'

const router = useRouter()
const searchQuery = ref('')
const loading = ref(false)
const activeCategory = ref<'packages' | 'classes'>('packages')

const packages = ref<any[]>([])
const publicClasses = ref<ClassInfo[]>([])

const pagination = ref({
  page: 1,
  per_page: 9,
  total: 0,
  pages: 0
})

const followingStates = ref<Record<number, 'idle' | 'loading' | 'done'>>({})

let debounceTimer: any = null

function onSearchInput() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    pagination.value.page = 1
    fetchData()
  }, 300)
}

function switchCategory(cat: 'packages' | 'classes') {
  activeCategory.value = cat
  searchQuery.value = ''
  pagination.value.page = 1
  fetchData()
}

async function fetchData() {
  if (activeCategory.value === 'packages') {
    await fetchPackages()
  } else {
    await fetchClasses()
  }
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

async function fetchClasses() {
  loading.value = true
  try {
    const res = await classService.getPublicClasses(searchQuery.value)
    publicClasses.value = res
    pagination.value = {
      page: 1,
      per_page: 999,
      total: res.length,
      pages: 1
    }
  } catch (err) {
    console.error('Erreur de chargement des classes publiques', err)
  } finally {
    loading.value = false
  }
}

function changePage(newPage: number) {
  pagination.value.page = newPage
  fetchData()
}

async function followClass(classId: number) {
  followingStates.value[classId] = 'loading'
  try {
    await classService.followClass(classId)
    followingStates.value[classId] = 'done'
    await fetchClasses()
  } catch (err) {
    console.error('Erreur lors du follow de la classe', err)
    followingStates.value[classId] = 'idle'
  }
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(() => {
  fetchData()
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
