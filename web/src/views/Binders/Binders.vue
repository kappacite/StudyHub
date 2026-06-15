<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header with Breadcrumbs and actions -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <!-- Breadcrumb navigation -->
      <div class="flex items-center gap-1.5 text-sm font-semibold">
        <button 
          @click="currentBinderId = null" 
          class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400 flex items-center gap-1"
        >
          <FolderClosed class="w-4 h-4" />
          Racine
        </button>
        
        <template v-for="(crumb, idx) in breadcrumbs" :key="crumb.id">
          <ChevronRight class="w-4 h-4 text-slate-400" />
          <button 
            @click="currentBinderId = crumb.id" 
            class="text-slate-500 hover:text-indigo-600 dark:text-slate-400 dark:hover:text-indigo-400"
            :class="[idx === breadcrumbs.length - 1 ? 'text-slate-800 dark:text-white font-bold pointer-events-none' : '']"
          >
            {{ crumb.name }}
          </button>
        </template>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-3">
        <template v-if="isOwner">
          <button
            v-if="currentBinderId !== null"
            @click="router.push(`/revision/binders/${currentBinderId}/stats`)"
            class="inline-flex items-center gap-2 px-4 py-2 border border-slate-200 dark:border-slate-800 rounded-xl text-sm font-semibold text-slate-600 dark:text-slate-350 hover:bg-slate-50 dark:hover:bg-slate-850 transition-all active:scale-95"
          >
            <BarChart3 class="w-4 h-4" />
            Stats
          </button>
          <button
            v-if="currentBinderId !== null"
            @click="openShareModal"
            class="inline-flex items-center gap-2 px-4 py-2 border rounded-xl text-sm font-semibold transition-all active:scale-95"
            :class="[
              currentBinder?.is_public 
                ? 'border-emerald-500 bg-emerald-50 text-emerald-600 dark:border-emerald-600 dark:bg-emerald-950/20 dark:text-emerald-400' 
                : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 text-slate-600 dark:text-slate-350'
            ]"
          >
            <Globe class="w-4 h-4" />
            {{ currentBinder?.is_public ? 'Public' : 'Partager' }}
          </button>
          <button
            v-if="currentBinderId !== null"
            @click="openClassShareModal"
            class="inline-flex items-center gap-2 px-4 py-2 border rounded-xl text-sm font-semibold transition-all active:scale-95"
            :class="[
              isSharedToClass
                ? 'border-indigo-500 bg-indigo-50 text-indigo-600 dark:border-indigo-600 dark:bg-indigo-950/20 dark:text-indigo-400'
                : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 text-slate-600 dark:text-slate-350'
            ]"
          >
            <GraduationCap class="w-4 h-4" />
            {{ isSharedToClass ? `Partagé (${sharedClasses.length})` : 'Classe' }}
          </button>

          <div class="relative">
            <button
              @click="showAddMenu = !showAddMenu"
              class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15"
            >
              <Plus class="w-4 h-4" />
              Ajouter
              <ChevronDown class="w-4 h-4" />
            </button>

            <template v-if="showAddMenu">
              <div class="fixed inset-0 z-10" @click="showAddMenu = false"></div>
              <div class="absolute right-0 mt-2 w-60 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-2xl z-20 p-1.5 animate-scale-up">
                <button v-for="item in addMenu" :key="item.label" @click="item.action" class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-left">
                  <component :is="item.icon" class="w-4 h-4 text-indigo-500 shrink-0" />
                  {{ item.label }}
                </button>
              </div>
            </template>
          </div>
        </template>
        <template v-else>
          <button 
            @click="cloneBinder"
            :disabled="cloning"
            class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all shadow-lg shadow-indigo-600/15 disabled:opacity-50"
          >
            <Loader2 v-if="cloning" class="w-4 h-4 animate-spin" />
            <Copy v-else class="w-4 h-4" />
            {{ cloning ? 'Copie en cours...' : 'Créer une copie personnelle' }}
          </button>
        </template>
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-100 bg-white p-3 dark:border-slate-800 dark:bg-slate-900">
      <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Filtrer</span>
      <button
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-bold"
        :class="selectedTagId === null ? 'bg-indigo-600 text-white' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-300'"
        @click="filterByTag(null)"
      >
        Tous
      </button>
      <button
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        type="button"
        class="rounded-xl px-3 py-1.5 text-xs font-bold"
        :style="selectedTagId === tag.id ? { backgroundColor: tag.color || '#4F46E5', color: '#fff' } : undefined"
        :class="selectedTagId === tag.id ? '' : 'bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-300'"
        @click="filterByTag(tag.id)"
      >
        {{ tag.name }}
      </button>
    </div>

    <!-- Read only / Follow class warning banner -->
    <div v-if="!isOwner" class="p-4 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/30 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-amber-850 dark:text-amber-300">
      <div class="flex items-center gap-2">
        <Eye class="w-5 h-5 text-amber-500 flex-shrink-0" />
        <span class="text-xs font-semibold">Vous visualisez ce dossier en lecture seule (cours suivi). Pour le modifier, veuillez créer une copie personnelle.</span>
      </div>
      <button 
        @click="cloneBinder"
        :disabled="cloning"
        class="px-3.5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-bold transition-all active:scale-95 disabled:opacity-50 flex items-center gap-1.5"
      >
        <Loader2 v-if="cloning" class="w-3.5 h-3.5 animate-spin" />
        <Copy v-else class="w-3.5 h-3.5" />
        Créer une copie
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="bindersStore.loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <svg class="animate-spin h-8 w-8 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Chargement...</span>
    </div>

    <div v-else class="space-y-8">
      <!-- Direct Subfolders Section -->
      <div>
        <h3 class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-4">Dossiers ({{ currentSubBinders.length }})</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div 
            v-for="folder in currentSubBinders" 
            :key="folder.id"
            class="flex items-center justify-between p-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl hover:border-indigo-500/30 dark:hover:border-indigo-500/30 shadow-sm transition-all duration-200 group cursor-pointer"
            @click="currentBinderId = folder.id"
          >
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 flex items-center justify-center group-hover:scale-105 transition-transform">
                <FolderClosed class="w-5 h-5 fill-indigo-100 dark:fill-indigo-950/20" />
              </div>
              <div class="min-w-0">
                <span class="font-bold truncate text-sm text-slate-800 dark:text-slate-200">{{ folder.name }}</span>
                <span v-if="folder.read_only" class="ml-1.5 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wide bg-amber-100 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400">Cours</span>
                <div v-if="folder.tags?.length" class="mt-1 flex flex-wrap gap-1">
                  <TagBadge v-for="tag in folder.tags" :key="tag.id" :tag="tag" />
                </div>
              </div>
            </div>
            
            <button 
              v-if="isOwner"
              @click.stop="confirmDelete(folder)" 
              class="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-all"
              title="Supprimer"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>

          <div 
            v-if="currentSubBinders.length === 0" 
            class="col-span-full border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-2xl p-8 flex flex-col items-center justify-center text-center text-slate-400"
          >
            <FolderClosed class="w-8 h-8 text-slate-300 dark:text-slate-700 mb-2" />
            <p class="text-xs font-semibold uppercase tracking-wider">Aucun sous-dossier</p>
          </div>
        </div>
      </div>

      <!-- Associated Contents Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Associated Notes -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2 mb-4">
            <FileText class="w-4 h-4 text-indigo-500" />
            Notes associées ({{ currentNotes.length }})
          </h3>
          
          <div class="space-y-3">
            <div 
              v-for="note in currentNotes" 
              :key="note.id"
              class="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800 rounded-2xl hover:border-slate-200 transition-colors cursor-pointer group"
              @click="router.push(`/notes/${note.id}`)"
            >
              <div class="min-w-0">
                <p class="text-sm font-bold truncate text-slate-800 dark:text-slate-200">
                  {{ note.title }}
                  <span v-if="note.read_only" class="ml-2 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wide bg-amber-100 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400">Cours · lecture seule</span>
                </p>
                <p class="text-[10px] text-slate-400 mt-0.5">Mis à jour il y a 2h</p>
              </div>
              <div class="flex items-center gap-1 shrink-0">
                <button
                  v-if="isOwner"
                  @click.stop="detachItem('note', note.id)"
                  class="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-amber-600 rounded-lg hover:bg-amber-50 dark:hover:bg-amber-950/30 transition-all"
                  title="Retirer du classeur (sans supprimer)"
                >
                  <FolderMinus class="w-4 h-4" />
                </button>
                <ChevronRight class="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>

            <div
              v-if="currentNotes.length === 0"
              class="text-center py-8 text-slate-400 text-xs font-semibold uppercase tracking-wider"
            >
              Aucune note dans ce dossier
            </div>
          </div>
        </div>

        <!-- Jeux de révision -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2">
              <Layers class="w-4 h-4 text-indigo-500" />
              Jeux de révision ({{ currentDecks.length }})
            </h3>
            <button v-if="isOwner" @click="openRevisionItem('basic')" class="text-xs font-bold text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              <Plus class="w-3.5 h-3.5" /> Item
            </button>
          </div>

          <div class="space-y-3">
            <div
              v-for="deck in currentDecks"
              :key="deck.id"
              class="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800 rounded-2xl hover:border-slate-200 transition-colors cursor-pointer group"
              @click="router.push(`/decks/${deck.id}/study`)"
            >
              <div class="min-w-0">
                <p class="text-sm font-bold truncate text-slate-800 dark:text-slate-200">{{ deck.name }}</p>
                <p class="text-[10px] text-indigo-500 dark:text-indigo-400 font-semibold uppercase tracking-wider mt-0.5">
                  {{ deck.card_count }} item(s)
                </p>
              </div>
              <div class="flex items-center gap-1">
                <button
                  v-if="isOwner"
                  @click.stop="openRevisionItemForDeck(deck.id)"
                  class="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-indigo-600 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-950/30 transition-all"
                  title="Ajouter un item"
                >
                  <Plus class="w-4 h-4" />
                </button>
                <button
                  v-if="isOwner"
                  @click.stop="detachItem('deck', deck.id)"
                  class="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-amber-600 rounded-lg hover:bg-amber-50 dark:hover:bg-amber-950/30 transition-all"
                  title="Retirer du classeur (sans supprimer)"
                >
                  <FolderMinus class="w-4 h-4" />
                </button>
                <ChevronRight class="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>

            <div
              v-if="currentDecks.length === 0"
              class="text-center py-8 text-slate-400 text-xs font-semibold uppercase tracking-wider"
            >
              Aucun jeu de révision dans ce dossier
            </div>
          </div>
        </div>

        <!-- Ensembles de révision (QCM, V/F, association, définition, ordre) -->
        <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl p-6 shadow-sm">
          <h3 class="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2 mb-4">
            <FileQuestion class="w-4 h-4 text-indigo-500" />
            Ensembles de révision ({{ currentSets.length }})
          </h3>

          <div class="space-y-3">
            <div
              v-for="set in currentSets"
              :key="set.id"
              class="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800 rounded-2xl hover:border-indigo-200 cursor-pointer group"
              @click="openSet(set)"
            >
              <div class="min-w-0">
                <p class="text-sm font-bold truncate text-slate-800 dark:text-slate-200">{{ set.name }}</p>
                <p class="text-[10px] text-indigo-500 dark:text-indigo-400 font-semibold uppercase tracking-wider mt-0.5">
                  {{ REVISION_TYPE_LABELS[set.type] }} · {{ set.item_count }} item(s)
                </p>
              </div>
              <div class="flex items-center gap-2 shrink-0">
                <button
                  @click.stop="router.push(`/revision/sets/${set.id}/stats`)"
                  class="p-1.5 text-slate-400 hover:text-indigo-600 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-950/30"
                  title="Statistiques"
                >
                  <BarChart3 class="w-4 h-4" />
                </button>
                <button
                  v-if="isOwner"
                  @click.stop="detachItem('set', set.id)"
                  class="p-1.5 text-slate-400 hover:text-amber-600 rounded-lg hover:bg-amber-50 dark:hover:bg-amber-950/30"
                  title="Retirer du classeur (sans supprimer)"
                >
                  <FolderMinus class="w-4 h-4" />
                </button>
                <span class="text-xs font-bold text-indigo-600 flex items-center gap-1">
                  {{ set.type === 'qcm' ? 'Lancer' : 'Étudier' }}
                  <ChevronRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </span>
              </div>
            </div>

            <div
              v-if="currentSets.length === 0"
              class="text-center py-8 text-slate-400 text-xs font-semibold uppercase tracking-wider"
            >
              Aucun ensemble de révision dans ce dossier
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Attach Existing Items Modal (C1) -->
    <div v-if="showAttachModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showAttachModal = false"></div>
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl w-full max-w-lg p-6 relative z-10 shadow-2xl animate-scale-up flex flex-col max-h-[80vh]">
        <h3 class="font-bold text-lg text-slate-800 dark:text-white mb-1">Ajouter un élément existant</h3>
        <p class="text-xs text-slate-400 mb-4">Déplace des éléments non rangés ou d'un autre classeur vers celui-ci.</p>

        <div class="flex-1 overflow-y-auto -mx-2 px-2 space-y-4">
          <div v-for="group in attachableGroups" :key="group.type">
            <p v-if="group.items.length" class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">{{ group.label }}</p>
            <label
              v-for="it in group.items" :key="`${group.type}:${it.id}`"
              class="flex items-center gap-3 p-2.5 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer"
            >
              <input type="checkbox" :checked="isSelected(group.type, it.id)" @change="toggleSelect(group.type, it.id)"
                     class="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
              <span class="text-sm font-semibold text-slate-700 dark:text-slate-200 truncate">{{ it.label }}</span>
            </label>
          </div>
          <p v-if="attachableGroups.every(g => g.items.length === 0)" class="text-center py-8 text-xs text-slate-400 uppercase tracking-wider">
            Aucun élément disponible à rattacher.
          </p>
        </div>

        <div class="flex items-center justify-end gap-3 mt-5">
          <button @click="showAttachModal = false" class="px-4 py-2 text-sm font-semibold text-slate-500 hover:text-slate-700 dark:hover:text-slate-300">Annuler</button>
          <button
            @click="confirmAttach"
            :disabled="selectedCount === 0 || attaching"
            class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all disabled:opacity-50"
          >
            <Loader2 v-if="attaching" class="w-4 h-4 animate-spin" />
            Ajouter{{ selectedCount ? ` (${selectedCount})` : '' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create Folder Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
    >
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showModal = false"></div>
      
      <!-- Modal box -->
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up">
        <h3 class="text-lg font-bold mb-4">Créer un nouveau dossier</h3>
        
        <form @submit.prevent="createFolder">
          <div class="space-y-4">
            <div>
              <label for="folder-name" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Nom du dossier</label>
              <input 
                id="folder-name" 
                type="text" 
                required 
                v-model="newFolderName"
                placeholder="Ex: Anatomie, Semestre 2..."
                class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium"
              />
            </div>
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Tags</label>
              <TagSelector v-model="folderTags" />
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 mt-6">
            <button 
              type="button" 
              @click="showModal = false"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
            >
              Annuler
            </button>
            <button 
              type="submit"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Créer
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Share Folder Modal -->
    <div 
      v-if="showShareModal"
      class="fixed inset-0 z-50 flex items-center justify-center px-4"
    >
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showShareModal = false"></div>
      
      <!-- Modal box -->
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up">
        <h3 class="text-lg font-bold mb-2">Partager sur l'Espace Communautaire</h3>
        <p class="text-xs text-slate-450 dark:text-slate-500 mb-4">
          Publiez ce classeur et toutes les ressources qu'il contient (notes, flashcards...) pour les rendre accessibles à la communauté.
        </p>
        
        <form @submit.prevent="saveShareSettings">
          <div class="space-y-4">
            <!-- Toggle Visibilité -->
            <div class="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800 rounded-2xl">
              <div>
                <label class="block text-xs font-bold text-slate-800 dark:text-slate-200">Statut de visibilité</label>
                <span class="text-[10px] text-slate-450">{{ shareIsPublic ? 'Visible sur la Marketplace' : 'Visible uniquement par vous' }}</span>
              </div>
              <button 
                type="button" 
                @click="shareIsPublic = !shareIsPublic"
                class="px-3 py-1.5 border rounded-xl text-xs font-bold transition-all active:scale-95"
                :class="[
                  shareIsPublic 
                    ? 'border-emerald-500 bg-emerald-50 text-emerald-600 dark:border-emerald-600 dark:bg-emerald-950/20 dark:text-emerald-400' 
                    : 'border-slate-200 dark:border-slate-800 text-slate-500'
                ]"
              >
                {{ shareIsPublic ? 'Public' : 'Privé' }}
              </button>
            </div>

            <!-- Description -->
            <div>
              <label for="share-description" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Description</label>
              <textarea 
                id="share-description" 
                v-model="shareDescription"
                placeholder="Décrivez le contenu de ce dossier..."
                rows="3"
                class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium"
              ></textarea>
            </div>

            <!-- Tags -->
            <div>
              <label for="share-tags" class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Mots-clés (tags, séparés par virgules)</label>
              <input 
                id="share-tags" 
                type="text" 
                v-model="shareTags"
                placeholder="Ex: Chimie, Médecine, Semestre 1"
                class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium"
              />
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 mt-6">
            <button 
              type="button" 
              @click="showShareModal = false"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
            >
              Annuler
            </button>
            <button 
              type="submit"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700 active:scale-95 transition-all"
            >
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- B2 — Partager le classeur à une classe (par référence, auto-actualisé) -->
    <div v-if="showClassShareModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showClassShareModal = false"></div>
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up">
        <h3 class="text-lg font-bold mb-2">Partager ce classeur à une classe</h3>
        <p class="text-xs text-slate-450 dark:text-slate-500 mb-4">
          Le classeur est partagé <strong>par référence</strong> : tout élément que vous y ajoutez ensuite
          devient automatiquement visible des élèves, en lecture seule.
        </p>

        <div v-if="classShareBusy && myClasses.length === 0" class="py-8 text-center text-sm text-slate-400">
          <Loader2 class="w-5 h-5 animate-spin inline" />
        </div>
        <div v-else-if="ownedClasses.length === 0" class="py-8 text-center text-sm text-slate-400">
          Vous n'animez aucune classe pour l'instant.
        </div>
        <ul v-else class="space-y-2 max-h-72 overflow-y-auto">
          <li
            v-for="c in ownedClasses"
            :key="c.id"
            class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800 rounded-2xl"
          >
            <div class="min-w-0">
              <p class="text-sm font-bold text-slate-800 dark:text-slate-200 truncate">{{ c.name }}</p>
              <span class="text-[10px] text-slate-450">{{ c.members_count }} membre(s)</span>
            </div>
            <button
              type="button"
              :disabled="classShareBusy"
              @click="toggleClassShare(c)"
              class="px-3 py-1.5 border rounded-xl text-xs font-bold transition-all active:scale-95 disabled:opacity-50 shrink-0"
              :class="[
                isClassShared(c.id)
                  ? 'border-indigo-500 bg-indigo-50 text-indigo-600 dark:border-indigo-600 dark:bg-indigo-950/20 dark:text-indigo-400'
                  : 'border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-white dark:hover:bg-slate-800'
              ]"
            >
              {{ isClassShared(c.id) ? 'Partagé ✓' : 'Partager' }}
            </button>
          </li>
        </ul>

        <div class="flex items-center justify-end mt-6">
          <button
            type="button"
            @click="showClassShareModal = false"
            class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800"
          >
            Fermer
          </button>
        </div>
      </div>
    </div>

    <!-- New "jeu de révision" (empty deck) Modal -->
    <div v-if="showDeckModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" @click="showDeckModal = false"></div>
      <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up">
        <h3 class="text-lg font-bold mb-4">Nouveau jeu de révision</h3>
        <form @submit.prevent="createDeck">
          <input
            v-model="newDeckName"
            type="text"
            required
            placeholder="Ex: Anatomie — chapitre 1"
            class="block w-full px-4 py-3 bg-slate-50 border border-slate-200 dark:bg-slate-800/40 dark:border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm font-medium"
          />
          <div class="flex items-center justify-end gap-3 mt-6">
            <button type="button" @click="showDeckModal = false" class="px-4 py-2 text-sm font-semibold rounded-xl text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800">Annuler</button>
            <button type="submit" class="px-4 py-2 text-sm font-bold rounded-xl text-white bg-indigo-600 hover:bg-indigo-700">Créer</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Typed revision item Modal -->
    <RevisionItemModal
      v-if="showRevisionModal"
      :binder-id="currentBinderId"
      :decks="currentDecks"
      :initial-type="revisionInitialType"
      :initial-deck-id="revisionDeckId"
      @close="showRevisionModal = false"
      @created="onRevisionCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import { useBindersStore } from '../../stores/binders'
import type { Binder } from '../../stores/binders'
import { useNotesStore } from '../../stores/notes'
import { useDecksStore } from '../../stores/decks'
import { useTagsStore, type Tag } from '../../stores/tags'
import TagBadge from '../../components/ui/TagBadge.vue'
import TagSelector from '../../components/ui/TagSelector.vue'
import RevisionItemModal from '../../components/decks/RevisionItemModal.vue'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionType } from '../../stores/revision'

// 'basic' = flashcard recto/verso (Deck) ; les autres types = ensembles de révision.
type RevisionItemType = RevisionType | 'basic'

const REVISION_TYPE_LABELS: Record<RevisionType, string> = {
  qcm: 'QCM',
  vf: 'Vrai / Faux',
  association: 'Association',
  definition: 'Définition',
  ordre: 'Ordre',
}
import { FolderClosed, Plus, ChevronRight, ChevronDown, FileText, Layers, Trash2, Globe, Copy, Eye, Loader2, FolderPlus, FileQuestion, CheckSquare, ListOrdered, Network, BarChart3, FolderMinus, FolderInput, GraduationCap } from 'lucide-vue-next'
import groupService, { type BinderClassRef } from '../../services/groupService'
import classService, { type ClassInfo } from '../../services/classService'
import type { BinderItemType } from '../../stores/binders'

const bindersStore = useBindersStore()
const notesStore = useNotesStore()
const decksStore = useDecksStore()
const revisionStore = useRevisionStore()
const tagsStore = useTagsStore()
const router = useRouter()
const route = useRoute()

const currentBinderId = ref<string | null>(null)

async function fetchMissingBinder(binderId: string) {
  try {
    const response = await api.get(`/binders/${binderId}`)
    const fetchedBinder = response.data
    if (!bindersStore.binders.some(b => b.id === fetchedBinder.id)) {
      bindersStore.binders.push(fetchedBinder)
    }
  } catch (error) {
    console.error('Erreur lors du chargement du classeur', error)
  }
}

watch(() => route.params.id, (newId) => {
  currentBinderId.value = (newId as string) || null
}, { immediate: true })

watch(currentBinderId, async (newVal) => {
  if (newVal !== null) {
    const exists = bindersStore.binders.some(b => b.id === newVal)
    if (!exists) {
      await fetchMissingBinder(newVal)
    }
  }
}, { immediate: true })
const showModal = ref(false)
const newFolderName = ref('')
const folderTags = ref<Tag[]>([])
const selectedTagId = ref<number | null>(null)

// Menu d'ajout unifié + modales de contenu
const showAddMenu = ref(false)
const showDeckModal = ref(false)
const newDeckName = ref('')
const showRevisionModal = ref(false)
const revisionInitialType = ref<RevisionItemType>('basic')
const revisionDeckId = ref<number | undefined>(undefined)

const addMenu = [
  { label: 'Sous-dossier', icon: FolderPlus, action: () => closeMenuThen(openCreateModal) },
  { label: 'Élément existant', icon: FolderInput, action: () => closeMenuThen(openAttachModal) },
  { label: 'Note', icon: FileText, action: () => closeMenuThen(addNote) },
  { label: 'Jeu de révision', icon: Layers, action: () => closeMenuThen(openNewDeck) },
  { label: 'Carte', icon: Layers, action: () => closeMenuThen(() => openRevisionItem('basic')) },
  { label: 'QCM', icon: FileQuestion, action: () => closeMenuThen(() => openRevisionItem('qcm')) },
  { label: 'Vrai / Faux', icon: CheckSquare, action: () => closeMenuThen(() => openRevisionItem('vf')) },
  { label: 'Définition', icon: FileText, action: () => closeMenuThen(() => openRevisionItem('definition')) },
  { label: 'Ordre', icon: ListOrdered, action: () => closeMenuThen(() => openRevisionItem('ordre')) },
  { label: 'Association', icon: Network, action: () => closeMenuThen(() => openRevisionItem('association')) },
]

function closeMenuThen(fn: () => void) {
  showAddMenu.value = false
  fn()
}

async function addNote() {
  const note = await notesStore.createNote('Nouvelle note', '', currentBinderId.value)
  router.push(`/notes/${note.id}?edit=true`)
}

function openNewDeck() {
  newDeckName.value = ''
  showDeckModal.value = true
}

async function createDeck() {
  if (!newDeckName.value.trim()) return
  await decksStore.createDeck(newDeckName.value.trim(), '', currentBinderId.value)
  showDeckModal.value = false
}

function openRevisionItem(type: RevisionItemType) {
  revisionInitialType.value = type
  revisionDeckId.value = undefined
  showRevisionModal.value = true
}

function openRevisionItemForDeck(deckId: number) {
  revisionInitialType.value = 'basic'
  revisionDeckId.value = deckId
  showRevisionModal.value = true
}

async function onRevisionCreated() {
  showRevisionModal.value = false
  await Promise.all([decksStore.fetchDecks(), revisionStore.fetchSets()])
}

// Refs pour le partage du classeur
const showShareModal = ref(false)
const shareIsPublic = ref(false)
const shareDescription = ref('')
const shareTags = ref('')

onMounted(async () => {
  await Promise.all([
    bindersStore.fetchBinders(),
    notesStore.fetchNotes(),
    decksStore.fetchDecks(),
    revisionStore.fetchSets(),
    tagsStore.fetchTags()
  ])
})

async function filterByTag(tagId: number | null) {
  selectedTagId.value = tagId
  await bindersStore.fetchBinders(tagId)
}

// Subfolders of the current binder
const currentSubBinders = computed(() => {
  return bindersStore.binders.filter(b => b.parent_id === currentBinderId.value)
})

// Notes belonging to the current binder
const currentNotes = computed(() => {
  return notesStore.notes.filter(n => n.binder_id === currentBinderId.value)
})

// Decks belonging to the current binder
const currentDecks = computed(() => {
  return decksStore.decks.filter(d => d.binder_id === currentBinderId.value)
})

// Revision sets (qcm/vf/…) belonging to the current binder
const currentSets = computed(() => {
  return revisionStore.sets.filter(s => s.binder_id === currentBinderId.value)
})

function openSet(set: { id: number; type: RevisionType }) {
  // QCM → passage scoré ; autres types → étude générique (révéler/corriger + SM-2).
  const path = set.type === 'qcm' ? 'run' : 'study'
  router.push(`/revision/sets/${set.id}/${path}`)
}

// --- C1 : rattacher / détacher des éléments existants --------------------------
const showAttachModal = ref(false)
const attaching = ref(false)
const selected = ref<Record<string, { type: BinderItemType; id: number | string }>>({})

const attachableGroups = computed(() => {
  const cur = currentBinderId.value
  return [
    {
      type: 'note' as BinderItemType, label: 'Notes',
      items: notesStore.notes.filter(n => n.binder_id !== cur && !n.read_only).map(n => ({ id: n.id, label: n.title })),
    },
    {
      type: 'deck' as BinderItemType, label: 'Jeux de révision',
      items: decksStore.decks.filter(d => d.binder_id !== cur).map(d => ({ id: d.id, label: d.name })),
    },
    {
      type: 'set' as BinderItemType, label: 'Ensembles de révision',
      items: revisionStore.sets.filter(s => s.binder_id !== cur).map(s => ({ id: s.id, label: s.name })),
    },
  ]
})

const selectedCount = computed(() => Object.keys(selected.value).length)
function keyOf(type: BinderItemType, id: number | string) { return `${type}:${id}` }
function isSelected(type: BinderItemType, id: number | string) { return keyOf(type, id) in selected.value }
function toggleSelect(type: BinderItemType, id: number | string) {
  const k = keyOf(type, id)
  if (k in selected.value) { delete selected.value[k] }
  else { selected.value[k] = { type, id } }
}

function openAttachModal() {
  selected.value = {}
  showAttachModal.value = true
}

async function refreshContentStores() {
  await Promise.all([notesStore.fetchNotes(), decksStore.fetchDecks(), revisionStore.fetchSets()])
}

async function confirmAttach() {
  if (!currentBinderId.value || selectedCount.value === 0) return
  attaching.value = true
  try {
    await bindersStore.attachItems(currentBinderId.value, Object.values(selected.value))
    await refreshContentStores()
    showAttachModal.value = false
  } catch (e) {
    console.error("Erreur lors du rattachement d'éléments", e)
  } finally {
    attaching.value = false
  }
}

async function detachItem(type: BinderItemType, id: number | string) {
  if (!currentBinderId.value) return
  try {
    await bindersStore.detachItems(currentBinderId.value, [{ type, id }])
    await refreshContentStores()
  } catch (e) {
    console.error("Erreur lors du retrait de l'élément", e)
  }
}

// Breadcrumbs trace path from root
const breadcrumbs = computed(() => {
  if (currentBinderId.value === null) return []
  
  const trail: Binder[] = []
  let current = bindersStore.binders.find(b => b.id === currentBinderId.value)
  
  while (current) {
    trail.unshift(current)
    const parentId = current.parent_id
    current = parentId !== null ? bindersStore.binders.find(b => b.id === parentId) : undefined
  }
  
  return trail
})

function openCreateModal() {
  newFolderName.value = ''
  folderTags.value = []
  showModal.value = true
}

async function createFolder() {
  if (newFolderName.value.trim()) {
    const binder = await bindersStore.createBinder(newFolderName.value.trim(), currentBinderId.value)
    if (folderTags.value.length > 0) {
      const updatedTags = await tagsStore.setTagsForEntity('binders', binder.id, folderTags.value.map(tag => tag.id))
      binder.tags = updatedTags
    }
    showModal.value = false
  }
}

async function confirmDelete(folder: Binder) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer le dossier "${folder.name}" et tous ses sous-dossiers ?`)) {
    await bindersStore.deleteBinder(folder.id)
  }
}

const currentBinder = computed(() => {
  if (currentBinderId.value === null) return null
  return bindersStore.binders.find(b => b.id === currentBinderId.value) || null
})

import { useAuthStore } from '../../stores/auth'
const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const isOwner = computed(() => {
  if (currentBinderId.value === null) return true
  return !currentBinder.value || currentBinder.value.user_id === currentUserId.value
})

const cloning = ref(false)
async function cloneBinder() {
  if (currentBinderId.value === null) return
  cloning.value = true
  try {
    const response = await api.post(`/packages/${currentBinderId.value}/clone`)
    const cloned = response.data
    await bindersStore.fetchBinders()
    router.push(`/binders/${cloned.id}`)
  } catch (err) {
    console.error('Erreur lors du clonage du classeur', err)
    alert('Impossible de copier ce classeur.')
  } finally {
    cloning.value = false
  }
}


function openShareModal() {
  if (!currentBinder.value) return
  shareIsPublic.value = currentBinder.value.is_public || false
  shareDescription.value = currentBinder.value.description || ''
  shareTags.value = currentBinder.value.tags ? currentBinder.value.tags.map(tag => tag.name).join(', ') : ''
  showShareModal.value = true
}

async function saveShareSettings() {
  if (!currentBinder.value) return
  const tagsArray = shareTags.value.split(',')
    .map(t => t.trim())
    .filter(t => t.length > 0)
  
  await bindersStore.updateBinder(currentBinder.value.id, {
    is_public: shareIsPublic.value,
    description: shareDescription.value.trim() || null,
    tags: tagsArray.length > 0 ? tagsArray : null
  })
  
  showShareModal.value = false
}

// --- B2 : partager le classeur à une classe (par référence, auto-actualisé) ----
const showClassShareModal = ref(false)
const myClasses = ref<ClassInfo[]>([])
const sharedClasses = ref<BinderClassRef[]>([])
const classShareBusy = ref(false)

// Classes que l'utilisateur anime (créateur) — seules cibles de partage proposées.
const ownedClasses = computed(() =>
  myClasses.value.filter(c => c.created_by === currentUserId.value)
)
const isSharedToClass = computed(() => sharedClasses.value.length > 0)

async function loadSharedClasses() {
  if (currentBinderId.value === null || !isOwner.value) {
    sharedClasses.value = []
    return
  }
  try {
    sharedClasses.value = await groupService.getBinderClasses(currentBinderId.value)
  } catch {
    sharedClasses.value = []
  }
}

async function openClassShareModal() {
  if (currentBinderId.value === null) return
  showClassShareModal.value = true
  classShareBusy.value = true
  try {
    myClasses.value = await classService.getMyClasses()
    await loadSharedClasses()
  } finally {
    classShareBusy.value = false
  }
}

function isClassShared(classId: number) {
  return sharedClasses.value.some(c => c.id === classId)
}

async function toggleClassShare(c: ClassInfo) {
  if (currentBinderId.value === null) return
  classShareBusy.value = true
  try {
    if (isClassShared(c.id)) {
      await groupService.unshareBinder(c.id, currentBinderId.value)
    } else {
      await groupService.shareBinder(c.id, currentBinderId.value, 'read')
    }
    await loadSharedClasses()
  } catch {
    alert('Action impossible sur cette classe.')
  } finally {
    classShareBusy.value = false
  }
}

// Met à jour l'indicateur « partagé » au changement de classeur.
watch(currentBinderId, loadSharedClasses, { immediate: true })
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.animate-scale-up {
  animation: scaleUp 0.15s ease-out forwards;
}
</style>
