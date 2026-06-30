import axios from 'axios'

// Mismo origen: el backend FastAPI sirve el frontend y expone /api.
const api = axios.create({ baseURL: '/' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('token')
      if (!location.pathname.startsWith('/login')) location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
