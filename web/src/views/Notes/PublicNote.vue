<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50/30 dark:from-[#0B0F19] dark:to-indigo-950/10">
    


    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-32 gap-4">
      <div class="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
      <span class="text-sm text-slate-400 font-medium">Chargement de la note...</span>
    </div>

    <!-- Erreur -->
    <div v-else-if="error" class="flex flex-col items-center justify-center py-32 gap-4 text-center px-6">
      <div class="w-16 h-16 rounded-2xl bg-rose-100 dark:bg-rose-950/30 flex items-center justify-center">
        <Lock class="w-8 h-8 text-rose-500" />
      </div>
      <h1 class="text-xl font-bold text-slate-800 dark:text-white">Note introuvable</h1>
      <p class="text-slate-500 dark:text-slate-400 max-w-sm">Cette note n'existe pas ou n'est plus partagée publiquement.</p>
      <router-link to="/" class="mt-2 text-indigo-600 hover:text-indigo-700 font-semibold text-sm">← Retour à l'accueil</router-link>
    </div>

    <!-- Note content -->
    <div v-else-if="note" class="max-w-4xl mx-auto px-6 py-10">
      
      <!-- Meta -->
      <div class="mb-8">
        <div class="flex items-center gap-2 mb-4">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-400 text-xs font-bold rounded-full">
            <Globe class="w-3 h-3" />
            Note publique
          </span>
          <span class="text-xs text-slate-400 dark:text-slate-500">
            Modifiée le {{ formatDate(note.updated_at) }}
          </span>
        </div>
        <h1 class="text-3xl font-bold text-slate-900 dark:text-white leading-tight">{{ note.title }}</h1>
      </div>

      <!-- Copy link -->
      <div class="mb-8 p-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-2xl flex items-center gap-3 shadow-sm">
        <Link2 class="w-4 h-4 text-slate-400 shrink-0" />
        <span class="text-xs text-slate-500 dark:text-slate-400 font-mono flex-1 truncate">{{ shareUrl }}</span>
        <button
          @click="copyLink"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg transition-all active:scale-95"
        >
          <Check v-if="copied" class="w-3.5 h-3.5" />
          <Copy v-else class="w-3.5 h-3.5" />
          {{ copied ? 'Copié !' : 'Copier' }}
        </button>
      </div>

      <!-- 1. Context Block -->
      <div 
        v-if="parsedNote.context"
        class="mb-6 bg-amber-50/50 border-l-4 border-amber-500 rounded-r-2xl p-5 dark:bg-amber-950/10 dark:border-amber-700/50"
      >
        <h3 class="text-xs font-bold text-amber-800 dark:text-amber-400 flex items-center gap-1.5 uppercase tracking-wider mb-2">
          <Compass class="w-4 h-4" />
          Contexte de la note
        </h3>
        <div 
          v-dompurify-html="renderMarkup(parsedNote.context)"
          class="prose prose-amber max-w-none text-xs leading-relaxed dark:prose-invert"
        ></div>
      </div>

      <!-- 2. Legacy Definitions Block -->
      <div 
        v-if="parsedNote.definition"
        class="mb-6 bg-emerald-50/30 border-l-4 border-emerald-500 rounded-r-2xl p-5 dark:bg-emerald-950/10 dark:border-emerald-700/50"
      >
        <h3 class="text-xs font-bold text-emerald-800 dark:text-emerald-400 flex items-center gap-1.5 uppercase tracking-wider mb-2">
          <BookOpen class="w-4 h-4" />
          Définitions clés
        </h3>
        <div 
          v-dompurify-html="renderMarkup(parsedNote.definition)"
          class="prose prose-emerald max-w-none text-xs leading-relaxed dark:prose-invert"
        ></div>
      </div>

      <!-- Note body rendered as markdown -->
      <article 
        class="prose prose-slate max-w-none dark:prose-invert leading-relaxed text-sm dark:text-slate-300 markdown-body bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-3xl p-8 shadow-sm"
        v-dompurify-html="renderMarkup(parsedNote.body)"
      ></article>

      <!-- CTA footer -->
      <div class="mt-12 p-8 bg-gradient-to-br from-indigo-600 to-purple-700 rounded-3xl text-center text-white shadow-xl shadow-indigo-500/20">
        <h2 class="text-xl font-bold mb-2">Envie de créer tes propres notes ?</h2>
        <p class="text-indigo-200 text-sm mb-6">StudyHub est gratuit et tout-en-un : notes, flashcards, diagrammes, PDF...</p>
        <router-link
          to="/register"
          class="inline-flex items-center gap-2 px-6 py-3 bg-white text-indigo-700 hover:bg-indigo-50 font-bold rounded-xl transition-all shadow active:scale-95"
        >
          Créer un compte gratuitement
          <ArrowRight class="w-4 h-4" />
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowRight, Globe, Lock, Link2, Copy, Check, Compass, BookOpen } from '@lucide/vue'
import api from '../../services/api'
import { marked } from 'marked'
import katex from 'katex'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import 'katex/dist/katex.min.css'

// Configure marked to use highlight.js for syntax highlighting in code blocks
marked.use({
  breaks: true,
  gfm: true,
  renderer: {
    code({ text, lang }: { text: string; lang?: string }) {
      const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
      const highlighted = hljs.highlight(text, { language }).value
      return `<pre><code class="hljs language-${language}">${highlighted}</code></pre>`
    }
  }
})

const route = useRoute()

const note = ref<any>(null)
const loading = ref(true)
const error = ref(false)
const copied = ref(false)

const shareUrl = computed(() => window.location.href)

function parseStructuredNote(rawContent: string) {
  let contextVal = ''
  let definitionVal = ''
  let bodyVal = rawContent

  const contextMatch = rawContent.match(/<!-- SECTION_CONTEXT -->([\s\S]*?)<!-- END_SECTION_CONTEXT -->/)
  if (contextMatch) {
    contextVal = contextMatch[1].trim()
  }

  const defMatch = rawContent.match(/<!-- SECTION_DEFINITION -->([\s\S]*?)<!-- END_SECTION_DEFINITION -->/)
  if (defMatch) {
    definitionVal = defMatch[1].trim()
  }

  const bodyMatch = rawContent.match(/<!-- SECTION_BODY -->([\s\S]*?)<!-- END_SECTION_BODY -->/)
  if (bodyMatch) {
    bodyVal = bodyMatch[1].trim()
  } else {
    bodyVal = rawContent
      .replace(/<!-- SECTION_CONTEXT -->[\s\S]*?<!-- END_SECTION_CONTEXT -->/g, '')
      .replace(/<!-- SECTION_DEFINITION -->[\s\S]*?<!-- END_SECTION_DEFINITION -->/g, '')
      .trim()
  }

  return {
    context: contextVal,
    definition: definitionVal,
    body: bodyVal
  }
}

const parsedNote = computed(() => {
  if (!note.value?.content) return { context: '', definition: '', body: '' }
  return parseStructuredNote(note.value.content)
})

function renderMarkup(text: string): string {
  const normalizedText = (text || '').replace(/\r\n/g, '\n')
  let temp = normalizedText.replace(/\n{3,}/g, (match) => {
    const count = match.length - 2
    return '\n\n' + Array(count).fill('&nbsp;').join('\n\n') + '\n\n'
  })
  const placeholders: string[] = []

  // 1. Double dollars $$ (Display equations block)
  temp = temp.replace(/\$\$([\s\S]+?)\$\$/g, (_match, formula) => {
    try {
      const html = katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false })
      const key = `LATEXBLOCKPLACEHOLDER${placeholders.length}`
      placeholders.push(html)
      return key
    } catch (e) {
      return `<span class="text-rose-500 font-bold border border-rose-200 p-1 rounded">LaTeX Block Error: ${formula}</span>`
    }
  })

  // 2. Single dollars $ (Inline equations)
  temp = temp.replace(/\$([\s\S]+?)\$/g, (_match, formula) => {
    try {
      const html = katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false })
      const key = `LATEXINLINEPLACEHOLDER${placeholders.length}`
      placeholders.push(html)
      return key
    } catch (e) {
      return `<span class="text-rose-500 font-bold">LaTeX Inline Error: ${formula}</span>`
    }
  })

  // 3. Definition Tooltips [term]{def:definition}
  temp = temp.replace(/\[([^\]]+)\]\{def:([^\}]+)\}/g, (_match, term, definition) => {
    const html = `<span class="group relative inline-block underline decoration-emerald-500 decoration-dashed cursor-help bg-emerald-50/30 dark:bg-emerald-950/20 px-1.5 py-0.5 rounded transition-all duration-200">${term}<span class="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 w-64 -translate-x-1/2 rounded-xl bg-slate-900 dark:bg-slate-950 p-3 text-xs font-medium text-slate-100 dark:text-slate-200 shadow-xl opacity-0 transition-opacity duration-200 group-hover:opacity-100 leading-normal normal-case text-center">${definition}</span></span>`
    const key = `DEFPLACEHOLDER${placeholders.length}`
    placeholders.push(html)
    return key
  })

  // 4. Diagram Integration [diagram:ID]
  temp = temp.replace(/\[diagram:(\d+)\]/g, (_match, idStr) => {
    const html = `<div class="text-xs text-slate-400 italic my-2">Schéma #${idStr}</div>`
    const key = `DIAGRAMPLACEHOLDER${placeholders.length}`
    placeholders.push(html)
    return key
  })

  // 5. Active Reading Placeholders (Trou, QCM, VF, Ordre, Assoc) - Read-only mode
  // Trou: {{trou::mot caché}}
  temp = temp.replace(/\{\{trou::(.*?)\}\}/g, (_rawTag, word) => {
    const displayHtml = `<span class="bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 px-1.5 py-0.5 rounded font-semibold border-b border-indigo-500">${word}</span>`;
    const key = `REVISIONPLACEHOLDER${placeholders.length}`;
    placeholders.push(displayHtml);
    return key;
  });

  // QCM: {{qcm::Question ?::Option1|*OptionCorrecte*|Option3}}
  temp = temp.replace(/\{\{qcm::(.*?)::(.*?)\}\}/g, (_rawTag, question, optionsStr) => {
    const options = optionsStr.split('|').map((o: string) => o.trim());
    const listItems = options.map((opt: string) => {
      const isCorrect = opt.startsWith('*') && opt.endsWith('*');
      const cleanOpt = opt.replace(/\*/g, '');
      return isCorrect 
        ? `<li class="font-extrabold text-emerald-600 dark:text-emerald-400">✓ ${cleanOpt} (Correct)</li>`
        : `<li>${cleanOpt}</li>`;
    }).join('');
    
    const displayHtml = `
      <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
        <strong class="text-[10px] uppercase tracking-wider text-slate-400 font-bold block mb-1">QCM</strong>
        <p class="font-bold text-sm text-slate-800 dark:text-slate-100 mb-2">${question}</p>
        <ul class="list-none pl-0 mt-2 space-y-1 text-xs text-slate-600 dark:text-slate-400">${listItems}</ul>
      </div>
    `;
    const key = `REVISIONPLACEHOLDER${placeholders.length}`;
    placeholders.push(displayHtml);
    return '\n\n' + key + '\n\n';
  });

  // VF: {{vf::Affirmation::Vrai/Faux::Justification}}
  temp = temp.replace(/\{\{vf::(.*?)::(.*?)::(.*?)\}\}/g, (_rawTag, assertion, answer, justification) => {
    const isVrai = answer.trim().toLowerCase() === "vrai";
    const displayHtml = `
      <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
        <strong class="text-[10px] uppercase tracking-wider text-slate-400 font-bold block mb-1">Vrai ou Faux</strong>
        <p class="font-semibold text-sm text-slate-800 dark:text-slate-100">${assertion}</p>
        <div class="mt-2 text-xs font-bold">Réponse : <span class="${isVrai ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">${answer}</span></div>
        <div class="text-xs text-slate-500 italic mt-1">${justification}</div>
      </div>
    `;
    const key = `REVISIONPLACEHOLDER${placeholders.length}`;
    placeholders.push(displayHtml);
    return '\n\n' + key + '\n\n';
  });

  // Ordre: {{ordre::Titre::Étape 1 > Étape 2 > Étape 3}}
  temp = temp.replace(/\{\{ordre::(.*?)::(.*?)\}\}/g, (_rawTag, title, stepsStr) => {
    const steps = stepsStr.split('>').map((s: string) => s.trim());
    const cleanStep = (str: string) => {
      const cleaned = str.replace(/^(?:étape\s*\d+[\s\-:]*|\d+[\.\s\-:]+)\s*/i, '').trim();
      return cleaned.length > 0 ? cleaned : str;
    };
    const stepItems = steps.map((s: string) => `<li class="mb-1">${cleanStep(s)}</li>`).join('');
    const displayHtml = `
      <div class="bg-slate-50/50 dark:bg-slate-900/50 p-2.5 border border-slate-200 dark:border-slate-800 rounded-xl my-2 max-w-2xl shadow-sm not-prose">
        <strong class="text-[9px] uppercase tracking-wider text-slate-400 font-bold block mb-0.5">Séquence : ${title}</strong>
        <ol class="list-decimal mt-1.5 space-y-0.5 text-xs" style="margin-left: 1rem !important; padding-left: 1rem !important;">${stepItems}</ol>
      </div>
    `;
    const key = `REVISIONPLACEHOLDER${placeholders.length}`;
    placeholders.push(displayHtml);
    return '\n\n' + key + '\n\n';
  });

  // Assoc: {{assoc::Titre::A=1 | B=2 | C=3}}
  temp = temp.replace(/\{\{assoc::(.*?)::(.*?)\}\}/g, (_rawTag, title, pairsStr) => {
    const pairs = pairsStr.split('|').map((p: string) => {
      const eqIdx = p.indexOf('=')
      if (eqIdx === -1) return { key: p.trim(), value: '' }
      return { key: p.substring(0, eqIdx).trim(), value: p.substring(eqIdx + 1).trim() }
    });
    const rows = pairs.map((p: { key: string, value: string }) => `<tr><td class="border border-slate-200 dark:border-slate-800 p-2 font-semibold text-slate-700 dark:text-slate-350">${p.key}</td><td class="border border-slate-200 dark:border-slate-800 p-2 text-slate-600 dark:text-slate-400">${p.value}</td></tr>`).join('');
    const displayHtml = `
      <div class="bg-slate-50/50 dark:bg-slate-900/50 p-4 border border-slate-200 dark:border-slate-800 rounded-2xl my-4 max-w-2xl shadow-sm not-prose">
        <strong class="text-[10px] uppercase tracking-wider text-slate-400 font-bold block mb-1">Associations : ${title}</strong>
        <table class="table-auto text-xs mt-3 w-full border-collapse border border-slate-200 dark:border-slate-800">
          <thead>
            <tr class="bg-slate-150 dark:bg-slate-800 font-bold">
              <th class="border border-slate-200 dark:border-slate-800 p-2 text-left">Clé</th>
              <th class="border border-slate-200 dark:border-slate-800 p-2 text-left">Liaison</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
    const key = `REVISIONPLACEHOLDER${placeholders.length}`;
    placeholders.push(displayHtml);
    return '\n\n' + key + '\n\n';
  });

  // 6. Markdown parse
  let html = marked.parse(temp) as string

  // 7. Put LaTeX, Definition, Diagram, and REVISION HTML back
  placeholders.forEach((placeholderHtml, idx) => {
    html = html.replace(new RegExp(`LATEXBLOCKPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
    html = html.replace(new RegExp(`LATEXINLINEPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
    html = html.replace(new RegExp(`DEFPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
    html = html.replace(new RegExp(`DIAGRAMPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
    html = html.replace(new RegExp(`REVISIONPLACEHOLDER${idx}(?!\\d)`, 'g'), () => placeholderHtml)
  })

  // Post-processing: strip <p> wrappers around block elements and remove empty <p> tags
  html = html.replace(/<p>\s*(<div\b)/gi, '$1')
  html = html.replace(/(<\/div>)\s*<\/p>/gi, '$1')
  html = html.replace(/<p>\s*<\/p>/gi, '')

  return html
}

function formatDate(iso: string) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('fr-FR', {
    day: 'numeric', month: 'long', year: 'numeric'
  })
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {}
}

onMounted(async () => {
  const token = route.params.token as string
  try {
    const { data } = await api.get(`/notes/public/${token}`)
    note.value = data
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>
