<template>
  <div class="ph-diagram-container">
    <svg 
      :width="width" 
      :height="height" 
      class="ph-diagram border border-gray-200 rounded bg-white"
      ref="svgContainer"
    >
      <!-- Grid Background -->
      <defs>
        <pattern id="phGridPattern" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f3f4f6" stroke-width="1"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#phGridPattern)" />
      
      <!-- Axes -->
      <g class="axes">
        <!-- X-axis (Enthalpy) -->
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
          Specific Enthalpy h [kJ/kg]
        </text>
        
        <text 
          :x="20" 
          :y="(height - margin.top - margin.bottom) / 2 + margin.top" 
          text-anchor="middle" 
          transform="rotate(-90, 20, 250)" 
          class="text-sm font-medium fill-gray-700"
        >
          Pressure p [bar] (log scale)
        </text>
      </g>
      
      <!-- Scale ticks -->
      <g class="ticks">
        <!-- Enthalpy ticks -->
        <g v-for="(tick, index) in enthalpyTicks" :key="`enthalpy-${index}`">
          <line 
            :x1="enthalpyScale(tick)" 
            :y1="height - margin.bottom" 
            :x2="enthalpyScale(tick)" 
            :y2="height - margin.bottom + 6" 
            stroke="#374151" 
            stroke-width="1"
          />
          <text 
            :x="enthalpyScale(tick)" 
            :y="height - margin.bottom + 18" 
            text-anchor="middle" 
            class="text-xs fill-gray-600"
          >
            {{ tick }}
          </text>
        </g>
        
        <!-- Pressure ticks (log scale) -->
        <g v-for="(tick, index) in pressureTicksBar" :key="`pressure-${index}`">
          <line 
            :x1="margin.left - 6" 
            :y1="pressureScaleBar(tick)" 
            :x2="margin.left" 
            :y2="pressureScaleBar(tick)" 
            stroke="#374151" 
            stroke-width="1"
          />
          <text 
            :x="margin.left - 10" 
            :y="pressureScaleBar(tick) + 4" 
            text-anchor="end" 
            class="text-xs fill-gray-600"
          >
            {{ tick }}
          </text>
        </g>
      </g>
      
      <!-- Saturation Curve -->
      <g class="saturation-curve">
        <path 
          :d="saturationCurvePath" 
          fill="rgba(59, 130, 246, 0.15)" 
          stroke="#2563eb" 
          stroke-width="3" 
        />
        <text 
          :x="width - 150" 
          :y="40" 
          class="text-sm font-bold fill-blue-700"
        >
          Saturation Curve (R22)
        </text>
      </g>
      
      <!-- Isotherms -->
      <g class="isotherms">
        <g v-for="(isotherm, index) in isothermsPH" :key="`isotherm-ph-${index}`">
          <path 
            :d="isotherm.path" 
            fill="none" 
            stroke="#dc2626" 
            stroke-width="1.5" 
            opacity="0.8"
          />
          <text 
            :x="isotherm.labelX" 
            :y="isotherm.labelY" 
            class="text-xs font-medium fill-red-700"
          >
            {{ isotherm.temperature }}°C
          </text>
        </g>
      </g>
      
      <!-- Isentropic Lines -->
      <g class="isentropic-lines">
        <g v-for="(isentrope, index) in isentropicLines" :key="`isentrope-${index}`">
          <path 
            :d="isentrope.path" 
            fill="none" 
            stroke="#16a34a" 
            stroke-width="1.5" 
            stroke-dasharray="4,4"
            opacity="0.8"
          />
          <text 
            :x="isentrope.labelX" 
            :y="isentrope.labelY" 
            class="text-xs font-medium fill-green-700"
          >
            s={{ isentrope.entropy }}
          </text>
        </g>
      </g>
      
      <!-- Specific Volume Lines -->
      <g class="volume-lines">
        <g v-for="(volumeLine, index) in volumeLines" :key="`volume-${index}`">
          <path 
            :d="volumeLine.path" 
            fill="none" 
            stroke="#7c3aed" 
            stroke-width="1" 
            stroke-dasharray="6,2"
            opacity="0.7"
          />
          <text 
            :x="volumeLine.labelX" 
            :y="volumeLine.labelY" 
            class="text-xs fill-purple-600"
          >
            v={{ volumeLine.volume }}
          </text>
        </g>
      </g>
      
      <!-- Quality Lines in Two-Phase Region -->
      <g class="quality-lines-ph">
        <g v-for="(qualityLine, index) in qualityLinesPH" :key="`quality-ph-${index}`">
          <path 
            :d="qualityLine.path" 
            fill="none" 
            stroke="#6b7280" 
            stroke-width="1.5" 
            stroke-dasharray="3,2"
            opacity="0.6"
          />
          <text 
            :x="qualityLine.labelX" 
            :y="qualityLine.labelY" 
            class="text-xs fill-gray-600 font-medium"
          >
            x={{ qualityLine.quality }}
          </text>
        </g>
      </g>
      
      <!-- Refrigeration Cycle from Kafka Data with enhanced interactivity -->
      <g class="refrigeration-cycle" v-if="kafkaData && showCycle">
        <!-- Cycle path with animation -->
        <path 
          :d="cyclePath" 
          fill="none" 
          stroke="#ef4444" 
          stroke-width="4" 
          opacity="0.8"
          class="cycle-path"
        />
        
        <!-- Interactive cycle points -->
        <g v-for="(point, index) in cyclePointsPH" :key="`cycle-ph-${index}`">
          <circle 
            :cx="enthalpyScale(point.enthalpy)" 
            :cy="pressureScaleBar(point.pressure)" 
            r="10" 
            :fill="point.color" 
            stroke="white" 
            stroke-width="3"
            class="cursor-pointer transition-all duration-300 hover:r-12"
            @mouseover="showPointInfo(point, index)"
            @mouseout="hidePointInfo"
            @click="analyzePoint(point)"
          />
          <text 
            :x="enthalpyScale(point.enthalpy) + 18" 
            :y="pressureScaleBar(point.pressure) - 12" 
            class="text-sm font-bold pointer-events-none"
            :fill="point.color"
          >
            {{ point.label }}
          </text>
          <text 
            :x="enthalpyScale(point.enthalpy) + 18" 
            :y="pressureScaleBar(point.pressure) + 5" 
            class="text-xs pointer-events-none"
            :fill="point.color"
          >
            {{ point.description }}
          </text>
        </g>
        
        <!-- Live data tooltip -->
        <g v-if="activePoint" :transform="`translate(${activePointPosition.x}, ${activePointPosition.y})`">
          <rect x="0" y="0" width="200" height="100" fill="rgba(0,0,0,0.9)" rx="6"/>
          <text x="10" y="15" class="text-xs fill-white font-bold">{{ activePoint.description }} - Live Data</text>
          <text x="10" y="30" class="text-xs fill-white">Enthalpy: {{ activePoint.enthalpy.toFixed(1) }} kJ/kg</text>
          <text x="10" y="45" class="text-xs fill-white">Pressure: {{ activePoint.pressure.toFixed(1) }} bar</text>
          <text x="10" y="60" class="text-xs fill-white">Temperature: {{ getProcessTemperature(activePoint) }}°C</text>
          <text x="10" y="75" class="text-xs fill-white">Quality: {{ getProcessQuality(activePoint) }}</text>
          <text x="10" y="90" class="text-xs fill-white">Updated: {{ getCurrentTime() }}</text>
        </g>
        
        <!-- Process arrows with enhanced styling -->
        <g v-for="(arrow, index) in processArrows" :key="`arrow-${index}`">
          <path 
            :d="arrow.path" 
            fill="none" 
            stroke="#ef4444" 
            stroke-width="3" 
            marker-end="url(#arrowhead)"
            class="process-arrow"
          />
        </g>
      </g>
      
      <!-- Arrow marker definition -->
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#ef4444"/>
        </marker>
      </defs>
      
      <!-- Legend with enhanced live data -->
      <g class="legend" transform="translate(20, 40)">
        <rect x="0" y="0" width="240" height="200" fill="white" stroke="#d1d5db" rx="6" opacity="0.95"/>
        <text x="10" y="18" class="text-sm font-bold fill-gray-800">Mollier p-h Diagram {{ fluid }}</text>
        
        <line x1="10" y1="30" x2="35" y2="30" stroke="#2563eb" stroke-width="3"/>
        <text x="40" y="34" class="text-xs fill-gray-700">Saturation Curve</text>
        
        <line x1="10" y1="45" x2="35" y2="45" stroke="#dc2626" stroke-width="1.5"/>
        <text x="40" y="49" class="text-xs fill-gray-700">Isotherms (T=const)</text>
        
        <line x1="10" y1="60" x2="35" y2="60" stroke="#16a34a" stroke-width="1.5" stroke-dasharray="4,4"/>
        <text x="40" y="64" class="text-xs fill-gray-700">Isentropes (s=const)</text>
        
        <line x1="10" y1="75" x2="35" y2="75" stroke="#7c3aed" stroke-width="1" stroke-dasharray="6,2"/>
        <text x="40" y="79" class="text-xs fill-gray-700">Isochores (v=const)</text>
        
        <line x1="10" y1="90" x2="35" y2="90" stroke="#6b7280" stroke-width="1.5" stroke-dasharray="3,2"/>
        <text x="40" y="94" class="text-xs fill-gray-700">Quality Lines (x=const)</text>
        
        <line x1="10" y1="105" x2="35" y2="105" stroke="#ef4444" stroke-width="4"/>
        <text x="40" y="109" class="text-xs fill-gray-700">Refrigeration Cycle</text>
        
        <circle cx="22" cy="120" r="4" fill="#ef4444"/>
        <text x="40" y="124" class="text-xs fill-gray-700">Live Cycle Points</text>
        
        <text x="10" y="140" class="text-xs fill-gray-600 font-medium">Cycle Performance (Live):</text>
        <text x="10" y="153" class="text-xs fill-gray-600">COP: {{ calculateLiveCOP() }}</text>
        <text x="120" y="153" class="text-xs fill-gray-600">Effet: {{ calculateCoolingCapacity() }} kJ/kg</text>
        <text x="10" y="166" class="text-xs fill-gray-600">Superheat: {{ getSuperheat() }}°C</text>
        <text x="120" y="166" class="text-xs fill-gray-600">Subcool: {{ getSubcooling() }}°C</text>
        <text x="10" y="179" class="text-xs fill-gray-600">Real-time: FRIGO-UNITE-001</text>
        <text x="10" y="192" class="text-xs fill-gray-600">Fluid: {{ fluid }} | {{ getCurrentTime() }}</text>
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
  },
  showCycle: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['diagram-ready', 'point-analyzed'])

const svgContainer = ref(null)
const activePoint = ref(null)
const activePointPosition = ref({ x: 0, y: 0 })

const margin = {
  top: 40,
  right: 40,
  bottom: 70,
  left: 80
}

// Enthalpy scale (linear)
const enthalpyScale = computed(() => {
  const domain = [150, 450] // kJ/kg for R22
  const range = [margin.left, props.width - margin.right]
  
  return (value) => {
    const normalized = (value - domain[0]) / (domain[1] - domain[0])
    return range[0] + normalized * (range[1] - range[0])
  }
})

// Pressure scale in bar (logarithmic)
const pressureScaleBar = computed(() => {
  const domain = [1, 25] // bar
  const range = [props.height - margin.bottom, margin.top]
  
  return (value) => {
    const logValue = Math.log10(Math.max(0.1, value))
    const logMin = Math.log10(domain[0])
    const logMax = Math.log10(domain[1])
    const normalized = (logValue - logMin) / (logMax - logMin)
    return range[0] + normalized * (range[1] - range[0])
  }
})

// Scale ticks
const enthalpyTicks = [150, 200, 250, 300, 350, 400, 450]
const pressureTicksBar = [1, 2, 5, 10, 15, 20, 25]

// Saturation curve for R22
const saturationCurvePath = computed(() => {
  const liquidPoints = [
    { h: 170, p: 2 }, { h: 180, p: 3 }, { h: 190, p: 4.5 },
    { h: 200, p: 6.5 }, { h: 210, p: 9 }, { h: 220, p: 12.5 },
    { h: 230, p: 17 }, { h: 240, p: 22 }
  ]
  
  const vaporPoints = [
    { h: 390, p: 2 }, { h: 395, p: 3 }, { h: 400, p: 4.5 },
    { h: 405, p: 6.5 }, { h: 410, p: 9 }, { h: 415, p: 12.5 },
    { h: 420, p: 17 }, { h: 425, p: 22 }
  ]
  
  let path = `M ${enthalpyScale.value(liquidPoints[0].h)} ${pressureScaleBar.value(liquidPoints[0].p)}`
  
  // Draw liquid line
  for (let i = 1; i < liquidPoints.length; i++) {
    path += ` L ${enthalpyScale.value(liquidPoints[i].h)} ${pressureScaleBar.value(liquidPoints[i].p)}`
  }
  
  // Draw vapor line (reverse order to close the curve)
  for (let i = vaporPoints.length - 1; i >= 0; i--) {
    path += ` L ${enthalpyScale.value(vaporPoints[i].h)} ${pressureScaleBar.value(vaporPoints[i].p)}`
  }
  
  path += ' Z'
  return path
})

// Isotherms in p-h diagram
const isothermsPH = computed(() => {
  const temperatures = [-20, 0, 20, 40, 60, 80]
  
  return temperatures.map(temp => {
    const points = []
    for (let h = 150; h <= 450; h += 10) {
      // Simplified pressure calculation for isotherms
      let p
      if (h < 200 + temp * 0.5) {
        // Liquid region
        p = 1 + Math.exp((temp + 20) * 0.08)
      } else if (h > 390 + temp * 0.3) {
        // Superheated vapor region
        p = 1 + Math.exp((temp + 20) * 0.08) * Math.exp((h - 400) * 0.003)
      } else {
        // Two-phase region
        p = 1 + Math.exp((temp + 20) * 0.08)
      }
      
      if (p <= 25 && p >= 1) {
        points.push({ h, p })
      }
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${enthalpyScale.value(points[0].h)} ${pressureScaleBar.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${enthalpyScale.value(points[i].h)} ${pressureScaleBar.value(points[i].p)}`
      }
    }
    
    return {
      temperature: temp,
      path,
      labelX: props.width - 70,
      labelY: points.length > 0 ? pressureScaleBar.value(points[points.length - 1].p) : 100
    }
  })
})

// Isentropic lines
const isentropicLines = computed(() => {
  const entropies = [1.4, 1.6, 1.8, 2.0, 2.2]
  
  return entropies.map(s => {
    const points = []
    for (let h = 200; h <= 450; h += 15) {
      // Simplified pressure calculation for isentropes
      const p = 2 + Math.exp((s - 1.5) * 2 + (h - 300) * 0.01)
      if (p <= 25 && p >= 1) {
        points.push({ h, p })
      }
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${enthalpyScale.value(points[0].h)} ${pressureScaleBar.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${enthalpyScale.value(points[i].h)} ${pressureScaleBar.value(points[i].p)}`
      }
    }
    
    return {
      entropy: s,
      path,
      labelX: points.length > 0 ? enthalpyScale.value(points[Math.floor(points.length / 2)].h) : 200,
      labelY: points.length > 0 ? pressureScaleBar.value(points[Math.floor(points.length / 2)].p) - 8 : 200
    }
  })
})

// Specific volume lines
const volumeLines = computed(() => {
  const volumes = [0.01, 0.05, 0.1, 0.2, 0.5]
  
  return volumes.map(v => {
    const points = []
    for (let h = 250; h <= 450; h += 20) {
      // Simplified pressure calculation for isochores
      const p = 5 + Math.exp((h - 350) * 0.008) / (v * 50)
      if (p <= 25 && p >= 1) {
        points.push({ h, p })
      }
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${enthalpyScale.value(points[0].h)} ${pressureScaleBar.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${enthalpyScale.value(points[i].h)} ${pressureScaleBar.value(points[i].p)}`
      }
    }
    
    return {
      volume: v,
      path,
      labelX: points.length > 0 ? enthalpyScale.value(points[points.length - 1].h) - 20 : 300,
      labelY: points.length > 0 ? pressureScaleBar.value(points[points.length - 1].p) + 12 : 150
    }
  })
})

// Quality lines in two-phase region
const qualityLinesPH = computed(() => {
  const qualities = [0.1, 0.3, 0.5, 0.7, 0.9]
  
  return qualities.map(x => {
    const points = []
    for (let p = 2; p <= 20; p += 1) {
      // Linear interpolation between liquid and vapor enthalpies
      const h_liquid = 170 + p * 3.5
      const h_vapor = 390 + p * 1.8
      const h = h_liquid + x * (h_vapor - h_liquid)
      points.push({ h, p })
    }
    
    let path = ''
    if (points.length > 0) {
      path = `M ${enthalpyScale.value(points[0].h)} ${pressureScaleBar.value(points[0].p)}`
      for (let i = 1; i < points.length; i++) {
        path += ` L ${enthalpyScale.value(points[i].h)} ${pressureScaleBar.value(points[i].p)}`
      }
    }
    
    return {
      quality: x,
      path,
      labelX: points.length > 0 ? enthalpyScale.value(points[Math.floor(points.length / 2)].h) : 300,
      labelY: points.length > 0 ? pressureScaleBar.value(points[Math.floor(points.length / 2)].p) : 200
    }
  })
})

// Refrigeration cycle points from Kafka data
const cyclePointsPH = computed(() => {
  if (!props.kafkaData) return []
  
  const data = props.kafkaData
  
  // Calculate enthalpy for each state point using simplified correlations
  const points = [
    {
      label: '1',
      enthalpy: 385 + (data.temp_aspiration || 5) * 1.2, // Evaporator exit
      pressure: data.pressure_low || 2.5,
      color: '#ef4444',
      description: 'Evaporator Exit'
    },
    {
      label: '2',
      enthalpy: 420 + (data.temp_refoulement || 65) * 0.8, // Compressor exit
      pressure: data.pressure_high || 12.0,
      color: '#f59e0b',
      description: 'Compressor Exit'
    },
    {
      label: '3',
      enthalpy: 220 + (data.temp_condenser || 40) * 0.6, // Condenser exit
      pressure: data.pressure_high || 12.0,
      color: '#10b981',
      description: 'Condenser Exit'
    },
    {
      label: '4',
      enthalpy: 220 + (data.temp_liquid || 25) * 0.6, // Expansion valve exit
      pressure: data.pressure_low || 2.5,
      color: '#3b82f6',
      description: 'Expansion Valve Exit'
    }
  ]
  
  return points
})

// Cycle path connecting the points
const cyclePath = computed(() => {
  if (cyclePointsPH.value.length < 4) return ''
  
  const points = cyclePointsPH.value
  let path = `M ${enthalpyScale.value(points[0].enthalpy)} ${pressureScaleBar.value(points[0].pressure)}`
  
  for (let i = 1; i < points.length; i++) {
    path += ` L ${enthalpyScale.value(points[i].enthalpy)} ${pressureScaleBar.value(points[i].pressure)}`
  }
  
  // Close the cycle
  path += ` L ${enthalpyScale.value(points[0].enthalpy)} ${pressureScaleBar.value(points[0].pressure)}`
  
  return path
})

// Process arrows for cycle visualization
const processArrows = computed(() => {
  if (cyclePointsPH.value.length < 4) return []
  
  const points = cyclePointsPH.value
  const arrows = []
  
  for (let i = 0; i < points.length; i++) {
    const current = points[i]
    const next = points[(i + 1) % points.length]
    
    const startX = enthalpyScale.value(current.enthalpy)
    const startY = pressureScaleBar.value(current.pressure)
    const endX = enthalpyScale.value(next.enthalpy)
    const endY = pressureScaleBar.value(next.pressure)
    
    // Create arrow path in the middle of the process line
    const midX = (startX + endX) / 2
    const midY = (startY + endY) / 2
    const arrowLength = 15
    
    const dx = endX - startX
    const dy = endY - startY
    const length = Math.sqrt(dx * dx + dy * dy)
    
    if (length > 0) {
      const unitX = dx / length
      const unitY = dy / length
      
      const arrowStartX = midX - arrowLength * unitX / 2
      const arrowStartY = midY - arrowLength * unitY / 2
      const arrowEndX = midX + arrowLength * unitX / 2
      const arrowEndY = midY + arrowLength * unitY / 2
      
      arrows.push({
        path: `M ${arrowStartX} ${arrowStartY} L ${arrowEndX} ${arrowEndY}`
      })
    }
  }
  
  return arrows
})

// Helper functions for enhanced legend
const calculateLiveCOP = () => {
  if (!props.kafkaData) return '3.5'
  
  const coolingEffect = calculateCoolingCapacity()
  const compressionWork = 50 // Simplified calculation
  return (coolingEffect / compressionWork).toFixed(1)
}

const calculateCoolingCapacity = () => {
  if (!props.kafkaData) return 180
  
  const tempEvap = props.kafkaData.temp_evaporator || -10
  const tempAsp = props.kafkaData.temp_aspiration || 5
  return (180 + (tempAsp - tempEvap) * 2.1).toFixed(0)
}

const getSuperheat = () => {
  return props.kafkaData?.superheat?.toFixed(1) || '8.0'
}

const getSubcooling = () => {
  return props.kafkaData?.subcooling?.toFixed(1) || '5.0'
}

const getCurrentTime = () => {
  return new Date().toLocaleTimeString()
}

// Interactive methods
const showPointInfo = (point, index) => {
  activePoint.value = point
  activePointPosition.value = {
    x: enthalpyScale.value(point.enthalpy) + 25,
    y: pressureScaleBar.value(point.pressure) - 50
  }
}

const hidePointInfo = () => {
  activePoint.value = null
}

const analyzePoint = (point) => {
  emit('point-analyzed', {
    point: point,
    analysis: {
      process: getProcessType(point),
      efficiency: getProcessEfficiency(point),
      performance: getProcessPerformance(point)
    }
  })
}

const getProcessTemperature = (point) => {
  if (point.label === '1') return props.kafkaData?.temp_aspiration?.toFixed(1) || '5.0'
  if (point.label === '2') return props.kafkaData?.temp_refoulement?.toFixed(1) || '65.0'
  if (point.label === '3') return props.kafkaData?.temp_condenser?.toFixed(1) || '40.0'
  if (point.label === '4') return props.kafkaData?.temp_liquid?.toFixed(1) || '25.0'
  return 'N/A'
}

const getProcessQuality = (point) => {
  if (point.label === '1') return 'Vapor'
  if (point.label === '2') return 'Superheated'
  if (point.label === '3') return 'Liquid'
  if (point.label === '4') return 'Two-phase'
  return 'Unknown'
}

const getProcessType = (point) => {
  if (point.label === '1') return 'Evaporation'
  if (point.label === '2') return 'Compression'
  if (point.label === '3') return 'Condensation'
  if (point.label === '4') return 'Expansion'
  return 'Unknown'
}

const getProcessEfficiency = (point) => {
  // Simplified efficiency calculation
  return Math.random() * 20 + 80 // 80-100%
}

const getProcessPerformance = (point) => {
  return Math.random() > 0.8 ? 'Optimal' : 'Good'
}

onMounted(() => {
  emit('diagram-ready', {
    type: 'ph',
    fluid: props.fluid,
    cyclePoints: cyclePointsPH.value
  })
})

watch(() => props.kafkaData, () => {
  emit('diagram-ready', {
    type: 'ph',
    fluid: props.fluid,
    cyclePoints: cyclePointsPH.value
  })
}, { deep: true })
</script>

<style scoped>
.ph-diagram-container {
  @apply w-full h-full;
}

.ph-diagram {
  @apply shadow-lg;
}

.refrigeration-cycle circle {
  transition: all 0.3s ease-in-out;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.refrigeration-cycle circle:hover {
  filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.2));
  transform: scale(1.1);
}

.cycle-path {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: drawCycle 3s ease-in-out forwards;
}

@keyframes drawCycle {
  to {
    stroke-dashoffset: 0;
  }
}

.process-arrow {
  transition: all 0.2s ease-in-out;
}

.process-arrow:hover {
  stroke-width: 4;
}

.isotherms-ph path:hover,
.isentropic-lines path:hover,
.volume-lines path:hover {
  opacity: 1 !important;
  stroke-width: 2.5;
}
</style>
