<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Simple Header -->
    <div class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <h1 class="text-xl font-bold text-gray-900">🧊 Refrigeration Dashboard</h1>
          <nav class="flex space-x-4">
            <router-link to="/test" class="text-blue-600 hover:text-blue-800">Test Page</router-link>
            <router-link to="/predictions" class="text-gray-600 hover:text-gray-800">Predictions</router-link>
            <router-link to="/alerts" class="text-gray-600 hover:text-gray-800">Alerts</router-link>
          </nav>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="text-center py-8">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">Welcome to Refrigeration Dashboard</h2>
          <p class="text-lg text-gray-600 mb-8">Monitor and predict maintenance needs for your refrigeration systems</p>
          
          <div class="space-y-4">
            <router-link to="/test" 
                         class="inline-block bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition duration-200">
              Go to Test Dashboard
            </router-link>
          </div>
        </div>

        <!-- Simple stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                    <span class="text-white font-bold text-sm">P</span>
                  </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Predictions</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ stats.total_predictions || 0 }}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                    <span class="text-white font-bold text-sm">A</span>
                  </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Alerts</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ stats.total_alerts || 0 }}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 rounded-md flex items-center justify-center" 
                       :class="stats.mongodb_connected ? 'bg-green-500' : 'bg-red-500'">
                    <span class="text-white font-bold text-sm">DB</span>
                  </div>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Database</dt>
                    <dd class="text-sm font-medium" 
                        :class="stats.mongodb_connected ? 'text-green-600' : 'text-red-600'">
                      {{ stats.mongodb_connected ? 'Connected' : 'Disconnected' }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRefrigerationStore } from '@/stores/refrigeration'

const store = useRefrigerationStore()

// Use store stats instead of local stats
const stats = computed(() => store.stats)

onMounted(async () => {
  console.log('Dashboard component mounted')
  // Store handles loading data, just make sure it's initialized
  if (!store.realtimeConnected) {
    await store.initializeStore()
  }
})
</script>
