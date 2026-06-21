<template>
  <div class="fixed bottom-6 right-6 z-[90] no-print">
    <!-- Minimized FAB -->
    <button 
      v-if="!isExpanded"
      @click="isExpanded = true"
      class="group relative flex items-center justify-center w-16 h-16 rounded-full bg-surface shadow-elev-3 border border-line hover:scale-105 active:scale-95 transition-all duration-200 cursor-pointer"
      :title="`Pomodoro (${phase}): ${formattedTime}`"
    >
      <!-- Circular Progress Ring (Around FAB) -->
      <svg class="absolute inset-0 w-16 h-16 transform -rotate-90">
        <circle
          class="text-line"
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
            phase === 'work' ? 'text-primary' : 'text-success'
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
        <Clock v-if="phase === 'idle'" class="w-6 h-6 text-ink-subtle group-hover:text-primary transition-colors" />
        <template v-else>
          <span class="text-[11px] font-bold tracking-tight text-ink">{{ formattedTime }}</span>
          <span class="text-[8px] font-bold uppercase" :class="phase === 'work' ? 'text-primary' : 'text-success'">
            {{ phase === 'work' ? 'Work' : 'Break' }}
          </span>
        </template>
      </div>

      <!-- Pulse Dot if running -->
      <span v-if="isRunning" class="absolute top-1 right-1 flex h-3 w-3">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" :class="phase === 'work' ? 'bg-primary/70' : 'bg-success/70'"></span>
        <span class="relative inline-flex rounded-full h-3 w-3" :class="phase === 'work' ? 'bg-primary' : 'bg-success'"></span>
      </span>
    </button>

    <!-- Expanded Dashboard Card -->
    <Transition name="slide-fade">
      <div 
        v-if="isExpanded"
        class="w-80 bg-surface/95 backdrop-blur-md rounded-2xl shadow-elev-3 border border-line p-5 flex flex-col space-y-4"
      >
        <!-- Card Header -->
        <div class="flex items-center justify-between pb-2 border-b border-line">
          <div class="flex items-center gap-2">
            <Clock class="w-4 h-4 text-primary" />
            <span class="font-bold text-sm text-ink">Minuteur Pomodoro</span>
          </div>
          <div class="flex items-center gap-1.5">
            <button 
              @click="showSettings = !showSettings"
              class="p-1 rounded-lg text-ink-subtle hover:text-ink hover:bg-surface-soft transition-colors"
              title="Paramètres"
            >
              <Settings class="w-4.5 h-4.5" />
            </button>
            <button 
              @click="isExpanded = false"
              class="p-1 rounded-lg text-ink-subtle hover:text-ink hover:bg-surface-soft transition-colors"
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
                class="text-line"
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
                  phase === 'work' ? 'text-primary' : 'text-success'
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
              <span class="text-3xl font-extrabold text-ink tracking-tight select-none">
                {{ formattedTime }}
              </span>
              <span class="text-[10px] font-bold uppercase tracking-wider mt-1 px-2.5 py-0.5 rounded-full bg-surface-soft"
                    :class="phase === 'work' ? 'text-primary' : phase === 'break' ? 'text-success' : 'text-ink-subtle'">
                {{ phase === 'work' ? 'Focus Work' : phase === 'break' ? 'Break' : 'Prêt' }}
              </span>
            </div>
          </div>

          <!-- Session Indicator Badge -->
          <div class="flex items-center gap-1 text-xs font-semibold text-ink-muted">
            <span>Sessions complétées :</span>
            <span class="flex items-center justify-center w-5 h-5 rounded-full bg-primary-soft text-primary font-bold text-[10px]">
              {{ sessionCount }}
            </span>
          </div>

          <!-- Control Buttons -->
          <div class="flex items-center justify-center gap-3 w-full pt-2">
            <!-- Reset Button -->
            <button 
              @click="reset" 
              class="p-2.5 rounded-xl border border-line hover:bg-surface-soft transition-colors text-ink-muted active:scale-95"
              title="Réinitialiser"
            >
              <RotateCcw class="w-4 h-4" />
            </button>

            <!-- Play / Pause Button -->
            <button 
              @click="isRunning ? pause() : start()"
              class="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-full text-white font-bold text-sm shadow-elev-primary active:scale-98 transition-all duration-200"
              :class="isRunning ? 'bg-ink hover:opacity-90' : 'bg-primary hover:bg-primary-strong'"
            >
              <component :is="isRunning ? Pause : Play" class="w-4 h-4 fill-current" />
              <span>{{ isRunning ? 'Pause' : 'Démarrer' }}</span>
            </button>

            <!-- Skip Button -->
            <button 
              @click="skip" 
              class="p-2.5 rounded-xl border border-line hover:bg-surface-soft transition-colors text-ink-muted active:scale-95"
              title="Passer"
            >
              <SkipForward class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Settings State Display -->
        <div v-else class="flex flex-col space-y-3 py-1">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-ink-muted uppercase tracking-wider">Configuration</span>
            <button
              @click="showSettings = false"
              class="text-xs font-semibold text-primary hover:text-primary-strong"
            >
              Retour
            </button>
          </div>

          <!-- Durations settings -->
          <div class="space-y-2 text-xs">
            <!-- Work minutes input -->
            <div class="flex items-center justify-between">
              <span class="text-ink-muted">Travail (min)</span>
              <input 
                v-model.number="localWorkMins" 
                type="number" 
                min="1" 
                max="120"
                class="w-16 px-2 py-1 border border-line rounded bg-transparent text-ink text-center font-bold"
              />
            </div>
            <!-- Break minutes input -->
            <div class="flex items-center justify-between">
              <span class="text-ink-muted">Pause (min)</span>
              <input 
                v-model.number="localBreakMins" 
                type="number" 
                min="1" 
                max="60"
                class="w-16 px-2 py-1 border border-line rounded bg-transparent text-ink text-center font-bold"
              />
            </div>
            <!-- Long Break minutes input -->
            <div class="flex items-center justify-between">
              <span class="text-ink-muted">Longue Pause (min)</span>
              <input 
                v-model.number="localLongBreakMins" 
                type="number" 
                min="1" 
                max="60"
                class="w-16 px-2 py-1 border border-line rounded bg-transparent text-ink text-center font-bold"
              />
            </div>
          </div>

          <!-- Alert settings -->
          <div class="space-y-2 pt-2 border-t border-line">
            <!-- Sound toggle -->
            <label class="flex items-center justify-between cursor-pointer text-xs">
              <span class="text-ink-muted">Effets sonores</span>
              <div class="relative inline-flex items-center">
                <input 
                  type="checkbox" 
                  v-model="localSound" 
                  class="sr-only peer"
                />
                <div class="w-9 h-5 bg-line rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-line after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
              </div>
            </label>

            <!-- Notifications toggle -->
            <label class="flex items-center justify-between cursor-pointer text-xs">
              <span class="text-ink-muted">Notifications</span>
              <div class="relative inline-flex items-center">
                <input 
                  type="checkbox" 
                  v-model="localNotifs" 
                  class="sr-only peer"
                />
                <div class="w-9 h-5 bg-line rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-line after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary"></div>
              </div>
            </label>
          </div>

          <!-- Save Button -->
          <button 
            @click="applySettings"
            class="w-full mt-2 py-2 bg-primary hover:bg-primary-strong text-white font-bold rounded-full text-xs"
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
