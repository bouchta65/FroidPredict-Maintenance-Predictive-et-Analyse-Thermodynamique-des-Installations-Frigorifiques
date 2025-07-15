<template>
  <Layout 
    :loading="false" 
    :stats="stats" 
    :is-real-time-connected="apiStatus === 'Connected'"
    @refresh="testAPI"
  >
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">🧊 Refrigeration Dashboard Test</h1>
      <p class="text-gray-600 mb-6">System connectivity and functionality testing center</p>
    </div>
    
    <!-- Test API Connection -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
        </svg>
        API Connection Test
      </h2>
      <div class="flex items-center space-x-4">
        <button @click="testAPI" 
                class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition duration-200 shadow-sm">
          Test API Connection
        </button>
        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
              :class="getStatusClass(apiStatus)">
          <div class="w-2 h-2 rounded-full mr-2" 
               :class="apiStatus === 'Connected' ? 'bg-green-500 animate-pulse' : 'bg-red-500'"></div>
          Status: {{ apiStatus }}
        </span>
      </div>
    </div>

    <!-- Test Data Generation -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        Generate Test Data
      </h2>
      <div class="flex items-center space-x-4">
        <button @click="generateTestData" 
                class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium transition duration-200 shadow-sm">
          Generate Test Data
        </button>
        <span class="text-gray-600">{{ testDataMessage }}</span>
      </div>
    </div>

    <!-- Stats Display -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Predictions</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.total_predictions || 0 }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-red-100 rounded-lg">
            <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Alerts</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.total_alerts || 0 }}</p>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 rounded-lg" :class="stats.mongodb_connected ? 'bg-green-100' : 'bg-red-100'">
            <svg class="w-6 h-6" :class="stats.mongodb_connected ? 'text-green-600' : 'text-red-600'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>
            </svg>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">Database</p>
            <p class="text-lg font-semibold" :class="stats.mongodb_connected ? 'text-green-600' : 'text-red-600'">
              {{ stats.mongodb_connected ? 'Connected' : 'Disconnected' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Navigation</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <router-link to="/" class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group">
          <div class="w-10 h-10 bg-blue-100 group-hover:bg-blue-200 rounded-lg flex items-center justify-center mr-4">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
            </svg>
          </div>
          <div>
            <h3 class="font-medium text-gray-900">Dashboard</h3>
            <p class="text-sm text-gray-500">Main overview</p>
          </div>
        </router-link>
        
        <router-link to="/predictions" class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group">
          <div class="w-10 h-10 bg-green-100 group-hover:bg-green-200 rounded-lg flex items-center justify-center mr-4">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <div>
            <h3 class="font-medium text-gray-900">Predictions</h3>
            <p class="text-sm text-gray-500">View analytics</p>
          </div>
        </router-link>
        
        <router-link to="/alerts" class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group">
          <div class="w-10 h-10 bg-red-100 group-hover:bg-red-200 rounded-lg flex items-center justify-center mr-4">
            <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
          </div>
          <div>
            <h3 class="font-medium text-gray-900">Alerts</h3>
            <p class="text-sm text-gray-500">Check issues</p>
          </div>
        </router-link>
        
        <router-link to="/diagrams" class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors group">
          <div class="w-10 h-10 bg-indigo-100 group-hover:bg-indigo-200 rounded-lg flex items-center justify-center mr-4">
            <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
          </div>
          <div>
            <h3 class="font-medium text-gray-900">Diagrams</h3>
            <p class="text-sm text-gray-500">Enthalpy analysis</p>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Debug Info -->
    <div class="bg-gray-800 rounded-xl p-6 mt-6">
      <h2 class="text-lg font-semibold text-white mb-4">Debug Info</h2>
      <pre class="text-sm text-gray-300 overflow-x-auto">{{ JSON.stringify({ stats, apiStatus, testDataMessage }, null, 2) }}</pre>
    </div>
  </Layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import Layout from '@/components/Layout.vue'
import { useRefrigerationStore } from '@/stores/refrigeration'

const store = useRefrigerationStore()
const apiStatus = ref('Not tested')
const testDataMessage = ref('Click button to generate test data')

// Use store stats instead of local stats
const stats = computed(() => store.stats)

onMounted(() => {
  console.log('TestDashboard component mounted')
  loadData()
})

const testAPI = async () => {
  try {
    apiStatus.value = 'Testing...'
    console.log('Testing API connection...')
    
    const response = await axios.get('/api/system_status')
    console.log('API Response:', response.data)
    
    if (response.data.status === 'running') {
      apiStatus.value = 'Connected ✅'
    } else {
      apiStatus.value = 'Error ❌'
    }
  } catch (error) {
    apiStatus.value = 'Failed ❌'
    console.error('API test failed:', error)
  }
}

const generateTestData = async () => {
  try {
    testDataMessage.value = 'Generating...'
    console.log('Generating test data...')
    
    const testData = {
      machine_id: `TEST_${Date.now()}`,
      temp_evaporator: -10.5,
      temp_condenser: 42.0,
      pressure_high: 13.2,
      pressure_low: 2.1,
      superheat: 8.5,
      subcooling: 5.2,
      compressor_current: 8.8,
      vibration: 0.025
    }
    
    const response = await axios.post('/api/refrigeration_prediction', testData)
    console.log('Test data response:', response.data)
    
    testDataMessage.value = 'Test data generated successfully ✅'
    
    // Reload data after 1 second
    setTimeout(loadData, 1000)
  } catch (error) {
    testDataMessage.value = 'Generation failed ❌'
    console.error('Test data generation failed:', error)
  }
}

const loadData = async () => {
  try {
    console.log('Loading dashboard data...')
    const response = await axios.get('/api/dashboard_data')
    console.log('Dashboard data:', response.data)
    
    if (response.data.status === 'success') {
      stats.value = response.data.stats
    }
  } catch (error) {
    console.error('Failed to load data:', error)
  }
}

const getStatusClass = (status) => {
  if (status.includes('✅')) {
    return 'bg-green-100 text-green-800'
  } else if (status.includes('❌')) {
    return 'bg-red-100 text-red-800'
  } else {
    return 'bg-yellow-100 text-yellow-800'
  }
}
</script>
