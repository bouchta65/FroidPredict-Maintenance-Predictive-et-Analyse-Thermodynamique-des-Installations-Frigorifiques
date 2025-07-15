import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'
import { useRefrigerationStore } from './stores/refrigeration'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize store with real database counts after app is mounted
app.mount('#app')

// Initialize the refrigeration store with real counts
const store = useRefrigerationStore()
store.initializeStore()
