<template>
  <PageContainer>
    <PageHeader title="Classes" subtitle="Vos cours, devoirs et groupes d'étude">
      <template #tabs>
        <Tabs v-model="activeTab" :tabs="visibleTabs" />
      </template>
    </PageHeader>

    <TeacherDashboard v-if="activeTab === 'teacher'" />
    <StudentClassView v-else-if="activeTab === 'student'" />
    <GroupsList v-else />
  </PageContainer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { PageContainer, PageHeader, Tabs } from '../../components/ui/base'
import type { TabItem } from '../../components/ui/base'
import { GraduationCap, BookOpen, UsersRound } from '@lucide/vue'
import classService from '../../services/classService'
import TeacherDashboard from './TeacherDashboard.vue'
import StudentClassView from './StudentClassView.vue'
import GroupsList from '../Groups/GroupsList.vue'

type TabKey = 'teacher' | 'student' | 'groups'

const route = useRoute()
const router = useRouter()

// L'onglet « Enseignant » n'apparaît que si l'utilisateur administre au moins une classe
// (propriétaire ou admin) — il n'existe pas de rôle global dans le store auth.
const isTeacher = ref(false)

const allTabs: Record<TabKey, TabItem> = {
  teacher: { key: 'teacher', label: 'Enseignant', icon: GraduationCap },
  student: { key: 'student', label: 'Élève', icon: BookOpen },
  groups: { key: 'groups', label: 'Groupes', icon: UsersRound },
}

const visibleTabs = computed<TabItem[]>(() =>
  (isTeacher.value ? ['teacher', 'student', 'groups'] : ['student', 'groups']).map(k => allTabs[k as TabKey])
)

function isValidTab(value: unknown): value is TabKey {
  return value === 'teacher' || value === 'student' || value === 'groups'
}

const activeTab = ref<TabKey>(isValidTab(route.query.tab) ? route.query.tab : 'student')

// Garder l'URL synchronisée (?tab=) — permet aux redirections /classes/teacher etc. de fonctionner.
watch(activeTab, (tab) => {
  if (route.query.tab !== tab) {
    router.replace({ query: { ...route.query, tab } })
  }
})

onMounted(async () => {
  try {
    const classes = await classService.getMyClasses()
    isTeacher.value = classes.some(c => c.my_role === 'admin' || c.my_role === 'owner')
  } catch {
    isTeacher.value = false
  }

  // Si l'onglet demandé est « teacher » mais l'utilisateur n'administre rien, ou si aucun
  // onglet valide n'est fourni, choisir un défaut cohérent.
  if (!isValidTab(route.query.tab)) {
    activeTab.value = isTeacher.value ? 'teacher' : 'student'
  } else if (route.query.tab === 'teacher' && !isTeacher.value) {
    activeTab.value = 'student'
  } else {
    activeTab.value = route.query.tab
  }
})
</script>
