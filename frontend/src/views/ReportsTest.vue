<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold text-gray-900 mb-2">📊 Reports Test Page</h1>
    <p class="text-gray-600 mb-6">This is a test page to check if routing works</p>
    
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Basic Test</h2>
      <p>If you can see this, the routing is working correctly.</p>
      <p>Current time: {{ currentTime }}</p>
      <button @click="testClick" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md">
        Test Button ({{ clickCount }})
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentTime = ref(new Date().toLocaleString())
const clickCount = ref(0)

const testClick = () => {
  clickCount.value++
  currentTime.value = new Date().toLocaleString()
}

onMounted(() => {
  console.log('Reports Test page mounted successfully')
})
</script>
