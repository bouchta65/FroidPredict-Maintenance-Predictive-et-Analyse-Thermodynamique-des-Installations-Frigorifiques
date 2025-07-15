import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useTestStore = defineStore('test', () => {
  const apiStatus = ref('checking...')
  const backendUrl = ref('http://localhost:5002')

  const testApiConnection = async () => {
    try {
      const response = await axios.get(`${backendUrl.value}/api/system_status`)
      if (response.data.status === 'running') {
        apiStatus.value = 'connected'
        return true
      } else {
        apiStatus.value = 'error'
        return false
      }
    } catch (error) {
      apiStatus.value = 'disconnected'
      console.error('API connection test failed:', error)
      return false
    }
  }

  return {
    apiStatus,
    backendUrl,
    testApiConnection
  }
})
