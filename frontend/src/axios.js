import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api/', // Django backend URL
  timeout: 5000, // Optional: Set a timeout for requests
  headers: {
    'Content-Type': 'application/json',
  },
})

export default axiosInstance