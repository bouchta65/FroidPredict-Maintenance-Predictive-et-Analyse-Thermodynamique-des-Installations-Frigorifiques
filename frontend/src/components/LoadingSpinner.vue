<template>
  <div class="flex flex-col items-center justify-center" :class="fullHeight ? 'h-64' : 'py-8'">
    <div class="relative">
      <!-- Enhanced spinner with multiple rings -->
      <div class="w-16 h-16 border-4 border-blue-100 rounded-full animate-ping"></div>
      <div class="absolute top-0 left-0 w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      <div class="absolute top-2 left-2 w-12 h-12 border-3 border-purple-400 border-t-transparent rounded-full animate-spin" style="animation-direction: reverse; animation-duration: 1.5s;"></div>
      <!-- Pulsing center dot -->
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full animate-pulse"></div>
      
      <!-- Orbiting dots -->
      <div class="absolute top-1/2 left-1/2 w-20 h-20 transform -translate-x-1/2 -translate-y-1/2">
        <div class="absolute w-2 h-2 bg-blue-400 rounded-full animate-spin" style="top: 0; left: 50%; margin-left: -4px; animation-duration: 2s;">
          <div class="w-2 h-2 bg-blue-400 rounded-full" style="transform: translateY(-10px);"></div>
        </div>
        <div class="absolute w-2 h-2 bg-purple-400 rounded-full animate-spin" style="top: 50%; right: 0; margin-top: -4px; animation-duration: 2s; animation-delay: 0.5s;">
          <div class="w-2 h-2 bg-purple-400 rounded-full" style="transform: translateX(10px);"></div>
        </div>
        <div class="absolute w-2 h-2 bg-indigo-400 rounded-full animate-spin" style="bottom: 0; left: 50%; margin-left: -4px; animation-duration: 2s; animation-delay: 1s;">
          <div class="w-2 h-2 bg-indigo-400 rounded-full" style="transform: translateY(10px);"></div>
        </div>
        <div class="absolute w-2 h-2 bg-cyan-400 rounded-full animate-spin" style="top: 50%; left: 0; margin-top: -4px; animation-duration: 2s; animation-delay: 1.5s;">
          <div class="w-2 h-2 bg-cyan-400 rounded-full" style="transform: translateX(-10px);"></div>
        </div>
      </div>
    </div>
    
    <div v-if="message" class="mt-6 text-center max-w-xs">
      <p class="text-gray-700 font-medium text-lg">{{ message }}</p>
      <p v-if="subMessage" class="text-gray-500 text-sm mt-2 leading-relaxed">{{ subMessage }}</p>
      
      <!-- Progress dots -->
      <div class="flex justify-center mt-4 space-x-1">
        <div v-for="i in 3" :key="i" 
             class="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
             :style="{ animationDelay: `${(i-1) * 0.2}s` }">
        </div>
      </div>
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

<style scoped>
/* Enhanced animations */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes ping {
  75%, 100% {
    transform: scale(2);
    opacity: 0;
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(-25%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
  }
  50% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Custom border width */
.border-3 {
  border-width: 3px;
}

/* Smooth transitions */
.animate-spin {
  animation: spin 1s linear infinite;
}

.animate-ping {
  animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.animate-bounce {
  animation: bounce 1s infinite;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
