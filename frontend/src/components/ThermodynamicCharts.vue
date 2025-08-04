<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-900 flex items-center">
        📊 Thermodynamic Charts Generator
      </h2>
      <div class="flex items-center space-x-2">
        <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
          {{ selectedFluid }}
        </span>
      </div>
    </div>

    <!-- Fluid Selection -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Select Refrigerant/Fluid</label>
      <select 
        v-model="selectedFluid" 
        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
      >
        <option value="R22">R22 (Freon-22)</option>
        <option value="R134a">R134a</option>
        <option value="R410A">R410A</option>
        <option value="R32">R32</option>
        <option value="R404A">R404A</option>
        <option value="H2O">Water/Steam</option>
        <option value="NH3">Ammonia (R717)</option>
        <option value="CO2">Carbon Dioxide (R744)</option>
      </select>
    </div>

    <!-- Chart Type Selection -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      
      <!-- S-p Diagram -->
      <div class="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors"
           :class="{'border-purple-500 bg-purple-50': selectedChart === 'sp'}">
        <div class="flex items-center mb-3">
          <input 
            type="radio" 
            id="sp-chart" 
            v-model="selectedChart" 
            value="sp"
            class="w-4 h-4 text-purple-600 border-gray-300 focus:ring-purple-500"
          >
          <label for="sp-chart" class="ml-3 text-sm font-medium text-gray-900">
            S-p Diagram (Entropy vs Pressure)
          </label>
        </div>
        <p class="text-xs text-gray-600 mb-3">
          Shows entropy on X-axis, pressure (log scale) on Y-axis with saturation dome and property lines.
        </p>
        <div class="text-xs text-gray-500">
          • Isotherms (T = const)<br>
          • Isoenthalps (h = const)<br>
          • Quality lines (x = 0.1-0.9)
        </div>
      </div>

      <!-- p-h Diagram (Mollier) -->
      <div class="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors"
           :class="{'border-purple-500 bg-purple-50': selectedChart === 'ph'}">
        <div class="flex items-center mb-3">
          <input 
            type="radio" 
            id="ph-chart" 
            v-model="selectedChart" 
            value="ph"
            class="w-4 h-4 text-purple-600 border-gray-300 focus:ring-purple-500"
          >
          <label for="ph-chart" class="ml-3 text-sm font-medium text-gray-900">
            p-h Diagram (Mollier Chart)
          </label>
        </div>
        <p class="text-xs text-gray-600 mb-3">
          Pressure vs enthalpy with refrigeration cycle visualization capabilities.
        </p>
        <div class="text-xs text-gray-500">
          • Isotherms<br>
          • Isoentropy lines<br>
          • Cycle points (1-2-3-4)
        </div>
      </div>

      <!-- p-v Diagram -->
      <div class="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors"
           :class="{'border-purple-500 bg-purple-50': selectedChart === 'pv'}">
        <div class="flex items-center mb-3">
          <input 
            type="radio" 
            id="pv-chart" 
            v-model="selectedChart" 
            value="pv"
            class="w-4 h-4 text-purple-600 border-gray-300 focus:ring-purple-500"
          >
          <label for="pv-chart" class="ml-3 text-sm font-medium text-gray-900">
            p-v Diagram (Pressure vs Volume)
          </label>
        </div>
        <p class="text-xs text-gray-600 mb-3">
          Pressure vs specific volume with thermodynamic process visualization.
        </p>
        <div class="text-xs text-gray-500">
          • Isotherms<br>
          • Isentropes<br>
          • Process paths
        </div>
      </div>
    </div>

    <!-- Chart Parameters -->
    <div v-if="selectedChart" class="bg-gray-50 rounded-lg p-4 mb-6">
      <h3 class="text-sm font-medium text-gray-900 mb-4">Chart Parameters for {{ getChartTitle() }}</h3>
      
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="param in getChartParameters()" :key="param.key">
          <label class="block text-xs font-medium text-gray-700 mb-1">{{ param.label }}</label>
          <input 
            type="number" 
            v-model.number="chartParams[param.key]"
            :step="param.step"
            :min="param.min"
            :max="param.max"
            class="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-purple-500"
          >
          <span class="text-xs text-gray-500">{{ param.unit }}</span>
        </div>
      </div>
    </div>

    <!-- Generation Options -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Output Format</label>
        <select 
          v-model="outputFormat" 
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="svg">SVG (Vector)</option>
          <option value="png">PNG (High-Res)</option>
          <option value="pdf">PDF (Publication)</option>
        </select>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Resolution/Quality</label>
        <select 
          v-model="quality" 
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="standard">Standard (800x600)</option>
          <option value="high">High (1600x1200)</option>
          <option value="publication">Publication (3200x2400)</option>
        </select>
      </div>
    </div>

    <!-- Advanced Options -->
    <div class="border-t border-gray-200 pt-4 mb-6">
      <button 
        @click="showAdvanced = !showAdvanced"
        class="flex items-center text-sm text-purple-600 hover:text-purple-800 transition-colors"
      >
        <svg class="w-4 h-4 mr-2 transform transition-transform" :class="{'rotate-90': showAdvanced}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
        Advanced Options
      </button>
      
      <div v-show="showAdvanced" class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="flex items-center text-sm text-gray-700">
            <input type="checkbox" v-model="options.showGrid" class="mr-2">
            Show Grid Lines
          </label>
        </div>
        <div>
          <label class="flex items-center text-sm text-gray-700">
            <input type="checkbox" v-model="options.showLegend" class="mr-2">
            Include Legend
          </label>
        </div>
        <div>
          <label class="flex items-center text-sm text-gray-700">
            <input type="checkbox" v-model="options.showCyclePoints" class="mr-2">
            Show Cycle Points
          </label>
        </div>
        <div>
          <label class="flex items-center text-sm text-gray-700">
            <input type="checkbox" v-model="options.colorCoded" class="mr-2">
            Color-Coded Lines
          </label>
        </div>
        <div>
          <label class="flex items-center text-sm text-gray-700">
            <input type="checkbox" v-model="options.shadeDome" class="mr-2">
            Shade Two-Phase Region
          </label>
        </div>
        <div>
          <label class="flex items-center text-sm text-gray-700">
            <input type="checkbox" v-model="options.vectorStyle" class="mr-2">
            Vector/SVG Style
          </label>
        </div>
      </div>
    </div>

    <!-- Real-time Preview -->
    <div v-if="selectedChart" class="bg-gray-50 rounded-lg p-4 mb-6">
      <h3 class="text-sm font-medium text-gray-900 mb-3">Chart Preview</h3>
      <div class="w-full h-64 bg-white border border-gray-200 rounded-lg flex items-center justify-center">
        <div v-if="isGeneratingPreview" class="text-center">
          <LoadingSpinner :full-height="false" message="Generating preview..." />
        </div>
        <div v-else-if="previewData" class="w-full h-full">
          <canvas ref="previewCanvas" class="w-full h-full"></canvas>
        </div>
        <div v-else class="text-center text-gray-500">
          <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 00-2-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <p class="text-sm">Select chart type to see preview</p>
        </div>
      </div>
    </div>

    <!-- Generation Buttons -->
    <div class="flex flex-col sm:flex-row gap-3">
      <button 
        @click="generatePreview"
        :disabled="!selectedChart || isGeneratingPreview"
        class="flex-1 bg-gradient-to-r from-purple-600 to-purple-700 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl"
      >
        <svg v-if="!isGeneratingPreview" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
        </svg>
        <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
        {{ isGeneratingPreview ? 'Generating...' : 'Generate Preview' }}
      </button>
      
      <button 
        @click="generateChart"
        :disabled="!selectedChart || isGenerating"
        class="flex-1 bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-green-800 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl"
      >
        <svg v-if="!isGenerating" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
        {{ isGenerating ? 'Generating...' : `Download ${outputFormat.toUpperCase()} Chart` }}
      </button>
    </div>

    <!-- Usage Instructions -->
    <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <h4 class="text-sm font-medium text-blue-900 mb-2">📋 Usage Instructions</h4>
      <div class="text-sm text-blue-800 space-y-1">
        <p><strong>1.</strong> Select your refrigerant/fluid from the dropdown</p>
        <p><strong>2.</strong> Choose the type of thermodynamic diagram you need</p>
        <p><strong>3.</strong> Adjust parameters if needed (ranges, resolution, etc.)</p>
        <p><strong>4.</strong> Preview the chart to verify appearance</p>
        <p><strong>5.</strong> Download in your preferred format (SVG, PNG, PDF)</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import LoadingSpinner from './LoadingSpinner.vue'

// Component state
const selectedFluid = ref('R22')
const selectedChart = ref('ph')
const outputFormat = ref('svg')
const quality = ref('high')
const showAdvanced = ref(false)
const isGenerating = ref(false)
const isGeneratingPreview = ref(false)
const previewData = ref(null)
const previewCanvas = ref(null)

// Chart parameters - dynamic based on selected chart and fluid
const chartParams = ref({
  // S-p parameters
  s_min: 0.8,
  s_max: 2.2,
  p_min: 0.1,
  p_max: 40,
  
  // p-h parameters  
  h_min: 150,
  h_max: 450,
  
  // p-v parameters
  v_min: 0.0001,
  v_max: 1.0
})

// Advanced options
const options = ref({
  showGrid: true,
  showLegend: true,
  showCyclePoints: true,
  colorCoded: true,
  shadeDome: true,
  vectorStyle: true
})

// Fluid properties database
const fluidProperties = {
  'R22': {
    name: 'R22 (Freon-22)',
    criticalTemp: 96.15, // °C
    criticalPressure: 4.99, // MPa
    ranges: {
      sp: { s_min: 0.8, s_max: 2.2, p_min: 0.1, p_max: 5.0 },
      ph: { h_min: 150, h_max: 450, p_min: 0.1, p_max: 5.0 },
      pv: { v_min: 0.0001, v_max: 1.0, p_min: 0.1, p_max: 5.0 }
    }
  },
  'R134a': {
    name: 'R134a',
    criticalTemp: 101.06,
    criticalPressure: 4.06,
    ranges: {
      sp: { s_min: 0.7, s_max: 2.0, p_min: 0.1, p_max: 4.1 },
      ph: { h_min: 180, h_max: 480, p_min: 0.1, p_max: 4.1 },
      pv: { v_min: 0.0001, v_max: 2.0, p_min: 0.1, p_max: 4.1 }
    }
  },
  'R410A': {
    name: 'R410A',
    criticalTemp: 72.13,
    criticalPressure: 4.90,
    ranges: {
      sp: { s_min: 0.9, s_max: 2.1, p_min: 0.2, p_max: 5.0 },
      ph: { h_min: 200, h_max: 500, p_min: 0.2, p_max: 5.0 },
      pv: { v_min: 0.00005, v_max: 0.5, p_min: 0.2, p_max: 5.0 }
    }
  },
  'H2O': {
    name: 'Water/Steam',
    criticalTemp: 373.95,
    criticalPressure: 22.064,
    ranges: {
      sp: { s_min: 0, s_max: 10, p_min: 0.001, p_max: 22 },
      ph: { h_min: 0, h_max: 4000, p_min: 0.001, p_max: 22 },
      pv: { v_min: 0.0001, v_max: 100, p_min: 0.001, p_max: 22 }
    }
  }
}

// Methods
const getChartTitle = () => {
  const titles = {
    'sp': 'S-p Diagram (Entropy vs Pressure)',
    'ph': 'p-h Diagram (Mollier Chart)', 
    'pv': 'p-v Diagram (Pressure vs Volume)'
  }
  return titles[selectedChart.value] || ''
}

const getChartParameters = () => {
  const params = {
    'sp': [
      { key: 's_min', label: 'Min Entropy', unit: 'kJ/(kg·K)', step: 0.1, min: 0, max: 10 },
      { key: 's_max', label: 'Max Entropy', unit: 'kJ/(kg·K)', step: 0.1, min: 0, max: 10 },
      { key: 'p_min', label: 'Min Pressure', unit: 'MPa', step: 0.01, min: 0.001, max: 50 },
      { key: 'p_max', label: 'Max Pressure', unit: 'MPa', step: 0.1, min: 0.1, max: 50 }
    ],
    'ph': [
      { key: 'h_min', label: 'Min Enthalpy', unit: 'kJ/kg', step: 10, min: 0, max: 5000 },
      { key: 'h_max', label: 'Max Enthalpy', unit: 'kJ/kg', step: 10, min: 0, max: 5000 },
      { key: 'p_min', label: 'Min Pressure', unit: 'MPa', step: 0.01, min: 0.001, max: 50 },
      { key: 'p_max', label: 'Max Pressure', unit: 'MPa', step: 0.1, min: 0.1, max: 50 }
    ],
    'pv': [
      { key: 'v_min', label: 'Min Volume', unit: 'm³/kg', step: 0.0001, min: 0.0001, max: 100 },
      { key: 'v_max', label: 'Max Volume', unit: 'm³/kg', step: 0.1, min: 0.001, max: 100 },
      { key: 'p_min', label: 'Min Pressure', unit: 'MPa', step: 0.01, min: 0.001, max: 50 },
      { key: 'p_max', label: 'Max Pressure', unit: 'MPa', step: 0.1, min: 0.1, max: 50 }
    ]
  }
  return params[selectedChart.value] || []
}

const updateParametersForFluid = () => {
  const fluid = fluidProperties[selectedFluid.value]
  if (fluid && fluid.ranges[selectedChart.value]) {
    const ranges = fluid.ranges[selectedChart.value]
    Object.assign(chartParams.value, ranges)
  }
}

const generatePreview = async () => {
  isGeneratingPreview.value = true
  try {
    const response = await axios.post('/api/charts/preview', {
      chartType: selectedChart.value,
      fluid: selectedFluid.value,
      parameters: chartParams.value,
      options: options.value,
      format: 'canvas_data'
    })
    
    previewData.value = response.data
    // Draw on canvas (simplified preview)
    drawPreviewChart()
  } catch (error) {
    console.error('Error generating preview:', error)
  } finally {
    isGeneratingPreview.value = false
  }
}

const generateChart = async () => {
  isGenerating.value = true
  try {
    const response = await axios.post('/api/charts/generate', {
      chartType: selectedChart.value,
      fluid: selectedFluid.value,
      parameters: chartParams.value,
      options: options.value,
      format: outputFormat.value,
      quality: quality.value
    }, {
      responseType: 'blob'
    })
    
    // Download the generated chart
    const timestamp = new Date().toISOString().slice(0, 10)
    const filename = `${selectedChart.value}_${selectedFluid.value}_${timestamp}.${outputFormat.value}`
    downloadFile(response.data, filename)
    
  } catch (error) {
    console.error('Error generating chart:', error)
    alert('Failed to generate chart. Please try again.')
  } finally {
    isGenerating.value = false
  }
}

const drawPreviewChart = () => {
  // Simplified preview drawing - would be enhanced with actual chart rendering
  if (!previewCanvas.value) return
  
  const ctx = previewCanvas.value.getContext('2d')
  const canvas = previewCanvas.value
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Draw axes
  ctx.strokeStyle = '#374151'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(50, canvas.height - 50)
  ctx.lineTo(canvas.width - 20, canvas.height - 50)
  ctx.moveTo(50, canvas.height - 50)
  ctx.lineTo(50, 20)
  ctx.stroke()
  
  // Draw sample curve (saturation dome approximation)
  ctx.strokeStyle = '#3B82F6'
  ctx.lineWidth = 3
  ctx.beginPath()
  ctx.moveTo(60, canvas.height - 60)
  
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radiusX = canvas.width * 0.3
  const radiusY = canvas.height * 0.25
  
  // Draw elliptical dome
  ctx.ellipse(centerX, centerY + 20, radiusX, radiusY, 0, Math.PI, 0)
  ctx.stroke()
  
  // Add labels
  ctx.fillStyle = '#374151'
  ctx.font = '12px sans-serif'
  ctx.fillText(getAxisLabel('x'), canvas.width - 80, canvas.height - 30)
  ctx.save()
  ctx.translate(25, 60)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText(getAxisLabel('y'), 0, 0)
  ctx.restore()
}

const getAxisLabel = (axis) => {
  const labels = {
    'sp': { x: 'Entropy [kJ/(kg·K)]', y: 'Pressure [MPa]' },
    'ph': { x: 'Enthalpy [kJ/kg]', y: 'Pressure [MPa]' },
    'pv': { x: 'Specific Volume [m³/kg]', y: 'Pressure [MPa]' }
  }
  return labels[selectedChart.value]?.[axis] || ''
}

const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// Watchers
watch([selectedFluid, selectedChart], () => {
  updateParametersForFluid()
  previewData.value = null
})

watch(chartParams, () => {
  // Debounced preview generation could go here
}, { deep: true })

// Initialize
onMounted(() => {
  updateParametersForFluid()
})
</script>

<style scoped>
/* Enhanced styling for thermodynamic charts component */
canvas {
  border-radius: 0.5rem;
}

/* Custom radio button styling */
input[type="radio"]:checked {
  background-color: #7C3AED;
  border-color: #7C3AED;
}

/* Responsive grid adjustments */
@media (max-width: 768px) {
  .grid-cols-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
