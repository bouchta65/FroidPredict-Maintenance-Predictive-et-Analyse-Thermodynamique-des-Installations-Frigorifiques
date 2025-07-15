<template>
  <div class="flex flex-col items-center justify-center" :class="fullHeight ? 'h-64' : 'py-8'">
    <div class="relative">
      <!-- Outer ring -->
      <div class="w-16 h-16 border-4 border-blue-200 rounded-full animate-ping"></div>
      <!-- Inner ring -->
      <div class="absolute top-0 left-0 w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      <!-- Center dot -->
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 bg-blue-600 rounded-full"></div>
    </div>
    <div v-if="message" class="mt-4 text-center">
      <p class="text-gray-600 font-medium">{{ message }}</p>
      <p v-if="subMessage" class="text-gray-400 text-sm mt-1">{{ subMessage }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: 'Loading...'
  },
  subMessage: {
    type: String,
    default: ''
  },
  fullHeight: {
    type: Boolean,
    default: true
  }
})
</script>
