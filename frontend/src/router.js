import { createRouter, createWebHistory } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HelloWorld, // Default component for the home route
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('./components/About.vue'), // Lazy-loaded component
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router