import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { io } from 'socket.io-client'

export const useRefrigerationStore = defineStore('refrigeration', () => {
  // State
  const predictions = ref([])
  const alerts = ref([])
  const analytics = ref([]) // Store analytics/diagram data
  const stats = ref({
    total_predictions: 0,
    total_alerts: 0,
    maintenance_alerts: 0,
    normal_status: 0,
    high_severity_alerts: 0,
    medium_severity_alerts: 0,
    low_severity_alerts: 0,
    total_analytics: 0, // Track analytics data count
    mongodb_connected: false
  })
  const socket = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const lastUpdated = ref(new Date())
  const realtimeConnected = ref(false)

  // Getters
  const recentPredictions = computed(() => predictions.value.slice(0, 10))
  const recentAlerts = computed(() => alerts.value.slice(0, 10))
  const recentAnalytics = computed(() => analytics.value.slice(0, 20)) // Recent analytics data
  
  const highSeverityAlerts = computed(() => 
    alerts.value.filter(alert => alert.severity === 'high')
  )
  
  const mediumSeverityAlerts = computed(() => 
    alerts.value.filter(alert => alert.severity === 'medium')
  )
  
  const lowSeverityAlerts = computed(() => 
    alerts.value.filter(alert => alert.severity === 'low')
  )
  
  // Analytics getters
  const uniqueMachines = computed(() => {
    const machines = analytics.value.map(data => data.machine_id)
    return [...new Set(machines)].sort()
  })
  
  const latestAnalyticsByMachine = computed(() => {
    const machineMap = new Map()
    analytics.value.forEach(data => {
      const existing = machineMap.get(data.machine_id)
      if (!existing || new Date(data.timestamp) > new Date(existing.timestamp)) {
        machineMap.set(data.machine_id, data)
      }
    })
    return Array.from(machineMap.values())
  })
  
  const averageCOP = computed(() => {
    if (analytics.value.length === 0) return 0
    const totalCOP = analytics.value.reduce((sum, data) => {
      return sum + (data.performance?.cop || 0)
    }, 0)
    return Math.round((totalCOP / analytics.value.length) * 100) / 100
  })
  
  // Alert categorization
  const maintenanceAlerts = computed(() => 
    alerts.value.filter(alert => 
      alert.severity === 'high' || 
      alert.type === 'maintenance' || 
      alert.prediction === 'failure' ||
      (alert.message && alert.message.toLowerCase().includes('maintenance'))
    )
  )
  
  const normalStatusAlerts = computed(() => 
    alerts.value.filter(alert => 
      alert.severity === 'low' || 
      alert.type === 'normal' || 
      alert.prediction === 'normal' ||
      (alert.message && alert.message.toLowerCase().includes('normal'))
    )
  )
  
  // Average confidence calculation
  const avgConfidence = computed(() => {
    if (predictions.value.length === 0) return 0
    
    const totalConfidence = predictions.value.reduce((sum, pred) => {
      const confidence = pred.confidence || pred.probability || 0
      return sum + (typeof confidence === 'number' ? confidence : 0)
    }, 0)
    
    return Math.round((totalConfidence / predictions.value.length) * 100) / 100
  })
  
  // Use real database counts instead of local array lengths
  const predictionCount = computed(() => stats.value.total_predictions || 0)
  const alertCount = computed(() => stats.value.total_alerts || 0)
  const analyticsCount = computed(() => stats.value.total_analytics || 0)
  
  // Use database counts for maintenance and normal status if available, otherwise fallback to local filtering
  const maintenanceAlertCount = computed(() => 
    stats.value.maintenance_alerts !== undefined 
      ? stats.value.maintenance_alerts 
      : maintenanceAlerts.value.length
  )
  
  const normalStatusCount = computed(() => 
    stats.value.normal_status !== undefined 
      ? stats.value.normal_status 
      : normalStatusAlerts.value.length
  )

  // Severity-based counts with database fallback
  const highSeverityCount = computed(() => 
    stats.value.high_severity_alerts !== undefined 
      ? stats.value.high_severity_alerts 
      : highSeverityAlerts.value.length
  )
  
  const mediumSeverityCount = computed(() => 
    stats.value.medium_severity_alerts !== undefined 
      ? stats.value.medium_severity_alerts 
      : mediumSeverityAlerts.value.length
  )
  
  const lowSeverityCount = computed(() => 
    stats.value.low_severity_alerts !== undefined 
      ? stats.value.low_severity_alerts 
      : lowSeverityAlerts.value.length
  )

  // Enhanced stats object that ensures consistency
  const enhancedStats = computed(() => ({
    ...stats.value,
    total_predictions: predictionCount.value,
    total_alerts: alertCount.value,
    total_analytics: analyticsCount.value,
    maintenance_alerts: maintenanceAlertCount.value,
    normal_status: normalStatusCount.value,
    high_severity_alerts: highSeverityCount.value,
    medium_severity_alerts: mediumSeverityCount.value,
    low_severity_alerts: lowSeverityCount.value
  }))

  // Actions
  const initializeSocket = () => {
    socket.value = io('http://localhost:5002')
    
    socket.value.on('connect', () => {
      realtimeConnected.value = true
      console.log('🔗 Store WebSocket connected for real-time updates')
      // Immediately sync real counts from database on connection
      refreshCounts()
    })
    
    socket.value.on('disconnect', () => {
      realtimeConnected.value = false
      console.log('🔌 Store WebSocket disconnected')
    })
    
    // Listen for count updates instead of individual items
    socket.value.on('prediction_count_updated', (data) => {
      stats.value.total_predictions = data.count
      lastUpdated.value = new Date()
      console.log('📊 Store: Prediction count updated to:', data.count)
    })
    
    socket.value.on('alert_count_updated', (data) => {
      stats.value.total_alerts = data.count
      lastUpdated.value = new Date()
      console.log('🚨 Store: Alert count updated to:', data.count)
    })
    
    socket.value.on('maintenance_alert_count_updated', (data) => {
      stats.value.maintenance_alerts = data.count
      lastUpdated.value = new Date()
      console.log('🔧 Store: Maintenance alert count updated to:', data.count)
    })
    
    socket.value.on('normal_status_count_updated', (data) => {
      stats.value.normal_status = data.count
      lastUpdated.value = new Date()
      console.log('✅ Store: Normal status count updated to:', data.count)
    })
    
    socket.value.on('high_severity_count_updated', (data) => {
      stats.value.high_severity_alerts = data.count
      lastUpdated.value = new Date()
      console.log('🔴 Store: High severity alert count updated to:', data.count)
    })
    
    socket.value.on('medium_severity_count_updated', (data) => {
      stats.value.medium_severity_alerts = data.count
      lastUpdated.value = new Date()
      console.log('🟡 Store: Medium severity alert count updated to:', data.count)
    })
    
    socket.value.on('low_severity_count_updated', (data) => {
      stats.value.low_severity_alerts = data.count
      lastUpdated.value = new Date()
      console.log('🟢 Store: Low severity alert count updated to:', data.count)
    })
    
    socket.value.on('analytics_count_updated', (data) => {
      stats.value.total_analytics = data.count
      lastUpdated.value = new Date()
      console.log('📈 Store: Analytics count updated to:', data.count)
    })
    
    // Listen for new analytics/diagram data
    socket.value.on('new_analytics_data', (data) => {
      // Check if analytics data already exists to avoid duplicates
      const exists = analytics.value.some(a => {
        if (a._id && data._id) {
          return a._id === data._id
        }
        // If no _id, use combination of fields that should be unique
        return a.machine_id === data.machine_id && 
               a.timestamp === data.timestamp
      })
      
      if (!exists) {
        analytics.value.unshift(data)
        // Keep only recent analytics data for UI performance
        if (analytics.value.length > 50) {
          analytics.value = analytics.value.slice(0, 50)
        }
      }
      lastUpdated.value = new Date()
      console.log('📈 Store: New analytics data received:', data.machine_id, exists ? '(duplicate skipped)' : '(added)')
    })
    
    socket.value.on('new_diagram_data', (data) => {
      // Alias for analytics data - same handler
      // Check if analytics data already exists to avoid duplicates
      const exists = analytics.value.some(a => {
        if (a._id && data._id) {
          return a._id === data._id
        }
        return a.machine_id === data.machine_id && 
               a.timestamp === data.timestamp
      })
      
      if (!exists) {
        analytics.value.unshift(data)
        if (analytics.value.length > 50) {
          analytics.value = analytics.value.slice(0, 50)
        }
      }
      lastUpdated.value = new Date()
      console.log('📊 Store: New diagram data received:', data.machine_id, exists ? '(duplicate skipped)' : '(added)')
    })
    
    // Still listen for individual items for list updates
    socket.value.on('new_prediction', (data) => {
      // Check if prediction already exists to avoid duplicates
      // Use _id if available, otherwise use combination of machine_id + timestamp + prediction
      const exists = predictions.value.some(p => {
        if (p._id && data._id) {
          return p._id === data._id
        }
        // If no _id, use combination of fields that should be unique
        return p.machine_id === data.machine_id && 
               p.timestamp === data.timestamp && 
               p.prediction === data.prediction
      })
      
      if (!exists) {
        predictions.value.unshift(data)
        if (predictions.value.length > 200) {
          predictions.value = predictions.value.slice(0, 200)
        }
      }
      lastUpdated.value = new Date()
      console.log('📊 Store: New prediction received:', data.machine_id, exists ? '(duplicate skipped)' : '(added)')
    })
    
    socket.value.on('new_alert', (alert) => {
      // Check if alert already exists to avoid duplicates
      // Use _id if available, otherwise use combination of machine_id + timestamp + message
      const exists = alerts.value.some(a => {
        if (a._id && alert._id) {
          return a._id === alert._id
        }
        // If no _id, use combination of fields that should be unique
        return a.machine_id === alert.machine_id && 
               a.timestamp === alert.timestamp && 
               (a.message === alert.message || a.type === alert.type)
      })
      
      if (!exists) {
        alerts.value.unshift(alert)
        if (alerts.value.length > 100) {
          alerts.value = alerts.value.slice(0, 100)
        }
      }
      lastUpdated.value = new Date()
      console.log('🚨 Store: New alert received:', alert.message || alert.type, exists ? '(duplicate skipped)' : '(added)')
    })
    
    socket.value.on('new_sensor_data', (data) => {
      lastUpdated.value = new Date()
      console.log('📡 Store: New sensor data:', data.machine_id)
    })
    
    // Backup: Sync counts every 30 seconds to ensure accuracy
    setInterval(() => {
      if (realtimeConnected.value) {
        refreshCounts()
        removeDuplicates() // Also clean duplicates periodically
        
        // Auto-refresh analytics every 2 minutes to keep data fresh
        const now = new Date()
        const lastAnalyticsUpdate = lastUpdated.value
        const timeDiff = now - lastAnalyticsUpdate
        if (timeDiff > 120000) { // 2 minutes
          loadAnalytics()
          console.log('🔄 Auto-refreshed analytics data')
        }
        
        console.log('🔄 Periodic count sync and cleanup completed')
      }
    }, 30000)
  }

  const loadDashboardData = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.get('/api/dashboard_data')
      const data = response.data
      
      if (data.status === 'success') {
        // Replace arrays completely to avoid duplicates from WebSocket
        predictions.value = data.predictions
        alerts.value = data.alerts
        analytics.value = data.analytics || [] // Load analytics if available
        stats.value = data.stats
        lastUpdated.value = new Date()
        console.log('📊 Dashboard loaded - Predictions:', data.stats.total_predictions, 'Alerts:', data.stats.total_alerts, 'Analytics:', data.stats.total_analytics || 0)
        console.log('📝 UI arrays reset - Predictions:', predictions.value.length, 'Alerts:', alerts.value.length, 'Analytics:', analytics.value.length)
      }
    } catch (err) {
      error.value = 'Failed to load dashboard data'
      console.error('Error loading dashboard data:', err)
    } finally {
      loading.value = false
    }
  }

  const loadPredictions = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.get('/api/predictions')
      const data = response.data
      
      if (data.status === 'success') {
        // Replace predictions array to avoid duplicates
        predictions.value = data.predictions
        console.log('📊 Predictions loaded:', predictions.value.length, 'items')
      }
    } catch (err) {
      error.value = 'Failed to load predictions'
      console.error('Error loading predictions:', err)
    } finally {
      loading.value = false
    }
  }

  const loadAlerts = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.get('/api/alerts')
      const data = response.data
      
      if (data.status === 'success') {
        // Replace alerts array to avoid duplicates
        alerts.value = data.alerts
        console.log('🚨 Alerts loaded:', alerts.value.length, 'items')
      }
    } catch (err) {
      error.value = 'Failed to load alerts'
      console.error('Error loading alerts:', err)
    } finally {
      loading.value = false
    }
  }

  const loadAnalytics = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.get('/api/enthalpy_diagram_data')
      const data = response.data
      
      if (data.status === 'success') {
        // Replace analytics array to avoid duplicates
        analytics.value = data.diagram_data || []
        console.log('📈 Analytics loaded:', analytics.value.length, 'items')
      }
    } catch (err) {
      error.value = 'Failed to load analytics data'
      console.error('Error loading analytics data:', err)
    } finally {
      loading.value = false
    }
  }

  const refreshCounts = async () => {
    try {
      const [predResponse, alertResponse, analyticsResponse, maintenanceResponse, normalResponse] = await Promise.all([
        axios.get('/api/predictions/count'),
        axios.get('/api/alerts/count'),
        axios.get('/api/analytics/count').catch(() => ({ data: { status: 'error' } })),
        axios.get('/api/alerts/count/maintenance').catch(() => ({ data: { status: 'error' } })),
        axios.get('/api/alerts/count/normal').catch(() => ({ data: { status: 'error' } }))
      ])
      
      if (predResponse.data.status === 'success') {
        stats.value.total_predictions = predResponse.data.count
      }
      
      if (alertResponse.data.status === 'success') {
        stats.value.total_alerts = alertResponse.data.count
      }
      
      if (analyticsResponse.data.status === 'success') {
        stats.value.total_analytics = analyticsResponse.data.count
      }
      
      if (maintenanceResponse.data.status === 'success') {
        stats.value.maintenance_alerts = maintenanceResponse.data.count
      }
      
      if (normalResponse.data.status === 'success') {
        stats.value.normal_status = normalResponse.data.count
      }
      
      // If specific endpoints are not available, calculate from current local data
      if (maintenanceResponse.data.status === 'error' || normalResponse.data.status === 'error') {
        await calculateAlertCounts()
      }
      
      lastUpdated.value = new Date()
      console.log('📊 Counts refreshed - Predictions:', stats.value.total_predictions, 'Alerts:', stats.value.total_alerts, 'Analytics:', stats.value.total_analytics, 'Maintenance:', stats.value.maintenance_alerts, 'Normal:', stats.value.normal_status)
    } catch (err) {
      console.warn('Failed to refresh counts:', err)
    }
  }

  // Calculate maintenance and normal alert counts from local data
  const calculateAlertCounts = async () => {
    try {
      // Get all alerts to calculate proportions
      const response = await axios.get('/api/alerts?limit=1000') // Get more alerts for better calculation
      if (response.data.status === 'success') {
        const allAlerts = response.data.alerts
        
        const maintenanceCount = allAlerts.filter(alert => 
          alert.severity === 'high' || 
          alert.type === 'maintenance' || 
          alert.prediction === 'failure' ||
          (alert.message && alert.message.toLowerCase().includes('maintenance'))
        ).length
        
        const normalCount = allAlerts.filter(alert => 
          alert.severity === 'low' || 
          alert.type === 'normal' || 
          alert.prediction === 'normal' ||
          (alert.message && alert.message.toLowerCase().includes('normal'))
        ).length

        // Calculate severity counts
        const highSeverityCount = allAlerts.filter(alert => alert.severity === 'high').length
        const mediumSeverityCount = allAlerts.filter(alert => alert.severity === 'medium').length
        const lowSeverityCount = allAlerts.filter(alert => alert.severity === 'low').length
        
        // Calculate proportions and apply to total count
        const totalSample = allAlerts.length
        if (totalSample > 0) {
          const maintenanceRatio = maintenanceCount / totalSample
          const normalRatio = normalCount / totalSample
          const highSeverityRatio = highSeverityCount / totalSample
          const mediumSeverityRatio = mediumSeverityCount / totalSample
          const lowSeverityRatio = lowSeverityCount / totalSample
          
          stats.value.maintenance_alerts = Math.round(stats.value.total_alerts * maintenanceRatio)
          stats.value.normal_status = Math.round(stats.value.total_alerts * normalRatio)
          stats.value.high_severity_alerts = Math.round(stats.value.total_alerts * highSeverityRatio)
          stats.value.medium_severity_alerts = Math.round(stats.value.total_alerts * mediumSeverityRatio)
          stats.value.low_severity_alerts = Math.round(stats.value.total_alerts * lowSeverityRatio)
          
          console.log('📊 Calculated alert counts from sample - Maintenance:', stats.value.maintenance_alerts, 'Normal:', stats.value.normal_status, 'High:', stats.value.high_severity_alerts, 'Medium:', stats.value.medium_severity_alerts, 'Low:', stats.value.low_severity_alerts)
        }
      }
    } catch (err) {
      console.warn('Failed to calculate alert counts:', err)
    }
  }

  // Helper function to remove duplicates from arrays
  const removeDuplicates = () => {
    // Remove duplicate predictions based on _id or combination of unique fields
    const uniquePredictions = predictions.value.filter((pred, index, self) =>
      index === self.findIndex(p => {
        if (p._id && pred._id) {
          return p._id === pred._id
        }
        // If no _id, use combination of fields that should be unique
        return p.machine_id === pred.machine_id && 
               p.timestamp === pred.timestamp && 
               p.prediction === pred.prediction
      })
    )
    
    // Remove duplicate alerts based on _id or combination of unique fields
    const uniqueAlerts = alerts.value.filter((alert, index, self) =>
      index === self.findIndex(a => {
        if (a._id && alert._id) {
          return a._id === alert._id
        }
        // If no _id, use combination of fields that should be unique
        return a.machine_id === alert.machine_id && 
               a.timestamp === alert.timestamp && 
               (a.message === alert.message || a.type === alert.type)
      })
    )
    
    if (predictions.value.length !== uniquePredictions.length) {
      console.log('🧹 Removed', predictions.value.length - uniquePredictions.length, 'duplicate predictions')
      predictions.value = uniquePredictions
    }
    
    if (alerts.value.length !== uniqueAlerts.length) {
      console.log('🧹 Removed', alerts.value.length - uniqueAlerts.length, 'duplicate alerts')
      alerts.value = uniqueAlerts
    }
  }

  // Manual cleanup function for existing duplicates
  const cleanupDuplicates = () => {
    console.log('🧹 Starting manual cleanup of duplicates...')
    console.log('📊 Before cleanup - Predictions:', predictions.value.length, 'Alerts:', alerts.value.length)
    
    // More thorough cleanup for predictions
    const seenPredictions = new Set()
    const cleanPredictions = predictions.value.filter(pred => {
      // Create a unique key based on available data
      let key
      if (pred._id) {
        key = pred._id
      } else {
        key = `${pred.machine_id}-${pred.timestamp}-${pred.prediction}`
      }
      
      if (seenPredictions.has(key)) {
        return false // Remove duplicate
      }
      seenPredictions.add(key)
      return true // Keep unique
    })
    
    // More thorough cleanup for alerts
    const seenAlerts = new Set()
    const cleanAlerts = alerts.value.filter(alert => {
      // Create a unique key based on available data
      let key
      if (alert._id) {
        key = alert._id
      } else {
        key = `${alert.machine_id}-${alert.timestamp}-${alert.message || alert.type}`
      }
      
      if (seenAlerts.has(key)) {
        return false // Remove duplicate
      }
      seenAlerts.add(key)
      return true // Keep unique
    })
    
    const predRemoved = predictions.value.length - cleanPredictions.length
    const alertsRemoved = alerts.value.length - cleanAlerts.length
    
    predictions.value = cleanPredictions
    alerts.value = cleanAlerts
    
    console.log('✅ Cleanup complete - Removed:', predRemoved, 'duplicate predictions,', alertsRemoved, 'duplicate alerts')
    console.log('📊 After cleanup - Predictions:', predictions.value.length, 'Alerts:', alerts.value.length)
    
    return { predRemoved, alertsRemoved }
  }

  const getSystemStatus = async () => {
    try {
      const response = await axios.get('/api/system_status')
      return response.data
    } catch (err) {
      console.error('Error getting system status:', err)
      return null
    }
  }

  const getEnthalpyDiagramData = async () => {
    try {
      const response = await axios.get('/api/enthalpy_diagram_data')
      return response.data
    } catch (err) {
      console.error('Error getting enthalpy diagram data:', err)
      return null
    }
  }

  // Get detailed stats for dashboard
  const getDetailedStats = () => {
    const detailedStats = {
      totalPredictions: predictionCount.value,
      maintenanceAlerts: maintenanceAlertCount.value,
      normalStatus: normalStatusCount.value,
      avgConfidence: avgConfidence.value,
      totalAlerts: alertCount.value,
      highSeverityAlerts: highSeverityAlerts.value.length,
      recentPredictionsCount: recentPredictions.value.length,
      recentAlertsCount: recentAlerts.value.length,
      lastUpdated: lastUpdated.value,
      realtimeConnected: realtimeConnected.value
    }
    
    console.log('📊 Detailed Stats Debug:', {
      'Database Counts': {
        predictionCount: predictionCount.value,
        alertCount: alertCount.value,
        maintenanceAlerts: maintenanceAlertCount.value,
        normalStatus: normalStatusCount.value
      },
      'Local Array Lengths': {
        predictionsArray: predictions.value.length,
        alertsArray: alerts.value.length,
        highSeverityLocal: highSeverityAlerts.value.length
      },
      'Raw Stats Object': stats.value
    })
    
    return detailedStats
  }

  // Initialize store with real database counts
  const initializeStore = async () => {
    console.log('🏪 Initializing store with real database counts...')
    
    // Load dashboard data first to get initial stats and data
    await loadDashboardData()
    
    // Load analytics data
    await loadAnalytics()
    
    // Remove any potential duplicates from initial load using thorough cleanup
    cleanupDuplicates()
    
    // Then sync with fresh counts from dedicated endpoints
    await refreshCounts()
    
    // Finally initialize WebSocket for real-time updates
    initializeSocket()
    
    console.log('✅ Store initialization complete!')
  }

  // Force refresh all data and counts
  const forceRefreshAll = async () => {
    console.log('🔄 Force refreshing all data and counts...')
    
    // Refresh counts first
    await refreshCounts()
    
    // Clean duplicates
    cleanupDuplicates()
    
    // Recalculate alert counts if needed
    await calculateAlertCounts()
    
    console.log('✅ Force refresh complete!')
    console.log('📊 Current Stats:', {
      predictionCount: predictionCount.value,
      alertCount: alertCount.value,
      maintenanceAlerts: maintenanceAlertCount.value,
      normalStatus: normalStatusCount.value,
      localArrays: {
        predictions: predictions.value.length,
        alerts: alerts.value.length
      }
    })
  }

  return {
    // State
    predictions,
    alerts,
    analytics,
    stats,
    enhancedStats,
    socket,
    loading,
    error,
    lastUpdated,
    realtimeConnected,
    
    // Getters
    recentPredictions,
    recentAlerts,
    recentAnalytics,
    uniqueMachines,
    latestAnalyticsByMachine,
    averageCOP,
    highSeverityAlerts,
    mediumSeverityAlerts,
    lowSeverityAlerts,
    maintenanceAlerts,
    normalStatusAlerts,
    avgConfidence,
    predictionCount,
    alertCount,
    analyticsCount,
    maintenanceAlertCount,
    normalStatusCount,
    highSeverityCount,
    mediumSeverityCount,
    lowSeverityCount,
    
    // Actions
    initializeSocket,
    loadDashboardData,
    loadPredictions,
    loadAlerts,
    loadAnalytics,
    refreshCounts,
    calculateAlertCounts,
    removeDuplicates,
    cleanupDuplicates,
    getSystemStatus,
    getEnthalpyDiagramData,
    getDetailedStats,
    initializeStore,
    forceRefreshAll
  }
})
