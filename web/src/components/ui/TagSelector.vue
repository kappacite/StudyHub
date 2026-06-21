<template>
  <div ref="rootRef" class="relative" :class="compact ? '' : 'space-y-2'">
    <button
      v-if="compact"
      type="button"
      class="flex h-9 w-full min-w-0 items-center justify-between gap-2 rounded-xl border border-line bg-surface px-3 text-xs font-bold text-ink-muted transition-all hover:border-primary/40 hover:bg-surface-soft"
      :disabled="disabled"
      @click="isOpen = !isOpen"
    >
      <span class="flex min-w-0 items-center gap-1.5">
        <span
          v-for="tag in selectedTags.slice(0, 2)"
          :key="tag.id"
          class="h-2.5 w-2.5 shrink-0 rounded-full"
          :style="{ backgroundColor: tag.color || '#F06292' }"
        ></span>
        <span class="truncate">{{ compactLabel }}</span>
      </span>
      <span class="rounded-lg bg-surface-soft px-1.5 py-0.5 text-[10px] text-ink-subtle">{{ selectedTags.length }}</span>
    </button>

    <div v-if="!compact" class="flex flex-wrap gap-1.5">
      <TagBadge
        v-for="tag in selectedTags"
        :key="tag.id"
        :tag="tag"
        removable
        @remove="removeTag(tag.id)"
      />
      <span v-if="selectedTags.length === 0" class="text-xs font-semibold text-ink-subtle">Aucun tag</span>
    </div>

    <div
      v-if="!compact || isOpen"
      class="tag-selector-panel"
      :class="compact ? 'absolute right-0 top-full z-50 mt-2 w-[min(22rem,calc(100vw-2rem))] rounded-2xl border border-line bg-surface p-3 shadow-elev-3' : ''"
    >
      <div v-if="compact" class="mb-3 flex flex-wrap gap-1.5">
        <TagBadge
          v-for="tag in selectedTags"
          :key="tag.id"
          :tag="tag"
          removable
          @remove="removeTag(tag.id)"
        />
        <span v-if="selectedTags.length === 0" class="text-xs font-semibold text-ink-subtle">Aucun tag</span>
      </div>

      <div class="flex flex-col gap-2 sm:flex-row">
      <select
        class="min-w-0 flex-1 rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
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
          class="min-w-0 flex-1 rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
          placeholder="Nouveau tag"
          :disabled="disabled || isCreating"
          @keydown.enter.prevent="createAndSelectTag"
        />
        <label class="relative flex h-9 w-11 shrink-0 cursor-pointer items-center justify-center rounded-xl border border-line bg-surface-soft transition hover:border-primary/40" title="Couleur du tag">
          <span class="h-5 w-5 rounded-full border border-white shadow-sm ring-1 ring-line" :style="{ backgroundColor: newTagColor }"></span>
          <input
            v-model="newTagColor"
            type="color"
            class="absolute inset-0 h-full w-full cursor-pointer opacity-0"
            :disabled="disabled || isCreating"
            aria-label="Couleur du tag"
          />
        </label>
        <button
          type="button"
          class="rounded-full bg-primary px-3 py-2 text-xs font-bold text-white transition hover:bg-primary-strong disabled:opacity-50"
          :disabled="disabled || isCreating || !newTagName.trim()"
          @click="createAndSelectTag"
        >
          Créer
        </button>
      </div>
    </div>

      <div class="mt-2 flex flex-wrap gap-1.5">
        <button
          v-for="color in presetColors"
          :key="color"
          type="button"
          class="h-6 w-6 rounded-full border-2 transition hover:scale-105"
          :class="newTagColor.toLowerCase() === color.toLowerCase() ? 'border-ink' : 'border-surface'"
          :style="{ backgroundColor: color }"
          :disabled="disabled || isCreating"
          @click="newTagColor = color"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import TagBadge from './TagBadge.vue'
import { useTagsStore, type Tag } from '../../stores/tags'

const props = withDefaults(defineProps<{
  modelValue: Tag[]
  disabled?: boolean
  compact?: boolean
}>(), {
  disabled: false,
  compact: false
})

const emit = defineEmits<{
  'update:modelValue': [tags: Tag[]]
  change: [tags: Tag[]]
}>()

const tagsStore = useTagsStore()
const newTagName = ref('')
const newTagColor = ref('#F06292')
const isCreating = ref(false)
const isOpen = ref(false)
const rootRef = ref<HTMLElement | null>(null)
const presetColors = ['#F06292', '#0F766E', '#F59E0B', '#E11D48', '#7C3AED', '#0284C7']

const selectedIds = computed(() => new Set(props.modelValue.map(tag => tag.id)))
const selectedTags = computed(() => props.modelValue)
const availableTags = computed(() => tagsStore.tags.filter(tag => !selectedIds.value.has(tag.id)))
const compactLabel = computed(() => {
  if (selectedTags.value.length === 0) return 'Tags'
  if (selectedTags.value.length === 1) return selectedTags.value[0].name
  return `${selectedTags.value[0].name} +${selectedTags.value.length - 1}`
})

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

function handleClickOutside(event: MouseEvent) {
  if (!props.compact || !isOpen.value) return
  if (rootRef.value && !rootRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleClickOutside))
</script>
