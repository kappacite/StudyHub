<template>
  <BaseModal
    :open="true"
    :title="isEdit ? 'Modifier l\'ensemble' : 'Nouvel ensemble de révision'"
    @close="$emit('close')"
  >
    <p class="text-xs text-ink-muted -mt-2 mb-4">
      Un ensemble regroupe plusieurs éléments de révision (flashcards, QCM, vrai/faux...) autour
      d'un même sujet.
    </p>
    <form class="space-y-4" @submit.prevent="submit">
      <BaseField label="Nom de l'ensemble" for-id="revision-set-name">
        <BaseInput id="revision-set-name" v-model="name" placeholder="Ex: Mécanismes SN1 / SN2" />
      </BaseField>
      <BaseField label="Description (optionnel)" for-id="revision-set-description">
        <textarea
          id="revision-set-description"
          v-model="description"
          rows="3"
          placeholder="Ex: Flashcards, QCM et vrai/faux sur les mécanismes de substitution."
          class="block w-full px-4 py-3 bg-surface border border-line rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/40 text-sm font-medium text-ink"
        ></textarea>
      </BaseField>
      <p v-if="error" class="text-xs text-danger">{{ error }}</p>
      <div class="flex items-center justify-end gap-2 pt-2">
        <BaseButton type="button" variant="ghost" @click="$emit('close')">Annuler</BaseButton>
        <BaseButton type="submit" :loading="saving" :disabled="!name.trim()">{{
          isEdit ? 'Enregistrer' : 'Créer'
        }}</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRevisionStore } from '../../stores/revision'
import type { RevisionSet } from '../../stores/revision'
import { BaseModal, BaseField, BaseInput, BaseButton } from '../ui/base'

const props = defineProps<{
  mode: 'create' | 'edit'
  binderId: string | null
  set?: RevisionSet
}>()
const emit = defineEmits<{
  (e: 'created', set: RevisionSet): void
  (e: 'updated'): void
  (e: 'close'): void
}>()

const isEdit = computed(() => props.mode === 'edit')
const name = ref(props.set?.name ?? '')
const description = ref(props.set?.description ?? '')
const saving = ref(false)
const error = ref('')

const revisionStore = useRevisionStore()

async function submit() {
  if (!name.value.trim() || saving.value) return
  saving.value = true
  error.value = ''
  try {
    if (isEdit.value && props.set) {
      await revisionStore.updateSet(props.set.id, {
        name: name.value.trim(),
        description: description.value.trim() || null,
      })
      emit('updated')
    } else {
      const created = await revisionStore.createSet(
        name.value.trim(),
        null,
        description.value.trim() || null,
        props.binderId,
      )
      emit('created', created)
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Impossible d'enregistrer l'ensemble."
  } finally {
    saving.value = false
  }
}
</script>
