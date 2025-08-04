<template>
  <div class="sp-diagram-container">
    <svg 
      :width="width" 
      :height="height" 
      class="sp-diagram border border-gray-200 rounded bg-white"
      ref="svgContainer"
    >
      <!-- Grid Background -->
      <defs>
        <pattern id="gridPattern" width="50" height="50" patternUnits="userSpaceOnUse">
          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e5e7eb" stroke-width="1"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#gridPattern)" />
      
      <!-- Axes -->
      <g class="axes">
        <!-- X-axis (Entropy) -->
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
          Entropy s [kJ/(kg·K)]
        </text>
        
        <text 
          :x="20" 
          :y="(height - margin.top - margin.bottom) / 2 + margin.top" 
          text-anchor="middle" 
          transform="rotate(-90, 20, 200)" 
          class="text-sm font-medium fill-gray-700"
        >
          Pressure p [MPa] (log scale)
        </text>
      </g>
      
      <!-- Scale ticks -->
      <g class="ticks">
        <!-- Entropy ticks -->
        <g v-for="(tick, index) in entropyTicks" :key="`entropy-${index}`">
          <line 
            :x1="entropyScale(tick)" 
            :y1="height - margin.bottom" 
            :x2="entropyScale(tick)" 
            :y2="height - margin.bottom + 6" 
            stroke="#374151" 
            stroke-width="1"
          />
          <text 
            :x="entropyScale(tick)" 
            :y="height - margin.bottom + 18" 
            text-anchor="middle" 
            class="text-xs fill-gray-600"
          >
            {{ tick.toFixed(1) }}
          </text>
        </g>
        
        <!-- Pressure ticks (log scale) -->
        <g v-for="(tick, index) in pressureTicks" :key="`pressure-${index}`">
          <line 
            :x1="margin.left - 6" 
            :y1="pressureScale(tick)" 
            :x2="margin.left" 
            :y2="pressureScale(tick)" 
            stroke="#374151" 
            stroke-width="1"
          />
          <text 
            :x="margin.left - 10" 
            :y="pressureScale(tick) + 4" 
            text-anchor="end" 
            class="text-xs fill-gray-600"
          >
            {{ tick.toFixed(2) }}
          </text>
        </g>
      </g>
      
      <!-- Saturation Dome -->
      <g class="saturation-dome">
        <path 
          :d="saturationDomePath" 
          fill="rgba(59, 130, 246, 0.1)" 
          stroke="#3b82f6" 
          stroke-width="2" 
          fill-rule="evenodd"
        />
        <text 
          :x="width - 120" 
          :y="30" 
          class="text-xs font-medium fill-blue-600"
        >
          Two-Phase Region (R22)
        </text>
      </g>
      
      <!-- Isotherms -->
      <g class="isotherms">
        <g v-for="(isotherm, index) in isotherms" :key="`isotherm-${index}`">
          <path 
            :d="isotherm.path" 
            fill="none" 
            stroke="#dc2626" 
            stroke-width="1" 
            stroke-dasharray="3,3"
            opacity="0.7"
          />
          <text 
            :x="isotherm.labelX" 
            :y="isotherm.labelY" 
            class="text-xs fill-red-600"
          >
            {{ isotherm.temperature }}°C
          </text>
        </g>
      </g>
      
      <!-- Isoenthalps -->
      <g class="isoenthalps">
        <g v-for="(isoenthalp, index) in isoenthalps" :key="`isoenthalp-${index}`">
          <path 
            :d="isoenthalp.path" 
            fill="none" 
            stroke="#16a34a" 
            stroke-width="1" 
            stroke-dasharray="5,5"
            opacity="0.7"
          />
          <text 
            :x="isoenthalp.labelX" 
            :y="isoenthalp.labelY" 
            class="text-xs fill-green-600"
          >
            {{ isoenthalp.enthalpy }}
          </text>
        </g>
      </g>
      
      <!-- Quality Lines -->
      <g class="quality-lines">
        <g v-for="(qualityLine, index) in qualityLines" :key="`quality-${index}`">
          <path 
            :d="qualityLine.path" 
            fill="none" 
            stroke="#6b7280" 
            stroke-width="1" 
            stroke-dasharray="2,2"
            opacity="0.6"
          />
          <text 
            :x="qualityLine.labelX" 
            :y="qualityLine.labelY" 
            class="text-xs fill-gray-600"
          >
            x={{ qualityLine.quality }}
          </text>
        </g>
      </g>
      
      <!-- Cycle Points from Kafka Data with hover effects -->
      <g class="cycle-points" v-if="kafkaData">
        <g v-for="(point, index) in cyclePoints" :key="`cycle-${index}`">
          <circle 
            :cx="entropyScale(point.entropy)" 
            :cy="pressureScale(point.pressure / 1000)" 
            r="8" 
            :fill="point.color" 
            stroke="white" 
            stroke-width="3"
            class="cursor-pointer transition-all duration-200 hover:r-10"
            @mouseover="showPointTooltip(point, index)"
            @mouseout="hidePointTooltip"
            @click="selectCyclePoint(point)"
          />
          <text 
            :x="entropyScale(point.entropy) + 12" 
            :y="pressureScale(point.pressure / 1000) - 10" 
            class="text-sm font-bold pointer-events-none"
            :fill="point.color"
          >
            {{ point.label }}
          </text>
          <text 
            :x="entropyScale(point.entropy) + 12" 
            :y="pressureScale(point.pressure / 1000) + 6" 
            class="text-xs pointer-events-none"
            :fill="point.color"
          >
            {{ point.description }}
          </text>
        </g>
        
        <!-- Tooltip for selected point -->
        <g v-if="selectedPoint" :transform="`translate(${tooltipPosition.x}, ${tooltipPosition.y})`">
          <rect x="0" y="0" width="160" height="80" fill="rgba(0,0,0,0.8)" rx="4"/>
          <text x="8" y="15" class="text-xs fill-white font-bold">{{ selectedPoint.description }}</text>
          <text x="8" y="30" class="text-xs fill-white">Entropy: {{ selectedPoint.entropy.toFixed(2) }} kJ/(kg·K)</text>
          <text x="8" y="45" class="text-xs fill-white">Pressure: {{ (selectedPoint.pressure/100).toFixed(1) }} bar</text>
          <text x="8" y="60" class="text-xs fill-white">Temperature: {{ getPointTemperature(selectedPoint) }}°C</text>
          <text x="8" y="75" class="text-xs fill-white">Live from Kafka</text>
        </g>
      </g>
      
      <!-- Legend with enhanced information -->
      <g class="legend" transform="translate(20, 30)">
        <rect x="0" y="0" width="220" height="160" fill="white" stroke="#d1d5db" rx="4" opacity="0.95"/>
        <text x="10" y="15" class="text-sm font-bold fill-gray-800">S-p Diagram {{ fluid }}</text>
        
        <line x1="10" y1="25" x2="30" y2="25" stroke="#3b82f6" stroke-width="2"/>
        <text x="35" y="29" class="text-xs fill-gray-700">Saturation Dome</text>
        
        <line x1="10" y1="40" x2="30" y2="40" stroke="#dc2626" stroke-width="1" stroke-dasharray="3,3"/>
        <text x="35" y="44" class="text-xs fill-gray-700">Isotherms (T=const)</text>
        
        <line x1="10" y1="55" x2="30" y2="55" stroke="#16a34a" stroke-width="1" stroke-dasharray="5,5"/>
        <text x="35" y="59" class="text-xs fill-gray-700">Isoenthalps (h=const)</text>
        
        <line x1="10" y1="70" x2="30" y2="70" stroke="#6b7280" stroke-width="1" stroke-dasharray="2,2"/>
        <text x="35" y="74" class="text-xs fill-gray-700">Quality Lines (x=const)</text>
        
        <circle cx="20" cy="85" r="4" fill="#ef4444"/>
        <text x="35" y="89" class="text-xs fill-gray-700">Cycle Points (Live)</text>
        
        <text x="10" y="105" class="text-xs fill-gray-600 font-medium">Real-time Kafka Data:</text>
        <text x="10" y="118" class="text-xs fill-gray-600">P_High: {{ getKafkaPressureHigh() }} bar</text>
        <text x="10" y="131" class="text-xs fill-gray-600">P_Low: {{ getKafkaPressureLow() }} bar</text>
        <text x="10" y="144" class="text-xs fill-gray-600">Installation: FRIGO-UNITE-001</text>
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

const emit = defineEmits(['diagram-ready', 'point-selected'])

const svgContainer = ref(null)
const selectedPoint = ref(null)
const tooltipPosition = ref({ x: 0, y: 0 })

const margin = {
  top: 40,
  right: 40,
  bottom: 60,
  left: 80
}

// Entropy scale (linear)
const entropyScale = computed(() => {
  const domain = [0.8, 2.2] // kJ/(kg·K) for R22
  const range = [margin.left, props.width - margin.right]
  
  return (value) => {
    const normalized = (value - domain[0]) / (domain[1] - domain[0])
    return range[0] + normalized * (range[1] - range[0])
  }
})

// Pressure scale (logarithmic)
const pressureScale = computed(() => {
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
const entropyTicks = [0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]
const pressureTicks = [0.1, 0.2, 0.5, 1.0, 2.0]

// Saturation dome path for R22
const saturationDomePath = computed(() => {
  const points = []
  
  // Simplified saturation curve for R22
  const liquidLine = [
    { s: 1.0, p: 0.15 }, { s: 1.1, p: 0.3 }, { s: 1.2, p: 0.6 },
    { s: 1.3, p: 1.0 }, { s: 1.4, p: 1.6 }, { s: 1.5, p: 2.4 }
  ]
  
  const vaporLine = [
    { s: 1.8, p: 0.15 }, { s: 1.85, p: 0.3 }, { s: 1.9, p: 0.6 },
    { s: 1.95, p: 1.0 }, { s: 2.0, p: 1.6 }, { s: 2.1, p: 2.4 }
  ]
  
  let path = `M ${entropyScale.value(liquidLine[0].s)} ${pressureScale.value(liquidLine[0].p)}`
  
  // Draw liquid line
  for (let i = 1; i < liquidLine.length; i++) {
    path += ` L ${entropyScale.value(liquidLine[i].s)} ${pressureScale.value(liquidLine[i].p)}`
  }
  
  // Draw vapor line (reverse order)
  for (let i = vaporLine.length - 1; i >= 0; i--) {
    path += ` L ${entropyScale.value(vaporLine[i].s)} ${pressureScale.value(vaporLine[i].p)}`
  }
  
  path += ' Z'
  return path
})

// Isotherms
const isotherms = computed(() => {
  const temperatures = [-20, 0, 20, 40, 60]
  
  return temperatures.map(temp => {
    const points = []
    for (let s = 0.8; s <= 2.2; s += 0.1) {
      // Simplified pressure calculation for isotherm
      const p = 0.1 + Math.exp((s - 1.0) * 2 + (temp + 20) * 0.02)
      if (p <= 2.5) {
        points.push({ s, p })
      }
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${entropyScale.value(points[0].s)} ${pressureScale.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${entropyScale.value(points[i].s)} ${pressureScale.value(points[i].p)}`
      }
    }
    
    return {
      temperature: temp,
      path,
      labelX: props.width - 60,
      labelY: points.length > 0 ? pressureScale.value(points[points.length - 1].p) : 100
    }
  })
})

// Isoenthalps
const isoenthalps = computed(() => {
  const enthalpies = [200, 250, 300, 350, 400]
  
  return enthalpies.map(h => {
    const points = []
    for (let s = 0.8; s <= 2.2; s += 0.1) {
      // Simplified pressure calculation for isoenthalp
      const p = 0.2 + Math.exp((h - 250) * 0.008 + (s - 1.5) * 1.5)
      if (p <= 2.5 && p >= 0.1) {
        points.push({ s, p })
      }
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${entropyScale.value(points[0].s)} ${pressureScale.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${entropyScale.value(points[i].s)} ${pressureScale.value(points[i].p)}`
      }
    }
    
    return {
      enthalpy: h,
      path,
      labelX: points.length > 0 ? entropyScale.value(points[0].s) + 10 : 100,
      labelY: points.length > 0 ? pressureScale.value(points[0].p) - 5 : 100
    }
  })
})

// Quality lines
const qualityLines = computed(() => {
  const qualities = [0.1, 0.3, 0.5, 0.7, 0.9]
  
  return qualities.map(x => {
    const points = []
    // Simplified quality line calculation
    for (let p = 0.15; p <= 2.0; p += 0.1) {
      const s_liquid = 1.0 + p * 0.3
      const s_vapor = 1.8 + p * 0.15
      const s = s_liquid + x * (s_vapor - s_liquid)
      points.push({ s, p })
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${entropyScale.value(points[0].s)} ${pressureScale.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${entropyScale.value(points[i].s)} ${pressureScale.value(points[i].p)}`
      }
    }
    
    return {
      quality: x,
      path,
      labelX: points.length > 0 ? entropyScale.value(points[Math.floor(points.length / 2)].s) : 100,
      labelY: points.length > 0 ? pressureScale.value(points[Math.floor(points.length / 2)].p) : 100
    }
  })
})

// Cycle points from Kafka data
const cyclePoints = computed(() => {
  if (!props.kafkaData) return []
  
  const data = props.kafkaData
  
  // Calculate entropy and pressure for cycle points
  const points = [
    {
      label: '1',
      entropy: 1.7, // Simplified entropy at evaporator exit
      pressure: (data.pressure_low || 2.5) * 100, // Convert bar to kPa
      color: '#ef4444',
      description: 'Evaporator Exit'
    },
    {
      label: '2',
      entropy: 1.8, // Simplified entropy at compressor exit
      pressure: (data.pressure_high || 12.0) * 100, // Convert bar to kPa
      color: '#f59e0b',
      description: 'Compressor Exit'
    },
    {
      label: '3',
      entropy: 1.3, // Simplified entropy at condenser exit
      pressure: (data.pressure_high || 12.0) * 100, // Convert bar to kPa
      color: '#10b981',
      description: 'Condenser Exit'
    },
    {
      label: '4',
      entropy: 1.3, // Simplified entropy at expansion valve exit
      pressure: (data.pressure_low || 2.5) * 100, // Convert bar to kPa
      color: '#3b82f6',
      description: 'Expansion Valve Exit'
    }
  ]
  
  return points
})

// Helper functions for legend
const getKafkaPressureHigh = () => {
  return props.kafkaData?.pressure_high?.toFixed(1) || '12.0'
}

const getKafkaPressureLow = () => {
  return props.kafkaData?.pressure_low?.toFixed(1) || '2.5'
}

// Interactive methods
const showPointTooltip = (point, index) => {
  selectedPoint.value = point
  tooltipPosition.value = {
    x: entropyScale.value(point.entropy) + 20,
    y: pressureScale.value(point.pressure / 1000) - 40
  }
}

const hidePointTooltip = () => {
  selectedPoint.value = null
}

const selectCyclePoint = (point) => {
  emit('point-selected', point)
  console.log('Selected cycle point:', point)
}

const getPointTemperature = (point) => {
  // Simplified temperature calculation based on point type
  if (point.label === '1') return props.kafkaData?.temp_aspiration?.toFixed(1) || '5.0'
  if (point.label === '2') return props.kafkaData?.temp_refoulement?.toFixed(1) || '65.0'
  if (point.label === '3') return props.kafkaData?.temp_condenser?.toFixed(1) || '40.0'
  if (point.label === '4') return props.kafkaData?.temp_evaporator?.toFixed(1) || '-10.0'
  return 'N/A'
}

onMounted(() => {
  emit('diagram-ready', {
    type: 'sp',
    fluid: props.fluid,
    cyclePoints: cyclePoints.value
  })
})

watch(() => props.kafkaData, () => {
  emit('diagram-ready', {
    type: 'sp',
    fluid: props.fluid,
    cyclePoints: cyclePoints.value
  })
}, { deep: true })
</script>

<style scoped>
.sp-diagram-container {
  @apply w-full h-full;
}

.sp-diagram {
  @apply shadow-sm;
}

.cycle-points circle {
  transition: all 0.2s ease-in-out;
}

.cycle-points circle:hover {
  r: 10;
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}

.isotherms path,
.isoenthalps path,
.quality-lines path {
  transition: opacity 0.2s ease-in-out;
}

.isotherms path:hover,
.isoenthalps path:hover,
.quality-lines path:hover {
  opacity: 1 !important;
  stroke-width: 2;
}

.legend {
  transition: opacity 0.2s ease-in-out;
}

.legend:hover {
  opacity: 1;
}
</style>
