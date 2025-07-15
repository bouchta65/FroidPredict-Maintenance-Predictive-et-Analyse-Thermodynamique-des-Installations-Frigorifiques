<template>
  <Layout 
    :loading="store.loading" 
    :stats="{ total_predictions: store.predictionCount, total_alerts: store.alertCount, total_analytics: store.analyticsCount, mongodb_connected: store.stats.mongodb_connected }" 
    :is-real-time-connected="store.realtimeConnected"
    @refresh="refreshAnalytics"
  >
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Enthalpy Diagrams</h1>
          <p class="mt-2 text-gray-600">
            Thermodynamic analysis and refrigeration cycle visualization
          </p>
        </div>
        <div class="flex items-center space-x-3">
          <!-- Real-time indicator -->
          <div class="flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm border"
               :class="store.realtimeConnected 
                 ? 'bg-green-50 text-green-700 border-green-200' 
                 : 'bg-red-50 text-red-700 border-red-200'">
            <div class="w-2 h-2 rounded-full"
                 :class="store.realtimeConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'"></div>
            <span class="font-medium">{{ store.realtimeConnected ? 'Live Analytics' : 'Offline' }}</span>
          </div>
          <div class="text-sm text-gray-500">
            {{ store.analyticsCount }} total records
          </div>
        </div>
      </div>
    </div>

    <!-- Controls -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <button
          @click="refreshAnalytics"
          :disabled="store.loading"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition duration-200 disabled:opacity-50 shadow-sm"
        >
          <span v-if="store.loading">Loading...</span>
          <span v-else>Refresh Data</span>
        </button>
        <select 
          v-model="selectedMachine"
          class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
        >
          <option value="">All Machines</option>
          <option v-for="machine in store.uniqueMachines" :key="machine" :value="machine">
            Machine {{ machine }}
          </option>
        </select>
        <div class="flex items-center space-x-4 ml-auto">
          <div class="text-sm text-gray-600">
            Showing {{ filteredDiagramData.length }} of {{ store.analytics.length }} records
          </div>
          <div class="text-sm text-gray-600">
            Avg COP: <span class="font-semibold text-blue-600">{{ store.averageCOP }}</span>
          </div>
          <div class="text-sm text-gray-500">
            Last updated: {{ formatLastUpdate }}
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="space-y-6">
        <!-- Loading State -->
        <div v-if="store.loading" class="flex justify-center items-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>

        <!-- Diagram Data -->
        <div v-else-if="store.analytics.length > 0" class="space-y-6">
          <div 
            v-for="data in filteredDiagramData" 
            :key="data._id || (data.machine_id + data.timestamp)"
            class="card relative"
          >
            <!-- Real-time indicator for new data -->
            <div v-if="isRecentData(data)" 
                 class="absolute top-4 right-4 px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full flex items-center">
              <div class="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
              New
            </div>
            
            <div class="mb-4">
              <h3 class="text-lg font-medium text-gray-900">
                Machine {{ data.machine_id }} - {{ formatDate(data.timestamp) }}
              </h3>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Cycle Points -->
              <div>
                <h4 class="text-md font-medium text-gray-700 mb-3">Refrigeration Cycle Points</h4>
                <div class="space-y-3">
                  <div 
                    v-for="(point, key) in data.cycle_points" 
                    :key="key"
                    class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ point.description }}</p>
                      <p class="text-xs text-gray-500">{{ key }}</p>
                    </div>
                    <div class="text-right space-y-1">
                      <div class="text-sm">
                        <span class="text-gray-500">T:</span>
                        <span class="font-medium ml-1">{{ point.T.toFixed(1) }}°C</span>
                      </div>
                      <div class="text-sm">
                        <span class="text-gray-500">P:</span>
                        <span class="font-medium ml-1">{{ point.P.toFixed(1) }} bar</span>
                      </div>
                      <div class="text-sm">
                        <span class="text-gray-500">h:</span>
                        <span class="font-medium ml-1">{{ point.h.toFixed(1) }} kJ/kg</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Performance Metrics -->
              <div>
                <h4 class="text-md font-medium text-gray-700 mb-3">Performance Metrics</h4>
                <div class="space-y-3">
                  <div class="p-3 bg-blue-50 rounded-lg">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-blue-900">COP (Coefficient of Performance)</span>
                      <span class="text-lg font-bold text-blue-900">
                        {{ data.performance.cop.toFixed(2) }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="p-3 bg-green-50 rounded-lg">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-green-900">Cooling Capacity</span>
                      <span class="text-lg font-bold text-green-900">
                        {{ data.performance.cooling_capacity.toFixed(1) }} kJ/kg
                      </span>
                    </div>
                  </div>
                  
                  <div class="p-3 bg-orange-50 rounded-lg">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-orange-900">Compression Work</span>
                      <span class="text-lg font-bold text-orange-900">
                        {{ data.performance.compression_work.toFixed(1) }} kJ/kg
                      </span>
                    </div>
                  </div>
                  
                  <div class="p-3 bg-red-50 rounded-lg">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium text-red-900">Condensation Heat</span>
                      <span class="text-lg font-bold text-red-900">
                        {{ data.performance.condensation_heat.toFixed(1) }} kJ/kg
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Cycle Diagram Placeholder -->
            <div class="mt-6">
              <h4 class="text-md font-medium text-gray-700 mb-3">P-h Diagram</h4>
              <div class="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                <div class="text-center">
                  <ChartPieIcon class="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p class="text-gray-500">Interactive P-h diagram will be implemented here</p>
                  <p class="text-xs text-gray-400 mt-1">Showing cycle points and refrigerant properties</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No Data State -->
        <div v-else class="card">
          <div class="text-center py-8">
            <ChartPieIcon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-500">No analytics data available</p>
            <div class="mt-4 space-x-2">
              <button @click="refreshAnalytics" 
                      class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition duration-200 shadow-sm">
                Load Analytics Data
              </button>
              <div class="text-sm text-gray-400 mt-2">
                Real-time updates: {{ store.realtimeConnected ? 'Active' : 'Disconnected' }}
              </div>
            </div>
          </div>
        </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRefrigerationStore } from '@/stores/refrigeration'
import Layout from '@/components/Layout.vue'
import { ChartPieIcon } from '@heroicons/vue/24/outline'
import moment from 'moment'

const store = useRefrigerationStore()
const selectedMachine = ref('')

onMounted(async () => {
  // Initialize store if not already connected
  if (!store.realtimeConnected) {
    await store.initializeStore()
  } else {
    // Just load analytics if already connected
    await store.loadAnalytics()
  }
})

const refreshAnalytics = async () => {
  await store.loadAnalytics()
  await store.refreshCounts()
}

const filteredDiagramData = computed(() => {
  if (!selectedMachine.value) {
    return store.analytics
  }
  return store.analytics.filter(data => data.machine_id === selectedMachine.value)
})

const formatDate = (timestamp) => {
  return moment(timestamp).format('MMM DD, YYYY HH:mm:ss')
}

const formatLastUpdate = computed(() => {
  return moment(store.lastUpdated).format('HH:mm:ss')
})

// Check if data is recent (within last 5 minutes)
const isRecentData = (data) => {
  const dataTime = moment(data.timestamp)
  const fiveMinutesAgo = moment().subtract(5, 'minutes')
  return dataTime.isAfter(fiveMinutesAgo)
}
</script>
