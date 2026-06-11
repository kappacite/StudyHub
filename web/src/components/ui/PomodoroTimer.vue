<template>
  <div class="fixed bottom-6 right-6 z-[90] no-print">
    <!-- Minimized FAB -->
    <button 
      v-if="!isExpanded"
      @click="isExpanded = true"
      class="group relative flex items-center justify-center w-16 h-16 rounded-full bg-white dark:bg-[#1E293B] shadow-2xl border border-slate-200 dark:border-slate-800 hover:scale-105 active:scale-95 transition-all duration-200 cursor-pointer"
      :title="`Pomodoro (${phase}): ${formattedTime}`"
    >
      <!-- Circular Progress Ring (Around FAB) -->
      <svg class="absolute inset-0 w-16 h-16 transform -rotate-90">
        <circle
          class="text-slate-100 dark:text-slate-800"
          stroke-width="3"
          stroke="currentColor"
          fill="transparent"
          r="28"
          cx="32"
          cy="32"
        />
        <circle
          :class="[
            'transition-all duration-300 ease-out',
            phase === 'work' ? 'text-indigo-600' : 'text-emerald-500'
          ]"
          stroke-width="3"
          :stroke-dasharray="2 * Math.PI * 28"
          :stroke-dashoffset="2 * Math.PI * 28 * (1 - progress / 100)"
          stroke-linecap="round"
          stroke="currentColor"
          fill="transparent"
          r="28"
          cx="32"
          cy="32"
        />
      </svg>

      <!-- FAB Content -->
      <div class="flex flex-col items-center justify-center z-10">
        <Clock v-if="phase === 'idle'" class="w-6 h-6 text-slate-400 dark:text-slate-500 group-hover:text-indigo-500 transition-colors" />
        <template v-else>
          <span class="text-[11px] font-bold tracking-tight text-slate-700 dark:text-slate-300">{{ formattedTime }}</span>
          <span class="text-[8px] font-bold uppercase" :class="phase === 'work' ? 'text-indigo-500' : 'text-emerald-500'">
            {{ phase === 'work' ? 'Work' : 'Break' }}
          </span>
        </template>
      </div>

      <!-- Pulse Dot if running -->
      <span v-if="isRunning" class="absolute top-1 right-1 flex h-3 w-3">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="phase === 'work' ? 'bg-indigo-400' : 'bg-emerald-400'"></span>
        <span class="relative inline-flex rounded-full h-3 w-3" :class="phase === 'work' ? 'bg-indigo-500' : 'bg-emerald-500'"></span>
      </span>
    </button>

    <!-- Expanded Dashboard Card -->
    <Transition name="slide-fade">
      <div 
        v-if="isExpanded"
        class="w-80 bg-white/95 dark:bg-[#111827]/95 backdrop-blur-md rounded-2xl shadow-2xl border border-slate-200/80 dark:border-slate-800/80 p-5 flex flex-col space-y-4"
      >
        <!-- Card Header -->
        <div class="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
          <div class="flex items-center gap-2">
            <Clock class="w-4 h-4 text-indigo-500" />
            <span class="font-bold text-sm text-slate-800 dark:text-slate-200">Minuteur Pomodoro</span>
          </div>
          <div class="flex items-center gap-1.5">
            <button 
              @click="showSettings = !showSettings"
              class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title="Paramètres"
            >
              <Settings class="w-4.5 h-4.5" />
            </button>
            <button 
              @click="isExpanded = false"
              class="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <X class="w-4.5 h-4.5" />
            </button>
          </div>
        </div>

        <!-- Normal State Display -->
        <div v-if="!showSettings" class="flex flex-col items-center py-2 space-y-4">
          <!-- Countdown Timer Radial Graphic -->
          <div class="relative w-36 h-36 flex items-center justify-center">
            <svg class="absolute inset-0 w-36 h-36 transform -rotate-90">
              <circle
                class="text-slate-100 dark:text-slate-800"
                stroke-width="5"
                stroke="currentColor"
                fill="transparent"
                r="64"
                cx="72"
                cy="72"
              />
              <circle
                :class="[
                  'transition-all duration-300 ease-out',
                  phase === 'work' ? 'text-indigo-600' : 'text-emerald-500'
                ]"
                stroke-width="5"
                :stroke-dasharray="2 * Math.PI * 64"
                :stroke-dashoffset="2 * Math.PI * 64 * (1 - progress / 100)"
                stroke-linecap="round"
                stroke="currentColor"
                fill="transparent"
                r="64"
                cx="72"
                cy="72"
              />
            </svg>

            <!-- Center Countdown Details -->
            <div class="flex flex-col items-center justify-center z-10">
              <span class="text-3xl font-extrabold text-slate-800 dark:text-slate-100 tracking-tight select-none">
                {{ formattedTime }}
              </span>
              <span class="text-[10px] font-bold uppercase tracking-wider mt-1 px-2.5 py-0.5 rounded-full bg-slate-50 dark:bg-slate-800/80"
                    :class="phase === 'work' ? 'text-indigo-600' : phase === 'break' ? 'text-emerald-500' : 'text-slate-400'">
                {{ phase === 'work' ? 'Focus Work' : phase === 'break' ? 'Break' : 'Prêt' }}
              </span>
            </div>
          </div>

          <!-- Session Indicator Badge -->
          <div class="flex items-center gap-1 text-xs font-semibold text-slate-500 dark:text-slate-400">
            <span>Sessions complétées :</span>
            <span class="flex items-center justify-center w-5 h-5 rounded-full bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 font-bold text-[10px]">
              {{ sessionCount }}
            </span>
          </div>

          <!-- Control Buttons -->
          <div class="flex items-center justify-center gap-3 w-full pt-2">
            <!-- Reset Button -->
            <button 
              @click="reset" 
              class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors text-slate-500 dark:text-slate-400 active:scale-95"
              title="Réinitialiser"
            >
              <RotateCcw class="w-4 h-4" />
            </button>

            <!-- Play / Pause Button -->
            <button 
              @click="isRunning ? pause() : start()"
              class="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-white font-bold text-sm shadow-lg shadow-indigo-500/20 active:scale-98 transition-all duration-200"
              :class="isRunning ? 'bg-slate-700 hover:bg-slate-800' : 'bg-indigo-600 hover:bg-indigo-700'"
            >
              <component :is="isRunning ? Pause : Play" class="w-4 h-4 fill-current" />
              <span>{{ isRunning ? 'Pause' : 'Démarrer' }}</span>
            </button>

            <!-- Skip Button -->
            <button 
              @click="skip" 
              class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/60 transition-colors text-slate-500 dark:text-slate-400 active:scale-95"
              title="Passer"
            >
              <SkipForward class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Settings State Display -->
        <div v-else class="flex flex-col space-y-3 py-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Configuration</span>
            <button 
              @click="showSettings = false"
              class="text-xs font-semibold text-indigo-500 hover:text-indigo-600"
            >
              Retour
            </button>
          </div>

          <!-- Durations settings -->
          <div class="space-y-2 text-xs">
            <!-- Work minutes input -->
            <div class="flex items-center justify-between">
              <span class="text-slate-600 dark:text-slate-400">Travail (min)</span>
              <input 
                v-model.number="localWorkMins" 
                type="number" 
                min="1" 
                max="120"
                class="w-16 px-2 py-1 border border-slate-200 dark:border-slate-800 rounded bg-transparent text-center font-bold"
              />
            </div>
            <!-- Break minutes input -->
            <div class="flex items-center justify-between">
              <span class="text-slate-600 dark:text-slate-400">Pause (min)</span>
              <input 
                v-model.number="localBreakMins" 
                type="number" 
                min="1" 
                max="60"
                class="w-16 px-2 py-1 border border-slate-200 dark:border-slate-800 rounded bg-transparent text-center font-bold"
              />
            </div>
            <!-- Long Break minutes input -->
            <div class="flex items-center justify-between">
              <span class="text-slate-600 dark:text-slate-400">Longue Pause (min)</span>
              <input 
                v-model.number="localLongBreakMins" 
                type="number" 
                min="1" 
                max="60"
                class="w-16 px-2 py-1 border border-slate-200 dark:border-slate-800 rounded bg-transparent text-center font-bold"
              />
            </div>
          </div>

          <!-- Alert settings -->
          <div class="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
            <!-- Sound toggle -->
            <label class="flex items-center justify-between cursor-pointer text-xs">
              <span class="text-slate-600 dark:text-slate-400">Effets sonores</span>
              <div class="relative inline-flex items-center">
                <input 
                  type="checkbox" 
                  v-model="localSound" 
                  class="sr-only peer"
                />
                <div class="w-9 h-5 bg-slate-200 dark:bg-slate-800 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600"></div>
              </div>
            </label>

            <!-- Notifications toggle -->
            <label class="flex items-center justify-between cursor-pointer text-xs">
              <span class="text-slate-600 dark:text-slate-400">Notifications</span>
              <div class="relative inline-flex items-center">
                <input 
                  type="checkbox" 
                  v-model="localNotifs" 
                  class="sr-only peer"
                />
                <div class="w-9 h-5 bg-slate-200 dark:bg-slate-800 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600"></div>
              </div>
            </label>
          </div>

          <!-- Save Button -->
          <button 
            @click="applySettings"
            class="w-full mt-2 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs"
          >
            Enregistrer les modifications
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { 
  Clock, 
  X, 
  Play, 
  Pause, 
  RotateCcw, 
  SkipForward, 
  Settings 
} from '@lucide/vue'
import { usePomodoro } from '../../composables/usePomodoro'

const isExpanded = ref(false)
const showSettings = ref(false)

const {
  phase,
  sessionCount,
  isRunning,
  workMinutes,
  breakMinutes,
  longBreakMinutes,
  enableSound,
  enableNotifications,
  formattedTime,
  progress,
  start,
  pause,
  reset,
  skip,
  saveSettings
} = usePomodoro()

// Local configurations bound to form
const localWorkMins = ref(workMinutes.value)
const localBreakMins = ref(breakMinutes.value)
const localLongBreakMins = ref(longBreakMinutes.value)
const localSound = ref(enableSound.value)
const localNotifs = ref(enableNotifications.value)

// Update local state when setting values in store change
watch([workMinutes, breakMinutes, longBreakMinutes, enableSound, enableNotifications], () => {
  localWorkMins.value = workMinutes.value
  localBreakMins.value = breakMinutes.value
  localLongBreakMins.value = longBreakMinutes.value
  localSound.value = enableSound.value
  localNotifs.value = enableNotifications.value
})

function applySettings() {
  saveSettings(
    localWorkMins.value,
    localBreakMins.value,
    localLongBreakMins.value,
    localSound.value,
    localNotifs.value
  )
  showSettings.value = false
}
</script>

<style scoped>
/* Slide-fade animation for expanded panel */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(12px) scale(0.95);
  opacity: 0;
}
</style>
