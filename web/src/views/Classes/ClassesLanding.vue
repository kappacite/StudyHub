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

// `isTeacher` (administre au moins une classe) ne sert qu'à choisir l'onglet par défaut :
// l'onglet « Enseignant » est TOUJOURS visible, sinon un utilisateur sans classe ne pourrait
// jamais créer sa première (le bouton « Créer une classe » vit dans TeacherDashboard, dont
// l'empty state invite justement à créer).
const isTeacher = ref(false)

const allTabs: Record<TabKey, TabItem> = {
  teacher: { key: 'teacher', label: 'Enseignant', icon: GraduationCap },
  student: { key: 'student', label: 'Élève', icon: BookOpen },
  groups: { key: 'groups', label: 'Groupes', icon: UsersRound },
}

const visibleTabs = computed<TabItem[]>(() =>
  (['teacher', 'student', 'groups'] as TabKey[]).map(k => allTabs[k])
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

  // Onglet demandé honoré tel quel (tous valides désormais) ; sinon défaut selon le profil.
  activeTab.value = isValidTab(route.query.tab)
    ? route.query.tab
    : (isTeacher.value ? 'teacher' : 'student')
})
</script>
