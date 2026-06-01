import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: number
  email: string
  username: string
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  // Initialisation à partir du localStorage
  function init() {
    const savedUser = localStorage.getItem('sh_user')
    const savedToken = localStorage.getItem('sh_token')
    if (savedUser && savedToken) {
      user.value = JSON.parse(savedUser)
      token.value = savedToken
    }
  }

  async function login(email: string, password: string): Promise<void> {
    // Simuler un appel réseau
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email.includes('@') && password.length >= 6) {
          const mockUser: User = {
            id: 1,
            email,
            username: email.split('@')[0],
            created_at: new Date().toISOString()
          }
          const mockToken = 'mock-jwt-token-xyz-12345'
          
          user.value = mockUser
          token.value = mockToken
          
          localStorage.setItem('sh_user', JSON.stringify(mockUser))
          localStorage.setItem('sh_token', mockToken)
          resolve()
        } else {
          reject(new Error('Email ou mot de passe incorrect (le mot de passe doit comporter au moins 6 caractères)'))
        }
      }, 1000)
    })
  }

  async function register(email: string, username: string, password: string): Promise<void> {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (email.includes('@') && username.length >= 3 && password.length >= 6) {
          const mockUser: User = {
            id: 1,
            email,
            username,
            created_at: new Date().toISOString()
          }
          const mockToken = 'mock-jwt-token-xyz-12345'
          
          user.value = mockUser
          token.value = mockToken
          
          localStorage.setItem('sh_user', JSON.stringify(mockUser))
          localStorage.setItem('sh_token', mockToken)
          resolve()
        } else {
          reject(new Error('Informations d\'inscription invalides'))
        }
      }, 1000)
    })
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('sh_user')
    localStorage.removeItem('sh_token')
  }

  async function refresh() {
    // Simuler le rafraîchissement du token
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        token.value = 'mock-jwt-token-refreshed-' + Date.now()
        localStorage.setItem('sh_token', token.value)
        resolve()
      }, 500)
    })
  }

  return {
    user,
    token,
    isAuthenticated,
    init,
    login,
    register,
    logout,
    refresh
  }
})
