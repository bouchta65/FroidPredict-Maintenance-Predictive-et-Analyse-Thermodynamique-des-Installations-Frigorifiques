<template>
  <div class="text-center py-12">
    <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full" :class="iconBgClass">
      <component :is="icon" class="h-8 w-8" :class="iconClass" />
    </div>
    <h3 class="mt-4 text-lg font-medium text-gray-900">{{ title }}</h3>
    <p class="mt-2 text-sm text-gray-500">{{ description }}</p>
    <div v-if="showAction" class="mt-6">
      <button
        @click="$emit('action')"
        type="button"
        class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        {{ actionText }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  ChartBarIcon,
  ExclamationTriangleIcon,
  ChartPieIcon,
  InboxIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'predictions', 'alerts', 'diagrams'].includes(value)
  },
  title: {
    type: String,
    default: 'No data available'
  },
  description: {
    type: String,
    default: 'There is no data to display at the moment.'
  },
  showAction: {
    type: Boolean,
    default: false
  },
  actionText: {
    type: String,
    default: 'Refresh'
  }
})

defineEmits(['action'])

const icon = computed(() => {
  switch (props.type) {
    case 'predictions':
      return ChartBarIcon
    case 'alerts':
      return ExclamationTriangleIcon
    case 'diagrams':
      return ChartPieIcon
    default:
      return InboxIcon
  }
})

const iconBgClass = computed(() => {
  switch (props.type) {
    case 'predictions':
      return 'bg-blue-100'
    case 'alerts':
      return 'bg-red-100'
    case 'diagrams':
      return 'bg-purple-100'
    default:
      return 'bg-gray-100'
  }
})

const iconClass = computed(() => {
  switch (props.type) {
    case 'predictions':
      return 'text-blue-600'
    case 'alerts':
      return 'text-red-600'
    case 'diagrams':
      return 'text-purple-600'
    default:
      return 'text-gray-600'
  }
})
</script>
