<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
    <div class="card">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <ChartBarIcon class="h-8 w-8 text-blue-600" />
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-gray-500">Total Predictions</p>
          <p class="text-2xl font-semibold text-gray-900">{{ stats.total_predictions }}</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <ExclamationTriangleIcon class="h-8 w-8 text-red-600" />
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-gray-500">Total Alerts</p>
          <p class="text-2xl font-semibold text-gray-900">{{ stats.total_alerts }}</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <ShieldExclamationIcon class="h-8 w-8 text-yellow-600" />
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-gray-500">High Priority</p>
          <p class="text-2xl font-semibold text-gray-900">{{ highPriorityCount }}</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <CircleStackIcon 
            class="h-8 w-8"
            :class="stats.mongodb_connected ? 'text-green-600' : 'text-red-600'"
          />
        </div>
        <div class="ml-3">
          <p class="text-sm font-medium text-gray-500">Database</p>
          <p class="text-sm font-semibold"
             :class="stats.mongodb_connected ? 'text-green-600' : 'text-red-600'"
          >
            {{ stats.mongodb_connected ? 'Connected' : 'Disconnected' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  ChartBarIcon, 
  ExclamationTriangleIcon, 
  ShieldExclamationIcon,
  CircleStackIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  stats: {
    type: Object,
    required: true
  },
  alerts: {
    type: Array,
    default: () => []
  }
})

// Use store for consistent counts instead of props.alerts filtering
import { useRefrigerationStore } from '@/stores/refrigeration'
const store = useRefrigerationStore()

const highPriorityCount = computed(() => {
  // Use store's high severity count if available, otherwise fallback to local filtering
  return store.highSeverityAlerts?.length || props.alerts.filter(alert => alert.severity === 'high').length
})
</script>
