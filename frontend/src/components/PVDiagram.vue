<template>
  <div class="pv-diagram-container">
    <svg 
      :width="width" 
      :height="height" 
      class="pv-diagram border border-gray-200 rounded bg-white"
      ref="svgContainer"
    >
      <!-- Grid Background -->
      <defs>
        <pattern id="pvGridPattern" width="45" height="45" patternUnits="userSpaceOnUse">
          <path d="M 45 0 L 0 0 0 45" fill="none" stroke="#f9fafb" stroke-width="1"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#pvGridPattern)" />
      
      <!-- Axes -->
      <g class="axes">
        <!-- X-axis (Specific Volume - Log scale) -->
        <line 
          :x1="margin.left" 
          :y1="height - margin.bottom" 
          :x2="width - margin.right" 
          :y2="height - margin.bottom" 
          stroke="#374151" 
          stroke-width="2"
        />
        
        <!-- Y-axis (Pressure - Log scale) -->
        <line 
          :x1="margin.left" 
          :y1="margin.top" 
          :x2="margin.left" 
          :y2="height - margin.bottom" 
          stroke="#374151" 
          stroke-width="2"
        />
        
        <!-- Axis labels -->
        <text 
          :x="(width - margin.left - margin.right) / 2 + margin.left" 
          :y="height - 10" 
          text-anchor="middle" 
          class="text-sm font-medium fill-gray-700"
        >
          Specific Volume v [m³/kg] (log scale)
        </text>
        
        <text 
          :x="20" 
          :y="(height - margin.top - margin.bottom) / 2 + margin.top" 
          text-anchor="middle" 
          transform="rotate(-90, 20, 250)" 
          class="text-sm font-medium fill-gray-700"
        >
          Pressure p [MPa] (log scale)
        </text>
      </g>
      
      <!-- Scale ticks -->
      <g class="ticks">
        <!-- Volume ticks (log scale) -->
        <g v-for="(tick, index) in volumeTicks" :key="`volume-${index}`">
          <line 
            :x1="volumeScale(tick)" 
            :y1="height - margin.bottom" 
            :x2="volumeScale(tick)" 
            :y2="height - margin.bottom + 6" 
            stroke="#374151" 
            stroke-width="1"
          />
          <text 
            :x="volumeScale(tick)" 
            :y="height - margin.bottom + 18" 
            text-anchor="middle" 
            class="text-xs fill-gray-600"
          >
            {{ tick }}
          </text>
        </g>
        
        <!-- Pressure ticks (log scale) -->
        <g v-for="(tick, index) in pressureTicksMPa" :key="`pressure-${index}`">
          <line 
            :x1="margin.left - 6" 
            :y1="pressureScaleMPa(tick)" 
            :x2="margin.left" 
            :y2="pressureScaleMPa(tick)" 
            stroke="#374151" 
            stroke-width="1"
          />
          <text 
            :x="margin.left - 10" 
            :y="pressureScaleMPa(tick) + 4" 
            text-anchor="end" 
            class="text-xs fill-gray-600"
          >
            {{ tick }}
          </text>
        </g>
      </g>
      
      <!-- Saturation Dome -->
      <g class="saturation-dome-pv">
        <path 
          :d="saturationDomePathPV" 
          fill="rgba(99, 102, 241, 0.12)" 
          stroke="#6366f1" 
          stroke-width="2.5" 
        />
        <text 
          :x="width - 180" 
          :y="35" 
          class="text-sm font-bold fill-indigo-700"
        >
          Two-Phase Region (R22)
        </text>
      </g>
      
      <!-- Isotherms -->
      <g class="isotherms-pv">
        <g v-for="(isotherm, index) in isothermsPV" :key="`isotherm-pv-${index}`">
          <path 
            :d="isotherm.path" 
            fill="none" 
            stroke="#dc2626" 
            stroke-width="2" 
            opacity="0.8"
          />
          <text 
            :x="isotherm.labelX" 
            :y="isotherm.labelY" 
            class="text-xs font-semibold fill-red-700"
          >
            {{ isotherm.temperature }}°C
          </text>
        </g>
      </g>
      
      <!-- Isentropes -->
      <g class="isentropes-pv">
        <g v-for="(isentrope, index) in isentropesPV" :key="`isentrope-pv-${index}`">
          <path 
            :d="isentrope.path" 
            fill="none" 
            stroke="#16a34a" 
            stroke-width="1.8" 
            stroke-dasharray="5,3"
            opacity="0.8"
          />
          <text 
            :x="isentrope.labelX" 
            :y="isentrope.labelY" 
            class="text-xs font-semibold fill-green-700"
          >
            s={{ isentrope.entropy }}
          </text>
        </g>
      </g>
      
      <!-- Compression Process from Kafka Data with enhanced visualization -->
      <g class="compression-process" v-if="kafkaData">
        <!-- Compression work visualization with animation -->
        <path 
          :d="compressionAreaPath" 
          fill="rgba(239, 68, 68, 0.2)" 
          stroke="#ef4444" 
          stroke-width="3"
          class="compression-area"
        />
        
        <!-- Interactive cycle points -->
        <g v-for="(point, index) in cyclePointsPV" :key="`cycle-pv-${index}`">
          <circle 
            :cx="volumeScale(point.volume)" 
            :cy="pressureScaleMPa(point.pressure)" 
            r="9" 
            :fill="point.color" 
            stroke="white" 
            stroke-width="3"
            class="cursor-pointer transition-all duration-300 hover:r-12"
            @mouseover="showWorkAnalysis(point, index)"
            @mouseout="hideWorkAnalysis"
            @click="analyzeCompression(point)"
          />
          <text 
            :x="volumeScale(point.volume) + 15" 
            :y="pressureScaleMPa(point.pressure) - 10" 
            class="text-sm font-bold pointer-events-none"
            :fill="point.color"
          >
            {{ point.label }}
          </text>
          <text 
            :x="volumeScale(point.volume) + 15" 
            :y="pressureScaleMPa(point.pressure) + 8" 
            class="text-xs pointer-events-none"
            :fill="point.color"
          >
            {{ point.description }}
          </text>
        </g>
        
        <!-- Real-time work analysis tooltip -->
        <g v-if="workAnalysis" :transform="`translate(${workAnalysisPosition.x}, ${workAnalysisPosition.y})`">
          <rect x="0" y="0" width="220" height="120" fill="rgba(0,0,0,0.9)" rx="6"/>
          <text x="10" y="15" class="text-xs fill-white font-bold">{{ workAnalysis.description }} - Analysis</text>
          <text x="10" y="30" class="text-xs fill-white">Volume: {{ workAnalysis.volume.toFixed(4) }} m³/kg</text>
          <text x="10" y="45" class="text-xs fill-white">Pressure: {{ workAnalysis.pressure.toFixed(2) }} MPa</text>
          <text x="10" y="60" class="text-xs fill-white">Work Contribution: {{ getWorkContribution(workAnalysis) }} kJ/kg</text>
          <text x="10" y="75" class="text-xs fill-white">Efficiency: {{ getPointEfficiency(workAnalysis) }}%</text>
          <text x="10" y="90" class="text-xs fill-white">Status: {{ getPointStatus(workAnalysis) }}</text>
          <text x="10" y="105" class="text-xs fill-white">Live from Compressor</text>
        </g>
        
        <!-- Compression work area label with animation -->
        <text 
          :x="compressionWorkLabelX" 
          :y="compressionWorkLabelY" 
          class="text-sm font-bold fill-red-600 work-label"
        >
          Work = {{ compressionWork.toFixed(1) }} kJ/kg
        </text>
        
        <!-- Real-time work indicator -->
        <circle
          :cx="compressionWorkLabelX + 100"
          :cy="compressionWorkLabelY"
          r="4"
          :fill="getWorkEfficiencyColor()"
          class="animate-pulse"
        />
      </g>
      
      <!-- Ideal Gas Lines (for comparison) -->
      <g class="ideal-gas-lines">
        <g v-for="(idealLine, index) in idealGasLines" :key="`ideal-${index}`">
          <path 
            :d="idealLine.path" 
            fill="none" 
            stroke="#f59e0b" 
            stroke-width="1" 
            stroke-dasharray="8,4"
            opacity="0.6"
          />
          <text 
            :x="idealLine.labelX" 
            :y="idealLine.labelY" 
            class="text-xs fill-amber-600"
          >
            pv={{ idealLine.pv }}
          </text>
        </g>
      </g>
      
      <!-- Enhanced Legend with live compressor analysis -->
      <g class="legend" transform="translate(20, 50)">
        <rect x="0" y="0" width="250" height="220" fill="white" stroke="#d1d5db" rx="6" opacity="0.95"/>
        <text x="10" y="18" class="text-sm font-bold fill-gray-800">p-v Analysis {{ fluid }}</text>
        
        <line x1="10" y1="30" x2="35" y2="30" stroke="#6366f1" stroke-width="2.5"/>
        <text x="40" y="34" class="text-xs fill-gray-700">Saturation Dome</text>
        
        <line x1="10" y1="45" x2="35" y2="45" stroke="#dc2626" stroke-width="2"/>
        <text x="40" y="49" class="text-xs fill-gray-700">Isotherms (T=const)</text>
        
        <line x1="10" y1="60" x2="35" y2="60" stroke="#16a34a" stroke-width="1.8" stroke-dasharray="5,3"/>
        <text x="40" y="64" class="text-xs fill-gray-700">Isentropes (s=const)</text>
        
        <line x1="10" y1="75" x2="35" y2="75" stroke="#f59e0b" stroke-width="1" stroke-dasharray="8,4"/>
        <text x="40" y="79" class="text-xs fill-gray-700">Ideal Gas (pv=const)</text>
        
        <rect x="10" y="88" width="25" height="8" fill="rgba(239, 68, 68, 0.2)" stroke="#ef4444"/>
        <text x="40" y="94" class="text-xs fill-gray-700">Compression Work Area</text>
        
        <circle cx="22" cy="105" r="4" fill="#ef4444"/>
        <text x="40" y="109" class="text-xs fill-gray-700">Live Cycle Points</text>
        
        <text x="10" y="125" class="text-xs fill-gray-600 font-medium">Compressor Real-time:</text>
        <text x="10" y="138" class="text-xs fill-gray-600">Current: {{ getCompressorCurrent() }}A</text>
        <text x="130" y="138" class="text-xs fill-gray-600">Power: {{ getCompressorPower() }}kW</text>
        <text x="10" y="151" class="text-xs fill-gray-600">Vibrations: {{ getVibrations() }}g</text>
        <text x="130" y="151" class="text-xs fill-gray-600">Speed: {{ getCompressorSpeed() }}rpm</text>
        <text x="10" y="164" class="text-xs fill-gray-600">Efficiency: {{ getVolumetricEfficiency() }}%</text>
        <text x="130" y="164" class="text-xs fill-gray-600">Work: {{ getLiveCompressionWork() }}kJ/kg</text>
        <text x="10" y="177" class="text-xs fill-gray-600">Pressure Ratio: {{ getPressureRatio() }}</text>
        <text x="130" y="177" class="text-xs fill-gray-600">Status: {{ getCompressorStatus() }}</text>
        
        <text x="10" y="195" class="text-xs fill-gray-600 font-medium">Live from Kafka Stream</text>
        <text x="10" y="208" class="text-xs fill-gray-600">FRIGO-UNITE-001 | {{ getCurrentTime() }}</text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  kafkaData: {
    type: Object,
    required: true
  },
  fluid: {
    type: String,
    default: 'R22'
  },
  width: {
    type: Number,
    default: 800
  },
  height: {
    type: Number,
    default: 600
  }
})

const emit = defineEmits(['diagram-ready'])

const svgContainer = ref(null)

const margin = {
  top: 50,
  right: 50,
  bottom: 70,
  left: 90
}

// Specific volume scale (logarithmic)
const volumeScale = computed(() => {
  const domain = [0.0001, 1.0] // m³/kg
  const range = [margin.left, props.width - margin.right]
  
  return (value) => {
    const logValue = Math.log10(Math.max(0.00001, value))
    const logMin = Math.log10(domain[0])
    const logMax = Math.log10(domain[1])
    const normalized = (logValue - logMin) / (logMax - logMin)
    return range[0] + normalized * (range[1] - range[0])
  }
})

// Pressure scale in MPa (logarithmic)
const pressureScaleMPa = computed(() => {
  const domain = [0.1, 2.5] // MPa
  const range = [props.height - margin.bottom, margin.top]
  
  return (value) => {
    const logValue = Math.log10(Math.max(0.01, value))
    const logMin = Math.log10(domain[0])
    const logMax = Math.log10(domain[1])
    const normalized = (logValue - logMin) / (logMax - logMin)
    return range[0] + normalized * (range[1] - range[0])
  }
})

// Scale ticks
const volumeTicks = [0.0001, 0.001, 0.01, 0.1, 1.0]
const pressureTicksMPa = [0.1, 0.2, 0.5, 1.0, 2.0]

// Saturation dome for R22 in p-v coordinates
const saturationDomePathPV = computed(() => {
  const liquidLine = [
    { v: 0.0008, p: 0.25 }, { v: 0.0009, p: 0.5 }, { v: 0.001, p: 0.8 },
    { v: 0.0012, p: 1.2 }, { v: 0.0015, p: 1.8 }, { v: 0.002, p: 2.4 }
  ]
  
  const vaporLine = [
    { v: 0.8, p: 0.25 }, { v: 0.4, p: 0.5 }, { v: 0.2, p: 0.8 },
    { v: 0.12, p: 1.2 }, { v: 0.08, p: 1.8 }, { v: 0.05, p: 2.4 }
  ]
  
  let path = `M ${volumeScale.value(liquidLine[0].v)} ${pressureScaleMPa.value(liquidLine[0].p)}`
  
  // Draw liquid line
  for (let i = 1; i < liquidLine.length; i++) {
    path += ` L ${volumeScale.value(liquidLine[i].v)} ${pressureScaleMPa.value(liquidLine[i].p)}`
  }
  
  // Draw vapor line (reverse order)
  for (let i = vaporLine.length - 1; i >= 0; i--) {
    path += ` L ${volumeScale.value(vaporLine[i].v)} ${pressureScaleMPa.value(vaporLine[i].p)}`
  }
  
  path += ' Z'
  return path
})

// Isotherms in p-v diagram
const isothermsPV = computed(() => {
  const temperatures = [-20, 0, 20, 40, 60, 80]
  
  return temperatures.map(temp => {
    const points = []
    for (let v = 0.001; v <= 1.0; v *= 1.5) {
      // Simplified pressure calculation using modified ideal gas law
      const R_specific = 96.15 // J/(kg·K) for R22
      const T_kelvin = temp + 273.15
      const p = (R_specific * T_kelvin) / (v * 1000000) // Convert to MPa
      
      if (p <= 2.5 && p >= 0.1) {
        points.push({ v, p })
      }
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${volumeScale.value(points[0].v)} ${pressureScaleMPa.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${volumeScale.value(points[i].v)} ${pressureScaleMPa.value(points[i].p)}`
      }
    }
    
    return {
      temperature: temp,
      path,
      labelX: points.length > 0 ? volumeScale.value(points[points.length - 1].v) - 30 : 200,
      labelY: points.length > 0 ? pressureScaleMPa.value(points[points.length - 1].p) - 5 : 150
    }
  })
})

// Isentropes in p-v diagram
const isentropesPV = computed(() => {
  const entropies = [1.4, 1.6, 1.8, 2.0, 2.2]
  
  return entropies.map(s => {
    const points = []
    for (let v = 0.005; v <= 0.5; v *= 1.4) {
      // Simplified isentropic relation: p * v^γ = constant
      const gamma = 1.18 // for R22
      const p = 1.0 * Math.pow(0.1 / v, gamma) // Reference point
      
      if (p <= 2.5 && p >= 0.1) {
        points.push({ v, p })
      }
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${volumeScale.value(points[0].v)} ${pressureScaleMPa.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${volumeScale.value(points[i].v)} ${pressureScaleMPa.value(points[i].p)}`
      }
    }
    
    return {
      entropy: s,
      path,
      labelX: points.length > 0 ? volumeScale.value(points[Math.floor(points.length / 2)].v) + 5 : 250,
      labelY: points.length > 0 ? pressureScaleMPa.value(points[Math.floor(points.length / 2)].p) - 8 : 200
    }
  })
})

// Ideal gas lines (pv = constant)
const idealGasLines = computed(() => {
  const constants = [50, 100, 200, 400]
  
  return constants.map(pv => {
    const points = []
    for (let v = 0.002; v <= 0.8; v *= 1.3) {
      const p = pv / (v * 1000) // Convert to MPa
      
      if (p <= 2.5 && p >= 0.1) {
        points.push({ v, p })
      }
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${volumeScale.value(points[0].v)} ${pressureScaleMPa.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${volumeScale.value(points[i].v)} ${pressureScaleMPa.value(points[i].p)}`
      }
    }
    
    return {
      pv: pv,
      path,
      labelX: points.length > 0 ? volumeScale.value(points[points.length - 1].v) - 40 : 300,
      labelY: points.length > 0 ? pressureScaleMPa.value(points[points.length - 1].p) + 12 : 250
    }
  })
})

// Cycle points from Kafka data in p-v coordinates
const cyclePointsPV = computed(() => {
  if (!props.kafkaData) return []
  
  const data = props.kafkaData
  
  // Calculate specific volumes using simplified correlations
  const R_specific = 96.15 // J/(kg·K) for R22
  
  const points = [
    {
      label: '1',
      volume: (R_specific * ((data.temp_aspiration || 5) + 273.15)) / ((data.pressure_low || 2.5) * 100000), // m³/kg
      pressure: (data.pressure_low || 2.5) / 10, // Convert bar to MPa
      color: '#ef4444',
      description: 'Suction'
    },
    {
      label: '2',
      volume: (R_specific * ((data.temp_refoulement || 65) + 273.15)) / ((data.pressure_high || 12.0) * 100000), // m³/kg
      pressure: (data.pressure_high || 12.0) / 10, // Convert bar to MPa
      color: '#f59e0b',
      description: 'Discharge'
    },
    {
      label: '3',
      volume: 0.001, // Liquid volume (very small)
      pressure: (data.pressure_high || 12.0) / 10, // Convert bar to MPa
      color: '#10b981',
      description: 'Liquid'
    },
    {
      label: '4',
      volume: 0.001, // Before expansion
      pressure: (data.pressure_low || 2.5) / 10, // Convert bar to MPa
      color: '#3b82f6',
      description: 'Expansion'
    }
  ]
  
  return points.filter(point => 
    point.volume >= 0.0001 && point.volume <= 1.0 &&
    point.pressure >= 0.1 && point.pressure <= 2.5
  )
})

// Compression work calculation and visualization
const compressionWork = computed(() => {
  if (!props.kafkaData || cyclePointsPV.value.length < 2) return 0
  
  const point1 = cyclePointsPV.value[0] // Suction
  const point2 = cyclePointsPV.value[1] // Discharge
  
  // Simplified work calculation: W = ∫ p dv (approximated)
  const avgPressure = (point1.pressure + point2.pressure) / 2 * 1000 // Convert to kPa
  const volumeChange = Math.abs(point2.volume - point1.volume)
  
  return avgPressure * volumeChange // kJ/kg
})

// Compression area path for work visualization
const compressionAreaPath = computed(() => {
  if (cyclePointsPV.value.length < 2) return ''
  
  const point1 = cyclePointsPV.value[0] // Suction
  const point2 = cyclePointsPV.value[1] // Discharge
  
  // Create a simple rectangular area to represent work
  const x1 = volumeScale.value(point1.volume)
  const y1 = pressureScaleMPa.value(point1.pressure)
  const x2 = volumeScale.value(point2.volume)
  const y2 = pressureScaleMPa.value(point2.pressure)
  
  return `M ${x1} ${y1} L ${x2} ${y1} L ${x2} ${y2} L ${x1} ${y2} Z`
})

// Compression work label position
const compressionWorkLabelX = computed(() => {
  if (cyclePointsPV.value.length < 2) return 200
  const point1 = cyclePointsPV.value[0]
  const point2 = cyclePointsPV.value[1]
  return (volumeScale.value(point1.volume) + volumeScale.value(point2.volume)) / 2
})

const compressionWorkLabelY = computed(() => {
  if (cyclePointsPV.value.length < 2) return 200
  const point1 = cyclePointsPV.value[0]
  const point2 = cyclePointsPV.value[1]
  return (pressureScaleMPa.value(point1.pressure) + pressureScaleMPa.value(point2.pressure)) / 2
})

// Helper functions for enhanced legend data
const getCompressorCurrent = () => {
  return props.kafkaData?.compressor_current?.toFixed(1) || '8.5'
}

const getVibrations = () => {
  return props.kafkaData?.vibration?.toFixed(1) || '2.1'
}

const getVolumetricEfficiency = () => {
  // Simplified calculation based on pressure ratio
  const pressureRatio = (props.kafkaData?.pressure_high || 12.0) / (props.kafkaData?.pressure_low || 2.5)
  const efficiency = Math.max(60, 95 - (pressureRatio - 2) * 8)
  return efficiency.toFixed(0)
}

const getCompressorPower = () => {
  const current = parseFloat(getCompressorCurrent())
  const voltage = 220 // Assumed voltage
  const power = (current * voltage * Math.sqrt(3) * 0.85) / 1000 // kW
  return power.toFixed(1)
}

const getCompressorSpeed = () => {
  // Simplified speed calculation based on load
  const current = parseFloat(getCompressorCurrent())
  const nominalCurrent = 10.0
  const nominalSpeed = 1450
  const speed = (current / nominalCurrent) * nominalSpeed
  return Math.round(speed)
}

const getLiveCompressionWork = () => {
  return compressionWork.value.toFixed(1)
}

const getPressureRatio = () => {
  const highPressure = props.kafkaData?.pressure_high || 12.0
  const lowPressure = props.kafkaData?.pressure_low || 2.5
  return (highPressure / lowPressure).toFixed(1)
}

const getCompressorStatus = () => {
  const current = parseFloat(getCompressorCurrent())
  const vibration = parseFloat(getVibrations())
  
  if (current > 9.5 || vibration > 3.0) return 'Alert'
  if (current > 9.0 || vibration > 2.5) return 'Warning'
  return 'Normal'
}

const getCurrentTime = () => {
  return new Date().toLocaleTimeString()
}

onMounted(() => {
  emit('diagram-ready', {
    type: 'pv',
    fluid: props.fluid,
    cyclePoints: cyclePointsPV.value,
    compressionWork: compressionWork.value
  })
})

watch(() => props.kafkaData, () => {
  emit('diagram-ready', {
    type: 'pv',
    fluid: props.fluid,
    cyclePoints: cyclePointsPV.value,
    compressionWork: compressionWork.value
  })
}, { deep: true })
</script>

<style scoped>
.pv-diagram-container {
  @apply w-full h-full;
}

.pv-diagram {
  @apply shadow-lg;
}
</style>
