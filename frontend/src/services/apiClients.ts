import axios from 'axios'
export const TOKEN_KEY = 'smart-credit-access-token'

const baseURL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

export const api = axios.create({
  baseURL,
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('smart-credit-access-token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})