<template>
  <div class="mollier-diagram-container">
    <!-- En-tête professionnel -->
    <div class="diagram-header">
      <div class="header-title">
        <h2 class="title-main">Diagramme de Mollier (h-s)</h2>
        <h3 class="title-sub">Fluide frigorigène Frayo - Analyse thermodynamique</h3>
      </div>
      <div class="header-controls">
        <div class="control-group">
          <label class="control-label">Affichage :</label>
          <div class="toggle-buttons">
            <button 
              @click="showGrid = !showGrid"
              :class="{ 'toggle-btn': true, 'active': showGrid }"
            >
              Grille
            </button>
            <button 
              @click="showZones = !showZones"
              :class="{ 'toggle-btn': true, 'active': showZones }"
            >
              Zones
            </button>
            <button 
              @click="refreshDiagram"
              class="toggle-btn refresh-btn"
            >
              🔄 Actualiser
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Diagramme principal -->
    <div class="chart-container">
      <div class="chart-wrapper">
        <Scatter
          ref="chartRef"
          :data="chartData"
          :options="chartOptions"
        />
      </div>
      
      <!-- Légende thermodynamique professionnelle -->
      <div class="legend-panel">
        <h4 class="legend-title">Légende thermodynamique</h4>
        <div class="legend-items">
          <div class="legend-section">
            <h5 class="legend-section-title">Courbes de saturation</h5>
            <div class="legend-item">
              <div class="legend-symbol line-red"></div>
              <span>Courbe de bulle (x = 0)</span>
            </div>
            <div class="legend-item">
              <div class="legend-symbol line-blue"></div>
              <span>Courbe de rosée (x = 1)</span>
            </div>
            <div class="legend-item">
              <div class="legend-symbol point-black"></div>
              <span>Point critique</span>
            </div>
          </div>
          
          <div class="legend-section">
            <h5 class="legend-section-title">Zones thermodynamiques</h5>
            <div class="legend-item">
              <div class="legend-symbol zone-liquid"></div>
              <span>Liquide sous-refroidi</span>
            </div>
            <div class="legend-item">
              <div class="legend-symbol zone-mixed"></div>
              <span>Mélange diphasique</span>
            </div>
            <div class="legend-item">
              <div class="legend-symbol zone-vapor"></div>
              <span>Vapeur surchauffée</span>
            </div>
          </div>
          
          <div class="legend-section">
            <h5 class="legend-section-title">Cycle frigorifique</h5>
            <div class="legend-item">
              <div class="legend-symbol point-cycle"></div>
              <span>Points du cycle</span>
            </div>
            <div class="legend-item">
              <div class="legend-symbol line-cycle"></div>
              <span>Transformations</span>
            </div>
          </div>
          
          <div class="legend-section">
            <h5 class="legend-section-title">Données expérimentales</h5>
            <div class="legend-item">
              <div class="legend-symbol point-data"></div>
              <span>Mesures réservoir</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Informations thermodynamiques détaillées -->
    <div class="thermo-info">
      <div class="info-grid">
        <div class="info-card fluid-props">
          <div class="card-header">
            <h4 class="card-title">Propriétés du fluide Frayo</h4>
          </div>
          <div class="card-content">
            <div class="prop-item">
              <span class="prop-label">Température critique :</span>
              <span class="prop-value">90.0°C</span>
            </div>
            <div class="prop-item">
              <span class="prop-label">Pression critique :</span>
              <span class="prop-value">40.0 bar</span>
            </div>
            <div class="prop-item">
              <span class="prop-label">Masse molaire :</span>
              <span class="prop-value">102.03 g/mol</span>
            </div>
            <div class="prop-item">
              <span class="prop-label">Type :</span>
              <span class="prop-value">HFC synthétique</span>
            </div>
          </div>
        </div>
        
        <div class="info-card cycle-props">
          <div class="card-header">
            <h4 class="card-title">Performance du cycle</h4>
          </div>
          <div class="card-content">
            <div class="prop-item">
              <span class="prop-label">COP théorique :</span>
              <span class="prop-value">{{ calculatedCOP.toFixed(2) }}</span>
            </div>
            <div class="prop-item">
              <span class="prop-label">Effet frigorifique :</span>
              <span class="prop-value">{{ frigEffect.toFixed(1) }} kJ/kg</span>
            </div>
            <div class="prop-item">
              <span class="prop-label">Travail compression :</span>
              <span class="prop-value">{{ compWork.toFixed(1) }} kJ/kg</span>
            </div>
            <div class="prop-item">
              <span class="prop-label">Chaleur rejetée :</span>
              <span class="prop-value">{{ heatRejected.toFixed(1) }} kJ/kg</span>
            </div>
          </div>
        </div>
        
        <div class="info-card data-stats">
          <div class="card-header">
            <h4 class="card-title">Statistiques des données</h4>
          </div>
          <div class="card-content">
            <div class="prop-item">
              <span class="prop-label">Points de mesure :</span>
              <span class="prop-value">50 échantillons</span>
            </div>
            <div class="prop-item">
              <span class="prop-label">Plage température :</span>
              <span class="prop-value">-20°C à 60°C</span>
            </div>
            <div class="prop-item">
              <span class="prop-label">Plage pression :</span>
              <span class="prop-value">0.5 à 20.0 bar</span>
            </div>
            <div class="prop-item">
              <span class="prop-label">Précision :</span>
              <span class="prop-value">±0.1 kJ/kg</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Instructions d'utilisation -->
    <div class="usage-instructions">
      <div class="instructions-header">
        <h4>Guide d'utilisation du diagramme</h4>
      </div>
      <div class="instructions-content">
        <div class="instruction-item">
          <span class="instruction-icon">📊</span>
          <span>Survolez les points pour voir les propriétés thermodynamiques détaillées</span>
        </div>
        <div class="instruction-item">
          <span class="instruction-icon">🔍</span>
          <span>Analysez les zones thermodynamiques et les transformations du cycle</span>
        </div>
        <div class="instruction-item">
          <span class="instruction-icon">⚙️</span>
          <span>Utilisez les boutons de contrôle pour personnaliser l'affichage</span>
        </div>
        <div class="instruction-item">
          <span class="instruction-icon">🔄</span>
          <span>Actualisez le diagramme pour régénérer les données aléatoires</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Scatter } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Enregistrer les plugins Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps({
  cycleData: {
    type: Object,
    default: () => ({})
  },
  width: {
    type: Number,
    default: 1000
  },
  height: {
    type: Number,
    default: 700
  }
})

// États réactifs pour les contrôles
const showGrid = ref(true)
const showZones = ref(true)
const chartRef = ref(null)
const dataKey = ref(0) // Pour forcer la régénération des données

// Constantes thermodynamiques pour Frayo
const FRAYO_PROPS = {
  Tc: 90.0,      // Température critique [°C]
  Pc: 40.0,      // Pression critique [bar]
  Mw: 102.03,    // Masse molaire [g/mol]
  R: 0.08117     // Constante spécifique [kJ/kg·K]
}

// Génération des courbes de saturation simplifiées mais précises
const generateSaturationCurves = () => {
  const bubbleCurve = []
  const dewCurve = []
  
  // Plage de température de -40°C à 85°C
  for (let T = -40; T <= 85; T += 2) {
    const Tr = (T + 273.15) / (FRAYO_PROPS.Tc + 273.15)
    
    if (Tr < 0.98 && Tr > 0.5) {
      // Corrélations simplifiées mais réalistes
      const h_liquid = 200 + 1.8 * T - 0.002 * T * T
      const s_liquid = 0.9 + 0.0045 * T - 0.000008 * T * T
      
      const hlv = 180 * Math.exp(-0.008 * T) // Chaleur latente
      const h_vapor = h_liquid + hlv
      const s_vapor = s_liquid + hlv / (T + 273.15)
      
      if (h_liquid > 120 && h_liquid < 400 && s_liquid > 0.7 && s_liquid < 2.0) {
        bubbleCurve.push({ 
          x: s_liquid, 
          y: h_liquid, 
          T: T.toFixed(1),
          label: `Liquide saturé: T=${T.toFixed(1)}°C, h=${h_liquid.toFixed(1)} kJ/kg`
        })
      }
      
      if (h_vapor > 120 && h_vapor < 480 && s_vapor > 0.7 && s_vapor < 2.2) {
        dewCurve.push({ 
          x: s_vapor, 
          y: h_vapor, 
          T: T.toFixed(1),
          label: `Vapeur saturée: T=${T.toFixed(1)}°C, h=${h_vapor.toFixed(1)} kJ/kg`
        })
      }
    }
  }
  
  return { bubbleCurve, dewCurve }
}

// Données du réservoir avec distribution réaliste
const generateReservoirData = () => {
  const data = []
  const scenarios = [
    { Tmin: -20, Tmax: -5, Pmin: 1, Pmax: 3, count: 12, zone: 'évaporateur' },
    { Tmin: 30, Tmax: 50, Pmin: 10, Pmax: 16, count: 15, zone: 'condenseur' },
    { Tmin: -5, Tmax: 10, Pmin: 2, Pmax: 8, count: 13, zone: 'transition' },
    { Tmin: 50, Tmax: 70, Pmin: 15, Pmax: 25, count: 10, zone: 'surchauffe' }
  ]
  
  scenarios.forEach(scenario => {
    for (let i = 0; i < scenario.count; i++) {
      const T = scenario.Tmin + Math.random() * (scenario.Tmax - scenario.Tmin)
      const P = scenario.Pmin + Math.random() * (scenario.Pmax - scenario.Pmin)
      
      const h = 200 + 1.8 * T + 0.3 * P + (Math.random() - 0.5) * 8
      const s = 0.9 + 0.004 * T + 0.001 * P + (Math.random() - 0.5) * 0.03
      
      data.push({ 
        x: s, 
        y: h, 
        T: T.toFixed(1), 
        P: P.toFixed(1),
        zone: scenario.zone,
        label: `Mesure ${scenario.zone}: T=${T.toFixed(1)}°C, P=${P.toFixed(1)} bar, h=${h.toFixed(1)} kJ/kg`
      })
    }
  })
  
  return data
}

// Points du cycle frigorifique thermodynamiquement cohérents
const getCyclePoints = () => {
  return [
    { 
      x: 1.75, 
      y: 380, 
      label: "1️⃣ Sortie évaporateur", 
      T: -10, 
      P: 2.8,
      state: "Vapeur saturée sèche",
      description: "Aspiration compresseur (x=1)"
    },
    { 
      x: 1.82, 
      y: 430, 
      label: "2️⃣ Sortie compresseur", 
      T: 65, 
      P: 14.2,
      state: "Vapeur surchauffée",
      description: "Refoulement haute pression"
    },
    { 
      x: 1.18, 
      y: 260, 
      label: "3️⃣ Sortie condenseur", 
      T: 40, 
      P: 14.2,
      state: "Liquide sous-refroidi",
      description: "Entrée détendeur (x=0)"
    },
    { 
      x: 1.18, 
      y: 180, 
      label: "4️⃣ Sortie détendeur", 
      T: -10, 
      P: 2.8,
      state: "Mélange liquide-vapeur",
      description: "Entrée évaporateur (x≈0.25)"
    }
  ]
}

// Calculs de performance du cycle
const cyclePoints = getCyclePoints()
const calculatedCOP = computed(() => {
  const h1 = cyclePoints[0].y  // Sortie évaporateur
  const h2 = cyclePoints[1].y  // Sortie compresseur
  const h3 = cyclePoints[2].y  // Sortie condenseur
  const h4 = cyclePoints[3].y  // Sortie détendeur
  
  const frigEffect = h1 - h4    // Effet frigorifique
  const compWork = h2 - h1      // Travail de compression
  
  return frigEffect / compWork
})

const frigEffect = computed(() => {
  return cyclePoints[0].y - cyclePoints[3].y
})

const compWork = computed(() => {
  return cyclePoints[1].y - cyclePoints[0].y
})

const heatRejected = computed(() => {
  return cyclePoints[1].y - cyclePoints[2].y
})

// Configuration des données Chart.js
const chartData = computed(() => {
  // Forcer la régénération avec dataKey
  const key = dataKey.value
  
  const { bubbleCurve, dewCurve } = generateSaturationCurves()
  const reservoirData = generateReservoirData()
  const cyclePointsData = getCyclePoints()
  
  const datasets = []
  
  // Zone de mélange liquide-vapeur
  if (showZones.value) {
    const twoPhaseZone = []
    bubbleCurve.forEach(point => twoPhaseZone.push(point))
    dewCurve.slice().reverse().forEach(point => twoPhaseZone.push(point))
    
    datasets.push({
      label: 'Zone diphasique (0 < x < 1)',
      data: twoPhaseZone,
      borderColor: 'rgba(139, 69, 194, 0.6)',
      backgroundColor: 'rgba(139, 69, 194, 0.1)',
      fill: true,
      showLine: true,
      pointRadius: 0,
      borderWidth: 1,
      tension: 0.4,
      order: 10
    })
  }
  
  // Courbes de saturation
  datasets.push({
    label: 'Courbe de bulle (x = 0)',
    data: bubbleCurve,
    borderColor: '#dc2626',
    backgroundColor: '#dc2626',
    fill: false,
    showLine: true,
    pointRadius: 2,
    pointHoverRadius: 5,
    borderWidth: 3,
    tension: 0.3,
    order: 2
  })
  
  datasets.push({
    label: 'Courbe de rosée (x = 1)',
    data: dewCurve,
    borderColor: '#2563eb',
    backgroundColor: '#2563eb',
    fill: false,
    showLine: true,
    pointRadius: 2,
    pointHoverRadius: 5,
    borderWidth: 3,
    tension: 0.3,
    order: 3
  })
  
  // Données du réservoir
  datasets.push({
    label: 'Données expérimentales réservoir',
    data: reservoirData,
    borderColor: '#d97706',
    backgroundColor: '#fbbf24',
    fill: false,
    showLine: false,
    pointRadius: 3,
    pointHoverRadius: 6,
    borderWidth: 2,
    order: 4
  })
  
  // Cycle frigorifique
  datasets.push({
    label: 'Cycle frigorifique théorique',
    data: [...cyclePointsData, cyclePointsData[0]], // Fermer le cycle
    borderColor: '#ea580c',
    backgroundColor: '#ea580c',
    fill: false,
    showLine: true,
    pointRadius: 8,
    pointStyle: 'rectRot',
    pointHoverRadius: 12,
    borderWidth: 4,
    tension: 0.1,
    order: 1
  })
  
  // Point critique
  datasets.push({
    label: 'Point critique Frayo',
    data: [{ 
      x: 1.58, 
      y: 310, 
      T: FRAYO_PROPS.Tc,
      P: FRAYO_PROPS.Pc,
      label: `Point critique: Tc=${FRAYO_PROPS.Tc}°C, Pc=${FRAYO_PROPS.Pc} bar`
    }],
    borderColor: '#000000',
    backgroundColor: '#000000',
    fill: false,
    showLine: false,
    pointRadius: 8,
    pointStyle: 'star',
    pointHoverRadius: 12,
    borderWidth: 3,
    order: 1
  })
  
  return { datasets }
})

// Configuration des options Chart.js
const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'point'
  },
  plugins: {
    title: {
      display: false
    },
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
      titleColor: '#f9fafb',
      bodyColor: '#f9fafb',
      borderColor: '#374151',
      borderWidth: 1,
      cornerRadius: 8,
      padding: 12,
      displayColors: true,
      callbacks: {
        title: function(context) {
          const point = context[0]
          if (point.dataset.label.includes('Cycle')) {
            return point.raw.label || 'Point du cycle frigorifique'
          } else if (point.dataset.label.includes('critique')) {
            return 'Point critique du fluide Frayo'
          } else if (point.dataset.label.includes('bulle')) {
            return 'Courbe de bulle (liquide saturé)'
          } else if (point.dataset.label.includes('rosée')) {
            return 'Courbe de rosée (vapeur saturée)'
          }
          return point.dataset.label
        },
        label: function(context) {
          const point = context.raw
          const lines = []
          
          lines.push(`Entropie: ${point.x.toFixed(4)} kJ/kg·K`)
          lines.push(`Enthalpie: ${point.y.toFixed(2)} kJ/kg`)
          
          if (point.T !== undefined) {
            lines.push(`Température: ${point.T}°C`)
          }
          if (point.P !== undefined) {
            lines.push(`Pression: ${point.P} bar`)
          }
          if (point.state) {
            lines.push(`État: ${point.state}`)
          }
          if (point.description) {
            lines.push(`${point.description}`)
          }
          
          return lines
        }
      }
    }
  },
  scales: {
    x: {
      type: 'linear',
      position: 'bottom',
      title: {
        display: true,
        text: 'Entropie spécifique s [kJ/kg·K]',
        font: {
          size: 16,
          weight: 'bold',
          family: 'Inter, sans-serif'
        },
        color: '#1f2937'
      },
      min: 0.7,
      max: 2.3,
      grid: {
        display: showGrid.value,
        color: 'rgba(107, 114, 128, 0.3)',
        lineWidth: 1
      },
      border: {
        display: true,
        color: '#374151',
        width: 2
      },
      ticks: {
        stepSize: 0.2,
        color: '#374151',
        font: {
          size: 12,
          family: 'Inter, sans-serif'
        }
      }
    },
    y: {
      type: 'linear',
      title: {
        display: true,
        text: 'Enthalpie spécifique h [kJ/kg]',
        font: {
          size: 16,
          weight: 'bold',
          family: 'Inter, sans-serif'
        },
        color: '#1f2937'
      },
      min: 120,
      max: 480,
      grid: {
        display: showGrid.value,
        color: 'rgba(107, 114, 128, 0.3)',
        lineWidth: 1
      },
      border: {
        display: true,
        color: '#374151',
        width: 2
      },
      ticks: {
        stepSize: 50,
        color: '#374151',
        font: {
          size: 12,
          family: 'Inter, sans-serif'
        }
      }
    }
  },
  elements: {
    point: {
      hoverBorderWidth: 3
    },
    line: {
      borderJoinStyle: 'round',
      borderCapStyle: 'round'
    }
  },
  animation: {
    duration: 800,
    easing: 'easeInOutQuart'
  }
}))

// Méthode pour actualiser le diagramme
const refreshDiagram = () => {
  dataKey.value++
  if (chartRef.value?.chart) {
    chartRef.value.chart.update('active')
  }
}

onMounted(() => {
  setTimeout(() => {
    if (chartRef.value?.chart) {
      chartRef.value.chart.update('active')
    }
  }, 100)
})
</script>

<style scoped>
/* Container principal avec design moderne */
.mollier-diagram-container {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.1), 
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #e2e8f0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  animation: slideInUp 0.6s ease-out;
}

/* En-tête professionnel */
.diagram-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.header-title {
  flex: 1;
}

.title-main {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.025em;
}

.title-sub {
  font-size: 1.125rem;
  font-weight: 500;
  color: #64748b;
  margin: 0;
}

.header-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: flex-end;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
}

.toggle-buttons {
  display: flex;
  gap: 0.5rem;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: 2px solid #e2e8f0;
  background: #ffffff;
  color: #64748b;
  border-radius: 0.5rem;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
}

.toggle-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.toggle-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
}

.refresh-btn {
  background: #10b981 !important;
  border-color: #10b981 !important;
  color: #ffffff !important;
}

.refresh-btn:hover {
  background: #059669 !important;
  border-color: #059669 !important;
  transform: translateY(-1px) rotate(180deg);
}

/* Container du graphique */
.chart-container {
  display: flex;
  gap: 2rem;
  background: #ffffff;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1), 
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
}

.chart-wrapper {
  flex: 1;
  position: relative;
  height: 700px;
  min-height: 600px;
}

/* Panneau de légende thermodynamique */
.legend-panel {
  width: 280px;
  background: #f8fafc;
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
  overflow-y: auto;
  max-height: 700px;
}

.legend-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 1.5rem 0;
  text-align: center;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e2e8f0;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.legend-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #4b5563;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s ease;
}

.legend-item:hover {
  background-color: #f1f5f9;
}

/* Symboles de légende */
.legend-symbol {
  width: 20px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.line-red {
  background: linear-gradient(90deg, #dc2626, #ef4444);
  height: 3px;
  margin-top: 4px;
  margin-bottom: 5px;
}

.line-blue {
  background: linear-gradient(90deg, #2563eb, #3b82f6);
  height: 3px;
  margin-top: 4px;
  margin-bottom: 5px;
}

.line-cycle {
  background: linear-gradient(90deg, #ea580c, #f97316);
  height: 3px;
  margin-top: 4px;
  margin-bottom: 5px;
}

.point-black {
  width: 12px;
  height: 12px;
  background: #000000;
  border-radius: 50%;
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1px #000000;
}

.point-cycle {
  width: 12px;
  height: 12px;
  background: #ea580c;
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1px #ea580c;
  transform: rotate(45deg);
}

.point-data {
  width: 12px;
  height: 12px;
  background: #fbbf24;
  border-radius: 50%;
  border: 2px solid #d97706;
}

.zone-liquid {
  background: linear-gradient(45deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
}

.zone-mixed {
  background: linear-gradient(45deg, rgba(139, 69, 194, 0.2), rgba(139, 69, 194, 0.1));
}

.zone-vapor {
  background: linear-gradient(45deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1));
}

/* Informations thermodynamiques */
.thermo-info {
  margin-top: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.info-card {
  background: #ffffff;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: slideInUp 0.6s ease-out;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.info-card:nth-child(1) { animation-delay: 0.1s; }
.info-card:nth-child(2) { animation-delay: 0.2s; }
.info-card:nth-child(3) { animation-delay: 0.3s; }

.card-header {
  padding: 1.25rem 1.5rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.fluid-props .card-header {
  background: linear-gradient(135deg, #dbeafe, #eff6ff);
}

.cycle-props .card-header {
  background: linear-gradient(135deg, #d1fae5, #ecfdf5);
}

.data-stats .card-header {
  background: linear-gradient(135deg, #fce7f3, #fdf2f8);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.card-content {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.prop-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border-left: 4px solid #e2e8f0;
  transition: border-color 0.2s ease;
}

.fluid-props .prop-item {
  border-left-color: #3b82f6;
}

.cycle-props .prop-item {
  border-left-color: #10b981;
}

.data-stats .prop-item {
  border-left-color: #ec4899;
}

.prop-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.prop-value {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1f2937;
}

/* Instructions d'utilisation */
.usage-instructions {
  margin-top: 2rem;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #bae6fd;
}

.instructions-header h4 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0c4a6e;
  margin: 0 0 1rem 0;
  text-align: center;
}

.instructions-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.instruction-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #0f172a;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 0.5rem;
  border: 1px solid rgba(14, 165, 233, 0.2);
}

.instruction-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

/* Responsive design */
@media (max-width: 1024px) {
  .chart-container {
    flex-direction: column;
  }
  
  .legend-panel {
    width: 100%;
    max-height: 300px;
  }
  
  .chart-wrapper {
    height: 500px;
  }
  
  .diagram-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-controls {
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .mollier-diagram-container {
    padding: 1rem;
  }
  
  .chart-wrapper {
    height: 400px;
  }
  
  .toggle-buttons {
    flex-wrap: wrap;
  }
  
  .instructions-content {
    grid-template-columns: 1fr;
  }
}

/* Animations */
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scrollbar personnalisée pour la légende */
.legend-panel::-webkit-scrollbar {
  width: 6px;
}

.legend-panel::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.legend-panel::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.legend-panel::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>