import axios from 'axios'

// In production: /api (nginx proxies to backend)
// In development: http://localhost:8000
const BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000' 
  : '/api'

const api = axios.create({
  baseURL: BASE_URL
})

// Automatically add client_id header to every request
api.interceptors.request.use(config => {
  const clientId = localStorage.getItem('client_id')
  if (clientId) {
    config.headers['x-client-id'] = clientId
  }
  return config
})

export default api
