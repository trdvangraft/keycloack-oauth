import axios from 'axios'
import { getToken, ensureValidToken } from './auth'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:80'

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
apiClient.interceptors.request.use(
  async (config) => {
    // Ensure we have a valid token before making the request
    const token = await ensureValidToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

export async function getUser() {
  const response = await apiClient.get('/user')
  return response.data
}

export async function getAnalytics() {
  const response = await apiClient.get('/analytics')
  return response.data
}

export async function incrementAnalytics() {
  const response = await apiClient.put('/analytics')
  return response.data
}

export default apiClient
