<template>
  <div class="space-y-8 animate-fade-in pb-16">
    <!-- Header Page -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 bg-gradient-to-r from-indigo-500/10 via-purple-500/5 to-transparent border border-indigo-500/10 rounded-3xl dark:from-indigo-950/20 dark:border-indigo-900/30">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Espace Révisions 🧠</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Multipliez l'efficacité de votre apprentissage grâce aux meilleures techniques cognitives.</p>
      </div>
      
      <!-- Tab selectors -->
      <div class="flex flex-wrap p-1 bg-slate-100 dark:bg-slate-800 rounded-2xl gap-1">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-4 py-2 text-xs font-bold rounded-xl transition-all"
          :class="[
            activeTab === tab.id 
              ? 'bg-white text-indigo-600 shadow-sm dark:bg-slate-700 dark:text-white' 
              : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200'
          ]"
        >
          {{ tab.name }}
        </button>
      </div>
    </div>

    <!-- Active Tab Panel -->
    <div class="transition-all duration-300">
      
      <!-- TAB 1: FLASHCARDS (ESPACEMENT SM-2) -->
      <div v-if="activeTab === 'flashcards'" class="space-y-6">
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <div class="flex items-center justify-between mb-6 flex-wrap gap-4 border-b border-slate-100 dark:border-slate-850/60 pb-4">
            <div>
              <h2 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
                <Layers class="w-5 h-5 text-indigo-500" />
                Decks de Répétition Espacée
              </h2>
              <p class="text-xs text-slate-400 mt-1">L'algorithme SM-2 calcule automatiquement la prochaine date de révision pour maximiser votre rétention.</p>
            </div>
            
            <button 
              @click="openGenerateModal"
              class="inline-flex items-center gap-2 px-4 py-2.5 text-xs font-bold text-white bg-indigo-650 hover:bg-indigo-700 rounded-xl transition-all shadow-md active:scale-95 duration-200"
            >
              <Sparkles class="w-4 h-4 text-amber-400 animate-pulse" />
              Générer depuis Notes / Classeurs
            </button>
          </div>
          
          <div v-if="decksLoading" class="flex items-center justify-center py-12">
            <svg class="animate-spin h-6 w-6 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div 
              v-for="deck in decksWithStats" 
              :key="deck.id"
              class="flex flex-col justify-between p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/20 border border-slate-100 dark:border-slate-800/80 hover:shadow-md transition-all group"
            >
              <div>
                <div class="flex items-start justify-between">
                  <h3 class="font-bold text-base text-slate-800 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate max-w-[200px]">
                    {{ deck.name }}
                  </h3>
                  
                  <span 
                    class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                    :class="deck.due_count > 0 ? 'bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-450' : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-450'"
                  >
                    {{ deck.due_count > 0 ? `${deck.due_count} À réviser` : 'À jour' }}
                  </span>
                </div>
                
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 line-clamp-2 min-h-[32px]">
                  {{ deck.description || 'Aucune description fournie.' }}
                </p>

                <div class="flex items-center gap-2 mt-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  <span>{{ deck.card_count }} carte(s)</span>
                  <span>•</span>
                  <span>Rétention : {{ deck.retention_rate }}%</span>
                </div>
              </div>

              <div class="flex gap-2 mt-6">
                <button 
                  @click="router.push(`/decks/${deck.id}/study`)"
                  class="flex-1 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all text-center shadow-sm shadow-indigo-600/10 hover:shadow-indigo-600/20 active:scale-[0.98]"
                >
                  {{ deck.due_count > 0 ? 'Réviser maintenant' : 'Révision libre' }}
                </button>
                <button 
                  @click="router.push('/decks')"
                  class="px-3 py-2 text-xs font-bold text-slate-600 hover:text-indigo-600 bg-white hover:bg-slate-100 border border-slate-200 dark:bg-slate-800 dark:text-slate-350 dark:border-slate-700 dark:hover:bg-slate-750 rounded-xl transition-all"
                  title="Gérer les cartes"
                >
                  Gérer
                </button>
              </div>
            </div>

            <div 
              v-if="decksStore.decks.length === 0" 
              class="col-span-full text-center py-12 bg-slate-50 dark:bg-slate-850/20 border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl"
            >
              <Layers class="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p class="text-sm font-semibold text-slate-500">Aucun deck de flashcards disponible</p>
              <button 
                @click="router.push('/decks')" 
                class="mt-4 px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl active:scale-95 transition-all"
              >
                Créer un deck
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: FEUILLE BLANCHE -->
      <div v-if="activeTab === 'blank-sheet'" class="space-y-6">
        <!-- Step 1: Configuration -->
        <div v-if="blankSheetStep === 'config'" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm max-w-2xl mx-auto">
          <h2 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-2">
            <FileText class="w-5 h-5 text-indigo-500" />
            Méthode de la Feuille Blanche
          </h2>
          <p class="text-xs text-slate-400 mb-6">
            Cette technique d'Active Recall consiste à écrire de mémoire tout ce dont vous vous souvenez sur un sujet, puis à le confronter au cours original pour identifier immédiatement vos lacunes.
          </p>

          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Source de révision</label>
              <div class="grid grid-cols-2 gap-4">
                <button 
                  @click="blankSheetSourceType = 'note'"
                  class="p-4 border rounded-2xl text-center font-semibold text-sm transition-all"
                  :class="[blankSheetSourceType === 'note' ? 'border-indigo-600 bg-indigo-50/50 text-indigo-600 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850/40']"
                >
                  Une Note Individuelle
                </button>
                <button 
                  @click="blankSheetSourceType = 'binder'"
                  class="p-4 border rounded-2xl text-center font-semibold text-sm transition-all"
                  :class="[blankSheetSourceType === 'binder' ? 'border-indigo-600 bg-indigo-50/50 text-indigo-600 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850/40']"
                >
                  Un Classeur entier
                </button>
              </div>
            </div>

            <!-- Note Selector -->
            <div v-if="blankSheetSourceType === 'note'">
              <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Sélectionnez la note</label>
              <select 
                v-model="selectedNoteId"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold transition-all"
              >
                <option :value="null" disabled>Choisir une note...</option>
                <option v-for="note in notesStore.notes" :key="note.id" :value="note.id">
                  {{ note.title }}
                </option>
              </select>
            </div>

            <!-- Binder Selector -->
            <div v-if="blankSheetSourceType === 'binder'">
              <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Sélectionnez le classeur</label>
              <select 
                v-model="selectedBinderId"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold transition-all"
              >
                <option :value="null" disabled>Choisir un classeur...</option>
                <option v-for="binder in bindersStore.binders" :key="binder.id" :value="binder.id">
                  {{ binder.name }}
                </option>
              </select>
            </div>

            <button 
              @click="startBlankSheet"
              :disabled="!isReadyToStartBlankSheet"
              class="w-full py-3 mt-4 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all shadow-md shadow-indigo-650/10 active:scale-[0.98]"
            >
              Démarrer la feuille blanche
            </button>
          </div>
        </div>

        <!-- Step 2: Recall Draft Work -->
        <div v-if="blankSheetStep === 'work'" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-6">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-850/60 pb-4">
            <div>
              <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-wider">Révision en cours : Feuille Blanche</span>
              <h2 class="text-lg font-bold">{{ blankSheetSubjectTitle }}</h2>
            </div>
            
            <div class="flex items-center gap-4 text-xs font-bold">
              <span class="text-slate-400">Mots saisis : {{ blankSheetWordCount }}</span>
              <span class="px-3 py-1 bg-rose-50 text-rose-600 dark:bg-rose-950/20 dark:text-rose-400 rounded-lg">
                Temps : {{ formatTimer(blankSheetTimer) }}
              </span>
            </div>
          </div>

          <textarea 
            v-model="blankSheetDraft"
            placeholder="Écrivez de mémoire tout ce que vous avez retenu sur le sujet..."
            rows="12"
            class="w-full p-6 text-sm border border-slate-200 dark:border-slate-800 rounded-2xl bg-slate-50/50 dark:bg-slate-850 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none font-sans leading-relaxed"
          ></textarea>

          <div class="flex gap-4">
            <button 
              @click="cancelReview"
              class="px-5 py-2.5 text-xs font-bold text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
            >
              Abandonner
            </button>
            <button 
              @click="evaluateBlankSheet"
              :disabled="!blankSheetDraft.trim()"
              class="flex-1 py-3 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-xl transition-all shadow-md active:scale-95"
            >
              Évaluer ma mémoire
            </button>
          </div>
        </div>

        <!-- Step 3: Interactive Results -->
        <div v-if="blankSheetStep === 'results'" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-8">
          <div class="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-100 dark:border-slate-850/60 pb-6 gap-6">
            <div>
              <span class="text-[10px] font-bold text-emerald-500 uppercase tracking-wider">Résultats de la révision</span>
              <h2 class="text-lg font-bold">{{ blankSheetSubjectTitle }}</h2>
              <p class="text-xs text-slate-400 mt-1">Étudié pendant {{ formatTimer(blankSheetTimer) }}.</p>
            </div>

            <!-- Radial Progress Badge -->
            <div class="flex items-center gap-4">
              <div class="relative w-16 h-16 rounded-full flex items-center justify-center bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400 font-extrabold text-lg border border-indigo-150/40">
                {{ blankSheetResult.score }}%
              </div>
              <div>
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Taux de rappel</p>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {{ blankSheetResult.remembered.length }} / {{ blankSheetResult.totalKeywords }} concepts clés retrouvés.
                </p>
              </div>
            </div>
          </div>

          <!-- Breakdown list -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Remembered -->
            <div class="p-5 rounded-2xl bg-emerald-50/30 border border-emerald-100 dark:bg-emerald-950/10 dark:border-emerald-900/30 space-y-3">
              <h3 class="text-xs font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 class="w-4 h-4 text-emerald-500" />
                Concepts Retenus ({{ blankSheetResult.remembered.length }})
              </h3>
              <div class="flex flex-wrap gap-1.5 pt-1">
                <span 
                  v-for="kw in blankSheetResult.remembered" 
                  :key="kw"
                  class="px-2.5 py-0.5 bg-white border border-emerald-200 text-emerald-700 dark:bg-emerald-900/10 dark:border-emerald-800/40 dark:text-emerald-450 text-[11px] font-semibold rounded-lg"
                >
                  {{ kw }}
                </span>
                <span v-if="blankSheetResult.remembered.length === 0" class="text-xs text-slate-400 font-medium">Aucun concept clé n'a été mémorisé.</span>
              </div>
            </div>

            <!-- Missed -->
            <div class="p-5 rounded-2xl bg-rose-50/30 border border-rose-100 dark:bg-rose-950/10 dark:border-rose-900/30 space-y-3">
              <h3 class="text-xs font-bold text-rose-800 dark:text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                <Flame class="w-4 h-4 text-rose-500" />
                Lacunes identifiées ({{ blankSheetResult.missed.length }})
              </h3>
              <div class="flex flex-wrap gap-1.5 pt-1">
                <span 
                  v-for="kw in blankSheetResult.missed" 
                  :key="kw"
                  class="px-2.5 py-0.5 bg-white border border-rose-200 text-rose-700 dark:bg-rose-900/10 dark:border-rose-800/40 dark:text-rose-450 text-[11px] font-semibold rounded-lg"
                >
                  {{ kw }}
                </span>
                <span v-if="blankSheetResult.missed.length === 0" class="text-xs text-slate-400 font-medium">Parfait ! Vous n'avez oublié aucun concept clé. 🎉</span>
              </div>
            </div>
          </div>

          <!-- Comparative Text View (Original text diff style) -->
          <div class="space-y-3">
            <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Analyse visuelle du document original
            </h3>
            <p class="text-xs text-slate-400">Les concepts clés oubliés sont <span class="bg-rose-100 text-rose-800 dark:bg-rose-950/50 dark:text-rose-350 px-1 rounded font-bold">surlignés en rouge</span>. Les concepts retenus sont <span class="bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-350 px-1 rounded font-bold">en vert</span>.</p>
            
            <div 
              class="w-full p-6 bg-slate-50 dark:bg-slate-850/50 border border-slate-200 dark:border-slate-800 rounded-2xl text-sm leading-relaxed whitespace-pre-line font-sans"
              v-html="blankSheetResult.highlightedText"
            ></div>
          </div>

          <button 
            @click="blankSheetStep = 'config'"
            class="px-6 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all shadow-md active:scale-95"
          >
            Faire une autre révision
          </button>
        </div>
      </div>

      <!-- TAB 3: METHODE FEYNMAN -->
      <div v-if="activeTab === 'feynman'" class="space-y-6">
        <!-- Step 1: Configuration -->
        <div v-if="feynmanStep === 'config'" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm max-w-2xl mx-auto">
          <h2 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-2">
            <Sparkles class="w-5 h-5 text-indigo-500" />
            Méthode Feynman
          </h2>
          <p class="text-xs text-slate-400 mb-6">
            La meilleure façon de comprendre un concept est de l'expliquer le plus simplement possible, comme si vous parliez à un enfant de 10 ans. Cette méthode met en évidence les points d'ombre de votre compréhension.
          </p>

          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Sélectionnez la note / concept</label>
              <select 
                v-model="selectedNoteId"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold transition-all"
              >
                <option :value="null" disabled>Choisir une note...</option>
                <option v-for="note in notesStore.notes" :key="note.id" :value="note.id">
                  {{ note.title }}
                </option>
              </select>
            </div>

            <button 
              @click="startFeynman"
              :disabled="selectedNoteId === null"
              class="w-full py-3 mt-4 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-xl transition-all shadow-md active:scale-95"
            >
              Lancer l'exercice de simplification
            </button>
          </div>
        </div>

        <!-- Step 2: Work Draft -->
        <div v-if="feynmanStep === 'work'" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-6">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-850/60 pb-4">
            <div>
              <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-wider">Exercice Feynman : Expliquer simplement</span>
              <h2 class="text-lg font-bold">{{ feynmanSubjectTitle }}</h2>
            </div>
            
            <div class="flex items-center gap-4 text-xs font-bold">
              <span class="text-slate-400">Mots : {{ feynmanWordCount }}</span>
              <span class="px-3 py-1 bg-rose-50 text-rose-600 dark:bg-rose-950/20 dark:text-rose-400 rounded-lg">
                Temps : {{ formatTimer(feynmanTimer) }}
              </span>
            </div>
          </div>

          <div class="p-4 bg-indigo-50/50 border-l-4 border-indigo-500 rounded-r-xl dark:bg-indigo-950/15 dark:border-indigo-900/40 text-xs leading-relaxed text-indigo-800 dark:text-indigo-400">
            <strong>Consigne :</strong> Décrivez ce concept avec vos propres mots en évitant les termes techniques trop complexes. Soyez clair, concis et illustrez votre explication par une métaphore ou un exemple simple.
          </div>

          <textarea 
            v-model="feynmanDraft"
            placeholder="Tapez votre explication simplifiée ici..."
            rows="10"
            class="w-full p-6 text-sm border border-slate-200 dark:border-slate-800 rounded-2xl bg-slate-50/50 dark:bg-slate-850 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none font-sans leading-relaxed"
          ></textarea>

          <div class="flex gap-4">
            <button 
              @click="cancelReview"
              class="px-5 py-2.5 text-xs font-bold text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
            >
              Abandonner
            </button>
            <button 
              @click="evaluateFeynman"
              :disabled="!feynmanDraft.trim()"
              class="flex-1 py-3 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-xl transition-all shadow-md active:scale-95"
            >
              Analyser mon explication
            </button>
          </div>
        </div>

        <!-- Step 3: Feedback Results -->
        <div v-if="feynmanStep === 'results'" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-8">
          <div class="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-100 dark:border-slate-850/60 pb-6 gap-6">
            <div>
              <span class="text-[10px] font-bold text-purple-500 uppercase tracking-wider">Analyse Feynman</span>
              <h2 class="text-lg font-bold">{{ feynmanSubjectTitle }}</h2>
              <p class="text-xs text-slate-400 mt-1">Soumis en {{ formatTimer(feynmanTimer) }}.</p>
            </div>

            <!-- Feynman Score -->
            <div class="flex items-center gap-4">
              <div class="relative w-16 h-16 rounded-full flex items-center justify-center bg-purple-50 dark:bg-purple-950/20 text-purple-600 dark:text-purple-400 font-extrabold text-lg border border-purple-150/40">
                {{ feynmanResult.score }}%
              </div>
              <div>
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Score de Simplicité</p>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Votre explication est claire et accessible.
                </p>
              </div>
            </div>
          </div>

          <!-- Evaluation Cards -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Jargon alert -->
            <div class="p-5 rounded-2xl border space-y-2" :class="[feynmanResult.jargonFound.length > 0 ? 'bg-amber-50/30 border-amber-100 dark:bg-amber-950/10 dark:border-amber-900/30' : 'bg-emerald-50/30 border-emerald-100 dark:bg-emerald-950/10 dark:border-emerald-900/30']">
              <h4 class="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5" :class="[feynmanResult.jargonFound.length > 0 ? 'text-amber-800 dark:text-amber-400' : 'text-emerald-800 dark:text-emerald-400']">
                <Compass class="w-4.5 h-4.5" />
                Mots complexes
              </h4>
              <p class="text-xs text-slate-400">Nombre de termes complexes ou de jargon conservés de la note d'origine.</p>
              <div v-if="feynmanResult.jargonFound.length > 0" class="flex flex-wrap gap-1 mt-2">
                <span v-for="w in feynmanResult.jargonFound" :key="w" class="px-2 py-0.5 bg-amber-50 dark:bg-amber-900/10 text-amber-600 text-[10px] font-semibold rounded-lg">{{ w }}</span>
              </div>
              <p v-else class="text-xs font-semibold text-emerald-600 mt-2">Félicitations ! Aucun mot complexe ou jargon repéré.</p>
            </div>

            <!-- Length check -->
            <div class="p-5 rounded-2xl bg-indigo-50/30 border border-indigo-100 dark:bg-indigo-950/10 dark:border-indigo-900/30 space-y-2">
              <h4 class="text-xs font-bold text-indigo-800 dark:text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                <Clock class="w-4.5 h-4.5 text-indigo-500" />
                Concision
              </h4>
              <p class="text-xs text-slate-400">Longueur idéale pour vulgariser : entre 50 et 150 mots.</p>
              <p class="text-sm font-bold text-slate-800 dark:text-white mt-3">
                Votre longueur : {{ feynmanWordCount }} mots
              </p>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold text-indigo-600 bg-indigo-50/50 dark:bg-indigo-900/20 uppercase tracking-wider mt-1 inline-block">
                {{ feynmanResult.lengthFeedback }}
              </span>
            </div>

            <!-- Suggestions -->
            <div class="p-5 rounded-2xl bg-slate-50 border border-slate-200 dark:bg-slate-850/50 dark:border-slate-800 space-y-2">
              <h4 class="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles class="w-4.5 h-4.5 text-indigo-500" />
                Suggestion
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed mt-2">
                {{ feynmanResult.suggestion }}
              </p>
            </div>
          </div>

          <button 
            @click="feynmanStep = 'config'"
            class="px-6 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all shadow-md active:scale-95"
          >
            Faire une autre révision
          </button>
        </div>
      </div>

      <!-- TAB 4: AUTO-QCM -->
      <div v-if="activeTab === 'quiz'" class="space-y-6">
        <!-- Step 1: Configuration -->
        <div v-if="quizStep === 'config'" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm max-w-2xl mx-auto">
          <h2 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2 mb-2">
            <Activity class="w-5 h-5 text-indigo-500" />
            Générateur de Quiz Interactif
          </h2>
          <p class="text-xs text-slate-400 mb-6">
            Entraînez-vous activement. Le système analyse le texte de la note sélectionnée pour extraire les concepts clés et générer des questions à choix multiples.
          </p>

          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Sélectionnez la note</label>
              <select 
                v-model="selectedNoteId"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-semibold transition-all"
              >
                <option :value="null" disabled>Choisir une note...</option>
                <option v-for="note in notesStore.notes" :key="note.id" :value="note.id">
                  {{ note.title }}
                </option>
              </select>
            </div>

            <button 
              @click="startQuiz"
              :disabled="selectedNoteId === null"
              class="w-full py-3 mt-4 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-xl transition-all shadow-md active:scale-95"
            >
              Générer mon Quiz
            </button>
          </div>
        </div>

        <!-- Step 2: Quiz Session -->
        <div v-if="quizStep === 'work'" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-8 max-w-3xl mx-auto">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-850/60 pb-4">
            <div>
              <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-wider">Quiz actif : {{ quizSubjectTitle }}</span>
              <h2 class="text-base font-bold">Répondez aux questions</h2>
            </div>
            
            <span class="px-3 py-1 bg-indigo-55 text-indigo-600 dark:bg-indigo-950/20 dark:text-indigo-400 text-xs font-bold rounded-lg">
              {{ quizQuestions.length }} Question(s)
            </span>
          </div>

          <div class="space-y-8">
            <div 
              v-for="(q, qIdx) in quizQuestions" 
              :key="qIdx"
              class="p-5 bg-slate-50 dark:bg-slate-850/50 border border-slate-200 dark:border-slate-800 rounded-2xl space-y-4"
            >
              <h3 class="font-bold text-sm leading-relaxed text-slate-800 dark:text-slate-200">
                Question {{ qIdx + 1 }} : {{ q.questionText }}
              </h3>

              <div class="grid grid-cols-1 gap-2.5">
                <button 
                  v-for="(opt, optIdx) in q.options" 
                  :key="optIdx"
                  @click="quizAnswers[qIdx] = opt"
                  class="w-full px-4 py-3 rounded-xl border text-left text-xs font-semibold transition-all active:scale-[0.99] flex items-center justify-between"
                  :class="[
                    quizAnswers[qIdx] === opt 
                      ? 'border-indigo-600 bg-indigo-50 text-indigo-600 dark:border-indigo-500 dark:bg-indigo-950/30 dark:text-indigo-400' 
                      : 'border-slate-200 hover:bg-slate-100/60 dark:border-slate-800 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-300'
                  ]"
                >
                  <span>{{ opt }}</span>
                  <span 
                    class="w-4 h-4 rounded-full border border-slate-350 flex items-center justify-center"
                    :class="[quizAnswers[qIdx] === opt ? 'border-indigo-600 bg-indigo-600 text-white dark:border-indigo-500 dark:bg-indigo-500' : '']"
                  >
                    <span v-if="quizAnswers[qIdx] === opt" class="w-1.5 h-1.5 rounded-full bg-white"></span>
                  </span>
                </button>
              </div>
            </div>
          </div>

          <div class="flex gap-4 border-t border-slate-100 dark:border-slate-850/60 pt-6">
            <button 
              @click="cancelReview"
              class="px-5 py-2.5 text-xs font-bold text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
            >
              Abandonner
            </button>
            <button 
              @click="evaluateQuiz"
              :disabled="!isQuizFinished"
              class="flex-1 py-3 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-xl transition-all shadow-md active:scale-95"
            >
              Valider mes réponses
            </button>
          </div>
        </div>

        <!-- Step 3: Quiz Feedback Results -->
        <div v-if="quizStep === 'results'" class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm space-y-8 max-w-3xl mx-auto">
          <div class="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-100 dark:border-slate-850/60 pb-6 gap-6">
            <div>
              <span class="text-[10px] font-bold text-indigo-500 uppercase tracking-wider">Résultats du Quiz</span>
              <h2 class="text-lg font-bold">{{ quizSubjectTitle }}</h2>
              <p class="text-xs text-slate-400 mt-1">Quiz complété.</p>
            </div>

            <!-- Quiz Radial Score -->
            <div class="flex items-center gap-4">
              <div class="relative w-16 h-16 rounded-full flex items-center justify-center bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600 dark:text-indigo-400 font-extrabold text-lg border border-indigo-150/40">
                {{ Math.round((quizResult.score / quizQuestions.length) * 100) }}%
              </div>
              <div>
                <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Score Final</p>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {{ quizResult.score }} / {{ quizQuestions.length }} réponses correctes.
                </p>
              </div>
            </div>
          </div>

          <!-- Question Correction Stack -->
          <div class="space-y-6">
            <div 
              v-for="(q, qIdx) in quizQuestions" 
              :key="qIdx"
              class="p-5 rounded-2xl border leading-relaxed space-y-3"
              :class="[
                quizAnswers[qIdx] === q.correctAnswer 
                  ? 'bg-emerald-50/20 border-emerald-100 dark:bg-emerald-950/5 dark:border-emerald-900/20' 
                  : 'bg-rose-50/20 border-rose-100 dark:bg-rose-950/5 dark:border-rose-900/20'
              ]"
            >
              <div class="flex items-start justify-between">
                <h4 class="font-bold text-sm text-slate-800 dark:text-slate-200">
                  Question {{ qIdx + 1 }} : {{ q.questionText }}
                </h4>
                <span 
                  class="px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider"
                  :class="[
                    quizAnswers[qIdx] === q.correctAnswer 
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-450' 
                      : 'bg-rose-100 text-rose-800 dark:bg-rose-950/40 dark:text-rose-450'
                  ]"
                >
                  {{ quizAnswers[qIdx] === q.correctAnswer ? 'Correct' : 'Incorrect' }}
                </span>
              </div>

              <div class="text-xs space-y-2 mt-2">
                <p class="text-slate-500">
                  Votre réponse : <strong :class="[quizAnswers[qIdx] === q.correctAnswer ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400']">{{ quizAnswers[qIdx] }}</strong>
                </p>
                <p v-if="quizAnswers[qIdx] !== q.correctAnswer" class="text-slate-500">
                  Réponse attendue : <strong class="text-emerald-600 dark:text-emerald-400">{{ q.correctAnswer }}</strong>
                </p>
              </div>
            </div>
          </div>

          <button 
            @click="quizStep = 'config'"
            class="px-6 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-all shadow-md active:scale-95"
          >
            Refaire un Quiz
          </button>
        </div>
    </div>

    <!-- Generate Flashcards Modal -->
    <div 
      v-if="showGenerateModal" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm no-print animate-fade-in"
    >
      <div 
        class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 w-full max-w-lg shadow-2xl space-y-6"
      >
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <Sparkles class="w-5 h-5 text-indigo-55" />
            Générer des Flashcards
          </h3>
          <button @click="showGenerateModal = false" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-sm">
            ✕
          </button>
        </div>

        <div class="space-y-4">
          <!-- Source selection -->
          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Source d'extraction</label>
            <div class="grid grid-cols-2 gap-4">
              <button 
                @click="genSourceType = 'note'"
                class="p-3 border rounded-xl text-center font-semibold text-xs transition-all"
                :class="[genSourceType === 'note' ? 'border-indigo-600 bg-indigo-50/50 text-indigo-600 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850/40']"
              >
                Une Note
              </button>
              <button 
                @click="genSourceType = 'binder'"
                class="p-3 border rounded-xl text-center font-semibold text-xs transition-all"
                :class="[genSourceType === 'binder' ? 'border-indigo-600 bg-indigo-50/50 text-indigo-600 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850/40']"
              >
                Un Classeur
              </button>
            </div>
          </div>

          <!-- Note Selector -->
          <div v-if="genSourceType === 'note'">
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Sélectionnez la note</label>
            <select 
              v-model="genNoteId"
              class="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option :value="null" disabled>Choisir une note...</option>
              <option v-for="n in notesStore.notes" :key="n.id" :value="n.id">{{ n.title }}</option>
            </select>
          </div>

          <!-- Binder Selector -->
          <div v-if="genSourceType === 'binder'">
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Sélectionnez le classeur</label>
            <select 
              v-model="genBinderId"
              class="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option :value="null" disabled>Choisir un classeur...</option>
              <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>

          <!-- Target Deck Select -->
          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Deck de destination</label>
            <div class="grid grid-cols-2 gap-4 mb-3">
              <button 
                @click="genDeckTarget = 'new'"
                class="p-3 border rounded-xl text-center font-semibold text-xs transition-all"
                :class="[genDeckTarget === 'new' ? 'border-indigo-600 bg-indigo-50/50 text-indigo-600 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850/40']"
              >
                Nouveau Deck
              </button>
              <button 
                @click="genDeckTarget = 'existing'"
                class="p-3 border rounded-xl text-center font-semibold text-xs transition-all"
                :class="[genDeckTarget === 'existing' ? 'border-indigo-600 bg-indigo-50/50 text-indigo-600 dark:border-indigo-500 dark:bg-indigo-950/20 dark:text-indigo-400' : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850/40']"
                :disabled="decksStore.decks.length === 0"
              >
                Deck existant
              </button>
            </div>

            <!-- New Deck Name Input -->
            <div v-if="genDeckTarget === 'new'">
              <input 
                type="text" 
                v-model="genNewDeckName" 
                placeholder="Nom du nouveau deck (ex: Chimie, Bio...)"
                class="w-full px-3 py-2 bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <!-- Existing Deck Dropdown -->
            <div v-if="genDeckTarget === 'existing'">
              <select 
                v-model="genExistingDeckId"
                class="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 dark:bg-slate-850 dark:border-slate-800 rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option :value="null" disabled>Choisir un deck...</option>
                <option v-for="d in decksStore.decks" :key="d.id" :value="d.id">{{ d.name }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Alert messages or status -->
        <div v-if="genStatusMessage" class="p-3 text-xs rounded-xl" :class="[genStatusIsError ? 'bg-rose-50 text-rose-600 dark:bg-rose-950/20 dark:text-rose-450' : 'bg-indigo-50 text-indigo-600 dark:bg-indigo-950/20 dark:text-indigo-400']">
          {{ genStatusMessage }}
        </div>

        <div class="flex gap-3 justify-end border-t border-slate-100 dark:border-slate-850/60 pt-4">
          <button 
            @click="showGenerateModal = false"
            class="px-4 py-2 text-xs font-bold text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
          >
            Fermer
          </button>
          <button 
            @click="executeFlashcardGeneration"
            :disabled="!isReadyToGenerate"
            class="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-xl transition-all shadow-md active:scale-95"
          >
            {{ genDeckTarget === 'new' ? 'Générer' : 'Mettre à jour' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDecksStore } from '../../stores/decks'
import { useNotesStore } from '../../stores/notes'
import { useBindersStore } from '../../stores/binders'
import api from '../../services/api'
import { 
  Layers, 
  FileText, 
  Sparkles, 
  Activity,
  CheckCircle2,
  Flame,
  Clock,
  Compass
} from '@lucide/vue'

const router = useRouter()
const decksStore = useDecksStore()
const notesStore = useNotesStore()
const bindersStore = useBindersStore()

const tabs = [
  { id: 'flashcards', name: 'Flashcards' },
  { id: 'blank-sheet', name: 'Feuille Blanche' },
  { id: 'feynman', name: 'Méthode Feynman' },
  { id: 'quiz', name: 'Quiz Auto-QCM' }
]

const activeTab = ref('flashcards')

// Decks logic
const decksLoading = ref(false)
const dueCounts = ref<Record<number, number>>({})
const retentionRates = ref<Record<number, number>>({})

const decksWithStats = computed(() => {
  return decksStore.decks.map(deck => {
    return {
      ...deck,
      due_count: dueCounts.value[deck.id] || 0,
      retention_rate: retentionRates.value[deck.id] || 0
    }
  })
})

// Blank Sheet logic
const blankSheetStep = ref<'config' | 'work' | 'results'>('config')
const blankSheetSourceType = ref<'note' | 'binder'>('note')
const selectedNoteId = ref<number | null>(null)
const selectedBinderId = ref<number | null>(null)
const blankSheetDraft = ref('')
const blankSheetTimer = ref(0)
let timerInterval: any = null

const blankSheetWordCount = computed(() => {
  if (!blankSheetDraft.value.trim()) return 0
  return blankSheetDraft.value.trim().split(/\s+/).length
})

const isReadyToStartBlankSheet = computed(() => {
  if (blankSheetSourceType.value === 'note') return selectedNoteId.value !== null
  return selectedBinderId.value !== null
})

const blankSheetSubjectTitle = computed(() => {
  if (blankSheetSourceType.value === 'note') {
    const note = notesStore.notes.find(n => n.id === selectedNoteId.value)
    return note ? note.title : 'Note sans titre'
  } else {
    const binder = bindersStore.binders.find(b => b.id === selectedBinderId.value)
    return binder ? `Classeur : ${binder.name}` : 'Classeur sans titre'
  }
})

// French stop words list to filter out common words in active recall evaluation
const stopWords = new Set([
  'comme', 'dans', 'votre', 'leurs', 'avec', 'pour', 'cette', 'mais', 'pour', 'dans',
  'cette', 'plus', 'avec', 'tout', 'tous', 'cette', 'sans', 'dans', 'cette', 'sont',
  'cette', 'cette', 'elle', 'elles', 'nous', 'vous', 'leur', 'leurs', 'ainsi', 'alors',
  'apres', 'assez', 'au profit', 'aujourd', 'aussi', 'autant', 'autour', 'autre', 'autres',
  'avant', 'avec', 'beaucoup', 'bien', 'bientot', 'car', 'ceci', 'cela', 'celle', 'celles',
  'celui', 'ceux', 'chaque', 'chez', 'comment', 'dehors',
  'depuis', 'derriere', 'desormais', 'dessous', 'dessus', 'devant', 'devenir', 'devenu',
  'devoir', 'differentes', 'differents', 'dire', 'divers', 'diverse', 'diverses', 'doit', 'doivent',
  'donc', 'dont', 'durant', 'effet', 'egalement', 'elles', 'encore', 'entre', 'envers', 'environ',
  'est-ce', 'etaient', 'etais', 'etait', 'etant', 'ete', 'etes', 'etre', 'faudra', 'faut', 'fois',
  'grace', 'hormis', 'hors', 'ici', 'il', 'ils', 'jamais', 'jusque', 'leur', 'leurs', 'lors', 'maintenant',
  'mais', 'malgre', 'meme', 'memes', 'mieux', 'moins', 'moment', 'monde', 'moyen', 'naguere', 'neanmoins',
  'notamment', 'notre', 'notres', 'nous', 'nouveau', 'nouveaux', 'nulle', 'nulles', 'outre', 'parfois',
  'parmi', 'partout', 'pendant', 'personne', 'peu', 'peut', 'peuvent', 'peux', 'plus', 'plusieurs',
  'plutot', 'pour', 'pourquoi', 'pourtant', 'pres', 'presque', 'puis', 'quand', 'quel', 'quelle', 'quelles',
  'quelque', 'quelques', 'quels', 'qui', 'quiconque', 'quoi', 'quoique', 'rien', 'sans', 'sauf', 'selon',
  'seraient', 'serais', 'serait', 'seront', 'ses', 'seulement', 'sinon', 'sitot', 'soi-t', 'soit', 'sommes',
  'son-t', 'sont', 'sous', 'souvent', 'suivante', 'suivantes', 'suivants', 'sujet', 'sur', 'surtout', 'tandis',
  'tant', 'tard', 'tel', 'telle', 'telles', 'tels', 'temps', 'tout', 'toute', 'toutes', 'touts', 'traverse',
  'tres', 'trois', 'trop', 'trouve', 'valeur', 'vers', 'voici', 'voila', 'voire', 'volontiers', 'votre',
  'votres', 'vous', 'vraisemblablement'
])

// Evaluation results schema
const blankSheetResult = ref({
  score: 0,
  remembered: [] as string[],
  missed: [] as string[],
  totalKeywords: 0,
  highlightedText: ''
})

// Feynman logic
const feynmanStep = ref<'config' | 'work' | 'results'>('config')
const feynmanDraft = ref('')
const feynmanTimer = ref(0)

const feynmanWordCount = computed(() => {
  if (!feynmanDraft.value.trim()) return 0
  return feynmanDraft.value.trim().split(/\s+/).length
})

const feynmanSubjectTitle = computed(() => {
  const note = notesStore.notes.find(n => n.id === selectedNoteId.value)
  return note ? note.title : ''
})

const feynmanResult = ref({
  score: 0,
  jargonFound: [] as string[],
  lengthFeedback: '',
  suggestion: ''
})

// Quiz / QCM logic
const quizStep = ref<'config' | 'work' | 'results'>('config')
const quizSubjectTitle = ref('')
interface QuizQuestion {
  questionText: string
  options: string[]
  correctAnswer: string
}
const quizQuestions = ref<QuizQuestion[]>([])
const quizAnswers = ref<Record<number, string>>({})
const quizResult = ref({
  score: 0
})

const isQuizFinished = computed(() => {
  return quizQuestions.value.length > 0 && 
    Object.keys(quizAnswers.value).length === quizQuestions.value.length
})

// Utility functions
function formatTimer(sec: number): string {
  const m = Math.floor(sec / 60).toString().padStart(2, '0')
  const s = (sec % 60).toString().padStart(2, '0')
  return `${m}:${s}`
}

function getCleanText(content: string): string {
  if (!content) return ''
  let clean = content
    .replace(/<!-- SECTION_CONTEXT -->[\s\S]*?<!-- END_SECTION_CONTEXT -->/g, '') // remove context headers if desired, or keep. Let's keep content and only strip comments
    .replace(/<!-- SECTION_CONTEXT -->/g, '')
    .replace(/<!-- END_SECTION_CONTEXT -->/g, '')
    .replace(/<!-- SECTION_DEFINITION -->/g, '')
    .replace(/<!-- END_SECTION_DEFINITION -->/g, '')
    .replace(/<!-- SECTION_BODY -->/g, '')
    .replace(/<!-- END_SECTION_BODY -->/g, '')
    .replace(/<!-- LINKED_NOTES: [\d,\s]* -->/g, '')
    .trim()
  
  // Replace definition tooltips [word]{def:definition} with just "word (definition)"
  clean = clean.replace(/\[([^\]]+)\]\{def:([^}]+)\}/g, '$1 ($2)')
  
  // Strip Markdown markers
  clean = clean
    .replace(/#+\s+/g, '')
    .replace(/\*\*|__/g, '')
    .replace(/\*|_/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/`[^`]+`/g, '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/\$\$[\s\S]*?\$\$/g, '')
    .replace(/\$[^\$]+\$/g, '')
  
  return clean
}

// Extrait les mots clés uniques d'un texte (mots > 4 caractères non vides, hors stopwords et en minuscules)
function extractKeywords(text: string): string[] {
  const words = text
    .toLowerCase()
    .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"'«»]/g, ' ')
    .split(/\s+/)
  
  const keywords = new Set<string>()
  for (const w of words) {
    const cleanW = w.trim()
    if (cleanW.length > 4 && !stopWords.has(cleanW) && !/^\d+$/.test(cleanW)) {
      keywords.add(cleanW)
    }
  }
  return Array.from(keywords)
}

function startTimer(timerRef: any) {
  timerRef.value = 0
  timerInterval = setInterval(() => {
    timerRef.value++
  }, 1000)
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

function cancelReview() {
  stopTimer()
  blankSheetStep.value = 'config'
  feynmanStep.value = 'config'
  quizStep.value = 'config'
  blankSheetDraft.value = ''
  feynmanDraft.value = ''
  quizQuestions.value = []
  quizAnswers.value = {}
}

// Method Feynman Action
function startFeynman() {
  const note = notesStore.notes.find(n => n.id === selectedNoteId.value)
  if (!note) return
  feynmanDraft.value = ''
  feynmanStep.value = 'work'
  startTimer(feynmanTimer)
}

async function evaluateFeynman() {
  stopTimer()
  
  const note = notesStore.notes.find(n => n.id === selectedNoteId.value)
  if (!note) return
  
  const cleanSourceText = getCleanText(note.content)
  const sourceKeywords = extractKeywords(cleanSourceText)
  
  // Feynman analysis parameters
  const draftWords = feynmanDraft.value.toLowerCase().split(/\s+/)
  const draftWordsSet = new Set(draftWords)
  
  // Detect complex keywords from source note that are present in feynman draft (jargon check)
  // Jargon means we used complex words without explaining them, or kept technical terms
  // Ideally Feynman method explains these simply. Let's find source keywords present in feynman
  const jargonUsed = sourceKeywords.filter(kw => draftWordsSet.has(kw))
  
  // Simplicity score decreases if too much complex keywords are used directly
  // and increases if explanation has balanced word length and conciseness
  let simplicityScore = 100
  simplicityScore -= jargonUsed.length * 4
  
  // Word count check
  let lengthMsg = 'Idéal'
  if (feynmanWordCount.value < 40) {
    simplicityScore -= 20
    lengthMsg = 'Trop court'
  } else if (feynmanWordCount.value > 180) {
    simplicityScore -= 15
    lengthMsg = 'Trop long / verbeux'
  }
  
  simplicityScore = Math.max(10, Math.min(100, simplicityScore))
  
  let suggest = 'Votre explication est excellente et fluide ! Continuer ainsi.'
  if (jargonUsed.length > 3) {
    suggest = `Essayez d'expliquer les termes complexes suivants par des métaphores ou de les décomposer : ${jargonUsed.slice(0, 3).join(', ')}.`
  } else if (feynmanWordCount.value < 40) {
    suggest = "Développez davantage en incluant un exemple concret ou une comparaison imagée pour clarifier la notion."
  }
  
  feynmanResult.value = {
    score: simplicityScore,
    jargonFound: jargonUsed,
    lengthFeedback: lengthMsg,
    suggestion: suggest
  }
  
  feynmanStep.value = 'results'
  
  // Log session to backend
  try {
    await api.post('/stats/sessions', {
      module: 'note',
      duration_seconds: feynmanTimer.value,
      cards_reviewed: sourceKeywords.length,
      cards_correct: Math.round(sourceKeywords.length * (simplicityScore / 100))
    })
  } catch (err) {
    console.error('Erreur logs Feynman', err)
  }
}

// Blank Sheet actions
async function startBlankSheet() {
  if (blankSheetSourceType.value === 'note' && selectedNoteId.value !== null) {
    router.push(`/notes/${selectedNoteId.value}/blurting?from=reviews`)
    return
  }
  
  blankSheetDraft.value = ''
  blankSheetStep.value = 'work'
  startTimer(blankSheetTimer)
}

async function evaluateBlankSheet() {
  stopTimer()
  
  let cleanSourceText = ''
  if (blankSheetSourceType.value === 'note') {
    const note = notesStore.notes.find(n => n.id === selectedNoteId.value)
    cleanSourceText = note ? getCleanText(note.content) : ''
  } else {
    // Combine notes in binder
    const notesInBinder = notesStore.notes.filter(n => n.binder_id === selectedBinderId.value)
    cleanSourceText = notesInBinder.map(n => getCleanText(n.content)).join('\n\n')
  }
  
  const sourceKeywords = extractKeywords(cleanSourceText)
  
  if (sourceKeywords.length === 0) {
    // Fallback if note has no keywords
    blankSheetResult.value = {
      score: 100,
      remembered: [],
      missed: [],
      totalKeywords: 0,
      highlightedText: cleanSourceText || 'Document d\'origine vide.'
    }
    blankSheetStep.value = 'results'
    return
  }
  
  // Check which keywords are in the draft
  const draftTextClean = blankSheetDraft.value.toLowerCase()
  const remembered = [] as string[]
  const missed = [] as string[]
  
  for (const kw of sourceKeywords) {
    // Simple check if word or substring exists in draft
    // Using regex to check word boundaries for accuracy
    const regex = new RegExp(`\\b${kw}\\w*\\b`, 'i')
    if (regex.test(draftTextClean)) {
      remembered.push(kw)
    } else {
      missed.push(kw)
    }
  }
  
  const score = Math.round((remembered.length / sourceKeywords.length) * 100)
  
  // Highlight original clean text to show a comparative view
  let highlighted = cleanSourceText
  
  // Sort keywords by length descending to replace larger terms first and avoid partial replacements
  const allKeywords = [...sourceKeywords].sort((a, b) => b.length - a.length)
  
  for (const kw of allKeywords) {
    const isRemembered = remembered.includes(kw)
    const replacementClass = isRemembered 
      ? 'bg-emerald-100 text-emerald-900 border-b border-emerald-400 dark:bg-emerald-950/60 dark:text-emerald-350 px-1 rounded' 
      : 'bg-rose-100 text-rose-900 border-b border-rose-400 dark:bg-rose-950/60 dark:text-rose-350 px-1 rounded font-bold'
    
    // Replace case-insensitively with wrapper
    const regex = new RegExp(`(${kw}\\w*)`, 'gi')
    highlighted = highlighted.replace(regex, `<span class="${replacementClass}">$1</span>`)
  }
  
  blankSheetResult.value = {
    score,
    remembered,
    missed,
    totalKeywords: sourceKeywords.length,
    highlightedText: highlighted
  }
  
  blankSheetStep.value = 'results'
  
  // Log session to backend database
  try {
    await api.post('/stats/sessions', {
      module: 'note',
      duration_seconds: blankSheetTimer.value,
      cards_reviewed: sourceKeywords.length,
      cards_correct: remembered.length
    })
  } catch (err) {
    console.error('Erreur de logs session feuille blanche', err)
  }
}

// Auto-QCM actions
function startQuiz() {
  const note = notesStore.notes.find(n => n.id === selectedNoteId.value)
  if (!note) return
  
  quizSubjectTitle.value = note.title
  quizAnswers.value = {}
  
  const cleanText = getCleanText(note.content)
  const keywords = extractKeywords(cleanText)
  
  // Generate QCM questions dynamically
  const sentences = cleanText.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 20)
  const generated = [] as QuizQuestion[]
  
  // Let's create questions from sentences containing keywords
  let sentenceCount = 0
  for (const sentence of sentences) {
    if (sentenceCount >= 4) break // Max 4 questions
    
    // Find keywords in this sentence
    const keywordsInSentence = keywords.filter(kw => {
      const regex = new RegExp(`\\b${kw}\\w*\\b`, 'i')
      return regex.test(sentence)
    })
    
    if (keywordsInSentence.length > 0) {
      // Pick one keyword as the answer
      const answer = keywordsInSentence[0]
      // Replace answer in sentence to create question
      const regex = new RegExp(`\\b${answer}\\w*\\b`, 'i')
      const questionText = sentence.replace(regex, '_________')
      
      // Generate distractors (choices)
      const distractors = keywords.filter(k => k !== answer)
      
      // Shuffle distractors and pick 3
      const shuffledDistractors = distractors.sort(() => 0.5 - Math.random()).slice(0, 3)
      
      // Make sure we have 4 options
      const options = [answer, ...shuffledDistractors]
      // Capitalize first letters of options
      const formattedOptions = options.map(o => o.charAt(0).toUpperCase() + o.slice(1)).sort()
      
      // Correct formatted answer
      const formattedCorrectAnswer = formattedOptions.find(o => o.toLowerCase().startsWith(answer.toLowerCase())) || answer
      
      generated.push({
        questionText: questionText.charAt(0).toUpperCase() + questionText.slice(1) + '.',
        options: formattedOptions,
        correctAnswer: formattedCorrectAnswer
      })
      
      sentenceCount++
    }
  }
  
  // Fallback if no questions could be parsed from sentences
  if (generated.length === 0 && keywords.length > 1) {
    // Fallback: simple vocabulary match question
    const answer = keywords[0]
    const questionText = `Quel concept est central dans le document "${note.title}" ?`
    const distractors = keywords.slice(1, 4)
    const options = [answer, ...distractors].map(o => o.charAt(0).toUpperCase() + o.slice(1)).sort()
    const formattedCorrect = options.find(o => o.toLowerCase().startsWith(answer.toLowerCase())) || answer
    
    generated.push({
      questionText,
      options,
      correctAnswer: formattedCorrect
    })
  }
  
  quizQuestions.value = generated
  quizStep.value = 'work'
}

async function evaluateQuiz() {
  let score = 0
  quizQuestions.value.forEach((q, idx) => {
    if (quizAnswers.value[idx] === q.correctAnswer) {
      score++
    }
  })
  
  quizResult.value = { score }
  quizStep.value = 'results'
  
  // Log study session
  try {
    await api.post('/stats/sessions', {
      module: 'flashcard',
      duration_seconds: 60, // Arbitrary duration for quiz
      cards_reviewed: quizQuestions.value.length,
      cards_correct: score
    })
  } catch (err) {
    console.error('Erreur logs Quiz QCM', err)
  }
}

async function fetchDecksStats() {
  const promises = decksStore.decks.map(async (deck) => {
    try {
      const response = await api.get(`/stats/decks/${deck.id}`)
      dueCounts.value[deck.id] = response.data.cards_to_review
      retentionRates.value[deck.id] = response.data.retention_rate
    } catch (error) {
      console.error(`Erreur stats deck ${deck.id}`, error)
      dueCounts.value[deck.id] = 0
      retentionRates.value[deck.id] = 0
    }
  })
  await Promise.all(promises)
}

// Flashcard Generation state variables and functions
const showGenerateModal = ref(false)
const genSourceType = ref<'note' | 'binder'>('note')
const genNoteId = ref<number | null>(null)
const genBinderId = ref<number | null>(null)
const genDeckTarget = ref<'new' | 'existing'>('new')
const genNewDeckName = ref('')
const genExistingDeckId = ref<number | null>(null)
const genStatusMessage = ref('')
const genStatusIsError = ref(false)

const isReadyToGenerate = computed(() => {
  if (genSourceType.value === 'note' && genNoteId.value === null) return false
  if (genSourceType.value === 'binder' && genBinderId.value === null) return false
  
  if (genDeckTarget.value === 'new') return genNewDeckName.value.trim().length > 0
  return genExistingDeckId.value !== null
})

function openGenerateModal() {
  genStatusMessage.value = ""
  genStatusIsError.value = false
  if (selectedNoteId.value) {
    genNoteId.value = selectedNoteId.value
  }
  showGenerateModal.value = true
}

function extractFlashcardsFromText(text: string): { front: string, back: string }[] {
  const cards: { front: string, back: string }[] = []
  if (!text) return cards
  
  // 1. Tooltips: [word]{def:definition}
  const tooltipRegex = /\[([^\]]+)\]\{def:([^}]+)\}/g
  let match
  while ((match = tooltipRegex.exec(text)) !== null) {
    const front = match[1].trim()
    const back = match[2].trim()
    if (front && back) {
      cards.push({ front, back })
    }
  }
  
  // 2. Glossary lists: "- **Term** : Definition"
  const boldGlossaryRegex = /(?:^|\n)(?:-\s*|\*\s*)\*\*([^*]+)\*\*\s*:\s*([^\n]+)/g
  while ((match = boldGlossaryRegex.exec(text)) !== null) {
    const front = match[1].trim()
    const back = match[2].trim()
    if (front && back && !cards.some(c => c.front.toLowerCase() === front.toLowerCase())) {
      cards.push({ front, back })
    }
  }
  
  // 3. Colons: "Front : Back"
  const simpleColonRegex = /(?:^|\n)([^:\n]{3,35})\s*:\s*([^.\n]{10,200})/g
  while ((match = simpleColonRegex.exec(text)) !== null) {
    const front = match[1].trim()
    const back = match[2].trim()
    if (front.startsWith('#') || front.startsWith('-') || front.startsWith('*') || front.startsWith('<!--')) {
      continue
    }
    if (front && back && !cards.some(c => c.front.toLowerCase() === front.toLowerCase())) {
      cards.push({ front, back })
    }
  }
  
  return cards
}

async function executeFlashcardGeneration() {
  if (!isReadyToGenerate.value) return
  
  genStatusMessage.value = "Analyse et extraction en cours..."
  genStatusIsError.value = false
  
  try {
    let sourceText = ""
    let subjectName = ""
    if (genSourceType.value === 'note') {
      const note = notesStore.notes.find(n => n.id === genNoteId.value)
      sourceText = note ? note.content : ""
      subjectName = note ? note.title : "la note"
    } else {
      const binder = bindersStore.binders.find(b => b.id === genBinderId.value)
      const notesInBinder = notesStore.notes.filter(n => n.binder_id === genBinderId.value)
      sourceText = notesInBinder.map(n => n.content).join("\n\n")
      subjectName = binder ? `classeur ${binder.name}` : "le classeur"
    }
    
    const extracted = extractFlashcardsFromText(sourceText)
    
    if (extracted.length === 0) {
      genStatusIsError.value = true
      genStatusMessage.value = "Aucune flashcard n'a pu être extraite. Ajoutez des définitions sous la forme '[concept]{def:explication}' ou '- **Concept** : explication' dans vos notes."
      return
    }
    
    let deckId: number
    let isNew = false
    
    if (genDeckTarget.value === 'new') {
      if (!genNewDeckName.value.trim()) {
        genStatusIsError.value = true
        genStatusMessage.value = "Veuillez spécifier un nom de deck."
        return
      }
      const newDeck = await decksStore.createDeck(genNewDeckName.value.trim(), `Généré depuis ${subjectName}`)
      deckId = newDeck.id
      isNew = true
    } else {
      if (!genExistingDeckId.value) {
        genStatusIsError.value = true
        genStatusMessage.value = "Veuillez choisir un deck existant."
        return
      }
      deckId = genExistingDeckId.value
    }
    
    // Fetch card cache
    const existingCards = await decksStore.fetchCardsForDeck(deckId)
    const existingFronts = new Set(existingCards.map(c => c.front.toLowerCase().trim()))
    
    let addedCount = 0
    let skippedCount = 0
    
    for (const card of extracted) {
      const frontClean = card.front.toLowerCase().trim()
      if (existingFronts.has(frontClean)) {
        skippedCount++
        continue
      }
      await decksStore.createCard(deckId, card.front, card.back)
      addedCount++
    }
    
    // Refresh local decks & stats
    await decksStore.fetchDecks()
    await fetchDecksStats()
    
    genStatusIsError.value = false
    genStatusMessage.value = `Succès ! ${addedCount} carte(s) ajoutée(s)${skippedCount > 0 ? ` (${skippedCount} doublon(s) ignoré(s))` : ''}.`
    
    if (isNew) {
      genNewDeckName.value = ""
      genDeckTarget.value = "existing"
      genExistingDeckId.value = deckId
    }
  } catch (error) {
    console.error("Erreur de génération des cartes", error)
    genStatusIsError.value = true
    genStatusMessage.value = "Une erreur est survenue lors de la création ou de l'ajout des flashcards."
  }
}

onMounted(async () => {
  decksLoading.value = true
  try {
    // Parallel fetch of all essential lists
    await Promise.all([
      decksStore.fetchDecks(),
      notesStore.fetchNotes(),
      bindersStore.fetchBinders()
    ])
    // Fetch deck due counts
    await fetchDecksStats()
  } catch (err) {
    console.error('Erreur chargement révisions', err)
  } finally {
    decksLoading.value = false
  }
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
