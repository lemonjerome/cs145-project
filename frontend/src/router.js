import { createRouter, createWebHistory } from 'vue-router'
import LandingPageView from './views/LandingPageView.vue'

const routes = [
  {
    path: '/',
    name: 'LandingPage',
    component: LandingPageView, // Default component for the home route
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router