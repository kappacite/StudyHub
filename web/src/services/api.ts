import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const api = axios.create({
  // En production derrière Nginx, utiliser une URL relative pour éviter les erreurs Mixed Content.
  // VITE_API_BASE_URL est vide → '/api/v1' (même domaine, Nginx proxifie vers le backend)
  // En dev → 'http://localhost:5000/api/v1'
  baseURL: import.meta.env.VITE_API_BASE_URL
    ? import.meta.env.VITE_API_BASE_URL + '/api/v1'
    : import.meta.env.DEV
      ? 'http://localhost:5000/api/v1'
      : '/api/v1',
  timeout: 10000,
})

// Request Interceptor: inject JWT token
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// Response Interceptor: handle token refresh and automatic redirects on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // If the refresh token itself failed, log out and redirect to login immediately
      if (originalRequest.url?.includes('/auth/refresh')) {
        const auth = useAuthStore()
        auth.logout()
        router.push('/login')
        return Promise.reject(error)
      }
      
      const auth = useAuthStore()
      
      try {
        await auth.refresh()
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${auth.token}`
        return api(originalRequest)
      } catch (refreshError) {
        auth.logout()
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export default api
