<template>
  <PageContainer size="wide">
    <PageHeader title="Bibliothèque" :breadcrumbs="breadcrumbItems">
      <template #actions>
        <!-- Racine (currentBinderId === null) : aucun onglet/contenu typé n'a de
             sens ici (rien de typé ne peut s'attacher a binder_id === null tant
             qu'on n'a pas navigue dans "Non classe") -- seule action : creer un
             classeur de premier niveau, qui devient l'action primaire de la grille
             (cf. mockup Bibliotheque.dc.html). -->
        <template v-if="currentBinderId === null">
          <BaseButton v-if="isOwner" size="sm" @click="openCreateModal">
            <template #icon><FolderPlus class="w-4 h-4" /></template>
            Nouveau classeur
          </BaseButton>
        </template>
        <template v-else-if="isOwner">
          <BaseButton
            v-if="isRealBinderId"
            variant="secondary"
            size="sm"
            @click="router.push(`/revision/binders/${currentBinderId}/stats`)"
          >
            <template #icon><BarChart3 class="w-4 h-4" /></template>
            Stats
          </BaseButton>
          <BaseButton
            v-if="isRealBinderId"
            :variant="currentBinder?.is_public ? 'soft' : 'secondary'"
            size="sm"
            @click="openShareModal"
          >
            <template #icon><Globe class="w-4 h-4" /></template>
            {{ currentBinder?.is_public ? 'Public' : 'Partager' }}
          </BaseButton>
          <BaseButton
            v-if="isRealBinderId"
            :variant="isSharedToClass ? 'soft' : 'secondary'"
            size="sm"
            @click="openClassShareModal"
          >
            <template #icon><GraduationCap class="w-4 h-4" /></template>
            {{ isSharedToClass ? `Partagé (${sharedClasses.length})` : 'Classe' }}
          </BaseButton>

          <BaseButton
            v-if="isRealBinderId && currentDecks.length > 0"
            size="sm"
            @click="reviseBinder"
          >
            <template #icon><Brain class="w-4 h-4" /></template>
            Réviser ce dossier
          </BaseButton>

          <BaseButton data-test="primary-action-button" size="sm" @click="primaryAction">
            <template #icon><component :is="primaryActionIcon" class="w-4 h-4" /></template>
            {{ primaryActionLabel }}
          </BaseButton>

          <div class="relative">
            <BaseButton variant="secondary" size="sm" @click="showAddMenu = !showAddMenu">
              <template #icon><Plus class="w-4 h-4" /></template>
              Ajouter
              <ChevronDown class="w-4 h-4" />
            </BaseButton>
            <template v-if="showAddMenu">
              <div class="fixed inset-0 z-10" @click="showAddMenu = false"></div>
              <div
                class="absolute right-0 mt-2 w-60 bg-surface border border-line rounded-2xl shadow-elev-3 z-20 p-1.5 animate-pop-in"
              >
                <button
                  v-for="item in addMenu"
                  :key="item.label"
                  class="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-ink hover:bg-surface-soft transition-colors text-left"
                  @click="item.action"
                >
                  <component :is="item.icon" class="w-4 h-4 text-primary shrink-0" />
                  {{ item.label }}
                </button>
              </div>
            </template>
          </div>

          <BaseButton
            v-if="isRealBinderId"
            variant="danger"
            size="sm"
            @click="confirmDeleteCurrentBinder"
          >
            <template #icon><Trash2 class="w-4 h-4" /></template>
            Supprimer
          </BaseButton>
        </template>
        <template v-else>
          <BaseButton :loading="cloning" @click="cloneBinder">
            <template #icon><Copy class="w-4 h-4" /></template>
            {{ cloning ? 'Copie en cours...' : 'Créer une copie personnelle' }}
          </BaseButton>
          <BaseButton
            v-if="currentBinder?.read_only"
            variant="ghost"
            size="sm"
            @click="confirmDeleteCurrentBinder"
          >
            <template #icon><Trash2 class="w-4 h-4" /></template>
            Retirer de ma vue
          </BaseButton>
        </template>
      </template>

      <template v-if="currentBinderId !== null" #tabs>
        <Tabs v-model="activeType" :tabs="contentTabs" />
      </template>
    </PageHeader>

    <!-- Filtre par tags -->
    <div class="flex flex-wrap items-center gap-2 rounded-2xl border border-line bg-surface p-3">
      <span class="text-xs font-bold uppercase tracking-wider text-ink-subtle">Filtrer</span>
      <button
        type="button"
        class="rounded-full px-3 py-1.5 text-xs font-bold transition-colors"
        :class="selectedTagId === null ? 'bg-primary text-white' : 'bg-surface-soft text-ink-muted'"
        @click="filterByTag(null)"
      >
        Tous
      </button>
      <button
        v-for="tag in tagsStore.tags"
        :key="tag.id"
        type="button"
        class="rounded-full px-3 py-1.5 text-xs font-bold transition-colors"
        :style="
          selectedTagId === tag.id
            ? { backgroundColor: tag.color || '#F06292', color: '#fff' }
            : undefined
        "
        :class="selectedTagId === tag.id ? '' : 'bg-surface-soft text-ink-muted'"
        @click="filterByTag(tag.id)"
      >
        {{ tag.name }}
      </button>
    </div>

    <!-- Bandeau lecture seule -->
    <div
      v-if="!isOwner"
      class="p-4 bg-warning-soft border border-warning/30 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-warning"
    >
      <div class="flex items-center gap-2">
        <Eye class="w-5 h-5 shrink-0" />
        <span class="text-xs font-semibold text-ink-muted"
          >Vous visualisez ce dossier en lecture seule (cours suivi). Pour le modifier, créez une
          copie personnelle.</span
        >
      </div>
      <BaseButton variant="soft" size="sm" :loading="cloning" @click="cloneBinder">
        <template #icon><Copy class="w-3.5 h-3.5" /></template>
        Créer une copie
      </BaseButton>
    </div>

    <!-- Loading -->
    <div v-if="bindersStore.loading" class="flex flex-col items-center justify-center py-20 gap-3">
      <svg
        class="animate-spin h-8 w-8 text-primary"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        ></circle>
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      <span class="text-sm font-semibold text-ink-subtle uppercase tracking-widest"
        >Chargement...</span
      >
    </div>

    <div v-else class="space-y-6">
      <!-- Grille de classeurs (Task 2 -- remplace l'arbre SplitView) : classeurs de
           premier niveau + "Non classé" à la racine, sous-classeurs directs à
           l'intérieur d'un classeur réel. Masquée uniquement pour le pseudo-classeur
           'non-classe', qui n'a pas d'enfants propres (ce n'est pas un nœud de
           hiérarchie) -- cf. childrenAtCurrentLevel. -->
      <div v-if="currentBinderId !== 'non-classe'">
        <h3
          v-if="currentBinderId !== null"
          class="text-xs font-bold uppercase tracking-wider text-ink-subtle mb-3"
        >
          Sous-classeurs
        </h3>
        <div
          v-if="childrenAtCurrentLevel.length > 0"
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          <BinderCard
            v-for="child in childrenAtCurrentLevel"
            :key="child.id"
            :binder="cardBinderProps(child)"
            :deck-count="cardAggregate(child).deckCount"
            :note-count="cardAggregate(child).noteCount"
            :last-activity-label="cardAggregate(child).lastActivityLabel"
            @click="goTo(child.id)"
          />
        </div>
        <p
          v-else-if="currentBinderId !== null"
          class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider"
        >
          Aucun sous-classeur
        </p>
      </div>

      <!-- Contenu typé (Notes/Révision/Autres) : uniquement à l'intérieur d'un
           classeur réel ou du pseudo-classeur "Non classé" -- jamais à la racine
           (currentBinderId === null), qui n'affiche que la grille ci-dessus. -->
      <template v-if="currentBinderId !== null">
        <div class="space-y-6">
          <!-- Notes -->
          <BaseCard v-if="activeType === 'notes'">
            <h3 class="font-bold text-sm text-ink flex items-center gap-2 mb-3">
              <FileText class="w-4 h-4 text-cat-note" />
              Notes ({{ currentNotes.length }})
            </h3>
            <div class="space-y-1">
              <ListRow
                v-for="note in currentNotes"
                :key="note.id"
                interactive
                class="group"
                :title="note.title"
                @click="router.push(`/notes/${note.id}`)"
              >
                <template #leading
                  ><div
                    class="w-9 h-9 rounded-xl bg-cat-note-soft text-cat-note flex items-center justify-center"
                  >
                    <FileText class="w-4.5 h-4.5" /></div
                ></template>
                <template #trailing>
                  <span
                    v-if="note.read_only"
                    class="px-1.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wide bg-warning-soft text-warning"
                    >Cours</span
                  >
                  <button
                    v-if="isOwner"
                    class="opacity-0 group-hover:opacity-100 p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft transition-all"
                    title="Retirer du classeur"
                    @click.stop="detachItem('note', note.id)"
                  >
                    <FolderMinus class="w-4 h-4" />
                  </button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <p
                v-if="currentNotes.length === 0"
                class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider"
              >
                Aucune note
              </p>
            </div>
          </BaseCard>

          <!-- Révision : fusion visuelle Decks + Ensembles -->
          <BaseCard v-if="activeType === 'revision'">
            <h3 class="font-bold text-sm text-ink flex items-center gap-2 mb-3">
              <FileQuestion class="w-4 h-4 text-cat-set" />
              Révision ({{ currentDecks.length + currentSets.length }})
            </h3>
            <div class="space-y-1">
              <ListRow
                v-for="deck in currentDecks"
                :key="`deck:${deck.id}`"
                interactive
                class="group"
                :title="deck.name"
                :subtitle="`${deck.card_count} carte(s)`"
                @click="router.push(`/decks/${deck.id}/study`)"
              >
                <template #leading
                  ><div
                    class="w-9 h-9 rounded-xl bg-cat-deck-soft text-cat-deck flex items-center justify-center"
                  >
                    <Layers class="w-4.5 h-4.5" /></div
                ></template>
                <template #trailing>
                  <button
                    v-if="isOwner"
                    class="p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft transition-all"
                    title="Retirer du classeur"
                    @click.stop="detachItem('deck', deck.id)"
                  >
                    <FolderMinus class="w-4 h-4" />
                  </button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <ListRow
                v-for="set in currentSets"
                :key="`set:${set.id}`"
                :data-test="`revision-row-set-${set.id}`"
                interactive
                class="group"
                :title="set.name"
                @click="router.push(`/revision/sets/${set.id}`)"
              >
                <template #leading
                  ><div
                    class="w-9 h-9 rounded-xl bg-cat-set-soft text-cat-set flex items-center justify-center"
                  >
                    <FileQuestion class="w-4.5 h-4.5" /></div
                ></template>
                <div class="min-w-0">
                  <span class="font-semibold text-sm text-ink truncate block">{{ set.name }}</span>
                  <span class="text-xs text-ink-subtle"
                    >{{ set.item_count }} élément(s) ·
                    {{ setAggregate(set.id).lastPassageLabel }}</span
                  >
                  <div
                    v-if="setAggregate(set.id).typesPresent.length"
                    class="flex items-center gap-1.5 mt-1"
                  >
                    <component
                      :is="TYPE_ICONS[t]"
                      v-for="t in setAggregate(set.id).typesPresent"
                      :key="t"
                      :data-test="`type-icon-${t}`"
                      class="w-3.5 h-3.5 text-ink-subtle"
                    />
                  </div>
                </div>
                <template #trailing>
                  <BaseBadge
                    v-if="setAggregate(set.id).dueCount > 0"
                    data-test="due-badge"
                    variant="accent"
                    size="sm"
                    >{{ setAggregate(set.id).dueCount }} dues</BaseBadge
                  >
                  <button
                    class="p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft"
                    title="Statistiques"
                    @click.stop="router.push(`/revision/sets/${set.id}/stats`)"
                  >
                    <BarChart3 class="w-4 h-4" />
                  </button>
                  <button
                    v-if="isOwner"
                    class="p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft transition-all"
                    title="Retirer du classeur"
                    @click.stop="detachItem('set', set.id)"
                  >
                    <FolderMinus class="w-4 h-4" />
                  </button>
                  <button
                    class="p-1.5 text-ink-subtle hover:text-primary rounded-lg hover:bg-primary-soft"
                    title="Éditer l'ensemble"
                    @click.stop="openSetEdit(set)"
                  >
                    <Pencil class="w-4 h-4" />
                  </button>
                  <button
                    v-if="isOwner"
                    class="p-1.5 text-ink-subtle hover:text-danger rounded-lg hover:bg-danger-soft"
                    title="Supprimer l'ensemble"
                    @click.stop="confirmDeleteSet(set)"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <p
                v-if="currentDecks.length === 0 && currentSets.length === 0"
                class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider"
              >
                Aucun élément de révision
              </p>
            </div>
          </BaseCard>

          <RevisionSetModal
            v-if="showSetModal"
            mode="create"
            :binder-id="filterBinderId"
            @close="showSetModal = false"
            @created="onSetCreated"
          />
          <RevisionSetModal
            v-if="editingSet"
            mode="edit"
            :binder-id="filterBinderId"
            :set="editingSet"
            @close="editingSet = null"
            @updated="onSetUpdated"
          />

          <!-- Diagrammes -->
          <BaseCard v-if="activeType === 'other'">
            <h3 class="font-bold text-sm text-ink flex items-center gap-2 mb-3">
              <Activity class="w-4 h-4 text-cat-diagram" />
              Diagrammes ({{ currentDiagrams.length }})
            </h3>
            <div class="space-y-1">
              <ListRow
                v-for="diagram in currentDiagrams"
                :key="diagram.id"
                interactive
                class="group"
                :title="diagram.title || 'Diagramme sans titre'"
                @click="router.push(`/diagrams?id=${diagram.id}`)"
              >
                <template #leading
                  ><div
                    class="w-9 h-9 rounded-xl bg-cat-diagram-soft text-cat-diagram flex items-center justify-center"
                  >
                    <Activity class="w-4.5 h-4.5" /></div
                ></template>
                <template #trailing>
                  <button
                    v-if="isOwner"
                    class="opacity-0 group-hover:opacity-100 p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft transition-all"
                    title="Retirer du classeur"
                    @click.stop="detachItem('diagram', diagram.id)"
                  >
                    <FolderMinus class="w-4 h-4" />
                  </button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <p
                v-if="currentDiagrams.length === 0"
                class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider"
              >
                Aucun diagramme
              </p>
            </div>
          </BaseCard>

          <!-- PDF -->
          <BaseCard v-if="activeType === 'other'">
            <h3 class="font-bold text-sm text-ink flex items-center gap-2 mb-3">
              <FileDown class="w-4 h-4 text-cat-pdf" />
              Documents PDF ({{ currentPdfs.length }})
            </h3>
            <div class="space-y-1">
              <ListRow
                v-for="pdf in currentPdfs"
                :key="pdf.id"
                interactive
                class="group"
                :title="pdf.name"
                @click="router.push('/pdfs')"
              >
                <template #leading
                  ><div
                    class="w-9 h-9 rounded-xl bg-cat-pdf-soft text-cat-pdf flex items-center justify-center"
                  >
                    <FileDown class="w-4.5 h-4.5" /></div
                ></template>
                <template #trailing>
                  <button
                    v-if="isOwner && !pdf.read_only"
                    class="opacity-0 group-hover:opacity-100 p-1.5 text-ink-subtle hover:text-warning rounded-lg hover:bg-warning-soft transition-all"
                    title="Retirer du classeur"
                    @click.stop="detachItem('pdf', pdf.id)"
                  >
                    <FolderMinus class="w-4 h-4" />
                  </button>
                  <ChevronRight class="w-4 h-4 text-ink-subtle" />
                </template>
              </ListRow>
              <p
                v-if="currentPdfs.length === 0"
                class="text-center py-6 text-ink-subtle text-xs font-semibold uppercase tracking-wider"
              >
                Aucun document PDF
              </p>
            </div>
          </BaseCard>
        </div>
      </template>
    </div>

    <!-- Modale : rattacher un élément existant -->
    <BaseModal
      :open="showAttachModal"
      title="Ajouter un élément existant"
      size="lg"
      @close="showAttachModal = false"
    >
      <p class="text-xs text-ink-muted -mt-2 mb-4">
        Déplace des éléments non rangés ou d'un autre classeur vers celui-ci.
      </p>
      <div class="max-h-[55vh] overflow-y-auto -mx-2 px-2 space-y-4">
        <div v-for="group in attachableGroups" :key="group.type">
          <p
            v-if="group.items.length"
            class="text-[10px] font-bold text-ink-subtle uppercase tracking-widest mb-1.5"
          >
            {{ group.label }}
          </p>
          <label
            v-for="it in group.items"
            :key="`${group.type}:${it.id}`"
            class="flex items-center gap-3 p-2.5 rounded-xl hover:bg-surface-soft cursor-pointer"
          >
            <input
              type="checkbox"
              :checked="isSelected(group.type, it.id)"
              class="rounded border-line text-primary focus:ring-primary"
              @change="toggleSelect(group.type, it.id)"
            />
            <span class="text-sm font-semibold text-ink truncate">{{ it.label }}</span>
          </label>
        </div>
        <p
          v-if="attachableGroups.every((g) => g.items.length === 0)"
          class="text-center py-8 text-xs text-ink-subtle uppercase tracking-wider"
        >
          Aucun élément disponible à rattacher.
        </p>
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="showAttachModal = false">Annuler</BaseButton>
        <BaseButton :disabled="selectedCount === 0" :loading="attaching" @click="confirmAttach"
          >Ajouter{{ selectedCount ? ` (${selectedCount})` : '' }}</BaseButton
        >
      </template>
    </BaseModal>

    <!-- Modale : créer un dossier -->
    <BaseModal :open="showModal" title="Créer un nouveau dossier" @close="showModal = false">
      <form class="space-y-4" @submit.prevent="createFolder">
        <BaseField label="Nom du dossier" for-id="folder-name">
          <BaseInput
            id="folder-name"
            v-model="newFolderName"
            placeholder="Ex: Anatomie, Semestre 2..."
          />
        </BaseField>
        <BaseField label="Tags">
          <TagSelector v-model="folderTags" />
        </BaseField>
        <div class="flex items-center justify-end gap-2 pt-2">
          <BaseButton type="button" variant="ghost" @click="showModal = false">Annuler</BaseButton>
          <BaseButton type="submit">Créer</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Modale : partage communautaire -->
    <BaseModal
      :open="showShareModal"
      title="Partager sur l'Espace Communautaire"
      @close="showShareModal = false"
    >
      <p class="text-xs text-ink-muted -mt-2 mb-4">
        Publiez ce classeur et ses ressources pour les rendre accessibles à la communauté.
      </p>
      <form class="space-y-4" @submit.prevent="saveShareSettings">
        <div
          class="flex items-center justify-between p-3.5 bg-surface-soft border border-line rounded-2xl"
        >
          <div>
            <span class="block text-xs font-bold text-ink">Statut de visibilité</span>
            <span class="text-[10px] text-ink-subtle">{{
              shareIsPublic ? 'Visible sur la Marketplace' : 'Visible uniquement par vous'
            }}</span>
          </div>
          <BaseButton
            type="button"
            size="sm"
            :variant="shareIsPublic ? 'soft' : 'secondary'"
            @click="shareIsPublic = !shareIsPublic"
          >
            {{ shareIsPublic ? 'Public' : 'Privé' }}
          </BaseButton>
        </div>
        <BaseField label="Description" for-id="share-description">
          <textarea
            id="share-description"
            v-model="shareDescription"
            rows="3"
            placeholder="Décrivez le contenu de ce dossier..."
            class="block w-full px-4 py-3 bg-surface border border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/40 text-sm font-medium text-ink"
          ></textarea>
        </BaseField>
        <BaseField label="Mots-clés (séparés par des virgules)" for-id="share-tags">
          <BaseInput
            id="share-tags"
            v-model="shareTags"
            placeholder="Ex: Chimie, Médecine, Semestre 1"
          />
        </BaseField>
        <div class="flex items-center justify-end gap-2 pt-2">
          <BaseButton type="button" variant="ghost" @click="showShareModal = false"
            >Annuler</BaseButton
          >
          <BaseButton type="submit">Enregistrer</BaseButton>
        </div>
      </form>
    </BaseModal>

    <!-- Modale : partage à une classe -->
    <BaseModal
      :open="showClassShareModal"
      title="Partager ce classeur à une classe"
      @close="showClassShareModal = false"
    >
      <p class="text-xs text-ink-muted -mt-2 mb-4">
        Le classeur est partagé <strong>par référence</strong> : tout élément ajouté ensuite devient
        automatiquement visible des élèves, en lecture seule.
      </p>
      <div
        v-if="classShareBusy && myClasses.length === 0"
        class="py-8 text-center text-sm text-ink-subtle"
      >
        <Loader2 class="w-5 h-5 animate-spin inline" />
      </div>
      <div v-else-if="ownedClasses.length === 0" class="py-8 text-center text-sm text-ink-subtle">
        Vous n'animez aucune classe pour l'instant.
      </div>
      <ul v-else class="space-y-2 max-h-72 overflow-y-auto">
        <li
          v-for="c in ownedClasses"
          :key="c.id"
          class="flex items-center justify-between p-3 bg-surface-soft border border-line rounded-2xl"
        >
          <div class="min-w-0">
            <p class="text-sm font-bold text-ink truncate">{{ c.name }}</p>
            <span class="text-[10px] text-ink-subtle">{{ c.members_count }} membre(s)</span>
          </div>
          <BaseButton
            size="sm"
            :variant="isClassShared(c.id) ? 'soft' : 'secondary'"
            :disabled="classShareBusy"
            @click="toggleClassShare(c)"
          >
            {{ isClassShared(c.id) ? 'Partagé ✓' : 'Partager' }}
          </BaseButton>
        </li>
      </ul>
      <template #footer>
        <BaseButton variant="ghost" @click="showClassShareModal = false">Fermer</BaseButton>
      </template>
    </BaseModal>
  </PageContainer>
</template>

<script lang="ts">
// Formatage relatif partagé "aujourd'hui / hier / il y a N jours" -- utilisé par
// setAggregate() (onglet Révision, ci-dessous) et binderAggregate() (Bibliothèque,
// Task 1 bibliotheque-redesign) pour ne pas dupliquer la logique de day-diff.
// Placé dans ce bloc <script> normal (plutôt que <script setup>) pour rester
// exportable et testable directement, sans monter le composant.
export function formatDayDiffLabel(mostRecentIso: string): string {
  const days = Math.floor((Date.now() - new Date(mostRecentIso).getTime()) / 86400000)
  if (days <= 0) return "aujourd'hui"
  if (days === 1) return 'hier'
  return `il y a ${days} jours`
}

export interface BinderAggregateResult {
  deckCount: number
  noteCount: number
  lastActivityLabel: string | null
}

// Agrégat client-side pour une carte de classeur (Bibliothèque, Task 1) : nombre de
// decks/notes rattachés à ce classeur, et libellé de dernière activité. L'activité la
// plus récente est le max de : updated_at des notes, updated_at des ensembles de
// révision, et created_at des decks (un Deck n'a pas d'updated_at -- cf.
// stores/decks.ts, ne pas fabriquer de valeur). Pas d'endpoint serveur dédié -- même
// principe client-side que setAggregate() ci-dessous. Types de paramètres structurels
// (pas d'import de Deck/Note/RevisionSet ici) pour rester dans ce bloc <script> sans
// entrer en collision avec les imports déjà faits dans <script setup> ci-dessous.
export function binderAggregate(
  binderId: string | null,
  decks: { binder_id: string | null; created_at: string }[],
  notes: { binder_id: string | null; updated_at: string }[],
  sets: { binder_id: string | null; updated_at?: string }[],
): BinderAggregateResult {
  const binderDecks = decks.filter((d) => d.binder_id === binderId)
  const binderNotes = notes.filter((n) => n.binder_id === binderId)
  const binderSets = sets.filter((s) => s.binder_id === binderId)

  const dates = [
    ...binderNotes.map((n) => n.updated_at),
    ...binderSets.map((s) => s.updated_at),
    ...binderDecks.map((d) => d.created_at),
  ].filter((d): d is string => Boolean(d))

  return {
    deckCount: binderDecks.length,
    noteCount: binderNotes.length,
    lastActivityLabel: dates.length ? formatDayDiffLabel(dates.sort().reverse()[0]) : null,
  }
}
</script>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import { useBindersStore } from '../../stores/binders'
import type { Binder } from '../../stores/binders'
import { useNotesStore } from '../../stores/notes'
import { useDecksStore } from '../../stores/decks'
import { useTagsStore, type Tag } from '../../stores/tags'
import TagSelector from '../../components/ui/TagSelector.vue'
import BinderCard, { type BinderCardBinder } from '../../components/binders/BinderCard.vue'
import {
  PageContainer,
  PageHeader,
  Tabs,
  ListRow,
  BaseCard,
  BaseButton,
  BaseModal,
  BaseField,
  BaseInput,
  BaseBadge,
} from '../../components/ui/base'
import type { TabItem } from '../../components/ui/base'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionSet, RevisionItem, RevisionItemType } from '../../stores/revision'
import RevisionSetModal from '../../components/decks/RevisionSetModal.vue'
import {
  Plus,
  ChevronRight,
  ChevronDown,
  FileText,
  Layers,
  Trash2,
  Globe,
  Copy,
  Eye,
  Loader2,
  FolderPlus,
  FileQuestion,
  BarChart3,
  FolderMinus,
  FolderInput,
  GraduationCap,
  Activity,
  FileDown,
  Brain,
  Pencil,
  HelpCircle,
  Rows3,
  BookOpen,
  ListOrdered,
  Shuffle,
} from 'lucide-vue-next'
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

// ─── Onglets de type de contenu (filtre du dossier courant) ─────────────────
type ContentType = 'notes' | 'revision' | 'other'
function isValidType(v: unknown): v is ContentType {
  return v === 'notes' || v === 'revision' || v === 'other'
}
const activeType = ref<ContentType>(isValidType(route.query.type) ? route.query.type : 'notes')
watch(activeType, (t) => {
  const q = t === 'notes' ? undefined : t
  if (route.query.type !== q) router.replace({ query: { ...route.query, type: q } })
})

const contentTabs = computed<TabItem[]>(() => [
  { key: 'notes', label: 'Notes' },
  { key: 'revision', label: 'Révision' },
  { key: 'other', label: 'Autres' },
])

const primaryActionLabel = computed(() => {
  if (activeType.value === 'notes') return 'Nouvelle note'
  if (activeType.value === 'revision') return 'Nouvel ensemble'
  return 'Diagramme'
})
const primaryActionIcon = computed(() =>
  activeType.value === 'notes' ? FileText : activeType.value === 'revision' ? Plus : Activity,
)
function primaryAction() {
  if (activeType.value === 'notes') return addNote()
  if (activeType.value === 'revision') {
    showSetModal.value = true
    return
  }
  return addDiagram()
}

const showSetModal = ref(false)
function onSetCreated() {
  showSetModal.value = false
  revisionStore.fetchSets()
}

const editingSet = ref<RevisionSet | null>(null)
function openSetEdit(set: RevisionSet) {
  editingSet.value = set
}
function onSetUpdated() {
  editingSet.value = null
  revisionStore.fetchSets()
}
async function confirmDeleteSet(set: RevisionSet) {
  if (!confirm(`Supprimer l'ensemble "${set.name}" et tous ses éléments ?`)) return
  await revisionStore.deleteSet(set.id)
}

// Agrégation par ensemble (types présents, cartes dues, dernier passage) pour la
// ligne de la liste Révision — même principe client-side que RevisionSetDetail.vue,
// pas de nouvel endpoint serveur (cf. spec « Ce qui n'est pas fait ici »).
// Meme mapping que TYPE_META dans RevisionSetDetail.vue (Task 5) -- un type doit
// afficher la meme icone partout dans l'app.
const TYPE_ICONS: Record<RevisionItemType, unknown> = {
  flashcard: Layers,
  qcm: HelpCircle,
  vf: Rows3,
  definition: BookOpen,
  ordre: ListOrdered,
  association: Shuffle,
}
const setItemsById = ref<Record<number, RevisionItem[]>>({})

function setAggregate(setId: number) {
  const items = setItemsById.value[setId] ?? []
  const typesPresent = Array.from(new Set(items.map((i) => i.type)))
  // "due" = programme pour maintenant ou dans le passe (next_review <= maintenant).
  const dueCount = items.filter(
    (i) => i.next_review && new Date(i.next_review).getTime() <= Date.now(),
  ).length
  const dates = items
    .map((i) => i.updated_at)
    .filter(Boolean)
    .sort()
    .reverse()
  const lastPassageLabel = dates.length
    ? `dernier passage ${formatDayDiffLabel(dates[0])}`
    : 'jamais passé'
  return { typesPresent, dueCount, lastPassageLabel }
}

async function fetchMissingBinder(binderId: string) {
  try {
    const response = await api.get(`/binders/${binderId}`)
    const fetchedBinder = response.data
    if (!bindersStore.binders.some((b) => b.id === fetchedBinder.id)) {
      bindersStore.binders.push(fetchedBinder)
    }
  } catch (error) {
    console.error('Erreur lors du chargement du classeur', error)
  }
}

// Navigation par URL : /bibliotheque/:id — le watch ci-dessous synchronise l'état.
function goTo(id: string | null) {
  router.push(id ? `/bibliotheque/${id}` : '/bibliotheque')
}

watch(
  () => route.params.id,
  (newId) => {
    currentBinderId.value = (newId as string) || null
  },
  { immediate: true },
)

watch(
  currentBinderId,
  async (newVal) => {
    // 'non-classe' est un pseudo-classeur (Task 2) : rien à charger côté API pour
    // cette valeur, ce n'est pas un vrai id de classeur.
    if (newVal !== null && newVal !== 'non-classe') {
      const exists = bindersStore.binders.some((b) => b.id === newVal)
      if (!exists) {
        await fetchMissingBinder(newVal)
      }
    }
  },
  { immediate: true },
)

// Vrai uniquement pour un classeur réel existant — jamais pour la racine (null) ni
// pour le pseudo-classeur 'non-classe' (pas d'id réel côté backend). Sert de garde
// pour toute action qui nécessite un vrai classeur : stats, partage, révision
// groupée, création de sous-classeur, rattachement d'un élément existant.
const isRealBinderId = computed(
  () => currentBinderId.value !== null && currentBinderId.value !== 'non-classe',
)

// Distinction explicite navigation vs filtrage de contenu (cf. brief Task 2) :
// `currentBinderId` porte la valeur de route/navigation — 'non-classe' y est une
// valeur légitime (grille, fil d'Ariane, goTo()). `filterBinderId` est la valeur
// attendue par les 3 computed de filtrage de contenu ci-dessous : aucune note/deck/
// ensemble n'a jamais littéralement `binder_id === 'non-classe'`, donc on retombe
// sur `null` pour ce cas précis. Ne jamais lire `currentBinderId` directement dans
// currentNotes/currentDecks/currentSets (et les 2 listes "Autres" ci-dessous) —
// c'est exactement le bug que ce nom explicite doit empêcher.
const filterBinderId = computed<string | null>(() =>
  currentBinderId.value === 'non-classe' ? null : currentBinderId.value,
)
const showModal = ref(false)
const newFolderName = ref('')
const folderTags = ref<Tag[]>([])
const selectedTagId = ref<number | null>(null)

const showAddMenu = ref(false)

// Computed (et non un tableau figé) : 'Sous-dossier'/'Élément existant' nécessitent
// un vrai classeur parent (createBinder/attachItems attendent un id réel côté
// backend) — masqués dans le pseudo-classeur 'Non classé'. 'Note'/'Diagramme'
// restent proposés : ils créent du contenu non classé valide (voir addNote/
// addDiagram, filterBinderId).
const addMenu = computed(() => {
  const items = [
    { label: 'Note', icon: FileText, action: () => closeMenuThen(addNote) },
    { label: 'Diagramme', icon: Activity, action: () => closeMenuThen(addDiagram) },
  ]
  if (isRealBinderId.value) {
    items.unshift(
      { label: 'Sous-dossier', icon: FolderPlus, action: () => closeMenuThen(openCreateModal) },
      {
        label: 'Élément existant',
        icon: FolderInput,
        action: () => closeMenuThen(openAttachModal),
      },
    )
  }
  return items
})

function closeMenuThen(fn: () => void) {
  showAddMenu.value = false
  fn()
}

async function addNote() {
  // filterBinderId (pas currentBinderId) : depuis 'Non classé', on crée une note
  // réellement non classée (binder_id: null), jamais binder_id: 'non-classe'.
  const note = await notesStore.createNote('Nouvelle note', '', filterBinderId.value)
  router.push(`/notes/${note.id}?edit=true`)
}

async function addDiagram() {
  // Crée un diagramme rattaché au dossier courant puis ouvre l'éditeur (?id=…).
  // L'éditeur (/diagrams) sélectionne le diagramme via route.query.id.
  const defaultCode = JSON.stringify({
    type: 'visual',
    nodes: [
      { id: 1, label: 'Concept central', type: 'rect', x: 250, y: 150, color: 'bg-indigo-600' },
    ],
    connections: [],
    backgroundImage: null,
    masks: [],
  })
  try {
    const res = await api.post('/diagrams', {
      title: 'Nouveau diagramme',
      code: defaultCode,
      // filterBinderId (pas currentBinderId) : cf. addNote() ci-dessus.
      binder_id: filterBinderId.value,
    })
    router.push(`/diagrams?id=${res.data.id}`)
  } catch (e) {
    console.error('Erreur lors de la création du diagramme', e)
  }
}

function reviseBinder() {
  if (!isRealBinderId.value) return
  // Réviser tout le dossier : runner StudyDeck en mode « dossier » (cartes dues
  // agrégées sur tous les decks du classeur). Le nom alimente l'en-tête du runner.
  const name = bindersStore.binders.find((b) => b.id === currentBinderId.value)?.name || 'Dossier'
  router.push(`/bibliotheque/${currentBinderId.value}/reviser?name=${encodeURIComponent(name)}`)
}

const showShareModal = ref(false)
const shareIsPublic = ref(false)
const shareDescription = ref('')
const shareTags = ref('')

interface BinderDiagram {
  id: number
  title: string
  binder_id: string | null
}
interface BinderPdf {
  id: string
  name: string
  binder_id: string | null
  read_only?: boolean
}
const allDiagrams = ref<BinderDiagram[]>([])
const allPdfs = ref<BinderPdf[]>([])

async function fetchBinderMedia() {
  try {
    const [diag, pdf] = await Promise.all([
      api.get('/diagrams?per_page=100'),
      api.get('/pdfs?per_page=100'),
    ])
    allDiagrams.value = diag.data.data
    allPdfs.value = pdf.data.data
  } catch (error) {
    console.error('Erreur lors du chargement des diagrammes/PDF', error)
  }
}

onMounted(async () => {
  await Promise.all([
    bindersStore.fetchBinders(),
    notesStore.fetchNotes(),
    decksStore.fetchDecks(),
    revisionStore.fetchSets(),
    tagsStore.fetchTags(),
    fetchBinderMedia(),
  ])
})

async function filterByTag(tagId: number | null) {
  selectedTagId.value = tagId
  await bindersStore.fetchBinders(tagId)
}

// Pseudo-classeur "Non classé" (Task 2) : représente le contenu avec
// binder_id === null. Objet plain literal, PAS un Binder — jamais poussé dans
// bindersStore.binders, pas de hiérarchie propre (childrenAtCurrentLevel renvoie
// [] pour lui, cf. plus bas). N'existe qu'à la racine.
interface VirtualBinderEntry {
  id: 'non-classe'
  name: string
  virtual: true
}
const NON_CLASSE_ENTRY: VirtualBinderEntry = { id: 'non-classe', name: 'Non classé', virtual: true }

function isVirtualEntry(entry: Binder | VirtualBinderEntry): entry is VirtualBinderEntry {
  return 'virtual' in entry
}

// Grille de classeurs au niveau courant (remplace l'arbre SplitView, Task 2) :
// - racine (null) : classeurs de premier niveau + carte virtuelle "Non classé" —
//   placée en dernier (les classeurs réels de l'utilisateur passent avant le
//   fourre-tout, cf. rapport de tâche).
// - classeur réel : ses sous-classeurs directs.
// - 'non-classe' : [] — ce n'est pas un nœud de hiérarchie, pas d'enfants propres.
const childrenAtCurrentLevel = computed<(Binder | VirtualBinderEntry)[]>(() => {
  if (currentBinderId.value === 'non-classe') return []
  if (currentBinderId.value === null) {
    return [...bindersStore.binders.filter((b) => b.parent_id === null), NON_CLASSE_ENTRY]
  }
  return bindersStore.binders.filter((b) => b.parent_id === currentBinderId.value)
})

function cardBinderProps(entry: Binder | VirtualBinderEntry): BinderCardBinder {
  if (isVirtualEntry(entry)) return { id: entry.id, name: entry.name }
  return { id: entry.id, name: entry.name, readOnly: entry.read_only }
}

// binderAggregate() attend un vrai id de classeur OU null (pour agréger le contenu
// non classé) — jamais la chaîne 'non-classe' : pour la carte virtuelle, on agrège
// donc bien sur `null`, exactement comme filterBinderId le fait pour le contenu
// affiché une fois qu'on a cliqué dessus.
function cardAggregate(entry: Binder | VirtualBinderEntry) {
  const id = isVirtualEntry(entry) ? null : entry.id
  return binderAggregate(id, decksStore.decks, notesStore.notes, revisionStore.sets)
}

// Les 3 filtres de contenu ci-dessous utilisent `filterBinderId`, PAS
// `currentBinderId` — voir la définition de filterBinderId plus haut pour la
// raison (distinction navigation vs filtrage).
const currentNotes = computed(() =>
  notesStore.notes.filter((n) => n.binder_id === filterBinderId.value),
)
const currentDecks = computed(() =>
  decksStore.decks.filter((d) => d.binder_id === filterBinderId.value),
)
const currentSets = computed(() =>
  revisionStore.sets.filter((s) => s.binder_id === filterBinderId.value),
)

async function loadSetAggregates() {
  await Promise.all(
    currentSets.value.map(async (set) => {
      if (setItemsById.value[set.id]) return
      setItemsById.value[set.id] = await revisionStore.fetchItems(set.id)
    }),
  )
}

watch(
  activeType,
  (t) => {
    if (t === 'revision') loadSetAggregates()
  },
  { immediate: true },
)
watch(currentSets, () => {
  if (activeType.value === 'revision') loadSetAggregates()
})

// Même raison que currentNotes/currentDecks/currentSets ci-dessus : filterBinderId,
// pas currentBinderId.
const currentDiagrams = computed(() =>
  allDiagrams.value.filter((d) => d.binder_id === filterBinderId.value),
)
const currentPdfs = computed(() =>
  allPdfs.value.filter((p) => p.binder_id === filterBinderId.value),
)

const showAttachModal = ref(false)
const attaching = ref(false)
const selected = ref<Record<string, { type: BinderItemType; id: number | string }>>({})

const attachableGroups = computed(() => {
  const cur = currentBinderId.value
  return [
    {
      type: 'note' as BinderItemType,
      label: 'Notes',
      items: notesStore.notes
        .filter((n) => n.binder_id !== cur && !n.read_only)
        .map((n) => ({ id: n.id, label: n.title })),
    },
    {
      type: 'deck' as BinderItemType,
      label: 'Jeux de révision',
      items: decksStore.decks
        .filter((d) => d.binder_id !== cur)
        .map((d) => ({ id: d.id, label: d.name })),
    },
    {
      type: 'set' as BinderItemType,
      label: 'Ensembles de révision',
      items: revisionStore.sets
        .filter((s) => s.binder_id !== cur)
        .map((s) => ({ id: s.id, label: s.name })),
    },
    {
      type: 'diagram' as BinderItemType,
      label: 'Diagrammes',
      items: allDiagrams.value
        .filter((d) => d.binder_id !== cur)
        .map((d) => ({ id: d.id, label: d.title || 'Diagramme sans titre' })),
    },
    {
      type: 'pdf' as BinderItemType,
      label: 'Documents PDF',
      items: allPdfs.value
        .filter((p) => p.binder_id !== cur && !p.read_only)
        .map((p) => ({ id: p.id, label: p.name })),
    },
  ]
})

const selectedCount = computed(() => Object.keys(selected.value).length)
function keyOf(type: BinderItemType, id: number | string) {
  return `${type}:${id}`
}
function isSelected(type: BinderItemType, id: number | string) {
  return keyOf(type, id) in selected.value
}
function toggleSelect(type: BinderItemType, id: number | string) {
  const k = keyOf(type, id)
  if (k in selected.value) {
    delete selected.value[k]
  } else {
    selected.value[k] = { type, id }
  }
}

function openAttachModal() {
  selected.value = {}
  showAttachModal.value = true
}

async function refreshContentStores() {
  await Promise.all([
    notesStore.fetchNotes(),
    decksStore.fetchDecks(),
    revisionStore.fetchSets(),
    fetchBinderMedia(),
  ])
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

// Fil d'Ariane (PageHeader) — navigation par URL.
const breadcrumbItems = computed(() => {
  const items: { label: string; to?: string }[] = [{ label: 'Racine', to: '/bibliotheque' }]
  if (currentBinderId.value === null) return items
  // Cas spécial explicite AVANT la boucle bindersStore.binders.find(...) : 'non-classe'
  // n'est pas un id de classeur réel, cette boucle ne le trouverait jamais et
  // produirait silencieusement un fil d'Ariane vide/faux (cf. brief Task 2).
  if (currentBinderId.value === 'non-classe') {
    return [...items, { label: 'Non classé' }]
  }
  const trail: Binder[] = []
  let current = bindersStore.binders.find((b) => b.id === currentBinderId.value)
  while (current) {
    trail.unshift(current)
    const parentId = current.parent_id
    current = parentId !== null ? bindersStore.binders.find((b) => b.id === parentId) : undefined
  }
  trail.forEach((b) => items.push({ label: b.name, to: `/bibliotheque/${b.id}` }))
  return items
})

function openCreateModal() {
  newFolderName.value = ''
  folderTags.value = []
  showModal.value = true
}

async function createFolder() {
  if (newFolderName.value.trim()) {
    const binder = await bindersStore.createBinder(
      newFolderName.value.trim(),
      currentBinderId.value,
    )
    if (folderTags.value.length > 0) {
      const updatedTags = await tagsStore.setTagsForEntity(
        'binders',
        binder.id,
        folderTags.value.map((tag) => tag.id),
      )
      binder.tags = updatedTags
    }
    showModal.value = false
  }
}

const currentBinder = computed(() => {
  if (currentBinderId.value === null) return null
  return bindersStore.binders.find((b) => b.id === currentBinderId.value) || null
})

// Supprime (ou retire, si classeur partagé en lecture seule) le classeur RÉEL
// actuellement ouvert, puis navigue vers son parent. Remplace, pour le classeur
// courant, l'ancienne suppression par ligne dans l'arbre (Task 2 — la grille de
// cartes n'expose pas d'action de suppression par carte, cf. BinderCard.vue Task 1
// : sans cette fonction, supprimer un classeur serait devenu impossible dans toute
// l'application).
async function confirmDeleteCurrentBinder() {
  const folder = currentBinder.value
  if (!folder) return
  const message = folder.read_only
    ? `Retirer le classeur partagé "${folder.name}" de votre espace ? (l'original n'est pas supprimé)`
    : `Êtes-vous sûr de vouloir supprimer le classeur "${folder.name}" et tous ses sous-classeurs ?`
  if (confirm(message)) {
    const parentId = folder.parent_id
    await bindersStore.deleteBinder(folder.id)
    goTo(parentId)
  }
}

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const isOwner = computed(() => {
  if (currentBinderId.value === null) return true
  return !currentBinder.value || currentBinder.value.user_id === currentUserId.value
})

const cloning = ref(false)
async function cloneBinder() {
  if (!isRealBinderId.value) return
  cloning.value = true
  try {
    const response = await api.post(`/packages/${currentBinderId.value}/clone`)
    const cloned = response.data
    await bindersStore.fetchBinders()
    router.push(`/bibliotheque/${cloned.id}`)
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
  shareTags.value = currentBinder.value.tags
    ? currentBinder.value.tags.map((tag) => tag.name).join(', ')
    : ''
  showShareModal.value = true
}

async function saveShareSettings() {
  if (!currentBinder.value) return
  const tagsArray = shareTags.value
    .split(',')
    .map((t) => t.trim())
    .filter((t) => t.length > 0)
  await bindersStore.updateBinder(currentBinder.value.id, {
    is_public: shareIsPublic.value,
    description: shareDescription.value.trim() || null,
    tags: tagsArray.length > 0 ? tagsArray : null,
  })
  showShareModal.value = false
}

const showClassShareModal = ref(false)
const myClasses = ref<ClassInfo[]>([])
const sharedClasses = ref<BinderClassRef[]>([])
const classShareBusy = ref(false)

const ownedClasses = computed(() =>
  myClasses.value.filter((c) => c.created_by === currentUserId.value),
)
const isSharedToClass = computed(() => sharedClasses.value.length > 0)

async function loadSharedClasses() {
  // L'endpoint /groups/binders/<id>/classes est réservé au PROPRIÉTAIRE du
  // classeur (404 sinon). On l'interroge donc seulement si l'on est certain de
  // posséder le classeur : objet chargé ET user_id correspondant. Un classeur
  // partagé (non possédé) ou pas encore chargé est ignoré — pas de 404.
  const binder = currentBinder.value
  if (!binder || binder.user_id !== currentUserId.value) {
    sharedClasses.value = []
    return
  }
  try {
    sharedClasses.value = await groupService.getBinderClasses(binder.id)
  } catch {
    sharedClasses.value = []
  }
}

async function openClassShareModal() {
  if (!isRealBinderId.value) return
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
  return sharedClasses.value.some((c) => c.id === classId)
}

async function toggleClassShare(c: ClassInfo) {
  // isRealBinderId à lui seul ne permet pas à TS de rétrécir le type de
  // currentBinderId.value (deux computed distincts) -- la vérification directe
  // ci-dessous fournit le rétrécissement `string` nécessaire pour groupService.
  const binderId = currentBinderId.value
  if (!isRealBinderId.value || binderId === null) return
  classShareBusy.value = true
  try {
    if (isClassShared(c.id)) {
      await groupService.unshareBinder(c.id, binderId)
    } else {
      await groupService.shareBinder(c.id, binderId, 'read')
    }
    await loadSharedClasses()
  } catch {
    alert('Action impossible sur cette classe.')
  } finally {
    classShareBusy.value = false
  }
}

// On observe currentBinder (et non currentBinderId) : l'indicateur « partagé »
// se met à jour dès que l'objet classeur est résolu après le chargement.
watch(currentBinder, loadSharedClasses, { immediate: true })
</script>
