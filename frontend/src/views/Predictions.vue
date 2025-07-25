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
              <h3 class="text-xl font-semibold text-gray-900">Sensor Records</h3>
              <div class="flex items-center space-x-4">
                <div class="relative">
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Search sensor or machine..."
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
                <select 
                  v-model="sensorFilter"
                  class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Sensors</option>
                  <option value="pressure">Pressure Sensors</option>
                  <option value="temperature">Temperature Sensors</option>
                  <option value="warning">Warning Status</option>
                  <option value="critical">Critical Status</option>
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
                    Sensor ID
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sensor Type
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sensor Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Machine
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <template v-for="prediction in filteredPredictions" :key="prediction._id || prediction.timestamp">
                  <!-- Pressure Sensors -->
                  <tr class="hover:bg-gray-50 transition duration-200">
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
                          <span class="text-blue-600 text-xs font-medium">HP</span>
                        </div>
                        <div>
                          <span class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}_HP_01</span>
                          <div class="text-xs text-gray-500">High Pressure</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-3 h-3 bg-red-400 rounded-full mr-2"></div>
                        <span class="text-sm text-gray-900">Pressure Sensor</span>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.pressure_high }} bar</div>
                      <div class="text-xs text-gray-500">High Pressure</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span 
                        class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                        :class="getSensorStatusColor(prediction.pressure_high, 'pressure_high')"
                      >
                        {{ getSensorStatus(prediction.pressure_high, 'pressure_high') }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(prediction.timestamp) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}</div>
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
                  </tr>
                  
                  <!-- Low Pressure Sensor -->
                  <tr class="hover:bg-gray-50 transition duration-200">
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
                        <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center mr-3">
                          <span class="text-yellow-600 text-xs font-medium">LP</span>
                        </div>
                        <div>
                          <span class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}_LP_01</span>
                          <div class="text-xs text-gray-500">Low Pressure</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-3 h-3 bg-yellow-400 rounded-full mr-2"></div>
                        <span class="text-sm text-gray-900">Pressure Sensor</span>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.pressure_low }} bar</div>
                      <div class="text-xs text-gray-500">Low Pressure</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span 
                        class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                        :class="getSensorStatusColor(prediction.pressure_low, 'pressure_low')"
                      >
                        {{ getSensorStatus(prediction.pressure_low, 'pressure_low') }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(prediction.timestamp) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}</div>
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
                  </tr>
                  
                  <!-- Evaporator Temperature Sensor -->
                  <tr class="hover:bg-gray-50 transition duration-200">
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
                          <span class="text-blue-600 text-xs font-medium">TE</span>
                        </div>
                        <div>
                          <span class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}_TE_01</span>
                          <div class="text-xs text-gray-500">Evaporator Temp</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-3 h-3 bg-blue-400 rounded-full mr-2"></div>
                        <span class="text-sm text-gray-900">Temperature Sensor</span>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.temp_evaporator }}°C</div>
                      <div class="text-xs text-gray-500">Evaporator</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span 
                        class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                        :class="getSensorStatusColor(prediction.temp_evaporator, 'temp_evaporator')"
                      >
                        {{ getSensorStatus(prediction.temp_evaporator, 'temp_evaporator') }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(prediction.timestamp) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}</div>
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
                  </tr>
                  
                  <!-- Condenser Temperature Sensor -->
                  <tr class="hover:bg-gray-50 transition duration-200">
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
                        <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mr-3">
                          <span class="text-red-600 text-xs font-medium">TC</span>
                        </div>
                        <div>
                          <span class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}_TC_01</span>
                          <div class="text-xs text-gray-500">Condenser Temp</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-3 h-3 bg-red-400 rounded-full mr-2"></div>
                        <span class="text-sm text-gray-900">Temperature Sensor</span>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.temp_condenser }}°C</div>
                      <div class="text-xs text-gray-500">Condenser</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span 
                        class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                        :class="getSensorStatusColor(prediction.temp_condenser, 'temp_condenser')"
                      >
                        {{ getSensorStatus(prediction.temp_condenser, 'temp_condenser') }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(prediction.timestamp) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}</div>
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
                  </tr>
                  
                  <!-- Superheat Sensor -->
                  <tr class="hover:bg-gray-50 transition duration-200">
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
                        <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                          <span class="text-purple-600 text-xs font-medium">SH</span>
                        </div>
                        <div>
                          <span class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}_SH_01</span>
                          <div class="text-xs text-gray-500">Superheat</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-3 h-3 bg-purple-400 rounded-full mr-2"></div>
                        <span class="text-sm text-gray-900">Derived Parameter</span>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.superheat }}°C</div>
                      <div class="text-xs text-gray-500">Superheat</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span 
                        class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                        :class="getSensorStatusColor(prediction.superheat, 'superheat')"
                      >
                        {{ getSensorStatus(prediction.superheat, 'superheat') }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(prediction.timestamp) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}</div>
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
                  </tr>
                  
                  <!-- Subcooling Sensor -->
                  <tr class="hover:bg-gray-50 transition duration-200 border-b-2 border-gray-300">
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
                        <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
                          <span class="text-green-600 text-xs font-medium">SC</span>
                        </div>
                        <div>
                          <span class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}_SC_01</span>
                          <div class="text-xs text-gray-500">Subcooling</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                        <span class="text-sm text-gray-900">Derived Parameter</span>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.subcooling }}°C</div>
                      <div class="text-xs text-gray-500">Subcooling</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span 
                        class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                        :class="getSensorStatusColor(prediction.subcooling, 'subcooling')"
                      >
                        {{ getSensorStatus(prediction.subcooling, 'subcooling') }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(prediction.timestamp) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ prediction.machine_id }}</div>
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
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
          
          <div v-if="filteredPredictions.length === 0" class="text-center py-12">
            <ChartBarIcon class="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p class="text-gray-500 font-medium">No sensor data available</p>
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
const sensorFilter = ref('')

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

  if (sensorFilter.value === 'pressure') {
    filtered = filtered.filter(p => p.pressure_high !== undefined || p.pressure_low !== undefined)
  } else if (sensorFilter.value === 'temperature') {
    filtered = filtered.filter(p => p.temp_evaporator !== undefined || p.temp_condenser !== undefined)
  } else if (sensorFilter.value === 'warning') {
    filtered = filtered.filter(p => p.prediction === 1)
  } else if (sensorFilter.value === 'critical') {
    filtered = filtered.filter(p => p.prediction === 1 && p.probability > 0.8)
  }

  return filtered
})

const formatDate = (timestamp) => {
  return moment(timestamp).format('MMM DD, YYYY HH:mm:ss')
}

// Sensor status validation functions
const getSensorStatus = (value, sensorType) => {
  const ranges = {
    pressure_high: { normal: [8, 16], warning: [16, 18], critical: [18, 22] },
    pressure_low: { normal: [1.5, 4.0], warning: [1.0, 1.5], critical: [0.5, 1.0] },
    temp_evaporator: { normal: [-25, 0], warning: [-30, -25], critical: [-35, -30] },
    temp_condenser: { normal: [25, 45], warning: [45, 55], critical: [55, 65] },
    superheat: { normal: [3, 15], warning: [15, 20], critical: [20, 30] },
    subcooling: { normal: [3, 8], warning: [2, 3], critical: [0, 2] }
  }
  
  const range = ranges[sensorType]
  if (!range) return 'normal'
  
  const [normalMin, normalMax] = range.normal
  const [warningMin, warningMax] = range.warning
  const [criticalMin, criticalMax] = range.critical
  
  if (value >= normalMin && value <= normalMax) return 'normal'
  if (value >= warningMin && value <= warningMax) return 'warning'
  if (value >= criticalMin && value <= criticalMax) return 'critical'
  return 'error'
}

const getSensorStatusColor = (value, sensorType) => {
  const status = getSensorStatus(value, sensorType)
  const colors = {
    normal: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    critical: 'bg-red-100 text-red-800',
    error: 'bg-gray-100 text-gray-800'
  }
  return colors[status] || colors.normal
}
</script>
