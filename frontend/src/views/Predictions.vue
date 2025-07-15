<template>
  <Layout 
    :loading="store.loading" 
    :stats="{ total_predictions: store.predictionCount, total_alerts: store.alertCount, mongodb_connected: store.stats.mongodb_connected }" 
    :is-real-time-connected="store.realtimeConnected"
    @refresh="store.refreshCounts()"
  >
    <!-- Header Section -->
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">Predictions Analytics</h1>
          <p class="text-gray-600">
            Historical prediction data and machine learning insights
          </p>
        </div>
        <div class="flex items-center space-x-4">
          <button class="bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition duration-200 shadow-sm">
            <ArrowDownTrayIcon class="w-4 h-4 inline mr-2" />
            Export Data
          </button>
          <button 
            @click="store.loadPredictions()"
            :disabled="store.loading"
            class="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 text-sm font-medium transition duration-200 disabled:opacity-50 shadow-sm"
          >
            <ArrowPathIcon class="w-4 h-4 inline mr-2" :class="{ 'animate-spin': store.loading }" />
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="space-y-6">
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
                <ChartBarIcon class="w-6 h-6 text-blue-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Total Predictions</p>
                <p class="text-2xl font-bold text-gray-900">{{ store.predictionCount }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-red-100 rounded-lg">
                <ExclamationTriangleIcon class="w-6 h-6 text-red-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Maintenance Alerts</p>
                <p class="text-2xl font-bold text-gray-900">{{ maintenanceNeededCount }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
                <CheckCircleIcon class="w-6 h-6 text-green-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Normal Status</p>
                <p class="text-2xl font-bold text-gray-900">{{ normalStatusCount }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-purple-100 rounded-lg">
                <CpuChipIcon class="w-6 h-6 text-purple-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Avg Confidence</p>
                <p class="text-2xl font-bold text-gray-900">{{ averageConfidence }}%</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="store.loading" class="flex justify-center items-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>

        <!-- Enhanced Predictions Table -->
        <div v-else class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
          <div class="p-6 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-xl font-semibold text-gray-900">Prediction Records</h3>
              <div class="flex items-center space-x-4">
                <div class="relative">
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Search machine ID..."
                    class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                  <MagnifyingGlassIcon class="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
                </div>
                <select 
                  v-model="statusFilter"
                  class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Status</option>
                  <option value="1">Maintenance Needed</option>
                  <option value="0">Normal</option>
                </select>
              </div>
            </div>
          </div>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Machine ID
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Temperature (°C)
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Pressure (bar)
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr 
                  v-for="prediction in filteredPredictions" 
                  :key="prediction._id || prediction.timestamp"
                  class="hover:bg-gray-50 transition duration-200"
                >
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span 
                      class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                      :class="prediction.prediction === 1 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
                    >
                      <component
                        :is="prediction.prediction === 1 ? ExclamationTriangleIcon : CheckCircleIcon"
                        class="w-4 h-4 mr-1"
                      />
                      {{ prediction.prediction === 1 ? 'Maintenance' : 'Normal' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                        <span class="text-blue-600 text-sm font-medium">{{ prediction.machine_id }}</span>
                      </div>
                      <span class="text-sm font-medium text-gray-900">Machine {{ prediction.machine_id }}</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(prediction.timestamp) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="w-full bg-gray-200 rounded-full h-2 mr-3" style="width: 60px;">
                        <div 
                          class="h-2 rounded-full"
                          :class="prediction.probability > 0.7 ? 'bg-red-500' : prediction.probability > 0.4 ? 'bg-yellow-500' : 'bg-green-500'"
                          :style="{ width: (prediction.probability * 100) + '%' }"
                        ></div>
                      </div>
                      <span class="text-sm font-medium text-gray-900">{{ Math.round(prediction.probability * 100) }}%</span>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div class="space-y-1">
                      <div class="flex items-center">
                        <span class="text-blue-600 text-xs">Evap:</span>
                        <span class="ml-1 font-medium">{{ prediction.temp_evaporator }}°C</span>
                      </div>
                      <div class="flex items-center">
                        <span class="text-red-600 text-xs">Cond:</span>
                        <span class="ml-1 font-medium">{{ prediction.temp_condenser }}°C</span>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div class="space-y-1">
                      <div class="flex items-center">
                        <span class="text-green-600 text-xs">High:</span>
                        <span class="ml-1 font-medium">{{ prediction.pressure_high }} bar</span>
                      </div>
                      <div class="flex items-center">
                        <span class="text-yellow-600 text-xs">Low:</span>
                        <span class="ml-1 font-medium">{{ prediction.pressure_low }} bar</span>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button class="text-blue-600 hover:text-blue-900 font-medium">
                      View Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div v-if="filteredPredictions.length === 0" class="text-center py-12">
            <ChartBarIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500 font-medium">No prediction data available</p>
            <p class="text-gray-400 text-sm">Try adjusting your search filters</p>
          </div>
        </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRefrigerationStore } from '@/stores/refrigeration'
import Layout from '@/components/Layout.vue'
import { 
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  CpuChipIcon,
  ArrowDownTrayIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon
} from '@heroicons/vue/24/outline'
import moment from 'moment'

const store = useRefrigerationStore()
const searchQuery = ref('')
const statusFilter = ref('')

onMounted(() => {
  store.loadPredictions()
})

const maintenanceNeededCount = computed(() => {
  // Use database count if available, otherwise fallback to local filtering
  return store.maintenanceAlertCount || store.predictions.filter(p => p.prediction === 1).length
})

const normalStatusCount = computed(() => {
  // Use database count if available, otherwise fallback to local filtering
  return store.normalStatusCount || store.predictions.filter(p => p.prediction === 0).length
})

const averageConfidence = computed(() => {
  if (store.predictions.length === 0) return 0
  const total = store.predictions.reduce((sum, p) => sum + p.probability, 0)
  return Math.round((total / store.predictions.length) * 100)
})

const criticalCount = computed(() => {
  return store.predictions.filter(p => p.prediction === 1 && p.probability > 0.8).length
})

const filteredPredictions = computed(() => {
  let filtered = store.predictions

  if (searchQuery.value) {
    filtered = filtered.filter(p => 
      p.machine_id.toString().toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (statusFilter.value !== '') {
    filtered = filtered.filter(p => p.prediction.toString() === statusFilter.value)
  }

  return filtered
})

const formatDate = (timestamp) => {
  return moment(timestamp).format('MMM DD, YYYY HH:mm:ss')
}
</script>
