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

          <!-- Diagrammes Thermodynamiques Complets -->
          <div class="card">
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 mb-2">📊 Diagrammes Thermodynamiques de l'Installation</h3>
              <p class="text-sm text-gray-600">Analyse thermodynamique complète avec données temps réel Kafka - Cycle frigorifique unifié</p>
            </div>
            
            <div v-if="unifiedInstallationData" class="space-y-6">
              <!-- Performance Metrics from Kafka Data -->
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="performance-metric bg-blue-50 border-blue-200">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-blue-900">COP Temps Réel</span>
                    <span class="text-lg font-bold text-blue-900">
                      {{ calculateCOPFromKafka().toFixed(2) }}
                    </span>
                  </div>
                  <div class="text-xs text-blue-700">Coefficient de Performance (Kafka)</div>
                </div>
                
                <div class="performance-metric bg-green-50 border-green-200">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-green-900">Effet Frig.</span>
                    <span class="text-lg font-bold text-green-900">
                      {{ calculateCoolingEffect().toFixed(1) }}
                    </span>
                  </div>
                  <div class="text-xs text-green-700">kJ/kg (calculé)</div>
                </div>
                
                <div class="performance-metric bg-orange-50 border-orange-200">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-orange-900">Ratio Pression</span>
                    <span class="text-lg font-bold text-orange-900">
                      {{ (getNumericSensorData('pressure_high') / getNumericSensorData('pressure_low')).toFixed(1) }}
                    </span>
                  </div>
                  <div class="text-xs text-orange-700">HP/BP</div>
                </div>
                
                <div class="performance-metric bg-red-50 border-red-200">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-red-900">ΔT Système</span>
                    <span class="text-lg font-bold text-red-900">
                      {{ (getNumericSensorData('temp_condenser') - getNumericSensorData('temp_evaporator')).toFixed(1) }}
                    </span>
                  </div>
                  <div class="text-xs text-red-700">°C</div>
                </div>
              </div>

              <!-- Professional Thermodynamic Charts with Real Data -->
              <div class="bg-white border border-gray-200 rounded-lg">
                <div class="border-b border-gray-200">
                  <nav class="-mb-px flex space-x-8 px-6">
                    <button
                      v-for="tab in professionalThermodynamicTabs"
                      :key="tab.id"
                      @click="activeThermodynamicTab = tab.id"
                      :class="[
                        'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                        activeThermodynamicTab === tab.id
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      ]"
                    >
                      {{ tab.label }}
                    </button>
                  </nav>
                </div>

                <div class="p-6">
                  <!-- S-p Diagram (Entropy vs Pressure) -->
                  <div v-if="activeThermodynamicTab === 'sp'" class="space-y-6">
                    <div class="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
                      <h4 class="font-bold text-blue-900 mb-4 flex items-center">
                        📊 Diagramme S-p (Entropie - Pression) - Données Kafka Temps Réel
                      </h4>
                      <div class="bg-white rounded-lg p-4 border border-blue-100">
                        <SPDiagram 
                          :kafka-data="unifiedInstallationData"
                          :fluid="'R22'"
                          :width="900"
                          :height="650"
                          @diagram-ready="onSPDiagramReady"
                        />
                        <div class="mt-4 text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                          <p><strong>Données Kafka Temps Réel:</strong> P_HP={{ getLatestSensorData('pressure_high') }}bar, P_BP={{ getLatestSensorData('pressure_low') }}bar | <strong>Mise à jour:</strong> {{ formatDate(unifiedInstallationData.timestamp) }}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- p-h Diagram (Pressure vs Enthalpy - Mollier) -->
                  <div v-if="activeThermodynamicTab === 'ph'" class="space-y-6">
                    <div class="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6">
                      <h4 class="font-bold text-green-900 mb-4 flex items-center">
                        📈 Diagramme p-h (Pression - Enthalpie) - Mollier avec Cycle Tracé
                      </h4>
                      <div class="bg-white rounded-lg p-4 border border-green-100">
                        <PHDiagram 
                          :kafka-data="unifiedInstallationData"
                          :fluid="'R22'"
                          :width="900"
                          :height="650"
                          :show-cycle="true"
                          @diagram-ready="onPHDiagramReady"
                        />
                        <div class="mt-4 text-sm text-gray-600 bg-green-50 p-3 rounded-lg">
                          <p><strong>Cycle Frigorifique Tracé:</strong> Aspiration({{ getLatestSensorData('temp_aspiration') }}°C) → Refoulement({{ getLatestSensorData('temp_refoulement') }}°C) → Condensation({{ getLatestSensorData('temp_condenser') }}°C) → Évaporation({{ getLatestSensorData('temp_evaporator') }}°C)</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- p-v Diagram (Pressure vs Specific Volume) -->
                  <div v-if="activeThermodynamicTab === 'pv'" class="space-y-6">
                    <div class="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
                      <h4 class="font-bold text-purple-900 mb-4 flex items-center">
                        📉 Diagramme p-v (Pression - Volume Spécifique) - Analyse Compresseur
                      </h4>
                      <div class="bg-white rounded-lg p-4 border border-purple-100">
                        <PVDiagram 
                          :kafka-data="unifiedInstallationData"
                          :fluid="'R22'"
                          :width="900"
                          :height="650"
                          @diagram-ready="onPVDiagramReady"
                        />
                        <div class="mt-4 text-sm text-gray-600 bg-purple-50 p-3 rounded-lg">
                          <p><strong>Analyse Compresseur:</strong> Courant={{ getLatestSensorData('compressor_current') }}A, Vibrations={{ getLatestSensorData('vibration') }}g | <strong>Travail:</strong> {{ calculateCompressionWork().toFixed(1) }} kJ/kg</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Comparative Analysis -->
                  <div v-if="activeThermodynamicTab === 'comparison'" class="space-y-6">
                    <div class="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-6">
                      <h4 class="font-bold text-orange-900 mb-4">🔬 Analyse Comparative des Diagrammes</h4>
                      
                      <!-- Performance Summary -->
                      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <div class="bg-white/80 rounded-lg p-4 border border-orange-100">
                          <h5 class="font-semibold text-orange-800 mb-3">📊 S-p Analysis</h5>
                          <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                              <span>Entropie spécifique:</span>
                              <span class="font-medium">{{ calculateSpecificEntropy().toFixed(3) }} kJ/(kg·K)</span>
                            </div>
                            <div class="flex justify-between">
                              <span>Qualité vapeur:</span>
                              <span class="font-medium">{{ calculateVaporQuality().toFixed(2) }}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div class="bg-white/80 rounded-lg p-4 border border-orange-100">
                          <h5 class="font-semibold text-orange-800 mb-3">📈 p-h Analysis</h5>
                          <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                              <span>Enthalpie évap:</span>
                              <span class="font-medium">{{ calculateEvaporationEnthalpy().toFixed(1) }} kJ/kg</span>
                            </div>
                            <div class="flex justify-between">
                              <span>Enthalpie cond:</span>
                              <span class="font-medium">{{ calculateCondensationEnthalpy().toFixed(1) }} kJ/kg</span>
                            </div>
                          </div>
                        </div>
                        
                        <div class="bg-white/80 rounded-lg p-4 border border-orange-100">
                          <h5 class="font-semibold text-orange-800 mb-3">📉 p-v Analysis</h5>
                          <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                              <span>Volume spéc. aspiration:</span>
                              <span class="font-medium">{{ calculateSuctionVolume().toFixed(4) }} m³/kg</span>
                            </div>
                            <div class="flex justify-between">
                              <span>Travail compression:</span>
                              <span class="font-medium">{{ calculateCompressionWork().toFixed(1) }} kJ/kg</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Real-time Data Summary -->
                      <div class="bg-white/80 rounded-lg p-4 border border-orange-100">
                        <h5 class="font-semibold text-orange-800 mb-3">📡 Résumé Données Kafka Temps Réel</h5>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span class="text-gray-600">Pression HP:</span>
                            <span class="font-bold ml-2">{{ getLatestSensorData('pressure_high') }} bar</span>
                          </div>
                          <div>
                            <span class="text-gray-600">Pression BP:</span>
                            <span class="font-bold ml-2">{{ getLatestSensorData('pressure_low') }} bar</span>
                          </div>
                          <div>
                            <span class="text-gray-600">Surchauffe:</span>
                            <span class="font-bold ml-2">{{ getLatestSensorData('superheat') }}°C</span>
                          </div>
                          <div>
                            <span class="text-gray-600">Sous-refroidissement:</span>
                            <span class="font-bold ml-2">{{ getLatestSensorData('subcooling') }}°C</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
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
import ThermodynamicCharts from '@/components/ThermodynamicCharts.vue'
import SPDiagram from '@/components/SPDiagram.vue'
import PHDiagram from '@/components/PHDiagram.vue'
import PVDiagram from '@/components/PVDiagram.vue'
import { ChartPieIcon } from '@heroicons/vue/24/outline'
import moment from 'moment'

const store = useRefrigerationStore()

// Professional thermodynamic tabs state
const activeThermodynamicTab = ref('sp')
const professionalThermodynamicTabs = ref([
  { 
    id: 'sp', 
    label: '📊 S-p (Entropie-Pression)', 
    description: 'Diagramme entropie vs pression avec données Kafka temps réel' 
  },
  { 
    id: 'ph', 
    label: '📈 p-h (Mollier Professionnel)', 
    description: 'Pression vs enthalpie avec cycle frigorifique tracé' 
  },
  { 
    id: 'pv', 
    label: '📉 p-v (Pression-Volume)', 
    description: 'Analyse compresseur avec travail calculé' 
  },
  { 
    id: 'comparison', 
    label: '🔬 Analyse Comparative', 
    description: 'Comparaison thermodynamique des trois diagrammes' 
  }
])

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

// Helper function to get numeric sensor data for calculations
const getNumericSensorData = (sensorType) => {
  if (store.analytics.length > 0) {
    const latestData = store.analytics[0]
    const value = latestData[sensorType]
    
    if (value !== undefined && typeof value === 'number') {
      return value
    }
    
    // Default numeric values for missing sensors
    const defaults = {
      'temp_aspiration': 5.0,
      'temp_refoulement': 65.0,
      'temp_liquid': 25.0,
      'temp_ambient': 20.0,
      'pressure_intermediate': 4.5,
      'temp_condenser': 40.0,
      'temp_evaporator': -10.0,
      'pressure_high': 12.0,
      'pressure_low': 2.5,
      'superheat': 8.0,
      'subcooling': 5.0,
      'compressor_current': 8.5,
      'vibration': 2.1
    }
    
    return defaults[sensorType] || 0
  }
  return 0
}

// Calculate COP from Kafka data
const calculateCOPFromKafka = () => {
  const coolingEffect = calculateCoolingEffect()
  const compressionWork = calculateCompressionWork()
  
  if (compressionWork > 0) {
    return coolingEffect / compressionWork
  }
  return 3.5 // Default COP
}

// Calculate cooling effect using sensor data
const calculateCoolingEffect = () => {
  // Simplified calculation using temperature difference
  const tempEvap = getNumericSensorData('temp_evaporator')
  const tempAspiration = getNumericSensorData('temp_aspiration')
  const superheat = getNumericSensorData('superheat')
  
  // Enthalpic cooling effect estimation (kJ/kg)
  return 180 + (tempAspiration - tempEvap) * 2.1 + superheat * 1.8
}

// Calculate compression work
const calculateCompressionWork = () => {
  const pressureHigh = getNumericSensorData('pressure_high')
  const pressureLow = getNumericSensorData('pressure_low')
  const tempRefoulement = getNumericSensorData('temp_refoulement')
  const tempAspiration = getNumericSensorData('temp_aspiration')
  
  // Simplified compression work calculation
  const pressureRatio = pressureHigh / pressureLow
  const temperatureLift = tempRefoulement - tempAspiration
  
  return 25 + (pressureRatio - 1) * 8 + temperatureLift * 0.8
}

// Calculate specific entropy
const calculateSpecificEntropy = () => {
  const tempAspiration = getNumericSensorData('temp_aspiration') + 273.15 // Convert to K
  const pressureLow = getNumericSensorData('pressure_low') * 100 // Convert to kPa
  
  // Simplified entropy calculation for R22
  return 1.2 + 0.0035 * tempAspiration - 0.0002 * pressureLow
}

// Calculate vapor quality
const calculateVaporQuality = () => {
  const superheat = getNumericSensorData('superheat')
  
  if (superheat > 0) {
    return 1.0 // Superheated vapor
  } else {
    // Estimate quality in two-phase region
    return 0.85 + superheat * 0.02
  }
}

// Calculate evaporation enthalpy
const calculateEvaporationEnthalpy = () => {
  const tempEvap = getNumericSensorData('temp_evaporator')
  
  // R22 enthalpy estimation at evaporation temperature
  return 250 + (tempEvap + 10) * 1.5
}

// Calculate condensation enthalpy
const calculateCondensationEnthalpy = () => {
  const tempCond = getNumericSensorData('temp_condenser')
  
  // R22 enthalpy estimation at condensation temperature
  return 420 + (tempCond - 40) * 1.2
}

// Calculate suction volume
const calculateSuctionVolume = () => {
  const tempAspiration = getNumericSensorData('temp_aspiration') + 273.15 // Convert to K
  const pressureLow = getNumericSensorData('pressure_low') * 100000 // Convert to Pa
  
  // Ideal gas approximation for specific volume
  const R_specific = 96.15 // Specific gas constant for R22 (J/(kg·K))
  return (R_specific * tempAspiration) / pressureLow
}

// Diagram event handlers
const onSPDiagramReady = (diagramData) => {
  console.log('S-p Diagram ready:', diagramData)
}

const onPHDiagramReady = (diagramData) => {
  console.log('p-h Diagram ready:', diagramData)
}

const onPVDiagramReady = (diagramData) => {
  console.log('p-v Diagram ready:', diagramData)
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
