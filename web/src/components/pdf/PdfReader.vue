<template>
  <div class="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800/80 rounded-3xl shadow-sm overflow-hidden">
    <!-- Toolbar -->
    <div class="flex items-center justify-between gap-3 px-4 py-3 border-b border-slate-100 dark:border-slate-800">
      <span class="text-sm font-bold text-slate-800 dark:text-white truncate">{{ pdfStore.activePdf?.name }}</span>
      <div class="flex items-center gap-2">
        <a
          v-if="pdfStore.activePdfUrl"
          :href="pdfStore.activePdfUrl"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-850 transition"
        >
          <ExternalLink class="w-3.5 h-3.5" />
          Ouvrir dans un onglet
        </a>
      </div>
    </div>

    <!-- Viewer -->
    <div class="relative bg-slate-100 dark:bg-slate-950" style="height: 75vh;">
      <div v-if="pdfStore.opening" class="absolute inset-0 flex items-center justify-center">
        <Loader2 class="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
      <iframe
        v-else-if="pdfStore.activePdfUrl"
        :src="pdfStore.activePdfUrl"
        class="w-full h-full"
        title="Document PDF"
      ></iframe>
      <div v-else class="absolute inset-0 flex flex-col items-center justify-center text-slate-400">
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
