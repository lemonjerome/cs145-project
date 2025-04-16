import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'

axios.defaults.baseURL = 'http://localhost:8000/internship'

const app = createApp(App)

app.use(createPinia())
app.use(router, axios )

app.mount('#app')
