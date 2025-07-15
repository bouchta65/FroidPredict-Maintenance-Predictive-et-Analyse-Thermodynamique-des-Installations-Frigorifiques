import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: Dashboard
    },
    {
      path: '/test',
      name: 'Test',
      component: () => import('@/views/TestDashboard.vue')
    },
    {
      path: '/predictions',
      name: 'Predictions',
      component: () => import('@/views/Predictions.vue')
    },
    {
      path: '/alerts',
      name: 'Alerts',
      component: () => import('@/views/Alerts.vue')
    },
    {
      path: '/diagrams',
      name: 'Diagrams',
      component: () => import('@/views/Diagrams.vue')
    }
  ]
})

export default router
