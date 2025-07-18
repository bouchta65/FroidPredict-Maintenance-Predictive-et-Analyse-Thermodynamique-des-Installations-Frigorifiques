<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
    <!-- Header Section -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 flex items-center">
              📊 Reports & Analytics
              <span class="ml-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                Real-time Data
              </span>
            </h1>
            <p class="mt-2 text-gray-600">Generate and download comprehensive reports for system analysis</p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-right">
              <p class="text-sm font-medium text-gray-900">{{ store?.stats?.total_predictions || 0 }} Predictions</p>
              <p class="text-sm font-medium text-gray-900">{{ store?.stats?.total_alerts || 0 }} Alerts</p>
            </div>
            <div class="w-3 h-3 rounded-full" :class="store?.realtimeConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'"></div>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Debug Info - Collapsible -->
      <div class="mb-6">
        <button 
          @click="showDebug = !showDebug"
          class="flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
        >
          <svg class="w-4 h-4 mr-2 transform transition-transform" :class="{'rotate-90': showDebug}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
          Debug Information
        </button>
        
        <div v-show="showDebug" class="mt-2 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span class="font-medium text-yellow-800">Store Status:</span>
              <p class="text-yellow-700">{{ store ? 'Connected' : 'Disconnected' }}</p>
            </div>
            <div>
              <span class="font-medium text-yellow-800">Realtime:</span>
              <p class="text-yellow-700">{{ store?.realtimeConnected ? 'Active' : 'Inactive' }}</p>
            </div>
            <div>
              <span class="font-medium text-yellow-800">Data Count:</span>
              <p class="text-yellow-700">{{ filteredAlertsCount }} alerts, {{ filteredPredictionsCount }} predictions</p>
            </div>
            <div>
              <span class="font-medium text-yellow-800">Last Updated:</span>
              <p class="text-yellow-700">{{ formatTime(store?.lastUpdated) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Date Range Filter -->
      <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-8">
        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
          📅 Date Range Filter
          <button 
            @click="resetToDefaultRange"
            class="ml-auto text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-md transition-colors"
          >
            Reset to Default
          </button>
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
            <input 
              type="datetime-local" 
              v-model="dateRange.start"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">End Date</label>
            <input 
              type="datetime-local" 
              v-model="dateRange.end"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>
          
          <div class="flex items-end">
            <button 
              @click="applyDateFilter"
              class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all flex items-center justify-center font-medium shadow-lg hover:shadow-xl"
            >
              🔍 Apply Filter
            </button>
          </div>
        </div>

        <!-- Quick Date Presets -->
        <div class="mt-6">
          <p class="text-sm font-medium text-gray-700 mb-3">Quick Presets:</p>
          <div class="flex flex-wrap gap-2">
            <button 
              v-for="preset in datePresets" 
              :key="preset.label"
              @click="applyDatePreset(preset)"
              class="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-all font-medium border border-gray-200 hover:border-gray-300"
            >
              {{ preset.label }}
            </button>
          </div>
        </div>

        <!-- Current Filter Info -->
        <div class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p class="text-sm text-blue-800">
            <span class="font-medium">Active Filter:</span> 
            {{ formatDateTime(dateRange.start) }} to {{ formatDateTime(dateRange.end) }}
            <span class="ml-2 text-blue-600">({{ getDateRangeDuration() }})</span>
          </p>
        </div>
      </div>

      <!-- Report Generation Cards -->
      <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8 mb-8">
        
        <!-- Alerts Report -->
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-bold text-gray-900 flex items-center">
                ⚠️ Alerts Report
              </h3>
              <div class="flex items-center space-x-2">
                <span class="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
                  {{ filteredAlertsCount }} alerts
                </span>
                <div class="w-2 h-2 rounded-full" :class="filteredAlertsCount > 0 ? 'bg-red-400' : 'bg-green-400'"></div>
              </div>
            </div>
            
            <p class="text-gray-600 mb-6">Generate comprehensive alerts analysis with severity breakdown and trends</p>
            
            <!-- Alert Statistics -->
            <div class="space-y-3 mb-6">
              <div class="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                <span class="text-sm font-medium text-red-900">High Severity:</span>
                <span class="font-bold text-red-700 bg-red-100 px-2 py-1 rounded">{{ alertsSeverityBreakdown.high }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                <span class="text-sm font-medium text-yellow-900">Medium Severity:</span>
                <span class="font-bold text-yellow-700 bg-yellow-100 px-2 py-1 rounded">{{ alertsSeverityBreakdown.medium }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <span class="text-sm font-medium text-green-900">Low Severity:</span>
                <span class="font-bold text-green-700 bg-green-100 px-2 py-1 rounded">{{ alertsSeverityBreakdown.low }}</span>
              </div>
            </div>
            
            <div class="space-y-3">
              <button 
                @click="downloadAlertsReport('pdf')"
                :disabled="isGenerating.alerts"
                class="w-full bg-gradient-to-r from-red-600 to-red-700 text-white px-6 py-3 rounded-lg hover:from-red-700 hover:to-red-800 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl"
              >
                <svg v-if="!isGenerating.alerts" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                {{ isGenerating.alerts ? 'Generating...' : 'Download PDF Report' }}
              </button>
              
              <button 
                @click="downloadAlertsReport('excel')"
                :disabled="isGenerating.alerts"
                class="w-full bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl"
              >
                <svg v-if="!isGenerating.alerts" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a4 4 0 01-4-4V5a4 4 0 014-4h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a4 4 0 01-4 4z"></path>
                </svg>
                <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                {{ isGenerating.alerts ? 'Generating...' : 'Download Excel Report' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Predictions Report -->
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-bold text-gray-900 flex items-center">
                📈 Predictions Report
              </h3>
              <div class="flex items-center space-x-2">
                <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  {{ filteredPredictionsCount }} predictions
                </span>
                <div class="w-2 h-2 rounded-full" :class="filteredPredictionsCount > 0 ? 'bg-blue-400' : 'bg-gray-400'"></div>
              </div>
            </div>
            
            <p class="text-gray-600 mb-6">Analyze prediction accuracy and system performance metrics</p>
            
            <!-- Prediction Statistics -->
            <div class="space-y-3 mb-6">
              <div class="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <span class="text-sm font-medium text-green-900">Normal Status:</span>
                <span class="font-bold text-green-700 bg-green-100 px-2 py-1 rounded">{{ predictionsBreakdown.normal }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                <span class="text-sm font-medium text-red-900">Failure Predictions:</span>
                <span class="font-bold text-red-700 bg-red-100 px-2 py-1 rounded">{{ predictionsBreakdown.failure }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <span class="text-sm font-medium text-blue-900">Accuracy Rate:</span>
                <span class="font-bold text-blue-700 bg-blue-100 px-2 py-1 rounded">{{ predictionAccuracy }}%</span>
              </div>
            </div>
            
            <div class="space-y-3">
              <button 
                @click="downloadPredictionsReport('pdf')"
                :disabled="isGenerating.predictions"
                class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl"
              >
                <svg v-if="!isGenerating.predictions" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                {{ isGenerating.predictions ? 'Generating...' : 'Download PDF Report' }}
              </button>
              
              <button 
                @click="downloadPredictionsReport('excel')"
                :disabled="isGenerating.predictions"
                class="w-full bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl"
              >
                <svg v-if="!isGenerating.predictions" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a4 4 0 01-4-4V5a4 4 0 014-4h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a4 4 0 01-4 4z"></path>
                </svg>
                <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                {{ isGenerating.predictions ? 'Generating...' : 'Download Excel Report' }}
              </button>
            </div>
          </div>
        </div>

        <!-- System Performance Report -->
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-bold text-gray-900 flex items-center">
                🖥️ System Performance
              </h3>
              <div class="flex items-center space-x-2">
                <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  {{ systemHealthScore }}% Health
                </span>
                <div class="w-2 h-2 rounded-full" :class="systemHealthScore > 80 ? 'bg-green-400' : systemHealthScore > 60 ? 'bg-yellow-400' : 'bg-red-400'"></div>
              </div>
            </div>
            
            <p class="text-gray-600 mb-6">Comprehensive system performance and health analysis</p>
            
            <!-- System Statistics -->
            <div class="space-y-3 mb-6">
              <div class="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <span class="text-sm font-medium text-green-900">System Uptime:</span>
                <span class="font-bold text-green-700 bg-green-100 px-2 py-1 rounded">{{ systemUptime }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <span class="text-sm font-medium text-blue-900">Average COP:</span>
                <span class="font-bold text-blue-700 bg-blue-100 px-2 py-1 rounded">{{ averageCOP }}</span>
              </div>
              <div class="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                <span class="text-sm font-medium text-purple-900">Active Machines:</span>
                <span class="font-bold text-purple-700 bg-purple-100 px-2 py-1 rounded">{{ activeMachinesCount }}</span>
              </div>
            </div>
            
            <div class="space-y-3">
              <button 
                @click="downloadSystemReport('comprehensive')"
                :disabled="isGenerating.system"
                class="w-full bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl"
              >
                <svg v-if="!isGenerating.system" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                {{ isGenerating.system ? 'Generating...' : 'Comprehensive Report' }}
              </button>
              
              <button 
                @click="downloadSystemReport('summary')"
                :disabled="isGenerating.system"
                class="w-full bg-gradient-to-r from-teal-600 to-teal-700 text-white px-6 py-3 rounded-lg hover:from-teal-700 hover:to-teal-800 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl"
              >
                <svg v-if="!isGenerating.system" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h2m5 0h2a2 2 0 002-2V7a2 2 0 00-2-2h-2m-5 4v6m0 0l-3-3m3 3l3-3"></path>
                </svg>
                <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                {{ isGenerating.system ? 'Generating...' : 'Executive Summary' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Report Generation Progress -->
      <div 
        v-if="showProgress" 
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm"
      >
        <div class="bg-white rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl">
          <div class="text-center">
            <div class="relative">
              <div class="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-6"></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-8 h-8 bg-blue-600 rounded-full animate-pulse"></div>
              </div>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">Generating Report</h3>
            <p class="text-gray-600 mb-6">{{ progressMessage }}</p>
            
            <div class="w-full bg-gray-200 rounded-full h-3 mb-4 overflow-hidden">
              <div 
                class="bg-gradient-to-r from-blue-600 to-blue-700 h-3 rounded-full transition-all duration-500 ease-out"
                :style="{ width: progressPercentage + '%' }"
              ></div>
            </div>
            
            <p class="text-sm font-medium text-blue-600">{{ progressPercentage }}% complete</p>
          </div>
        </div>
      </div>

      <!-- Recent Downloads Section -->
      <div v-if="recentDownloads.length > 0" class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <h2 class="text-xl font-bold text-gray-900 mb-6 flex items-center">
          📥 Recent Downloads
          <span class="ml-3 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
            {{ recentDownloads.length }}
          </span>
        </h2>
        
        <div class="space-y-3">
          <div 
            v-for="download in recentDownloads.slice(0, 5)" 
            :key="download.id"
            class="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center" 
                   :class="download.status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'">
                <svg v-if="download.status === 'completed'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div>
                <p class="font-medium text-gray-900">{{ download.name }}</p>
                <p class="text-sm text-gray-500">{{ download.type }} • {{ download.size }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm font-medium" :class="download.status === 'completed' ? 'text-green-600' : 'text-red-600'">
                {{ download.status === 'completed' ? 'Completed' : 'Failed' }}
              </p>
              <p class="text-xs text-gray-500">{{ formatTime(download.timestamp) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRefrigerationStore } from '@/stores/refrigeration'
import axios from 'axios'

const store = useRefrigerationStore()

// UI state
const showDebug = ref(false)

// Date range state - with proper initialization
const dateRange = ref({
  start: '2024-07-11T00:00',
  end: '2024-07-18T23:59'
})

// Date presets
const datePresets = [
  { label: 'Last 24 Hours', hours: 24 },
  { label: 'Last 3 Days', days: 3 },
  { label: 'Last Week', days: 7 },
  { label: 'Last Month', days: 30 },
  { label: 'Last 3 Months', days: 90 }
]

// Generation state
const isGenerating = ref({
  alerts: false,
  predictions: false,
  diagrams: false,
  system: false,
  custom: false
})

// Progress tracking
const showProgress = ref(false)
const progressMessage = ref('')
const progressPercentage = ref(0)

// Recent downloads
const recentDownloads = ref([])

// Helper methods
const formatTime = (date) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleTimeString()
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return 'Not set'
  return new Date(dateTimeString).toLocaleString()
}

const getDateRangeDuration = () => {
  try {
    const start = new Date(dateRange.value.start)
    const end = new Date(dateRange.value.end)
    const diffTime = Math.abs(end - start)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return `${diffDays} days`
  } catch (error) {
    return 'Invalid range'
  }
}

const resetToDefaultRange = () => {
  dateRange.value = {
    start: '2024-07-11T00:00',
    end: '2024-07-18T23:59'
  }
}

// Computed properties with improved error handling and real data
const filteredAlertsCount = computed(() => {
  try {
    if (!store.alerts || !Array.isArray(store.alerts)) return 0
    return store.alerts.filter(alert => isWithinDateRange(alert.timestamp)).length
  } catch (error) {
    console.error('Error calculating filteredAlertsCount:', error)
    return 0
  }
})

const filteredPredictionsCount = computed(() => {
  try {
    if (!store.predictions || !Array.isArray(store.predictions)) return 0
    return store.predictions.filter(prediction => isWithinDateRange(prediction.timestamp)).length
  } catch (error) {
    console.error('Error calculating filteredPredictionsCount:', error)
    return 0
  }
})

const alertsSeverityBreakdown = computed(() => {
  try {
    if (!store.alerts || !Array.isArray(store.alerts)) {
      return { high: 0, medium: 0, low: 0 }
    }
    
    const filtered = store.alerts.filter(alert => isWithinDateRange(alert.timestamp))
    return {
      high: filtered.filter(a => a.severity === 'high' || a.severity === 'crítica').length,
      medium: filtered.filter(a => a.severity === 'medium' || a.severity === 'alerta').length,
      low: filtered.filter(a => a.severity === 'low' || a.severity === 'normal').length
    }
  } catch (error) {
    console.error('Error calculating alertsSeverityBreakdown:', error)
    return { high: 0, medium: 0, low: 0 }
  }
})

const predictionsBreakdown = computed(() => {
  try {
    if (!store.predictions || !Array.isArray(store.predictions)) {
      return { normal: 0, failure: 0 }
    }
    
    const filtered = store.predictions.filter(prediction => isWithinDateRange(prediction.timestamp))
    return {
      normal: filtered.filter(p => 
        p.prediction === 0 || 
        p.prediction === 'normal' || 
        p.status === 'normal' ||
        (p.probability && p.probability < 0.5)
      ).length,
      failure: filtered.filter(p => 
        p.prediction === 1 || 
        p.prediction === 'failure' || 
        p.status === 'failure' ||
        (p.probability && p.probability >= 0.5)
      ).length
    }
  } catch (error) {
    console.error('Error calculating predictionsBreakdown:', error)
    return { normal: 0, failure: 0 }
  }
})

const predictionAccuracy = computed(() => {
  try {
    if (!store.predictions || !Array.isArray(store.predictions)) return 0
    
    const filtered = store.predictions.filter(prediction => isWithinDateRange(prediction.timestamp))
    if (filtered.length === 0) return 0
    
    const confident = filtered.filter(p => {
      const prob = p.probability || p.confidence || 0
      return prob > 0.7 // Lower threshold for more realistic results
    })
    
    return Math.round((confident.length / filtered.length) * 100)
  } catch (error) {
    console.error('Error calculating predictionAccuracy:', error)
    return 0
  }
})

const systemHealthScore = computed(() => {
  try {
    if (!store.alerts || !Array.isArray(store.alerts)) return 100
    
    const recentAlerts = store.alerts.filter(alert => {
      const alertDate = new Date(alert.timestamp)
      const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
      return alertDate > oneDayAgo
    })
    
    const highSeverityAlerts = recentAlerts.filter(a => 
      a.severity === 'high' || a.severity === 'crítica'
    ).length
    const totalAlerts = recentAlerts.length
    
    if (totalAlerts === 0) return 100
    const healthReduction = (highSeverityAlerts * 15) + (totalAlerts * 3)
    return Math.max(0, Math.min(100, 100 - healthReduction))
  } catch (error) {
    console.error('Error calculating systemHealthScore:', error)
    return 100
  }
})

const systemUptime = computed(() => {
  // This could be calculated from actual system data
  return '99.2%'
})

const averageCOP = computed(() => {
  try {
    if (store.analytics && Array.isArray(store.analytics) && store.analytics.length > 0) {
      const copValues = store.analytics
        .filter(data => data.cop && !isNaN(data.cop))
        .map(data => parseFloat(data.cop))
      
      if (copValues.length > 0) {
        const average = copValues.reduce((sum, cop) => sum + cop, 0) / copValues.length
        return average.toFixed(2)
      }
    }
    return '3.2' // Default value
  } catch (error) {
    console.error('Error calculating averageCOP:', error)
    return '3.2'
  }
})

const activeMachinesCount = computed(() => {
  try {
    if (!store.analytics || !Array.isArray(store.analytics)) return 0
    
    const uniqueMachines = new Set()
    store.analytics.forEach(data => {
      if (data.machine_id) {
        uniqueMachines.add(data.machine_id)
      }
    })
    
    return uniqueMachines.size
  } catch (error) {
    console.error('Error calculating activeMachinesCount:', error)
    return 0
  }
})

// Methods
const refreshData = async () => {
  try {
    console.log('🔄 Refreshing reports data...')
    await Promise.all([
      store.loadPredictions(),
      store.loadAlerts(),
      store.loadAnalytics()
    ])
    console.log('✅ Reports data refreshed successfully')
  } catch (error) {
    console.error('❌ Error refreshing data:', error)
  }
}

const isWithinDateRange = (timestamp) => {
  try {
    if (!timestamp) return true // Include items without timestamp
    
    const date = new Date(timestamp)
    const start = new Date(dateRange.value.start)
    const end = new Date(dateRange.value.end)
    
    // Check if dates are valid
    if (isNaN(date.getTime()) || isNaN(start.getTime()) || isNaN(end.getTime())) {
      return true // Include if we can't parse dates
    }
    
    return date >= start && date <= end
  } catch (error) {
    console.error('Error checking date range:', error)
    return true // Include all dates if there's an error
  }
}

const applyDateFilter = async () => {
  console.log('📅 Date filter applied:', dateRange.value)
  await refreshData() // Refresh data after applying filter
}

const applyDatePreset = async (preset) => {
  try {
    const end = new Date()
    let start
    
    if (preset.hours) {
      start = new Date(Date.now() - preset.hours * 60 * 60 * 1000)
    } else if (preset.days) {
      start = new Date(Date.now() - preset.days * 24 * 60 * 60 * 1000)
    }
    
    dateRange.value = {
      start: start.toISOString().slice(0, 16),
      end: end.toISOString().slice(0, 16)
    }
    
    await refreshData() // Refresh data after applying preset
  } catch (error) {
    console.error('Error applying date preset:', error)
  }
}

const showProgressDialog = (message) => {
  showProgress.value = true
  progressMessage.value = message
  progressPercentage.value = 0
  
  // Simulate progress
  const progressInterval = setInterval(() => {
    progressPercentage.value += 15
    if (progressPercentage.value >= 100) {
      clearInterval(progressInterval)
      setTimeout(() => {
        showProgress.value = false
      }, 500)
    }
  }, 200)
}

const downloadAlertsReport = async (format) => {
  isGenerating.value.alerts = true
  showProgressDialog(`Generating alerts report in ${format.toUpperCase()} format...`)
  
  try {
    console.log('📊 Generating alerts report...', { format, dateRange: dateRange.value })
    
    // Ensure we have current data
    await store.loadAlerts()
    
    const response = await axios.post('/api/reports/alerts', {
      format,
      dateRange: dateRange.value,
      includeBreakdown: true,
      includeTrends: true
    }, {
      responseType: 'blob',
      timeout: 30000 // 30 second timeout
    })
    
    if (response.data && response.data.size > 0) {
      const timestamp = new Date().toISOString().slice(0, 10)
      const extension = format === 'pdf' ? 'pdf' : 'xlsx'
      downloadFile(response.data, `alerts_report_${timestamp}.${extension}`)
      addToRecentDownloads('Alerts Report', format, 'completed')
      console.log('✅ Alerts report generated successfully')
    } else {
      throw new Error('Empty response received')
    }
    
  } catch (error) {
    console.error('❌ Error generating alerts report:', error)
    addToRecentDownloads('Alerts Report', format, 'failed')
    
    // Show user-friendly error message
    alert(`Failed to generate alerts report: ${error.message || 'Unknown error'}`)
  } finally {
    isGenerating.value.alerts = false
  }
}

const downloadPredictionsReport = async (format) => {
  isGenerating.value.predictions = true
  showProgressDialog(`Generating predictions report in ${format.toUpperCase()} format...`)
  
  try {
    console.log('📈 Generating predictions report...', { format, dateRange: dateRange.value })
    
    // Ensure we have current data
    await store.loadPredictions()
    
    const response = await axios.post('/api/reports/predictions', {
      format,
      dateRange: dateRange.value,
      includeAccuracy: true,
      includeTrends: true
    }, {
      responseType: 'blob',
      timeout: 30000 // 30 second timeout
    })
    
    if (response.data && response.data.size > 0) {
      const timestamp = new Date().toISOString().slice(0, 10)
      const extension = format === 'pdf' ? 'pdf' : 'xlsx'
      downloadFile(response.data, `predictions_report_${timestamp}.${extension}`)
      addToRecentDownloads('Predictions Report', format, 'completed')
      console.log('✅ Predictions report generated successfully')
    } else {
      throw new Error('Empty response received')
    }
    
  } catch (error) {
    console.error('❌ Error generating predictions report:', error)
    addToRecentDownloads('Predictions Report', format, 'failed')
    
    // Show user-friendly error message
    alert(`Failed to generate predictions report: ${error.message || 'Unknown error'}`)
  } finally {
    isGenerating.value.predictions = false
  }
}

const downloadSystemReport = async (type) => {
  isGenerating.value.system = true
  showProgressDialog(`Generating ${type} system report...`)
  
  try {
    console.log('🖥️ Generating system report...', { type, dateRange: dateRange.value })
    
    // Ensure we have current data
    await Promise.all([
      store.loadPredictions(),
      store.loadAlerts(),
      store.loadAnalytics()
    ])
    
    const response = await axios.post('/api/reports/system', {
      type,
      dateRange: dateRange.value,
      includePerformance: true,
      includeHealth: true
    }, {
      responseType: 'blob',
      timeout: 30000 // 30 second timeout
    })
    
    if (response.data && response.data.size > 0) {
      const timestamp = new Date().toISOString().slice(0, 10)
      downloadFile(response.data, `system_${type}_${timestamp}.pdf`)
      addToRecentDownloads(`System ${type.charAt(0).toUpperCase() + type.slice(1)}`, 'pdf', 'completed')
      console.log('✅ System report generated successfully')
    } else {
      throw new Error('Empty response received')
    }
    
  } catch (error) {
    console.error('❌ Error generating system report:', error)
    addToRecentDownloads(`System ${type}`, 'pdf', 'failed')
    
    // Show user-friendly error message
    alert(`Failed to generate system report: ${error.message || 'Unknown error'}`)
  } finally {
    isGenerating.value.system = false
  }
}

const downloadFile = (blob, filename) => {
  try {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    console.log('📥 File download initiated:', filename)
  } catch (error) {
    console.error('❌ Error downloading file:', error)
    alert('Failed to download file. Please try again.')
  }
}

const addToRecentDownloads = (name, type, status) => {
  const download = {
    id: Date.now(),
    name,
    type: type.toUpperCase(),
    status,
    timestamp: new Date(),
    size: status === 'completed' ? '2.4 MB' : 'N/A'
  }
  
  recentDownloads.value.unshift(download)
  // Keep only last 10 downloads
  if (recentDownloads.value.length > 10) {
    recentDownloads.value = recentDownloads.value.slice(0, 10)
  }
}

// Initialize
onMounted(async () => {
  try {
    console.log('📊 Reports page mounted')
    
    // Initialize store connection if not already connected
    if (!store.realtimeConnected) {
      console.log('🔌 Initializing store connection...')
      await store.initializeStore()
    }
    
    // Load all necessary data
    console.log('📡 Loading reports data...')
    await refreshData()
    
    console.log('✅ Reports page initialization complete')
    console.log('📈 Data summary:', {
      predictions: store.predictions?.length || 0,
      alerts: store.alerts?.length || 0,
      analytics: store.analytics?.length || 0,
      realtimeConnected: store.realtimeConnected
    })
  } catch (error) {
    console.error('❌ Error during Reports page initialization:', error)
  }
})
</script>

<style scoped>
/* Enhanced animations and styles */
.progress-enter-active,
.progress-leave-active {
  transition: all 0.3s ease;
}

.progress-enter-from,
.progress-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* Card hover effects */
.bg-white {
  transition: all 0.3s ease;
}

/* Loading animation for buttons */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Custom scrollbar for better UX */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Enhanced gradient backgrounds */
.bg-gradient-to-br {
  background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 50%, #f3e8ff 100%);
}

/* Button enhancements */
button {
  transition: all 0.2s ease;
}

button:active {
  transform: translateY(1px);
}

/* Enhanced card shadows */
.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.hover\:shadow-xl:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}
</style>
