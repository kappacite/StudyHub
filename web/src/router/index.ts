import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
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
      // ─── Sections canoniques (refonte 5 sections) ───────────────────────
      {
        path: 'accueil',
        name: 'Accueil',
        // S1 : Accueil = fusion Dashboard + Focus (vue action-first).
        component: () => import('../views/Home/Accueil.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'bibliotheque/:id?',
        name: 'Bibliotheque',
        component: () => import('../views/Binders/Binders.vue'),
        meta: { requiresAuth: true }
      },
      {
        // Réviser un dossier entier : agrège les cartes dues de tous ses decks.
        // Réutilise le runner StudyDeck (mode « dossier »).
        path: 'bibliotheque/:id/reviser',
        name: 'StudyBinder',
        component: () => import('../views/Decks/StudyDeck.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'reviser',
        name: 'Reviser',
        component: () => import('../views/Reviews/Reviews.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'classes',
        name: 'Classes',
        component: () => import('../views/Classes/ClassesLanding.vue'),
        meta: { requiresAuth: true }
      },

      // ─── Redirections des anciennes routes liste → sections ─────────────
      // Activées en S0 : cibles déjà fonctionnelles, aucun router.push interne cassé.
      { path: 'dashboard', redirect: { name: 'Accueil' } },
      { path: 'focus', redirect: { name: 'Accueil' } },
      { path: 'binders/:id?', redirect: to => ({ name: 'Bibliotheque', params: to.params, query: to.query }) },
      { path: 'reviews', redirect: { name: 'Reviser' } },
      { path: 'classes/teacher', redirect: { name: 'Classes', query: { tab: 'teacher' } } },
      { path: 'classes/student', redirect: { name: 'Classes', query: { tab: 'student' } } },
      { path: 'groups', redirect: { name: 'Classes', query: { tab: 'groups' } } },

      // ─── Routes encore réelles (redirect différé à leur lot) ────────────
      // /decks (S3), /notes /pdfs /diagrams (S2).
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
        path: 'revision/sets/:id/manage',
        name: 'RevisionSetManage',
        component: () => import('../views/Reviews/RevisionSetManage.vue'),
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
        // Feuille préservée : GroupsList est aussi monté dans l'onglet Groupes de Classes,
        // mais le détail d'un groupe garde sa route propre.
        path: 'groups/:id',
        name: 'GroupDetail',
        component: () => import('../views/Groups/GroupDetail.vue'),
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
    redirect: { name: 'Accueil' }
  }
]

const router = createRouter({
  // En desktop (Electron), l'app est servie via un protocole custom (app://-) sans
  // serveur HTTP : l'history HTML5 casserait au rechargement/deep-link. On bascule
  // donc en hash history, gated par le flag de build VITE_DESKTOP (web inchangé).
  history: import.meta.env.VITE_DESKTOP === 'true'
    ? createWebHashHistory()
    : createWebHistory(import.meta.env.BASE_URL),
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
    next({ name: 'Accueil' })
  } else {
    next()
  }
})

export default router
