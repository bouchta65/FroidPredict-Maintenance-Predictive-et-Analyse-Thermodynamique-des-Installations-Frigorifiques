<template>
  <nav class="bg-white shadow-lg border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex">
          <!-- Logo and Brand -->
          <div class="flex-shrink-0 flex items-center">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg">🧊</span>
              </div>
              <div>
                <h1 class="text-xl font-bold text-gray-900">FroidPredict</h1>
                <p class="text-xs text-gray-500">Predictive Maintenance</p>
              </div>
            </div>
          </div>
          
          <!-- Navigation Links -->
          <div class="hidden sm:ml-8 sm:flex sm:space-x-1">
            <router-link
              v-for="item in navigation"
              :key="item.name"
              :to="item.to"
              class="group px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
              :class="$route.name === item.name 
                ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
            >
              <component 
                :is="item.icon" 
                class="w-4 h-4" 
                :class="$route.name === item.name ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-600'"
              />
              <span>{{ item.label }}</span>
            </router-link>
          </div>
        </div>

        <!-- Right side -->
        <div class="flex items-center space-x-4">
          <!-- Notifications -->
          <div class="relative">
            <button class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition duration-200">
              <BellIcon class="w-5 h-5" />
              <span v-if="unreadAlertsCount > 0" 
                    class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {{ unreadAlertsCount > 9 ? '9+' : unreadAlertsCount }}
              </span>
            </button>
          </div>

          <!-- Connection Status -->
          <div class="flex items-center space-x-3">
            <div 
              class="flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm border"
              :class="isConnected 
                ? 'bg-green-50 text-green-700 border-green-200' 
                : 'bg-red-50 text-red-700 border-red-200'"
            >
              <div 
                class="w-2 h-2 rounded-full"
                :class="isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'"
              ></div>
              <span class="font-medium">{{ isConnected ? 'Live' : 'Offline' }}</span>
            </div>
          </div>

          <!-- Settings -->
          <button class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition duration-200">
            <CogIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div class="sm:hidden border-t border-gray-200">
      <div class="px-2 pt-2 pb-3 space-y-1">
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.to"
          class="block px-3 py-2 rounded-md text-base font-medium transition duration-200"
          :class="$route.name === item.name 
            ? 'bg-blue-50 text-blue-700' 
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'"
        >
          <div class="flex items-center space-x-3">
            <component :is="item.icon" class="w-5 h-5" />
            <span>{{ item.label }}</span>
          </div>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useRefrigerationStore } from '@/stores/refrigeration'
import { 
  HomeIcon, 
  ChartBarIcon, 
  ExclamationTriangleIcon, 
  ChartPieIcon,
  BellIcon,
  CogIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const store = useRefrigerationStore()

const navigation = [
  { name: 'Dashboard', label: 'Dashboard', to: '/', icon: HomeIcon },
  { name: 'Predictions', label: 'Predictions', to: '/predictions', icon: ChartBarIcon },
  { name: 'Alerts', label: 'Alerts', to: '/alerts', icon: ExclamationTriangleIcon },
  { name: 'Diagrams', label: 'Diagrams', to: '/diagrams', icon: ChartPieIcon },
]

const isConnected = computed(() => {
  return store.socket && store.socket.connected
})

const unreadAlertsCount = computed(() => {
  return store.highSeverityAlerts.length
})
</script>
