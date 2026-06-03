import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Auth/Login.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Auth/Register.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/',
    component: () => import('../components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard/Dashboard.vue')
      },
      {
        path: 'binders',
        name: 'Binders',
        component: () => import('../views/Binders/Binders.vue')
      },
      {
        path: 'decks',
        name: 'Decks',
        component: () => import('../views/Decks/Decks.vue')
      },
      {
        path: 'decks/:id/study',
        name: 'StudyDeck',
        component: () => import('../views/Decks/StudyDeck.vue')
      },
      {
        path: 'reviews',
        name: 'Reviews',
        component: () => import('../views/Reviews/Reviews.vue')
      },
      {
        path: 'notes',
        name: 'Notes',
        component: () => import('../views/Notes/Notes.vue')
      },
      {
        path: 'notes/:id',
        name: 'NoteEdit',
        component: () => import('../views/Notes/NoteEdit.vue')
      },
      {
        path: 'diagrams',
        name: 'Diagrams',
        component: () => import('../views/Diagrams/Diagrams.vue')
      },
      {
        path: 'pdfs',
        name: 'PDFs',
        component: () => import('../views/PDFs/PDFs.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guestOnly && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
