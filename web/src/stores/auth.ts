import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export interface User {
  id: number
  email: string
  username: string
  created_at: string
}

interface LoginResponse {
  access_token: string
  refresh_token: string
  user: User
}

interface RefreshResponse {
  access_token: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  function init() {
    const savedUser = localStorage.getItem('sh_user')
    const savedToken = localStorage.getItem('sh_token')
    const savedRefreshToken = localStorage.getItem('sh_refresh_token')
    if (savedUser && savedToken && savedRefreshToken) {
      user.value = JSON.parse(savedUser)
      token.value = savedToken
      refreshToken.value = savedRefreshToken
    }
  }

  async function login(email: string, password: string): Promise<void> {
    try {
      const response = await api.post<LoginResponse>('/auth/login', { email, password })
      const { access_token, refresh_token, user: loggedUser } = response.data
      
      token.value = access_token
      refreshToken.value = refresh_token
      user.value = loggedUser
      
      localStorage.setItem('sh_user', JSON.stringify(loggedUser))
      localStorage.setItem('sh_token', access_token)
      localStorage.setItem('sh_refresh_token', refresh_token)
    } catch (error: any) {
      const msg = error.response?.data?.error?.message || 'Identifiants ou mot de passe incorrect.'
      throw new Error(msg)
    }
  }

  async function register(email: string, username: string, password: string): Promise<void> {
    try {
      await api.post('/auth/register', { email, username, password })
      // Auto login after registration
      await login(email, password)
    } catch (error: any) {
      const msg = error.response?.data?.error?.message || 'Erreur lors de l\'inscription.'
      throw new Error(msg)
    }
  }

  async function logout(): Promise<void> {
    try {
      if (token.value) {
        await api.post('/auth/logout')
      }
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      user.value = null
      token.value = null
      refreshToken.value = null
      localStorage.removeItem('sh_user')
      localStorage.removeItem('sh_token')
      localStorage.removeItem('sh_refresh_token')
    }
  }

  async function refresh(): Promise<void> {
    try {
      if (!refreshToken.value) throw new Error('Pas de refresh token')
      
      // Call endpoint by sending the refresh token in Authorization header
      const response = await api.post<RefreshResponse>('/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${refreshToken.value}`
        }
      })
      
      const { access_token } = response.data
      token.value = access_token
      localStorage.setItem('sh_token', access_token)
    } catch (error) {
      logout()
      throw error
    }
  }

  return {
    user,
    token,
    refreshToken,
    isAuthenticated,
    init,
    login,
    register,
    logout,
    refresh
  }
})
