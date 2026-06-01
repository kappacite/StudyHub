import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import { useAuthStore } from './stores/auth'
import './style.css'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Initialiser l'état auth à partir de localStorage
const authStore = useAuthStore()
authStore.init()

app.use(router)
app.mount('#app')
