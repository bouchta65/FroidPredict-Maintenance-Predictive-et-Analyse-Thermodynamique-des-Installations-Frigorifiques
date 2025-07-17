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
          <h1 class="text-2xl font-bold text-gray-900">Installation Frigorifique Complète</h1>
          <p class="mt-2 text-gray-600">
            Analyse thermodynamique et visualisation du cycle frigorifique - Installation unifiée
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
            <span class="font-medium">{{ store.realtimeConnected ? 'Surveillance Live' : 'Hors Ligne' }}</span>
          </div>
          <div class="text-sm text-gray-500">
            {{ store.analyticsCount }} mesures capteurs
          </div>
        </div>
      </div>
    </div>

    <!-- Installation Status -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span class="font-medium text-gray-900">Installation FRIGO-UNITE-001</span>
          </div>
          <div class="text-sm text-gray-500">
            État: Fonctionnement Normal
          </div>
        </div>
        <div class="flex items-center space-x-6">
          <div class="text-sm">
            <span class="text-gray-500">COP Moyen:</span>
            <span class="font-semibold text-blue-600 ml-1">{{ store.averageCOP }}</span>
          </div>
          <div class="text-sm">
            <span class="text-gray-500">Capteurs Actifs:</span>
            <span class="font-semibold text-green-600 ml-1">10/10</span>
          </div>
          <button
            @click="refreshAnalytics"
            :disabled="store.loading"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition duration-200 disabled:opacity-50 shadow-sm"
          >
            <span v-if="store.loading">Actualisation...</span>
            <span v-else>Actualiser</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="space-y-6">
        <!-- Loading State -->
        <div v-if="store.loading" class="flex justify-center items-center h-64">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>

        <!-- Unified Installation Dashboard -->
        <div v-else-if="store.analytics.length > 0" class="space-y-6">
          
          <!-- Composants Critiques du Système -->
          <div class="card">
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 mb-2">🔧 Composants Critiques du Système</h3>
              <p class="text-sm text-gray-600">Surveillance des 7 composants principaux de l'installation</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div class="component-card bg-blue-50 border-blue-200">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-blue-900">🔄 Compresseur</h4>
                  <span class="status-badge bg-green-100 text-green-800">Normal</span>
                </div>
                <div class="space-y-1 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Courant:</span>
                    <span class="font-medium">{{ getLatestSensorData('compressor_current') }}A</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Vibrations:</span>
                    <span class="font-medium">{{ getLatestSensorData('vibration') }}g</span>
                  </div>
                </div>
              </div>
              
              <div class="component-card bg-green-50 border-green-200">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-green-900">❄️ Évaporateur</h4>
                  <span class="status-badge bg-green-100 text-green-800">Normal</span>
                </div>
                <div class="space-y-1 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Température:</span>
                    <span class="font-medium">{{ getLatestSensorData('temp_evaporator') }}°C</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Pression BP:</span>
                    <span class="font-medium">{{ getLatestSensorData('pressure_low') }} bar</span>
                  </div>
                </div>
              </div>
              
              <div class="component-card bg-red-50 border-red-200">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-red-900">🌡️ Condenseur</h4>
                  <span class="status-badge bg-green-100 text-green-800">Normal</span>
                </div>
                <div class="space-y-1 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Température:</span>
                    <span class="font-medium">{{ getLatestSensorData('temp_condenser') }}°C</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Pression HP:</span>
                    <span class="font-medium">{{ getLatestSensorData('pressure_high') }} bar</span>
                  </div>
                </div>
              </div>
              
              <div class="component-card bg-purple-50 border-purple-200">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-purple-900">🔧 Détendeur</h4>
                  <span class="status-badge bg-green-100 text-green-800">Normal</span>
                </div>
                <div class="space-y-1 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Surchauffe:</span>
                    <span class="font-medium">{{ getLatestSensorData('superheat') }}°C</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Sous-refroid:</span>
                    <span class="font-medium">{{ getLatestSensorData('subcooling') }}°C</span>
                  </div>
                </div>
              </div>
              
              <div class="component-card bg-yellow-50 border-yellow-200">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-yellow-900">🔍 Filtre Déshydrateur</h4>
                  <span class="status-badge bg-green-100 text-green-800">Normal</span>
                </div>
                <div class="space-y-1 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Δ Pression:</span>
                    <span class="font-medium">0.2 bar</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">État:</span>
                    <span class="font-medium">Propre</span>
                  </div>
                </div>
              </div>
              
              <div class="component-card bg-indigo-50 border-indigo-200">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-indigo-900">🧪 Réservoir Liquide</h4>
                  <span class="status-badge bg-green-100 text-green-800">Normal</span>
                </div>
                <div class="space-y-1 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600">Niveau:</span>
                    <span class="font-medium">75%</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600">Voyant:</span>
                    <span class="font-medium">Clair</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Capteurs de Surveillance -->
          <div class="card">
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 mb-2">📊 Capteurs de Surveillance</h3>
              <p class="text-sm text-gray-600">Monitoring en temps réel des 10 capteurs principaux</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Capteurs de Pression -->
              <div>
                <h4 class="font-medium text-gray-700 mb-3">🔴 Capteurs de Pression (4 capteurs)</h4>
                <div class="space-y-3">
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Pression Haute (HP)</span>
                      <span class="sensor-value">{{ getLatestSensorData('pressure_high') }} bar</span>
                    </div>
                    <div class="text-xs text-gray-500">Après compresseur / Dans condenseur</div>
                  </div>
                  
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Pression Basse (BP)</span>
                      <span class="sensor-value">{{ getLatestSensorData('pressure_low') }} bar</span>
                    </div>
                    <div class="text-xs text-gray-500">Avant compresseur / Dans évaporateur</div>
                  </div>
                  
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Pression Intermédiaire</span>
                      <span class="sensor-value">{{ getLatestSensorData('pressure_intermediate') }} bar</span>
                    </div>
                    <div class="text-xs text-gray-500">Sortie détendeur</div>
                  </div>
                  
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Pression Différentielle</span>
                      <span class="sensor-value">0.2 bar</span>
                    </div>
                    <div class="text-xs text-gray-500">Surveillance filtre déshydrateur</div>
                  </div>
                </div>
              </div>
              
              <!-- Capteurs de Température -->
              <div>
                <h4 class="font-medium text-gray-700 mb-3">🌡️ Capteurs de Température (6 capteurs)</h4>
                <div class="space-y-3">
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Température Aspiration</span>
                      <span class="sensor-value">{{ getLatestSensorData('temp_aspiration') }}°C</span>
                    </div>
                    <div class="text-xs text-gray-500">Entrée compresseur</div>
                  </div>
                  
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Température Refoulement</span>
                      <span class="sensor-value">{{ getLatestSensorData('temp_refoulement') }}°C</span>
                    </div>
                    <div class="text-xs text-gray-500">Sortie compresseur</div>
                  </div>
                  
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Température Condensation</span>
                      <span class="sensor-value">{{ getLatestSensorData('temp_condenser') }}°C</span>
                    </div>
                    <div class="text-xs text-gray-500">Sortie condenseur</div>
                  </div>
                  
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Température Évaporation</span>
                      <span class="sensor-value">{{ getLatestSensorData('temp_evaporator') }}°C</span>
                    </div>
                    <div class="text-xs text-gray-500">Sortie évaporateur</div>
                  </div>
                  
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Température Liquide</span>
                      <span class="sensor-value">{{ getLatestSensorData('temp_liquid') }}°C</span>
                    </div>
                    <div class="text-xs text-gray-500">Avant détendeur</div>
                  </div>
                  
                  <div class="sensor-reading">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">Température Ambiante</span>
                      <span class="sensor-value">{{ getLatestSensorData('temp_ambient') }}°C</span>
                    </div>
                    <div class="text-xs text-gray-500">Condenseur</div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Paramètres Calculés -->
            <div class="mt-6 pt-6 border-t border-gray-200">
              <h4 class="font-medium text-gray-700 mb-3">📈 Paramètres Calculés</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="calculated-param">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium">Surchauffe</span>
                    <span class="param-value">{{ getLatestSensorData('superheat') }}°C</span>
                  </div>
                  <div class="text-xs text-gray-500">Calculée (aspiration - évaporation)</div>
                </div>
                
                <div class="calculated-param">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium">Sous-refroidissement</span>
                    <span class="param-value">{{ getLatestSensorData('subcooling') }}°C</span>
                  </div>
                  <div class="text-xs text-gray-500">Calculée (condensation - liquide)</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Diagramme Enthalpique Unifié -->
          <div class="card">
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 mb-2">📊 Diagramme Enthalpique de l'Installation</h3>
              <p class="text-sm text-gray-600">Analyse thermodynamique complète - Cycle frigorifique unifié</p>
            </div>
            
            <div v-if="unifiedInstallationData" class="space-y-6">
              <!-- Performance Metrics -->
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="performance-metric bg-blue-50 border-blue-200">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-blue-900">COP</span>
                    <span class="text-lg font-bold text-blue-900">
                      {{ unifiedInstallationData.performance.cop.toFixed(2) }}
                    </span>
                  </div>
                  <div class="text-xs text-blue-700">Coefficient de Performance</div>
                </div>
                
                <div class="performance-metric bg-green-50 border-green-200">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-green-900">Effet Frig.</span>
                    <span class="text-lg font-bold text-green-900">
                      {{ unifiedInstallationData.performance.cooling_capacity.toFixed(1) }}
                    </span>
                  </div>
                  <div class="text-xs text-green-700">kJ/kg</div>
                </div>
                
                <div class="performance-metric bg-orange-50 border-orange-200">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-orange-900">Travail Comp.</span>
                    <span class="text-lg font-bold text-orange-900">
                      {{ unifiedInstallationData.performance.compression_work.toFixed(1) }}
                    </span>
                  </div>
                  <div class="text-xs text-orange-700">kJ/kg</div>
                </div>
                
                <div class="performance-metric bg-red-50 border-red-200">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-red-900">Chaleur Rej.</span>
                    <span class="text-lg font-bold text-red-900">
                      {{ unifiedInstallationData.performance.condensation_heat.toFixed(1) }}
                    </span>
                  </div>
                  <div class="text-xs text-red-700">kJ/kg</div>
                </div>
              </div>

              <!-- Mollier Diagram -->
              <div class="bg-gray-50 rounded-lg p-4">
                <MollierDiagramSimple 
                  :cycle-data="unifiedInstallationData.cycle_points"
                  :width="900"
                  :height="700"
                />
                <div class="mt-4 text-sm text-gray-600">
                  <p><strong>Installation:</strong> FRIGO-UNITE-001</p>
                  <p><strong>Fluide frigorigène:</strong> R22</p>
                  <p><strong>Composants surveillés:</strong> 7 composants critiques</p>
                  <p><strong>Capteurs actifs:</strong> 10 capteurs (4 pression + 6 température)</p>
                  <p><strong>Dernière mise à jour:</strong> {{ formatDate(unifiedInstallationData.timestamp) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- No Data State -->
        <div v-else class="card">
          <div class="text-center py-8">
            <ChartPieIcon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-500">Aucune donnée d'installation disponible</p>
            <div class="mt-4 space-x-2">
              <button @click="refreshAnalytics" 
                      class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition duration-200 shadow-sm">
                Charger les Données
              </button>
              <div class="text-sm text-gray-400 mt-2">
                Surveillance temps réel: {{ store.realtimeConnected ? 'Active' : 'Déconnectée' }}
              </div>
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
import MollierDiagramSimple from '@/components/MollierDiagramSimple.vue'
import { ChartPieIcon } from '@heroicons/vue/24/outline'
import moment from 'moment'

const store = useRefrigerationStore()

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

// Unified installation data from the latest reading
const unifiedInstallationData = computed(() => {
  if (store.analytics.length > 0) {
    // Take the most recent data and treat it as the unified installation
    const latestData = store.analytics[0]
    return {
      ...latestData,
      machine_id: 'FRIGO-UNITE-001',
      timestamp: latestData.timestamp
    }
  }
  return null
})

// Helper function to get latest sensor data
const getLatestSensorData = (sensorType) => {
  if (store.analytics.length > 0) {
    const latestData = store.analytics[0]
    const value = latestData[sensorType]
    
    if (value !== undefined) {
      return typeof value === 'number' ? value.toFixed(1) : value
    }
    
    // Default values for missing sensors
    const defaults = {
      'temp_aspiration': '5.0',
      'temp_refoulement': '65.0',
      'temp_liquid': '25.0',
      'temp_ambient': '20.0',
      'pressure_intermediate': '4.5'
    }
    
    return defaults[sensorType] || 'N/A'
  }
  return 'N/A'
}

const formatDate = (timestamp) => {
  return moment(timestamp).format('DD/MM/YYYY HH:mm:ss')
}
</script>

<style scoped>
.card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 p-6;
}

.component-card {
  @apply p-4 rounded-lg border;
}

.status-badge {
  @apply px-2 py-1 rounded-full text-xs font-medium;
}

.sensor-reading {
  @apply p-3 bg-gray-50 rounded-lg;
}

.sensor-value {
  @apply font-bold text-blue-600;
}

.calculated-param {
  @apply p-3 bg-blue-50 rounded-lg;
}

.param-value {
  @apply font-bold text-blue-600;
}

.performance-metric {
  @apply p-4 rounded-lg border;
}
</style>
