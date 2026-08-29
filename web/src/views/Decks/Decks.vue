<template>
  <div class="space-y-6 animate-fade-in">
    <!-- View 1: Decks List (Main View) -->
    <template v-if="!selectedDeck">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-xl font-bold">Mes Decks de Flashcards</h1>
          <p class="text-xs text-ink-subtle dark:text-ink-muted mt-1">
            Créez et révisez vos cartes mémoire avec l'algorithme de répétition espacée SM-2
          </p>
        </div>

        <div class="flex items-center gap-3">
          <button
            class="inline-flex items-center gap-2 px-4 py-2 border border-line dark:border-line rounded-xl text-sm font-semibold text-ink-muted dark:text-ink-subtle hover:bg-surface-soft dark:hover:bg-surface-soft active:scale-95 transition-all cursor-pointer"
            @click="showAnkiModal = true"
          >
            <Upload class="w-4 h-4 text-primary" />
            Importer Anki
          </button>

          <button
            class="inline-flex items-center gap-2 px-4 py-2 border border-line dark:border-line rounded-xl text-sm font-semibold text-ink-muted dark:text-ink-subtle hover:bg-surface-soft dark:hover:bg-surface-soft active:scale-95 transition-all cursor-pointer"
            @click="openGenerateModal"
          >
            <Sparkles class="w-4 h-4 text-warning" />
            Générer depuis Notes / Classeurs
          </button>

          <button
            class="inline-flex items-center gap-2 px-4 py-2 border border-transparent rounded-xl text-sm font-semibold text-white bg-primary hover:bg-primary-strong active:scale-95 transition-all shadow-lg shadow-elev-primary cursor-pointer"
            @click="openCreateDeckModal"
          >
            <Plus class="w-4 h-4" />
            Nouveau Deck
          </button>
        </div>
      </div>

      <div
        class="flex flex-wrap items-center gap-2 rounded-2xl border border-line bg-surface p-3 dark:border-line dark:bg-surface-soft"
      >
        <span class="text-xs font-bold uppercase tracking-wider text-ink-subtle">Filtrer</span>
        <button
          type="button"
          class="rounded-xl px-3 py-1.5 text-xs font-bold"
          :class="
            selectedTagId === null
              ? 'bg-primary text-white'
              : 'bg-surface-soft text-ink-muted dark:bg-surface-soft dark:text-ink-subtle'
          "
          @click="filterByTag(null)"
        >
          Tous
        </button>
        <button
          v-for="tag in tagsStore.tags"
          :key="tag.id"
          type="button"
          class="rounded-xl px-3 py-1.5 text-xs font-bold"
          :style="
            selectedTagId === tag.id
              ? { backgroundColor: tag.color || '#4F46E5', color: '#fff' }
              : undefined
          "
          :class="
            selectedTagId === tag.id
              ? ''
              : 'bg-surface-soft text-ink-muted dark:bg-surface-soft dark:text-ink-subtle'
          "
          @click="filterByTag(tag.id)"
        >
          {{ tag.name }}
        </button>
      </div>

      <!-- Decks Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="deck in decksStore.decks"
          :key="deck.id"
          class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm flex flex-col justify-between hover:shadow-md transition-all duration-200 group"
        >
          <div>
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-2 flex-wrap">
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold text-primary bg-primary-soft dark:bg-primary-soft dark:text-primary uppercase tracking-wider"
                >
                  {{ deck.card_count }} cartes
                </span>
                <span
                  v-if="deck.reversed"
                  class="inline-flex items-center px-2 py-1 rounded-lg text-[10px] font-bold text-warning bg-warning-soft dark:bg-warning-soft dark:text-warning uppercase tracking-wider"
                  title="Mode inversé activé"
                >
                  ⇄ Inversé
                </span>
              </div>

              <div
                class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <button
                  class="p-1 text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle rounded-lg hover:bg-surface-soft dark:hover:bg-surface-soft"
                  title="Modifier"
                  @click.stop="openEditDeckModal(deck)"
                >
                  <Edit class="w-4 h-4" />
                </button>
                <button
                  class="p-1 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft dark:hover:bg-danger-soft"
                  title="Supprimer"
                  @click.stop="deleteDeck(deck)"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>

            <h3 class="font-bold text-lg text-ink dark:text-white mt-4">{{ deck.name }}</h3>
            <p class="text-xs text-ink-muted dark:text-ink-subtle mt-2 line-clamp-2">
              {{ deck.description || 'Aucune description' }}
            </p>
            <div v-if="deck.tags?.length" class="mt-3 flex flex-wrap gap-1.5">
              <TagBadge v-for="tag in deck.tags" :key="tag.id" :tag="tag" />
            </div>
          </div>

          <div class="flex items-center gap-3 mt-6 pt-4 border-t border-line-soft dark:border-line">
            <!-- Study button -->
            <button
              class="flex-1 px-4 py-2 border border-transparent rounded-xl text-xs font-bold text-white bg-primary hover:bg-primary-strong active:scale-95 transition-all text-center"
              @click="router.push(`/decks/${deck.id}/study`)"
            >
              Étudier
            </button>
            <!-- View cards button -->
            <button
              class="flex-1 px-4 py-2 border border-line dark:border-line rounded-xl text-xs font-bold text-ink-muted hover:bg-surface-soft dark:text-ink-subtle dark:hover:bg-surface-soft active:scale-95 transition-all"
              @click="selectDeck(deck)"
            >
              Gérer cartes
            </button>
          </div>
        </div>

        <div
          v-if="decksStore.decks.length === 0"
          class="col-span-full border-2 border-dashed border-line dark:border-line rounded-3xl p-12 flex flex-col items-center justify-center text-center text-ink-subtle"
        >
          <Layers class="w-12 h-12 text-ink-subtle dark:text-ink mb-3" />
          <h4 class="font-bold text-ink dark:text-ink-subtle">Aucun deck disponible</h4>
          <p class="text-xs mt-1">Commencez par créer votre premier deck pour étudier !</p>
          <button
            class="mt-4 px-4 py-2 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl transition-all"
            @click="openCreateDeckModal"
          >
            Créer un Deck
          </button>
        </div>
      </div>
    </template>

    <!-- View 2: Cards Detail View (Manage Cards inside selected Deck) -->
    <template v-else>
      <div class="flex items-center gap-2 text-sm font-semibold">
        <button
          class="text-ink-muted hover:text-primary dark:text-ink-subtle dark:hover:text-primary"
          @click="selectedDeck = null"
        >
          Decks
        </button>
        <ChevronRight class="w-4 h-4 text-ink-subtle" />
        <span class="text-ink dark:text-white font-bold">{{ selectedDeck.name }}</span>
      </div>

      <div
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl p-6 shadow-sm"
      >
        <div>
          <h2 class="text-lg font-bold">{{ selectedDeck.name }}</h2>
          <p class="text-xs text-ink-muted mt-1">{{ selectedDeck.description }}</p>
          <p class="text-xs font-semibold text-primary uppercase tracking-wider mt-2">
            {{ currentCards.length }} cartes au total
          </p>
        </div>

        <div class="flex items-center gap-3">
          <button
            class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-primary hover:bg-primary-strong transition-all shadow-md shadow-elev-primary"
            @click="router.push(`/decks/${selectedDeck.id}/study`)"
          >
            Lancer l'étude
          </button>
          <button
            class="px-4 py-2 text-sm font-semibold rounded-xl border border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft transition-all text-ink-muted dark:text-ink-subtle"
            @click="openCreateCardModal"
          >
            Ajouter une carte
          </button>
        </div>
      </div>

      <!-- Cards List -->
      <div class="space-y-4">
        <h3
          class="text-xs font-semibold text-ink-subtle dark:text-ink-muted uppercase tracking-wider"
        >
          Cartes du Deck
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="card in currentCards"
            :key="card.id"
            class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-2xl p-5 shadow-sm hover:border-line dark:hover:border-line transition-colors group flex flex-col justify-between"
          >
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <span class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest"
                  >Recto (Front)</span
                >
                <p class="text-sm font-bold text-ink dark:text-ink-subtle mt-1">{{ card.front }}</p>
              </div>
              <div
                class="border-t sm:border-t-0 sm:border-l border-line-soft dark:border-line pt-3 sm:pt-0 sm:pl-4"
              >
                <span class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest"
                  >Verso (Back)</span
                >
                <p class="text-sm text-ink-muted dark:text-ink-subtle mt-1">{{ card.back }}</p>
              </div>
            </div>

            <div
              class="flex items-center justify-between gap-4 mt-6 pt-3 border-t border-line-soft dark:border-line"
            >
              <!-- SM-2 Stats badge -->
              <span class="text-[10px] text-ink-subtle font-semibold uppercase tracking-wider">
                Intervalle : {{ card.interval }}j | EF : {{ card.ease_factor.toFixed(2) }}
                <template v-if="(card.tuning ?? 1) !== 1"> | ×{{ card.tuning }}</template>
              </span>
              <div class="flex items-center gap-1">
                <button
                  class="p-1 rounded-lg hover:bg-surface-soft dark:hover:bg-surface-soft"
                  :class="
                    historyCardId === card.id
                      ? 'text-primary'
                      : 'text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle'
                  "
                  title="Courbe d'apprentissage"
                  @click="toggleHistory(card)"
                >
                  <Activity class="w-3.5 h-3.5" />
                </button>
                <button
                  class="p-1 text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle rounded-lg hover:bg-surface-soft dark:hover:bg-surface-soft opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Modifier"
                  @click="openEditCardModal(card)"
                >
                  <Edit class="w-3.5 h-3.5" />
                </button>
                <button
                  class="p-1 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft dark:hover:bg-danger-soft opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Supprimer"
                  @click="deleteCard(card.id)"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <!-- Courbe d'apprentissage (dépliée à la demande) -->
            <div
              v-if="historyCardId === card.id"
              class="mt-3 pt-3 border-t border-line-soft dark:border-line text-primary"
            >
              <div
                v-if="historyLoading"
                class="flex items-center gap-2 text-xs text-ink-subtle py-3 justify-center"
              >
                <RefreshCw class="w-3.5 h-3.5 animate-spin" /> Chargement…
              </div>
              <LearningCurve v-else :entries="historyEntries" />
            </div>
          </div>

          <div
            v-if="currentCards.length === 0"
            class="col-span-full border-2 border-dashed border-line dark:border-line rounded-2xl p-12 flex flex-col items-center justify-center text-center text-ink-subtle"
          >
            <Layers class="w-10 h-10 text-ink-subtle dark:text-ink mb-2" />
            <p class="text-xs font-semibold uppercase tracking-wider">Aucune carte dans ce deck</p>
            <button
              class="mt-3 px-3.5 py-1.5 text-xs font-bold text-white bg-primary hover:bg-primary-strong rounded-xl transition-all"
              @click="openCreateCardModal"
            >
              Ajouter une Carte
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Create/Edit Deck Modal -->
    <div v-if="showDeckModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div
        class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm"
        @click="showDeckModal = false"
      ></div>
      <div
        class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up"
      >
        <h3 class="text-lg font-bold mb-4">
          {{ isEditingDeck ? 'Modifier le deck' : 'Créer un nouveau deck' }}
        </h3>
        <form @submit.prevent="submitDeckForm">
          <div class="space-y-4">
            <div>
              <label
                for="deck-name"
                class="block text-xs font-semibold uppercase tracking-wider text-ink-subtle mb-2"
                >Nom du deck</label
              >
              <input
                id="deck-name"
                v-model="deckForm.name"
                type="text"
                required
                class="block w-full px-4 py-3 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-medium"
                placeholder="Ex: Vocabulaire Espagnol"
              />
            </div>
            <div>
              <label
                for="deck-desc"
                class="block text-xs font-semibold uppercase tracking-wider text-ink-subtle mb-2"
                >Description</label
              >
              <textarea
                id="deck-desc"
                v-model="deckForm.description"
                rows="3"
                class="block w-full px-4 py-3 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-medium"
                placeholder="Ex: Verbes irréguliers et vocabulaire utile pour voyager."
              ></textarea>
            </div>
            <div class="flex items-start gap-3 rounded-xl border border-line dark:border-line p-3">
              <input
                id="deck-reversed"
                v-model="deckForm.reversed"
                type="checkbox"
                class="mt-0.5 accent-primary shrink-0"
              />
              <label for="deck-reversed" class="cursor-pointer">
                <span class="block text-sm font-semibold text-ink dark:text-ink-subtle"
                  >Mode inversé</span
                >
                <span class="block text-xs text-ink-subtle"
                  >Réviser aussi chaque carte dans le sens verso → recto (suivi SM-2
                  distinct).</span
                >
              </label>
            </div>
            <div>
              <label
                for="deck-tuning"
                class="block text-xs font-semibold uppercase tracking-wider text-ink-subtle mb-2"
              >
                Fine-tuning par défaut — {{ tuningLabel(deckForm.tuning_default) }}
              </label>
              <input
                id="deck-tuning"
                v-model.number="deckForm.tuning_default"
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                class="w-full accent-primary"
              />
              <div class="flex justify-between text-[10px] text-ink-subtle mt-1">
                <span>plus fréquent</span><span>plus espacé</span>
              </div>
            </div>
            <div v-if="isEditingDeck">
              <label
                class="block text-xs font-semibold uppercase tracking-wider text-ink-subtle mb-2"
                >Tags</label
              >
              <TagSelector v-model="deckForm.tags" @change="saveDeckTags" />
            </div>
          </div>
          <div class="flex items-center justify-end gap-3 mt-6">
            <button
              type="button"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-ink-muted hover:bg-surface-soft dark:hover:bg-surface-soft"
              @click="showDeckModal = false"
            >
              Annuler
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-primary hover:bg-primary-strong"
            >
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create/Edit Card Modal -->
    <div v-if="showCardModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div
        class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm"
        @click="showCardModal = false"
      ></div>
      <div
        class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl w-full max-w-md p-6 relative z-10 shadow-2xl animate-scale-up"
      >
        <h3 class="text-lg font-bold mb-4">
          {{ isEditingCard ? 'Modifier la carte' : 'Ajouter une carte' }}
        </h3>
        <form @submit.prevent="submitCardForm">
          <div class="space-y-4">
            <div>
              <label
                for="card-front"
                class="block text-xs font-semibold uppercase tracking-wider text-ink-subtle mb-2"
                >Recto (Question / Terme)</label
              >
              <input
                id="card-front"
                v-model="cardForm.front"
                type="text"
                required
                class="block w-full px-4 py-3 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-medium"
                placeholder="Ex: El coche"
              />
            </div>
            <div>
              <label
                for="card-back"
                class="block text-xs font-semibold uppercase tracking-wider text-ink-subtle mb-2"
                >Verso (Réponse / Définition)</label
              >
              <textarea
                id="card-back"
                v-model="cardForm.back"
                required
                rows="3"
                class="block w-full px-4 py-3 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary text-sm font-medium"
                placeholder="Ex: La voiture"
              ></textarea>
            </div>
            <div v-if="isEditingCard">
              <label
                for="card-tuning"
                class="block text-xs font-semibold uppercase tracking-wider text-ink-subtle mb-2"
              >
                Fine-tuning — {{ tuningLabel(cardForm.tuning) }}
              </label>
              <input
                id="card-tuning"
                v-model.number="cardForm.tuning"
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                class="w-full accent-primary"
              />
              <div class="flex justify-between text-[10px] text-ink-subtle mt-1">
                <span>réviser plus souvent</span><span>réviser moins souvent</span>
              </div>
            </div>
          </div>
          <div class="flex items-center justify-end gap-3 mt-6">
            <button
              type="button"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-ink-muted hover:bg-surface-soft dark:hover:bg-surface-soft"
              @click="showCardModal = false"
            >
              Annuler
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-sm font-semibold rounded-xl text-white bg-primary hover:bg-primary-strong"
            >
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Anki Import Modal -->
    <AnkiImportModal
      :is-open="showAnkiModal"
      @close="showAnkiModal = false"
      @success="decksStore.fetchDecks"
    />

    <!-- Generate Flashcards Modal (génération IA depuis une note ou un classeur) -->
    <div v-if="showGenerateModal" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div
        class="absolute inset-0 bg-slate-950/40 backdrop-blur-sm"
        @click="showGenerateModal = false"
      ></div>
      <div
        class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl w-full max-w-lg p-6 relative z-10 shadow-2xl animate-scale-up space-y-6"
      >
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-bold text-ink dark:text-white flex items-center gap-2">
            <Sparkles class="w-5 h-5 text-primary" />
            Générer des Flashcards
          </h3>
          <button
            class="text-ink-subtle hover:text-ink-muted dark:hover:text-ink-subtle text-sm"
            @click="showGenerateModal = false"
          >
            ✕
          </button>
        </div>

        <p class="text-xs text-ink-muted -mt-2">
          L'IA analyse votre note ou votre classeur pour rédiger des questions/réponses ciblées,
          prêtes à réviser.
        </p>

        <div class="space-y-4">
          <!-- Source selection -->
          <div>
            <label class="block text-xs font-bold text-ink-subtle uppercase tracking-wider mb-2"
              >Source d'extraction</label
            >
            <div class="grid grid-cols-2 gap-4">
              <button
                class="p-3 border rounded-xl text-center font-semibold text-xs transition-all"
                :class="[
                  genSourceType === 'note'
                    ? 'border-primary bg-primary-soft text-primary dark:border-primary dark:bg-primary-soft dark:text-primary'
                    : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft',
                ]"
                @click="genSourceType = 'note'"
              >
                Une Note
              </button>
              <button
                class="p-3 border rounded-xl text-center font-semibold text-xs transition-all"
                :class="[
                  genSourceType === 'binder'
                    ? 'border-primary bg-primary-soft text-primary dark:border-primary dark:bg-primary-soft dark:text-primary'
                    : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft',
                ]"
                @click="genSourceType = 'binder'"
              >
                Un Classeur
              </button>
            </div>
          </div>

          <!-- Note Selector -->
          <div v-if="genSourceType === 'note'">
            <label class="block text-xs font-bold text-ink-subtle uppercase tracking-wider mb-2"
              >Sélectionnez la note</label
            >
            <select
              v-model="genNoteId"
              class="w-full px-3 py-2.5 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option :value="null" disabled>Choisir une note...</option>
              <option v-for="n in notesStore.notes" :key="n.id" :value="n.id">
                {{ n.title }}
              </option>
            </select>
          </div>

          <!-- Binder Selector -->
          <div v-if="genSourceType === 'binder'">
            <label class="block text-xs font-bold text-ink-subtle uppercase tracking-wider mb-2"
              >Sélectionnez le classeur</label
            >
            <select
              v-model="genBinderId"
              class="w-full px-3 py-2.5 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option :value="null" disabled>Choisir un classeur...</option>
              <option v-for="b in bindersStore.binders" :key="b.id" :value="b.id">
                {{ b.name }}
              </option>
            </select>
          </div>

          <!-- Target Deck Select -->
          <div>
            <label class="block text-xs font-bold text-ink-subtle uppercase tracking-wider mb-2"
              >Deck de destination</label
            >
            <div class="grid grid-cols-2 gap-4 mb-3">
              <button
                class="p-3 border rounded-xl text-center font-semibold text-xs transition-all"
                :class="[
                  genDeckTarget === 'new'
                    ? 'border-primary bg-primary-soft text-primary dark:border-primary dark:bg-primary-soft dark:text-primary'
                    : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft',
                ]"
                @click="genDeckTarget = 'new'"
              >
                Nouveau Deck
              </button>
              <button
                class="p-3 border rounded-xl text-center font-semibold text-xs transition-all"
                :class="[
                  genDeckTarget === 'existing'
                    ? 'border-primary bg-primary-soft text-primary dark:border-primary dark:bg-primary-soft dark:text-primary'
                    : 'border-line dark:border-line hover:bg-surface-soft dark:hover:bg-surface-soft',
                ]"
                :disabled="decksStore.decks.length === 0"
                @click="genDeckTarget = 'existing'"
              >
                Deck existant
              </button>
            </div>

            <!-- New Deck Name Input -->
            <div v-if="genDeckTarget === 'new'">
              <input
                v-model="genNewDeckName"
                type="text"
                placeholder="Nom du nouveau deck (ex: Chimie, Bio...)"
                class="w-full px-3 py-2 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <!-- Existing Deck Dropdown -->
            <div v-if="genDeckTarget === 'existing'">
              <select
                v-model="genExistingDeckId"
                class="w-full px-3 py-2.5 bg-surface-soft border border-line dark:bg-surface-soft dark:border-line rounded-xl text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option :value="null" disabled>Choisir un deck...</option>
                <option v-for="d in decksStore.decks" :key="d.id" :value="d.id">
                  {{ d.name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Coverage slider -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="block text-xs font-bold text-ink-subtle uppercase tracking-wider"
              >Taux de couverture</label
            >
            <span class="text-xs font-bold text-primary tabular-nums">{{ genCoverage }}%</span>
          </div>
          <input
            v-model.number="genCoverage"
            type="range"
            min="0"
            max="100"
            step="5"
            class="w-full accent-primary cursor-pointer"
            aria-label="Taux de couverture des notions"
          />
          <p class="mt-1.5 text-[11px] leading-snug text-ink-muted dark:text-ink-subtle">
            Part des <strong>notions</strong> importantes de la note transformées en flashcards. 100
            % = toutes les notions à réviser (définitions, nuances, faits clés) — pas le texte brut.
          </p>
        </div>

        <!-- Alert messages or status -->
        <div
          v-if="genStatusMessage"
          class="p-3 text-xs rounded-xl"
          :class="[
            genStatusIsError
              ? 'bg-danger-soft text-danger dark:bg-danger-soft dark:text-danger'
              : 'bg-primary-soft text-primary dark:bg-primary-soft dark:text-primary',
          ]"
        >
          {{ genStatusMessage }}
        </div>

        <div class="flex gap-3 justify-end border-t border-line dark:border-line pt-4">
          <button
            class="px-4 py-2 text-xs font-bold text-ink-muted hover:text-ink dark:text-ink-subtle dark:hover:text-ink-subtle"
            @click="showGenerateModal = false"
          >
            Fermer
          </button>
          <button
            :disabled="!isReadyToGenerate"
            class="px-5 py-2 text-xs font-bold text-white bg-primary hover:bg-primary-strong disabled:opacity-50 rounded-xl transition-all shadow-md active:scale-95"
            @click="executeFlashcardGeneration"
          >
            {{ genDeckTarget === 'new' ? 'Générer' : 'Mettre à jour' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDecksStore } from '../../stores/decks'
import type { Deck, Flashcard, CardHistoryEntry } from '../../stores/decks'
import { useNotesStore } from '../../stores/notes'
import { useBindersStore } from '../../stores/binders'
import { useTagsStore, type Tag } from '../../stores/tags'
import api from '../../services/api'
import TagBadge from '../../components/ui/TagBadge.vue'
import TagSelector from '../../components/ui/TagSelector.vue'
import LearningCurve from '../../components/decks/LearningCurve.vue'
import {
  Plus,
  ChevronRight,
  Layers,
  Edit,
  Trash2,
  Upload,
  Activity,
  RefreshCw,
  Sparkles,
} from '@lucide/vue'
import AnkiImportModal from '../../components/decks/AnkiImportModal.vue'

const decksStore = useDecksStore()
const notesStore = useNotesStore()
const bindersStore = useBindersStore()
const tagsStore = useTagsStore()
const router = useRouter()
const route = useRoute()

const selectedDeck = ref<Deck | null>(null)
const selectedTagId = ref<number | null>(null)
const showAnkiModal = ref(false)

// Deck Form Modal
const showDeckModal = ref(false)
const isEditingDeck = ref(false)
const deckForm = ref<{
  id: number
  name: string
  description: string
  reversed: boolean
  tuning_default: number
  tags: Tag[]
}>({ id: 0, name: '', description: '', reversed: false, tuning_default: 1.0, tags: [] })

// Card Form Modal
const showCardModal = ref(false)
const isEditingCard = ref(false)
const cardForm = ref({ id: 0, front: '', back: '', tuning: 1.0 })

// Courbe d'apprentissage (historique par carte)
const historyCardId = ref<number | null>(null)
const historyEntries = ref<CardHistoryEntry[]>([])
const historyLoading = ref(false)

// Filtered cards for selected deck
const currentCards = computed(() => {
  if (!selectedDeck.value) return []
  return decksStore.cards.filter((c) => c.deck_id === selectedDeck.value!.id)
})

onMounted(async () => {
  await Promise.all([
    tagsStore.fetchTags(),
    decksStore.fetchDecks(),
    notesStore.fetchNotes(),
    bindersStore.fetchBinders(),
  ])
  const deckIdQuery = route.query.id
  if (deckIdQuery) {
    const deckId = parseInt(deckIdQuery as string)
    const deck = decksStore.decks.find((d) => d.id === deckId)
    if (deck) {
      selectDeck(deck)
    }
  }
})

watch(
  () => route.query.id,
  (newId) => {
    if (newId) {
      const deckId = parseInt(newId as string)
      const deck = decksStore.decks.find((d) => d.id === deckId)
      if (deck) {
        selectDeck(deck)
      }
    } else {
      selectedDeck.value = null
    }
  },
)

async function filterByTag(tagId: number | null) {
  selectedTagId.value = tagId
  await decksStore.fetchDecks(tagId)
}

function selectDeck(deck: Deck) {
  selectedDeck.value = deck
}

// Deck CRUD Methods
function openCreateDeckModal() {
  isEditingDeck.value = false
  deckForm.value = {
    id: 0,
    name: '',
    description: '',
    reversed: false,
    tuning_default: 1.0,
    tags: [],
  }
  showDeckModal.value = true
}

function openEditDeckModal(deck: Deck) {
  isEditingDeck.value = true
  deckForm.value = {
    id: deck.id,
    name: deck.name,
    description: deck.description,
    reversed: deck.reversed,
    tuning_default: deck.tuning_default,
    tags: deck.tags || [],
  }
  showDeckModal.value = true
}

async function submitDeckForm() {
  if (isEditingDeck.value) {
    await decksStore.updateDeck(
      deckForm.value.id,
      deckForm.value.name,
      deckForm.value.description,
      {
        reversed: deckForm.value.reversed,
        tuning_default: deckForm.value.tuning_default,
      },
    )
    await saveDeckTags(deckForm.value.tags)
  } else {
    await decksStore.createDeck(
      deckForm.value.name,
      deckForm.value.description,
      null,
      deckForm.value.reversed,
      deckForm.value.tuning_default,
    )
  }
  showDeckModal.value = false
}

async function saveDeckTags(tags: Tag[]) {
  if (!isEditingDeck.value || deckForm.value.id === 0) return
  const updatedTags = await tagsStore.setTagsForEntity(
    'decks',
    deckForm.value.id,
    tags.map((tag) => tag.id),
  )
  const deck = decksStore.decks.find((item) => item.id === deckForm.value.id)
  if (deck) deck.tags = updatedTags
  deckForm.value.tags = updatedTags
}

async function deleteDeck(deck: Deck) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer le deck "${deck.name}" et toutes ses cartes ?`)) {
    await decksStore.deleteDeck(deck.id)
    if (selectedDeck.value?.id === deck.id) selectedDeck.value = null
  }
}

// Card CRUD Methods
function openCreateCardModal() {
  isEditingCard.value = false
  cardForm.value = { id: 0, front: '', back: '', tuning: 1.0 }
  showCardModal.value = true
}

function openEditCardModal(card: Flashcard) {
  isEditingCard.value = true
  cardForm.value = { id: card.id, front: card.front, back: card.back, tuning: card.tuning ?? 1.0 }
  showCardModal.value = true
}

async function submitCardForm() {
  if (!selectedDeck.value) return

  if (isEditingCard.value) {
    await decksStore.updateCard(
      cardForm.value.id,
      cardForm.value.front,
      cardForm.value.back,
      cardForm.value.tuning,
    )
  } else {
    await decksStore.createCard(selectedDeck.value.id, cardForm.value.front, cardForm.value.back)
  }
  showCardModal.value = false
}

async function deleteCard(cardId: number) {
  if (confirm('Voulez-vous supprimer cette carte ?')) {
    await decksStore.deleteCard(cardId)
    if (historyCardId.value === cardId) historyCardId.value = null
  }
}

async function toggleHistory(card: Flashcard) {
  if (historyCardId.value === card.id) {
    historyCardId.value = null
    return
  }
  if (!selectedDeck.value) return
  historyCardId.value = card.id
  historyLoading.value = true
  historyEntries.value = []
  try {
    historyEntries.value = await decksStore.fetchCardHistory(selectedDeck.value.id, card.id)
  } catch (e) {
    console.error('Erreur de chargement de la courbe', e)
  } finally {
    historyLoading.value = false
  }
}

// Libellé lisible du fine-tuning (multiplicateur SM-2).
function tuningLabel(t: number): string {
  if (t < 1) return `révision +fréquente (×${t})`
  if (t > 1) return `révision +espacée (×${t})`
  return 'normal (×1)'
}

// Flashcard Generation state variables and functions
const showGenerateModal = ref(false)
const genSourceType = ref<'note' | 'binder'>('note')
const genNoteId = ref<string | null>(null)
const genBinderId = ref<string | null>(null)
const genDeckTarget = ref<'new' | 'existing'>('new')
const genNewDeckName = ref('')
const genExistingDeckId = ref<number | null>(null)
// Taux de couverture des notions (0–100). Défaut équilibré à 75 %.
const genCoverage = ref(75)
const genStatusMessage = ref('')
const genStatusIsError = ref(false)

const isReadyToGenerate = computed(() => {
  if (genSourceType.value === 'note' && genNoteId.value === null) return false
  if (genSourceType.value === 'binder' && genBinderId.value === null) return false

  if (genDeckTarget.value === 'new') return genNewDeckName.value.trim().length > 0
  return genExistingDeckId.value !== null
})

function openGenerateModal() {
  genStatusMessage.value = ''
  genStatusIsError.value = false
  showGenerateModal.value = true
}

function extractFlashcardsFromText(text: string): { front: string; back: string }[] {
  const cards: { front: string; back: string }[] = []
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
    if (front && back && !cards.some((c) => c.front.toLowerCase() === front.toLowerCase())) {
      cards.push({ front, back })
    }
  }

  // 3. Colons: "Front : Back"
  const simpleColonRegex = /(?:^|\n)([^:\n]{3,35})\s*:\s*([^.\n]{10,200})/g
  while ((match = simpleColonRegex.exec(text)) !== null) {
    const front = match[1].trim()
    const back = match[2].trim()
    if (
      front.startsWith('#') ||
      front.startsWith('-') ||
      front.startsWith('*') ||
      front.startsWith('<!--')
    ) {
      continue
    }
    if (front && back && !cards.some((c) => c.front.toLowerCase() === front.toLowerCase())) {
      cards.push({ front, back })
    }
  }

  return cards
}

// Récupère le texte source local (pour le repli hors-ligne sans IA)
function localSourceText(): string {
  if (genSourceType.value === 'note') {
    const note = notesStore.notes.find((n) => n.id === genNoteId.value)
    return note ? note.content : ''
  }
  const notesInBinder = notesStore.notes.filter((n) => n.binder_id === genBinderId.value)
  return notesInBinder.map((n) => n.content).join('\n\n')
}

async function executeFlashcardGeneration() {
  if (!isReadyToGenerate.value) return

  genStatusMessage.value =
    "Génération par IA en cours... (cela peut prendre jusqu'à une minute, ne fermez pas la fenêtre)"
  genStatusIsError.value = false

  try {
    let subjectName = ''
    if (genSourceType.value === 'note') {
      const note = notesStore.notes.find((n) => n.id === genNoteId.value)
      subjectName = note ? note.title : 'la note'
    } else {
      const binder = bindersStore.binders.find((b) => b.id === genBinderId.value)
      subjectName = binder ? `classeur ${binder.name}` : 'le classeur'
    }

    // 1. Génération par IA (backend Gemini). Repli sur l'extraction locale
    //    par motifs si l'IA est indisponible (clé absente, réseau…).
    let extracted: { front: string; back: string }[] = []
    let usedFallback = false
    try {
      const payload: Record<string, unknown> =
        genSourceType.value === 'note'
          ? { source_type: 'note', note_id: genNoteId.value, coverage: genCoverage.value }
          : { source_type: 'binder', binder_id: genBinderId.value, coverage: genCoverage.value }
      // Deck existant ciblé : on transmet son id pour que l'IA voie les cartes
      // déjà présentes et évite d'en régénérer des variantes (pertinence du deck).
      if (genDeckTarget.value === 'existing' && genExistingDeckId.value) {
        payload.deck_id = genExistingDeckId.value
      }
      // Génération IA longue : on dépasse le timeout global (10 s) et le
      // timeout backend Gemini (90 s) pour ne pas couper une requête qui aboutit.
      const res = await api.post('/flashcards/generate', payload, { timeout: 120000 })
      extracted = res.data.flashcards || []
    } catch (aiErr) {
      const status = (aiErr as { response?: { status?: number } })?.response?.status
      const backendMsg = (aiErr as { response?: { data?: { error?: { message?: string } } } })
        ?.response?.data?.error?.message

      // 401/429/400 : ce n'est pas « l'IA indisponible » → message précis, pas de repli.
      if (status === 401) {
        genStatusIsError.value = true
        genStatusMessage.value =
          'Votre session a expiré. Reconnectez-vous, puis relancez la génération.'
        return
      }
      if (status === 429) {
        genStatusIsError.value = true
        genStatusMessage.value =
          'Trop de générations en peu de temps. Patientez quelques minutes avant de réessayer.'
        return
      }
      if (status === 400) {
        genStatusIsError.value = true
        genStatusMessage.value =
          backendMsg || 'La source ne contient pas assez de texte pour générer des flashcards.'
        return
      }

      // 502 / réseau / autres : l'IA est réellement indisponible → repli local.
      console.warn("Génération IA indisponible, repli sur l'extraction locale.", aiErr)
      extracted = extractFlashcardsFromText(localSourceText())
      usedFallback = true
    }

    if (extracted.length === 0) {
      genStatusIsError.value = true
      genStatusMessage.value = usedFallback
        ? "L'IA est indisponible et aucune flashcard n'a pu être extraite localement. Réessayez plus tard ou ajoutez des définitions ('- **Concept** : explication') dans vos notes."
        : "L'IA n'a généré aucune flashcard. Vérifiez que la source contient assez de contenu."
      return
    }

    let deckId: number
    let isNew = false

    if (genDeckTarget.value === 'new') {
      if (!genNewDeckName.value.trim()) {
        genStatusIsError.value = true
        genStatusMessage.value = 'Veuillez spécifier un nom de deck.'
        return
      }
      const newDeck = await decksStore.createDeck(
        genNewDeckName.value.trim(),
        `Généré depuis ${subjectName}`,
      )
      deckId = newDeck.id
      isNew = true
    } else {
      if (!genExistingDeckId.value) {
        genStatusIsError.value = true
        genStatusMessage.value = 'Veuillez choisir un deck existant.'
        return
      }
      deckId = genExistingDeckId.value
    }

    // Fetch card cache
    const existingCards = await decksStore.fetchCardsForDeck(deckId)
    const existingFronts = new Set(existingCards.map((c) => c.front.toLowerCase().trim()))

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

    // Refresh local decks
    await decksStore.fetchDecks()

    genStatusIsError.value = false
    const sourceLabel = usedFallback
      ? ' (extraction locale, IA indisponible)'
      : ' (générées par IA)'
    genStatusMessage.value = `Succès ! ${addedCount} carte(s) ajoutée(s)${skippedCount > 0 ? ` (${skippedCount} doublon(s) ignoré(s))` : ''}${sourceLabel}.`

    if (isNew) {
      genNewDeckName.value = ''
      genDeckTarget.value = 'existing'
      genExistingDeckId.value = deckId
    }
  } catch (error) {
    console.error('Erreur de génération des cartes', error)
    genStatusIsError.value = true
    genStatusMessage.value =
      "Une erreur est survenue lors de la création ou de l'ajout des flashcards."
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleUp {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-scale-up {
  animation: scaleUp 0.15s ease-out forwards;
}
</style>
