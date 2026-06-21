<template>
  <div class="space-y-20 py-10 animate-fade-in">
    <!-- Hero Section -->
    <section class="relative flex flex-col items-center text-center px-4 pt-10 pb-6 overflow-hidden">
      <!-- Halos décoratifs -->
      <div class="absolute -top-40 w-96 h-96 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="absolute -right-20 top-20 w-80 h-80 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>

      <!-- Badge -->
      <div class="inline-flex items-center gap-2 px-3 py-1 bg-primary-soft border border-primary/20 rounded-full text-xs font-bold text-primary mb-6 animate-pulse">
        <Sparkles class="w-3.5 h-3.5" />
        Découvrez la nouvelle façon d'étudier
      </div>

      <!-- Titre principal -->
      <h1 class="text-4xl md:text-6xl font-black tracking-tight max-w-4xl leading-tight text-ink">
        Propulsez votre apprentissage avec <span class="text-primary">StudyHub</span>
      </h1>

      <!-- Sous-titre -->
      <p class="text-base md:text-lg text-ink-muted mt-6 max-w-2xl leading-relaxed">
        L'application d'étude tout-en-un conçue pour les étudiants. Créez des fiches de révision intelligentes, dessinez des schémas interactifs, annotez vos PDF et étudiez avec la répétition espacée.
      </p>

      <!-- CTA -->
      <div class="flex flex-col sm:flex-row items-center gap-4 mt-10 w-full justify-center">
        <BaseButton size="lg" class="w-full sm:w-auto group" @click="goToDashboard">
          Démarrer gratuitement
          <ArrowRight class="w-4 h-4 transition-transform group-hover:translate-x-1" />
        </BaseButton>
        <BaseButton variant="secondary" size="lg" class="w-full sm:w-auto" @click="goToExplore">
          Découvrir les cours publics
          <Globe class="w-4 h-4 text-primary" />
        </BaseButton>
      </div>
    </section>

    <!-- Fonctionnalités clés -->
    <section class="max-w-6xl mx-auto px-4">
      <div class="text-center max-w-3xl mx-auto mb-16">
        <h2 class="text-2xl md:text-3xl font-extrabold tracking-tight text-ink">Une boîte à outils complète pour réussir</h2>
        <p class="text-sm text-ink-muted mt-2">Plus besoin d'éparpiller vos cours sur dix applications. Tout est centralisé et interconnecté.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <BaseCard
          v-for="f in features"
          :key="f.title"
          interactive
          class="group"
        >
          <div class="p-3.5 rounded-2xl w-fit mb-6" :class="f.iconClass">
            <component :is="f.icon" class="w-6 h-6" />
          </div>
          <h3 class="font-bold text-base text-ink transition-colors" :class="f.hoverClass">{{ f.title }}</h3>
          <p class="text-xs text-ink-muted mt-2 leading-relaxed">{{ f.desc }}</p>
        </BaseCard>
      </div>
    </section>

    <!-- Preuve sociale / stats -->
    <section class="bg-primary text-white rounded-3xl p-8 md:p-12 max-w-6xl mx-auto shadow-elev-primary">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center divide-y md:divide-y-0 md:divide-x divide-white/20">
        <div class="pt-6 md:pt-0">
          <p class="text-3xl md:text-4xl font-black">98%</p>
          <p class="text-xs text-white/80 mt-1 uppercase tracking-wider font-bold">Des étudiants améliorent leurs notes</p>
        </div>
        <div class="pt-6 md:pt-0">
          <p class="text-3xl md:text-4xl font-black">10x</p>
          <p class="text-xs text-white/80 mt-1 uppercase tracking-wider font-bold">Mémorisation plus rapide</p>
        </div>
        <div class="pt-6 md:pt-0">
          <p class="text-3xl md:text-4xl font-black">Gratuit</p>
          <p class="text-xs text-white/80 mt-1 uppercase tracking-wider font-bold">Sans engagement pour l'auto-apprentissage</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { BaseButton, BaseCard } from '../../components/ui/base'
import { Sparkles, ArrowRight, Brain, BookOpen, Activity, FileDown, Folder, Globe } from '@lucide/vue'

const router = useRouter()

// Cartes de fonctionnalités — accents via tokens (cat-*/sémantiques), pas de couleur brute.
const features = [
  { title: 'Flashcards & Répétition Espacée', icon: Brain, iconClass: 'bg-cat-deck-soft text-cat-deck', hoverClass: 'group-hover:text-cat-deck',
    desc: 'Mémorisez à long terme grâce à notre algorithme basé sur la méthode SM-2. Planification intelligente des cartes selon vos réponses.' },
  { title: 'Lecture Active', icon: BookOpen, iconClass: 'bg-success-soft text-success', hoverClass: 'group-hover:text-success',
    desc: 'Intégrez des questions à trous (clozes), des QCM ou des vrai/faux directement dans vos notes de cours et révisez-les instantanément.' },
  { title: "Masques d'Image (Occlusion)", icon: Activity, iconClass: 'bg-cat-diagram-soft text-cat-diagram', hoverClass: 'group-hover:text-cat-diagram',
    desc: "Masquez visuellement des schémas d'anatomie, des frises chronologiques ou des légendes de diagrammes pour les transformer en cartes de révision." },
  { title: 'Liaison de Documents PDF', icon: FileDown, iconClass: 'bg-cat-pdf-soft text-cat-pdf', hoverClass: 'group-hover:text-cat-pdf',
    desc: "Affichez vos notes de cours et vos PDF en écran partagé. Citez les passages importants d'un clic pour y revenir plus tard instantanément." },
  { title: 'Classeurs & Dossiers', icon: Folder, iconClass: 'bg-accent-soft text-accent', hoverClass: 'group-hover:text-accent',
    desc: 'Organisez vos cours avec une arborescence de dossiers claire. Regroupez notes, fiches de révision et diagrammes par matière ou par semestre.' },
  { title: 'Marketplace Communautaire', icon: Globe, iconClass: 'bg-info-soft text-info', hoverClass: 'group-hover:text-info',
    desc: 'Partagez vos classeurs de cours ou importez ceux de la communauté d\'un simple clic pour gagner du temps et profiter des synthèses collectives.' },
]

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
