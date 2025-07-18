import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import { useRefrigerationStore } from './stores/refrigeration'
import axios from 'axios'

// Configure axios to use the Vite proxy - remove baseURL to use relative paths
// This will automatically use the proxy configured in vite.config.js
// axios.defaults.baseURL = 'http://localhost:5002' // Remove this line

// Add request interceptor for debugging
axios.interceptors.request.use(config => {
  console.log('🌐 API Request:', config.method?.toUpperCase(), config.url)
  return config
}, error => {
  console.error('❌ Request Error:', error)
  return Promise.reject(error)
})

// Add response interceptor for debugging
axios.interceptors.response.use(response => {
  console.log('✅ API Response:', response.status, response.config.url)
  return response
}, error => {
  console.error('❌ API Error:', error.response?.status, error.config?.url, error.message)
  return Promise.reject(error)
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize store with real database counts after app is mounted
app.mount('#app')

// Initialize the refrigeration store with real counts
const store = useRefrigerationStore()
store.initializeStore()
