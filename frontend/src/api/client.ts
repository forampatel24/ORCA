import axios from 'axios'

export const api = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('orca_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export async function login(email: string, password: string) {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const { data } = await api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
  localStorage.setItem('orca_token', data.access_token)
  return data
}

export async function chat(message: string, location?: { lat: number; lon: number }) {
  const { data } = await api.post('/chat/', { message, location })
  return data
}

export async function getNearestPFZ(lat: number, lon: number, radius = 50) {
  const { data } = await api.get('/pfz/nearest', { params: { latitude: lat, longitude: lon, radius } })
  return data
}

export async function getWeather(lat: number, lon: number) {
  const { data } = await api.get('/weather/', { params: { latitude: lat, longitude: lon } })
  return data
}

export async function getHazards(lat: number, lon: number) {
  const { data } = await api.get('/hazards/', { params: { latitude: lat, longitude: lon } })
  return data
}
