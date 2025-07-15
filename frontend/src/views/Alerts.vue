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
          <h1 class="text-2xl font-bold text-gray-900 mb-2">System Alerts</h1>
          <p class="text-gray-600">
            Monitor critical system alerts and notifications
          </p>
        </div>
        <div class="flex items-center space-x-4">
          <button class="bg-white border border-gray-300 rounded-lg px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition duration-200 shadow-sm">
            <FunnelIcon class="w-4 h-4 inline mr-2" />
            Filter
          </button>
          <button 
            @click="store.loadAlerts()"
            :disabled="store.loading"
            class="bg-red-600 hover:bg-red-700 text-white rounded-lg px-4 py-2 text-sm font-medium transition duration-200 disabled:opacity-50 shadow-sm"
          >
            <ArrowPathIcon class="w-4 h-4 inline mr-2" :class="{ 'animate-spin': store.loading }" />
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="space-y-6">
        <!-- Alert Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-red-100 rounded-lg">
                <ExclamationTriangleIcon class="w-6 h-6 text-red-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">High Priority</p>
                <p class="text-2xl font-bold text-gray-900">{{ getAlertCountBySeverity('high') }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-yellow-100 rounded-lg">
                <ExclamationTriangleIcon class="w-6 h-6 text-yellow-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Medium Priority</p>
                <p class="text-2xl font-bold text-gray-900">{{ getAlertCountBySeverity('medium') }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
                <CheckCircleIcon class="w-6 h-6 text-green-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Low Priority</p>
                <p class="text-2xl font-bold text-gray-900">{{ getAlertCountBySeverity('low') }}</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
                <ClockIcon class="w-6 h-6 text-blue-600" />
              </div>
              <div class="ml-4">
                <p class="text-sm font-medium text-gray-500">Total Alerts</p>
                <p class="text-2xl font-bold text-gray-900">{{ store.alertCount }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Alert Filters -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div class="flex flex-wrap items-center gap-4">
            <h3 class="text-lg font-medium text-gray-900">Filter by severity:</h3>
            <div class="flex space-x-2">
              <button
                v-for="severity in ['all', 'high', 'medium', 'low']"
                :key="severity"
                @click="selectedSeverity = severity"
                class="px-4 py-2 rounded-lg font-medium text-sm transition duration-200 border"
                :class="selectedSeverity === severity 
                  ? getSeverityActiveClass(severity)
                  : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'"
              >
                {{ severity.charAt(0).toUpperCase() + severity.slice(1) }}
                <span class="ml-2 px-2 py-0.5 bg-white bg-opacity-50 rounded-full text-xs">
                  {{ severity === 'all' ? store.alerts.length : getAlertCountBySeverity(severity) }}
                </span>
              </button>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="store.loading" class="flex justify-center items-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-refrigeration-600"></div>
        </div>

        <!-- Alerts List -->
        <div v-else class="space-y-4">
          <div 
            v-for="alert in filteredAlerts" 
            :key="alert._id || alert.timestamp"
            class="bg-white rounded-xl shadow-sm border-l-4 border border-gray-200 hover:shadow-md transition duration-200"
            :class="getAlertBorderClass(alert.severity)"
          >
            <div class="p-6">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-3">
                    <span 
                      class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                      :class="getSeverityBadgeClass(alert.severity)"
                    >
                      <component 
                        :is="getAlertIcon(alert.type)" 
                        class="w-4 h-4 mr-1"
                      />
                      {{ alert.severity.toUpperCase() }}
                    </span>
                    <span class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                      {{ alert.type }}
                    </span>
                    <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                      Machine {{ alert.machine_id }}
                    </span>
                  </div>
                  
                  <p class="text-gray-900 font-medium mb-2">{{ alert.message }}</p>
                  
                  <div class="flex items-center text-sm text-gray-500">
                    <ClockIcon class="w-4 h-4 mr-1" />
                    {{ formatDate(alert.timestamp) }}
                  </div>
                </div>
                
                <div class="ml-6 flex-shrink-0">
                  <component 
                    :is="getAlertIcon(alert.type)" 
                    class="h-8 w-8"
                    :class="getAlertIconColor(alert.severity)"
                  />
                </div>
              </div>
              
              <!-- Additional Data -->
              <div v-if="alert.data" class="mt-6 pt-4 border-t border-gray-200">
                <h4 class="text-sm font-medium text-gray-900 mb-3">System Parameters</h4>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div class="bg-blue-50 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <span class="text-blue-700 text-sm font-medium">Evaporator</span>
                      <span class="text-blue-900 font-bold">{{ alert.data.temp_evaporator }}°C</span>
                    </div>
                  </div>
                  <div class="bg-red-50 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <span class="text-red-700 text-sm font-medium">Condenser</span>
                      <span class="text-red-900 font-bold">{{ alert.data.temp_condenser }}°C</span>
                    </div>
                  </div>
                  <div class="bg-green-50 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <span class="text-green-700 text-sm font-medium">Superheat</span>
                      <span class="text-green-900 font-bold">{{ alert.data.superheat }}°C</span>
                    </div>
                  </div>
                  <div class="bg-purple-50 rounded-lg p-3">
                    <div class="flex items-center justify-between">
                      <span class="text-purple-700 text-sm font-medium">Current</span>
                      <span class="text-purple-900 font-bold">{{ alert.data.compressor_current }}A</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="filteredAlerts.length === 0" class="bg-white rounded-xl shadow-sm border border-gray-200 p-12">
            <div class="text-center">
              <ExclamationTriangleIcon class="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 class="text-lg font-medium text-gray-900 mb-2">No alerts found</h3>
              <p class="text-gray-500">No alerts match the selected filter criteria.</p>
            </div>
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
  ExclamationTriangleIcon,
  FireIcon,
  BoltIcon,
  ChartBarIcon,
  CogIcon,
  CheckCircleIcon,
  ClockIcon,
  FunnelIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'
import moment from 'moment'

const store = useRefrigerationStore()
const selectedSeverity = ref('all')

onMounted(() => {
  store.loadAlerts()
})

const filteredAlerts = computed(() => {
  if (selectedSeverity.value === 'all') {
    return store.alerts
  }
  return store.alerts.filter(alert => alert.severity === selectedSeverity.value)
})

const formatDate = (timestamp) => {
  return moment(timestamp).format('MMM DD, YYYY HH:mm:ss')
}

const getAlertCountBySeverity = (severity) => {
  // Use store's computed properties for accurate database counts
  switch (severity) {
    case 'high':
      return store.highSeverityCount
    case 'medium':
      return store.mediumSeverityCount
    case 'low':
      return store.lowSeverityCount
    default:
      return store.alerts.filter(alert => alert.severity === severity).length
  }
}

const getSeverityActiveClass = (severity) => {
  switch (severity) {
    case 'all':
      return 'bg-blue-600 text-white border-blue-600'
    case 'high':
      return 'bg-red-600 text-white border-red-600'
    case 'medium':
      return 'bg-yellow-600 text-white border-yellow-600'
    case 'low':
      return 'bg-green-600 text-white border-green-600'
    default:
      return 'bg-gray-600 text-white border-gray-600'
  }
}

const getAlertBorderClass = (severity) => {
  switch (severity) {
    case 'high':
      return 'border-l-red-500'
    case 'medium':
      return 'border-l-yellow-500'
    case 'low':
      return 'border-l-green-500'
    default:
      return 'border-l-gray-500'
  }
}

const getSeverityBadgeClass = (severity) => {
  switch (severity) {
    case 'high':
      return 'bg-red-100 text-red-800'
    case 'medium':
      return 'bg-yellow-100 text-yellow-800'
    case 'low':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getAlertIcon = (type) => {
  switch (type) {
    case 'temperature':
      return FireIcon
    case 'pressure':
      return ChartBarIcon
    case 'current':
      return BoltIcon
    case 'vibration':
      return CogIcon
    default:
      return ExclamationTriangleIcon
  }
}

const getAlertIconColor = (severity) => {
  switch (severity) {
    case 'high':
      return 'text-red-500'
    case 'medium':
      return 'text-yellow-500'
    case 'low':
      return 'text-green-500'
    default:
      return 'text-gray-500'
  }
}
</script>
