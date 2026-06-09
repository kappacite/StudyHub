import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: Array<RouteRecordRaw> = [
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
    component: () => import('../components/layout/PublicLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/Marketplace/Home.vue')
      },
      {
        path: 'explore',
        name: 'Explore',
        component: () => import('../views/Marketplace/Explore.vue')
      },
      {
        path: 'package/:id',
        name: 'PackagePreview',
        component: () => import('../views/Marketplace/PackagePreview.vue')
      },
      {
        path: 'notes/public/:token',
        name: 'PublicNote',
        component: () => import('../views/Notes/PublicNote.vue')
      }
    ]
  },
  {
    path: '/',
    component: () => import('../components/layout/AppLayout.vue'),
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard/Dashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'binders',
        name: 'Binders',
        component: () => import('../views/Binders/Binders.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'decks',
        name: 'Decks',
        component: () => import('../views/Decks/Decks.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'decks/:id/study',
        name: 'StudyDeck',
        component: () => import('../views/Decks/StudyDeck.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'reviews',
        name: 'Reviews',
        component: () => import('../views/Reviews/Reviews.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'notes',
        name: 'Notes',
        component: () => import('../views/Notes/Notes.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'notes/:id',
        name: 'NoteEdit',
        component: () => import('../views/Notes/NoteEdit.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'notes/:id/blurting',
        name: 'Blurting',
        component: () => import('../views/Notes/Blurting.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'diagrams',
        name: 'Diagrams',
        component: () => import('../views/Diagrams/Diagrams.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'pdfs',
        name: 'PDFs',
        component: () => import('../views/PDFs/PDFs.vue'),
        meta: { requiresAuth: true }
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
