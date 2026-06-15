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
        path: 'focus',
        name: 'Focus',
        component: () => import('../views/Focus/FocusPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'binders/:id?',
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
        path: 'revision/sets/:id/run',
        name: 'QcmRun',
        component: () => import('../views/Reviews/QcmRun.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'revision/sets/:id/study',
        name: 'RevisionStudy',
        component: () => import('../views/Reviews/RevisionStudy.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'revision/sets/:id/stats',
        name: 'RevisionSetStats',
        component: () => import('../views/Reviews/RevisionSetStats.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'revision/binders/:id/stats',
        name: 'RevisionBinderStats',
        component: () => import('../views/Reviews/RevisionBinderStats.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'reviews',
        name: 'Reviews',
        component: () => import('../views/Reviews/Reviews.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'planning',
        name: 'Planning',
        component: () => import('../views/Planning/PlanningPage.vue'),
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
        path: 'notes/:id/quiz',
        name: 'NoteQuiz',
        component: () => import('../views/Notes/NoteQuiz.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'notes/:id/evaluation',
        name: 'NoteEvaluation',
        component: () => import('../views/Notes/NoteEvaluation.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'exam/setup',
        name: 'ExamSetup',
        component: () => import('../views/Exam/ExamSetup.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'exam/:id',
        name: 'ExamSession',
        component: () => import('../views/Exam/ExamSession.vue'),
        meta: { requiresAuth: true, immersive: true }
      },
      {
        path: 'exam/:id/results',
        name: 'ExamResults',
        component: () => import('../views/Exam/ExamResults.vue'),
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
      },
      {
        path: 'groups',
        name: 'Groups',
        component: () => import('../views/Groups/GroupsList.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'groups/:id',
        name: 'GroupDetail',
        component: () => import('../views/Groups/GroupDetail.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'classes/teacher',
        name: 'TeacherDashboard',
        component: () => import('../views/Classes/TeacherDashboard.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'classes/student',
        name: 'StudentClassView',
        component: () => import('../views/Classes/StudentClassView.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'classes/:classId/assignments/:asgnId',
        name: 'AssignmentDetail',
        component: () => import('../views/Classes/AssignmentDetail.vue'),
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
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Si c'est la même page et que seuls les paramètres de requête/hash changent, ne pas scroller
    if (to.path === from.path) {
      return false
    }
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  }
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
