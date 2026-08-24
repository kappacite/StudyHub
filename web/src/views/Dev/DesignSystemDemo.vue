<template>
  <PageContainer>
    <PageHeader title="Design System — Direction A « Fiche »">
      <template #actions>
        <BaseButton data-test="toggle-theme" variant="secondary" size="sm" @click="toggleDark">
          {{ isDark ? 'Thème clair' : 'Thème sombre' }}
        </BaseButton>
      </template>
    </PageHeader>

    <section data-demo="bouton" class="space-y-3">
      <h2 class="font-display text-display-md">Boutons</h2>
      <div class="flex flex-wrap items-center gap-3">
        <BaseButton variant="primary">Primaire</BaseButton>
        <BaseButton variant="secondary">Secondaire</BaseButton>
        <BaseButton variant="ghost">Discret</BaseButton>
        <BaseButton variant="soft">Doux</BaseButton>
        <BaseButton variant="danger">Supprimer</BaseButton>
        <BaseButton variant="primary" loading>Chargement</BaseButton>
        <BaseButton variant="primary" disabled>Désactivé</BaseButton>
      </div>
    </section>

    <section data-demo="champ" class="space-y-3 max-w-sm">
      <h2 class="font-display text-display-md">Champs</h2>
      <BaseField label="Matière" hint="Ex. Chimie organique">
        <BaseInput v-model="demoInput" placeholder="Chimie organique" />
      </BaseField>
      <BaseField label="Email" required error="Adresse invalide">
        <BaseInput v-model="demoInput" type="email" />
      </BaseField>
    </section>

    <section data-demo="carte" class="space-y-3">
      <h2 class="font-display text-display-md">Cartes</h2>
      <div class="grid grid-cols-2 gap-4 max-w-lg">
        <BaseCard>Carte statique</BaseCard>
        <BaseCard interactive>Carte interactive (survol)</BaseCard>
      </div>
    </section>

    <section data-demo="badge" class="space-y-3">
      <h2 class="font-display text-display-md">Badges</h2>
      <div class="flex flex-wrap gap-2">
        <BaseBadge variant="neutral">Neutre</BaseBadge>
        <BaseBadge variant="primary">Primaire</BaseBadge>
        <BaseBadge variant="accent">Accent</BaseBadge>
        <BaseBadge variant="success">Succès</BaseBadge>
        <BaseBadge variant="danger">Danger</BaseBadge>
        <BaseBadge size="sm" variant="info">Petit</BaseBadge>
      </div>
    </section>

    <section data-demo="onglet" class="space-y-3">
      <h2 class="font-display text-display-md">Onglets</h2>
      <Tabs
        v-model="activeTab"
        :tabs="[
          { key: 'a', label: 'Enseignant' },
          { key: 'b', label: 'Groupes', badge: 3 },
        ]"
      />
    </section>

    <section data-demo="info-bulle" class="space-y-3">
      <h2 class="font-display text-display-md">Info-bulle</h2>
      <BaseTooltip content="Facteur de facilité SM2 : 2.5 par défaut">
        <span class="underline decoration-dotted cursor-help text-sm">Survoler ce texte</span>
      </BaseTooltip>
    </section>

    <section data-demo="etat-vide" class="space-y-3">
      <h2 class="font-display text-display-md">État vide</h2>
      <BaseCard>
        <BaseEmptyState
          title="Aucune fiche à réviser"
          description="Revenez demain, ou ajoutez un nouveau deck."
        >
          <template #actions>
            <BaseButton size="sm">Créer un deck</BaseButton>
          </template>
        </BaseEmptyState>
      </BaseCard>
    </section>

    <section data-demo="squelette" class="space-y-3 max-w-sm">
      <h2 class="font-display text-display-md">Squelette de chargement</h2>
      <div class="space-y-2">
        <BaseSkeleton custom-class="h-4 w-3/4" />
        <BaseSkeleton custom-class="h-4 w-full" />
        <BaseSkeleton rounded="rounded-full" custom-class="h-10 w-10" />
      </div>
    </section>

    <section data-demo="toast" class="space-y-3 max-w-sm">
      <h2 class="font-display text-display-md">Toasts</h2>
      <div class="space-y-2">
        <BaseToast variant="success" title="Enregistré" message="Le deck a été mis à jour." />
        <BaseToast variant="danger" title="Échec" message="La synchronisation a échoué." />
      </div>
    </section>

    <section data-demo="modale" class="space-y-3">
      <h2 class="font-display text-display-md">Modale</h2>
      <BaseButton @click="modalOpen = true">Ouvrir la modale</BaseButton>
      <BaseModal :open="modalOpen" title="Supprimer ce deck ?" @close="modalOpen = false">
        <p class="text-sm text-ink-muted">Cette action est irréversible.</p>
        <template #footer>
          <BaseButton variant="secondary" @click="modalOpen = false">Annuler</BaseButton>
          <BaseButton variant="danger" @click="modalOpen = false">Supprimer</BaseButton>
        </template>
      </BaseModal>
    </section>
  </PageContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  BaseButton,
  BaseCard,
  BaseBadge,
  BaseField,
  BaseInput,
  BaseModal,
  BaseEmptyState,
  BaseSkeleton,
  BaseToast,
  BaseTooltip,
  Tabs,
  PageContainer,
  PageHeader,
} from '../../components/ui/base'

const isDark = ref(document.documentElement.classList.contains('dark'))
const demoInput = ref('')
const activeTab = ref('a')
const modalOpen = ref(false)

function toggleDark() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}
</script>
