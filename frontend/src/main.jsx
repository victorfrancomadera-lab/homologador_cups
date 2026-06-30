import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth'
import Login from './pages/Login'
import Buscador from './pages/Buscador'
import Admin from './pages/Admin'
import Layout from './pages/Layout'
import './styles.css'

function Protected({ children, adminOnly }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="spinner">Cargando…</div>
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && !user.is_admin) return <Navigate to="/" replace />
  return children
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            element={
              <Protected>
                <Layout />
              </Protected>
            }
          >
            <Route path="/" element={<Buscador />} />
            <Route
              path="/admin"
              element={
                <Protected adminOnly>
                  <Admin />
                </Protected>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
)
