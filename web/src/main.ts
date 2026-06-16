import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { MotionPlugin } from '@vueuse/motion'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'
import App from './App.vue'

import DOMPurify from 'dompurify'

const app = createApp(App)
const pinia = createPinia()

app.directive('dompurify-html', (el, binding) => {
  el.innerHTML = DOMPurify.sanitize(binding.value || '')
})

app.use(pinia)
app.use(MotionPlugin)

// Initialiser l'état auth à partir de localStorage
const authStore = useAuthStore()
authStore.init()

app.use(router)
app.mount('#app')

// Enregistrement des outils WebMCP pour les agents d'exploration IA
if (typeof window !== 'undefined' && 'modelContext' in navigator) {
  try {
    const controller = new AbortController();
    (navigator as any).modelContext.registerTool({
      name: "explore_packages",
      description: "Rechercher et explorer les packages d'étude publics dans la marketplace de StudyHub",
      inputSchema: {
        type: "object",
        properties: {
          search: { type: "string", description: "Terme de recherche pour filtrer les packages" }
        }
      }
    }, async (args: any) => {
      console.log("WebMCP execute explore_packages", args);
      return { success: true, message: "Recherche de packages effectuée avec succès." };
    }, { signal: controller.signal });
  } catch (e) {
    console.error("Erreur d'enregistrement WebMCP:", e);
  }
}
