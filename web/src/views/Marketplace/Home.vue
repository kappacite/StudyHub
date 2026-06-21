<template>
  <div class="space-y-20 py-10 animate-fade-in">
    <!-- Hero Section -->
    <section class="relative flex flex-col items-center text-center px-4 pt-10 pb-6 overflow-hidden">
      <!-- Background glowing gradient circles -->
      <div class="absolute -top-40 w-96 h-96 bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -right-20 top-20 w-80 h-80 bg-purple-500/10 dark:bg-purple-500/5 rounded-full blur-3xl pointer-events-none"></div>
      
      <!-- Sparkles Badge -->
      <div class="inline-flex items-center gap-2 px-3 py-1 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100/50 dark:border-indigo-900/30 rounded-full text-xs font-bold text-indigo-600 dark:text-indigo-400 mb-6 animate-pulse">
        <Sparkles class="w-3.5 h-3.5" />
        Découvrez la nouvelle façon d'étudier
      </div>

      <!-- Main Headline -->
      <h1 class="text-4xl md:text-6xl font-black tracking-tight max-w-4xl leading-tight bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 dark:from-white dark:via-indigo-100 dark:to-white bg-clip-text text-transparent">
        Propulsez votre apprentissage avec <span class="bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600 bg-clip-text text-transparent">StudyHub</span>
      </h1>
      
      <!-- Sub-headline -->
      <p class="text-base md:text-lg text-slate-500 dark:text-slate-400 mt-6 max-w-2xl leading-relaxed">
        L'application d'étude tout-en-un conçue pour les étudiants. Créez des fiches de révision intelligentes, dessinez des schémas interactifs, annotez vos PDF et étudiez avec la répétition espacée.
      </p>

      <!-- CTA Buttons -->
      <div class="flex flex-col sm:flex-row items-center gap-4 mt-10 w-full justify-center">
        <button 
          @click="goToDashboard"
          class="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-2xl text-sm font-extrabold shadow-lg shadow-indigo-500/25 hover:shadow-xl hover:shadow-indigo-500/30 active:scale-95 transition-all flex items-center justify-center gap-2 group"
        >
          Démarrer gratuitement
          <ArrowRight class="w-4 h-4 transition-transform group-hover:translate-x-1" />
        </button>
        <button 
          @click="goToExplore"
          class="w-full sm:w-auto px-8 py-3.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-250 rounded-2xl text-sm font-bold hover:bg-slate-50 dark:hover:bg-slate-850 active:scale-95 transition-all flex items-center justify-center gap-2"
        >
          Découvrir les cours publics
          <Globe class="w-4 h-4 text-indigo-500" />
        </button>
      </div>
    </section>

    <!-- Key Features Grid -->
    <section class="max-w-6xl mx-auto px-4">
      <div class="text-center max-w-3xl mx-auto mb-16">
        <h2 class="text-2xl md:text-3xl font-extrabold tracking-tight">Une boîte à outils complète pour réussir</h2>
        <p class="text-sm text-slate-400 dark:text-slate-500 mt-2">Plus besoin d'éparpiller vos cours sur dix applications. Tout est centralisé et interconnecté.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <!-- Feature 1: Flashcards -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200 group">
          <div class="p-3.5 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-2xl w-fit mb-6">
            <Brain class="w-6 h-6" />
          </div>
          <h3 class="font-bold text-base text-slate-850 dark:text-white group-hover:text-indigo-600 transition-colors">Flashcards & Répétition Espacée</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
            Mémorisez à long terme grâce à notre algorithme basé sur la méthode SM-2. Planification intelligente des cartes selon vos réponses.
          </p>
        </div>

        <!-- Feature 2: Active Reading -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200 group">
          <div class="p-3.5 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-450 rounded-2xl w-fit mb-6">
            <BookOpen class="w-6 h-6" />
          </div>
          <h3 class="font-bold text-base text-slate-850 dark:text-white group-hover:text-emerald-600 transition-colors">Lecture Active</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
            Intégrez des questions à trous (clozes), des QCM ou des vrai/faux directement dans vos notes de cours et révisez-les instantanément.
          </p>
        </div>

        <!-- Feature 3: Image Occlusion -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200 group">
          <div class="p-3.5 bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 rounded-2xl w-fit mb-6">
            <Activity class="w-6 h-6" />
          </div>
          <h3 class="font-bold text-base text-slate-850 dark:text-white group-hover:text-purple-600 transition-colors">Masques d'Image (Occlusion)</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
            Masquez visuellement des schémas d'anatomie, des frises chronologiques ou des légendes de diagrammes pour les transformer en cartes de révision.
          </p>
        </div>

        <!-- Feature 4: PDF Deep-Linking -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200 group">
          <div class="p-3.5 bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 rounded-2xl w-fit mb-6">
            <FileDown class="w-6 h-6" />
          </div>
          <h3 class="font-bold text-base text-slate-850 dark:text-white group-hover:text-rose-600 transition-colors">Liaison de Documents PDF</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
            Affichez vos notes de cours et vos PDF en écran partagé. Citez les passages importants d'un clic pour y revenir plus tard instantanément.
          </p>
        </div>

        <!-- Feature 5: Classeurs Structurés -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200 group">
          <div class="p-3.5 bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 rounded-2xl w-fit mb-6">
            <Folder class="w-6 h-6" />
          </div>
          <h3 class="font-bold text-base text-slate-850 dark:text-white group-hover:text-amber-600 transition-colors">Classeurs & Dossiers</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
            Organisez vos cours avec une arborescence de dossiers claire. Regroupez notes, fiches de révision et diagrammes par matière ou par semestre.
          </p>
        </div>

        <!-- Feature 6: Marketplace -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200 group">
          <div class="p-3.5 bg-cyan-50 dark:bg-cyan-950/40 text-cyan-600 dark:text-cyan-400 rounded-2xl w-fit mb-6">
            <Globe class="w-6 h-6" />
          </div>
          <h3 class="font-bold text-base text-slate-850 dark:text-white group-hover:text-cyan-600 transition-colors">Marketplace Communautaire</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">
            Partagez vos classeurs de cours ou importez ceux de la communauté d'un simple clic pour gagner du temps et profiter des synthèses collectives.
          </p>
        </div>
      </div>
    </section>

    <!-- Social Proof / Stats Section -->
    <section class="bg-indigo-600 text-white rounded-3xl p-8 md:p-12 max-w-6xl mx-auto shadow-xl shadow-indigo-600/10">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center divide-y md:divide-y-0 md:divide-x divide-indigo-500/40">
        <div class="pt-6 md:pt-0">
          <p class="text-3xl md:text-4xl font-black">98%</p>
          <p class="text-xs text-indigo-200 mt-1 uppercase tracking-wider font-bold">Des étudiants améliorent leurs notes</p>
        </div>
        <div class="pt-6 md:pt-0">
          <p class="text-3xl md:text-4xl font-black">10x</p>
          <p class="text-xs text-indigo-200 mt-1 uppercase tracking-wider font-bold">Mémorisation plus rapide</p>
        </div>
        <div class="pt-6 md:pt-0">
          <p class="text-3xl md:text-4xl font-black">Gratuit</p>
          <p class="text-xs text-indigo-200 mt-1 uppercase tracking-wider font-bold">Sans engagement pour l'auto-apprentissage</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Sparkles, ArrowRight, Brain, BookOpen, Activity, FileDown, Folder, Globe } from '@lucide/vue'

const router = useRouter()

function goToDashboard() {
  router.push('/accueil')
}

function goToExplore() {
  router.push('/explore')
}
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
