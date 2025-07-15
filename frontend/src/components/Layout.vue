<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar with centralized store data -->
    <Sidebar />

    <!-- Main Content Area -->
    <div class="lg:pl-64">
      <!-- Top Header Bar -->
      <div class="sticky top-0 z-40 bg-white shadow-sm border-b border-gray-200">
        <div class="px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between items-center h-16">
            <!-- Page Title -->
            <div class="flex items-center space-x-4">
              <h1 class="text-xl font-semibold text-gray-900">{{ pageTitle }}</h1>
              <div v-if="loading" class="flex items-center space-x-2">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span class="text-sm text-gray-500">Loading...</span>
              </div>
            </div>

            <!-- Header Actions -->
            <div class="flex items-center space-x-4">
              <!-- Notifications -->
              <button class="relative p-2 text-gray-400 hover:text-gray-500 rounded-full hover:bg-gray-100">
                <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-3.5-3.5a1.414 1.414 0 010-2L21 7h-5M9 7H4l3.5 3.5a1.414 1.414 0 010 2L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span v-if="stats.total_alerts > 0" class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
              </button>

              <!-- Real-time Status -->
              <div class="flex items-center space-x-2 px-3 py-1 rounded-full text-sm" 
                   :class="isRealTimeConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                <div class="w-2 h-2 rounded-full" 
                     :class="isRealTimeConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'"></div>
                <span>{{ isRealTimeConnected ? 'Live' : 'Offline' }}</span>
              </div>

              <!-- Refresh Button -->
              <button @click="$emit('refresh')" 
                      class="p-2 text-gray-400 hover:text-gray-500 rounded-full hover:bg-gray-100">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Page Content -->
      <main class="py-6">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useRefrigerationStore } from '../stores/refrigeration'
import Sidebar from './Sidebar.vue'

const route = useRoute()
const store = useRefrigerationStore()

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['refresh'])

// Use store data instead of props
const stats = computed(() => store.stats)
const isRealTimeConnected = computed(() => store.realtimeConnected)

const pageTitle = computed(() => {
  const titles = {
    'Dashboard': 'Dashboard Overview',
    'Test': 'System Test Center',
    'Predictions': 'Prediction Analytics',
    'Alerts': 'System Alerts',
    'Diagrams': 'Enthalpy Diagrams'
  }
  return titles[route.name] || 'Dashboard'
})

const systemStatus = computed(() => {
  return isRealTimeConnected.value ? 'online' : 'offline'
})
</script>
