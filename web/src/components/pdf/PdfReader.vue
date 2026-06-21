<template>
  <div class="bg-surface dark:bg-surface-soft border border-line dark:border-line rounded-3xl shadow-sm overflow-hidden">
    <!-- Toolbar -->
    <div class="flex items-center justify-between gap-3 px-4 py-3 border-b border-line dark:border-line">
      <span class="text-sm font-bold text-ink dark:text-white truncate">{{ pdfStore.activePdf?.name }}</span>
      <div class="flex items-center gap-2">
        <a
          v-if="pdfStore.activePdfUrl"
          :href="pdfStore.activePdfUrl"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-line dark:border-line text-xs font-semibold text-ink-muted dark:text-ink-subtle hover:bg-surface-soft dark:hover:bg-surface-soft transition"
        >
          <ExternalLink class="w-3.5 h-3.5" />
          Ouvrir dans un onglet
        </a>
      </div>
    </div>

    <!-- Viewer -->
    <div class="relative bg-surface-soft dark:bg-surface-soft" style="height: 75vh;">
      <div v-if="pdfStore.opening" class="absolute inset-0 flex items-center justify-center">
        <Loader2 class="w-8 h-8 text-primary animate-spin" />
      </div>
      <iframe
        v-else-if="pdfStore.activePdfUrl"
        :src="pdfStore.activePdfUrl"
        class="w-full h-full"
        title="Document PDF"
      ></iframe>
      <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-ink-subtle">
        <FileText class="w-10 h-10 mb-2 opacity-50" />
        <p class="text-xs font-semibold uppercase tracking-wider">Document indisponible</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePdfStore } from '../../stores/pdf'
import { ExternalLink, Loader2, FileText } from '@lucide/vue'

const pdfStore = usePdfStore()
</script>
