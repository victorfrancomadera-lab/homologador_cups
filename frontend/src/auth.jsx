import { createContext, useContext, useEffect, useState } from 'react'
import api from './api'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  async function refresh() {
    if (!localStorage.getItem('token')) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const { data } = await api.get('/api/auth/me')
      setUser(data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function login(username, password) {
    const body = new URLSearchParams({ username, password })
    const { data } = await api.post('/api/auth/login', body)
    localStorage.setItem('token', data.access_token)
    await refresh()
  }

  function logout() {
    localStorage.removeItem('token')
    setUser(null)
    location.href = '/login'
  }

  return (
    <AuthCtx.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthCtx.Provider>
  )
}

export const useAuth = () => useContext(AuthCtx)
