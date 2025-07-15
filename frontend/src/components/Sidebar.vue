<template>
  <!-- Modern SaaS Dashboard Sidebar -->
  <div class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl lg:translate-x-0 transition-all duration-300 ease-in-out border-r border-gray-100" 
       :class="{ '-translate-x-full': !sidebarOpen, 'translate-x-0': sidebarOpen }">
    
    <!-- Logo Section -->
    <div class="flex items-center h-16 px-6 border-b border-gray-100 bg-white">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 bg-gradient-to-tr from-blue-500 to-teal-400 rounded-lg flex items-center justify-center relative">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <!-- Refresh indicator -->
          <div v-if="isRefreshing" class="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-ping"></div>
        </div>
        <div class="flex-1">
          <h1 class="text-lg font-semibold text-gray-900">FroidPredict</h1>
          <p class="text-xs text-gray-500">Analytics Platform</p>
        </div>
        <!-- Manual refresh button -->
        <button @click="refreshData" 
                :disabled="isRefreshing"
                class="p-1.5 text-gray-400 hover:text-blue-500 rounded-lg hover:bg-blue-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                :class="{ 'animate-spin': isRefreshing }">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="mt-6 px-3">
      <div class="space-y-1">
        
        <!-- Dashboard -->
        <router-link to="/" 
                     class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
                     :class="$route.name === 'Dashboard' ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-500' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'">
          <svg class="mr-3 h-5 w-5 flex-shrink-0 transition-colors duration-200" 
               :class="$route.name === 'Dashboard' ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'" 
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6a2 2 0 01-2 2H10a2 2 0 01-2-2V5z" />
          </svg>
          Dashboard
        </router-link>

        <!-- Analytics (Diagrams) -->
        <router-link to="/diagrams" 
                     class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
                     :class="$route.name === 'Diagrams' ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-500' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'">
          <svg class="mr-3 h-5 w-5 flex-shrink-0 transition-colors duration-200" 
               :class="$route.name === 'Diagrams' ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'" 
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Analytics
        </router-link>

        <!-- Alerts -->
        <router-link to="/alerts" 
                     class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
                     :class="$route.name === 'Alerts' ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-500' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'">
          <svg class="mr-3 h-5 w-5 flex-shrink-0 transition-colors duration-200" 
               :class="$route.name === 'Alerts' ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'" 
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          Alerts
          <span v-if="alertCount > 0" 
                class="alert-badge ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 animate-pulse">
            {{ alertCount }}
          </span>
        </router-link>

        <!-- Reports (Test Dashboard) -->
        <router-link to="/test" 
                     class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
                     :class="$route.name === 'Test' ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-500' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'">
          <svg class="mr-3 h-5 w-5 flex-shrink-0 transition-colors duration-200" 
               :class="$route.name === 'Test' ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'" 
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Reports
        </router-link>

        <!-- Predictions -->
        <router-link to="/predictions" 
                     class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200"
                     :class="$route.name === 'Predictions' ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-500' : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'">
          <svg class="mr-3 h-5 w-5 flex-shrink-0 transition-colors duration-200" 
               :class="$route.name === 'Predictions' ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'" 
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          Predictions
          <span v-if="predictionCount > 0" 
                class="prediction-badge ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 transition-all duration-200">
            {{ predictionCount }}
          </span>
        </router-link>

        <!-- Guide -->
        <a href="#" 
           class="group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 text-gray-700 hover:bg-gray-50 hover:text-gray-900">
          <svg class="mr-3 h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-500 transition-colors duration-200" 
               fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          Guide
        </a>

      </div>

      <!-- Section Divider -->
      <div class="mt-8 pt-6 border-t border-gray-100">
        <div class="flex items-center justify-between px-3 mb-3">
          <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">
            System Status
          </h3>
          <div class="flex items-center space-x-1">
            <div class="w-1.5 h-1.5 rounded-full transition-all duration-200" 
                 :class="realtimeConnected ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'"></div>
            <span class="text-xs font-medium" 
                  :class="realtimeConnected ? 'text-green-600' : 'text-yellow-600'">
              {{ realtimeConnected ? 'Live' : 'Polling' }}
            </span>
          </div>
        </div>
        
        <!-- Quick Stats -->
        <div class="space-y-3">
          <!-- System Health -->
          <div class="px-3 py-2 bg-gray-50 rounded-lg transition-all duration-200 hover:bg-gray-100">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 rounded-full transition-all duration-200" 
                     :class="systemStatus === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'"></div>
                <span class="text-sm text-gray-700">System Online</span>
              </div>
              <span class="text-xs font-medium" 
                    :class="systemStatus === 'online' ? 'text-green-600' : 'text-red-600'">
                {{ systemUptime }}%
              </span>
            </div>
          </div>
          
          <!-- Database Status -->
          <div class="px-3 py-2 bg-gray-50 rounded-lg transition-all duration-200 hover:bg-gray-100">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 rounded-full transition-all duration-200" 
                     :class="dbStatus === 'connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'"></div>
                <span class="text-sm text-gray-700">Database</span>
              </div>
              <span class="text-xs font-medium" 
                    :class="dbStatus === 'connected' ? 'text-green-600' : 'text-red-600'">
                {{ dbStatus === 'connected' ? 'Connected' : 'Offline' }}
              </span>
            </div>
          </div>

          <!-- Last Update Info -->
          <div class="px-3 py-2 bg-blue-50 rounded-lg">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <svg class="w-3 h-3 text-blue-500" 
                     :class="{ 'animate-spin': isRefreshing }" 
                     fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span class="text-xs text-blue-700">Last Update</span>
              </div>
              <span class="text-xs font-medium text-blue-600">
                {{ formattedLastUpdate }}
              </span>
            </div>
          </div>

          <!-- Auto Generation Status -->
          <div class="px-3 py-2 bg-green-50 rounded-lg">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-green-500 rounded-full" 
                     :class="{ 'animate-pulse': realtimeConnected }"></div>
                <span class="text-xs text-green-700">Auto Updates</span>
              </div>
              <div class="flex items-center space-x-1">
                <span class="text-xs font-medium text-green-600">
                  {{ realtimeConnected ? 'Live' : 'Polling' }}
                </span>
                <svg v-if="realtimeConnected" class="w-3 h-3 text-green-500 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- User Profile Section -->
    <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-100 bg-white">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-gradient-to-tr from-blue-500 to-teal-400 rounded-full flex items-center justify-center">
            <span class="text-white text-sm font-medium">SE</span>
          </div>
        </div>
        <div class="ml-3 flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">
            System Engineer
          </p>
          <p class="text-xs text-gray-500 truncate">
            engineer@froidpredict.com
          </p>
        </div>
        <div class="ml-2">
          <button class="p-1.5 text-gray-400 hover:text-gray-500 rounded-lg hover:bg-gray-100 transition-colors duration-200">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Mobile menu button -->
  <div class="lg:hidden fixed top-4 left-4 z-50">
    <button @click="sidebarOpen = !sidebarOpen" 
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-600 bg-white hover:bg-gray-50 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 shadow-md border border-gray-200">
      <svg class="h-6 w-6" 
           :class="{ 'hidden': sidebarOpen, 'block': !sidebarOpen }" 
           fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
      <svg class="h-6 w-6" 
           :class="{ 'block': sidebarOpen, 'hidden': !sidebarOpen }" 
           fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>

  <!-- Mobile sidebar overlay -->
  <div v-if="sidebarOpen" 
       @click="sidebarOpen = false" 
       class="lg:hidden fixed inset-0 z-40 bg-gray-600 bg-opacity-75 transition-opacity duration-300">
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRefrigerationStore } from '../stores/refrigeration'

const route = useRoute()
const sidebarOpen = ref(false)
const store = useRefrigerationStore()

// Use store's centralized count state for consistent real-time updates
const predictionCount = computed(() => store.predictionCount)
const alertCount = computed(() => store.alertCount)
const systemStatus = ref('online')
const dbStatus = ref('connected')
const systemUptime = ref(98.5)
const isRefreshing = ref(false)
const realtimeConnected = computed(() => store.realtimeConnected)
const formattedLastUpdate = computed(() => {
  return store.lastUpdated.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
})

// Refresh intervals
let statusRefreshInterval = null

// Props for initial data (optional override)
const props = defineProps({
  initialPredictionCount: {
    type: Number,
    default: 0
  },
  initialAlertCount: {
    type: Number,
    default: 0
  },
  refreshInterval: {
    type: Number,
    default: 10000 // 10 seconds (faster refresh)
  },
  statusInterval: {
    type: Number,
    default: 5000 // 5 seconds (faster status updates)
  }
})

// API endpoints for data fetching
const API_BASE = '/api'

// Fetch system status
const fetchSystemStatus = async () => {
  try {
    const response = await fetch(`${API_BASE}/system/status`)
    if (response.ok) {
      const data = await response.json()
      systemStatus.value = data.system_status || 'online'
      dbStatus.value = data.db_status || 'connected'
      systemUptime.value = data.uptime || 98.5
    }
  } catch (error) {
    console.warn('Failed to fetch system status:', error)
    // Keep current values on error
  }
}

// Manual refresh function - force refresh when user clicks
const refreshData = async () => {
  isRefreshing.value = true
  try {
    // Force refresh counts from API and system status
    await Promise.all([
      store.refreshCounts(),
      fetchSystemStatus()
    ])
  } finally {
    isRefreshing.value = false
  }
}

// Close sidebar when route changes (mobile)
const closeOnRouteChange = () => {
  if (window.innerWidth < 1024) {
    sidebarOpen.value = false
  }
}

// Handle escape key
const handleEscape = (e) => {
  if (e.key === 'Escape' && sidebarOpen.value) {
    sidebarOpen.value = false
  }
}

// Initialize data and intervals
onMounted(async () => {
  document.addEventListener('keydown', handleEscape)
  
  // Initialize the store's WebSocket connection for real-time updates
  store.initializeSocket()
  
  // Load initial data once
  await store.loadDashboardData()
  await fetchSystemStatus()
  
  // Only setup status refresh interval - counts are handled by WebSocket events
  statusRefreshInterval = setInterval(fetchSystemStatus, props.statusInterval)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  
  // Clear status refresh interval
  if (statusRefreshInterval) {
    clearInterval(statusRefreshInterval)
  }
})
</script>
