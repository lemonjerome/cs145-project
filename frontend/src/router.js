import { createRouter, createWebHistory } from 'vue-router'
import LandingPageView from './views/LandingPageView.vue'
import GpxFormView from './views/GpxFormView.vue'
import DestinationFommView from './views/DestinationFormView.vue'
import SimulateFormView from './views/SimulateFormView.vue'

const routes = [
  {
    path: '/',
    name: 'LandingPage',
    component: LandingPageView, // Default component for the home route
  },
  {
    path: '/route',
    name: 'GpxForm',
    component: GpxFormView, // Component for the route form
  },
  {
    path: '/destination',
    name: 'DestinationForm',
    component: DestinationFommView, // Component for the destination form
  },
  {
    path: '/simulate',
    name: 'SimulateForm',
    component: SimulateFormView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router