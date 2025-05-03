import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'

// Use environment variables for the base URL
axios.defaults.baseURL = import.meta.env.VITE_BACKEND_API_URL

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
