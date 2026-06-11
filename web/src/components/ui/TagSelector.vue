<template>
  <div class="space-y-2">
    <div class="flex flex-wrap gap-1.5">
      <TagBadge
        v-for="tag in selectedTags"
        :key="tag.id"
        :tag="tag"
        removable
        @remove="removeTag(tag.id)"
      />
      <span v-if="selectedTags.length === 0" class="text-xs font-semibold text-slate-400">Aucun tag</span>
    </div>

    <div class="flex flex-col gap-2 sm:flex-row">
      <select
        class="min-w-0 flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold dark:border-slate-800 dark:bg-slate-900"
        :disabled="disabled"
        @change="addSelectedTag"
      >
        <option value="">Ajouter un tag...</option>
        <option v-for="tag in availableTags" :key="tag.id" :value="tag.id">{{ tag.name }}</option>
      </select>

      <div class="flex gap-2">
        <input
          v-model="newTagName"
          type="text"
          maxlength="30"
          class="min-w-0 flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold dark:border-slate-800 dark:bg-slate-900"
          placeholder="Nouveau tag"
          :disabled="disabled || isCreating"
          @keydown.enter.prevent="createAndSelectTag"
        />
        <input
          v-model="newTagColor"
          type="color"
          class="h-9 w-10 rounded-xl border border-slate-200 bg-white p-1 dark:border-slate-800 dark:bg-slate-900"
          :disabled="disabled || isCreating"
          title="Couleur du tag"
        />
        <button
          type="button"
          class="rounded-xl bg-indigo-600 px-3 py-2 text-xs font-bold text-white hover:bg-indigo-700 disabled:opacity-50"
          :disabled="disabled || isCreating || !newTagName.trim()"
          @click="createAndSelectTag"
        >
          Créer
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import TagBadge from './TagBadge.vue'
import { useTagsStore, type Tag } from '../../stores/tags'

const props = withDefaults(defineProps<{
  modelValue: Tag[]
  disabled?: boolean
}>(), {
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [tags: Tag[]]
  change: [tags: Tag[]]
}>()

const tagsStore = useTagsStore()
const newTagName = ref('')
const newTagColor = ref('#4F46E5')
const isCreating = ref(false)

const selectedIds = computed(() => new Set(props.modelValue.map(tag => tag.id)))
const selectedTags = computed(() => props.modelValue)
const availableTags = computed(() => tagsStore.tags.filter(tag => !selectedIds.value.has(tag.id)))

function update(tags: Tag[]) {
  emit('update:modelValue', tags)
  emit('change', tags)
}

function addSelectedTag(event: Event) {
  const select = event.target as HTMLSelectElement
  const tagId = Number(select.value)
  const tag = tagsStore.tags.find(item => item.id === tagId)
  if (tag) update([...props.modelValue, tag])
  select.value = ''
}

function removeTag(tagId: number) {
  update(props.modelValue.filter(tag => tag.id !== tagId))
}

async function createAndSelectTag() {
  const name = newTagName.value.trim()
  if (!name) return
  isCreating.value = true
  try {
    const tag = await tagsStore.createTag(name, newTagColor.value)
    update([...props.modelValue, tag])
    newTagName.value = ''
  } finally {
    isCreating.value = false
  }
}
</script>
