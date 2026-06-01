import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

const api = axios.create({
  // Backend URL can be set using VITE_API_BASE_URL env variable, fallback to default Flask dev port
  baseURL: (import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000') + '/api/v1',
  timeout: 10000,
})

// Request Interceptor: inject JWT token
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
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
