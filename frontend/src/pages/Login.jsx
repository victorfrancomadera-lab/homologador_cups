import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo iniciar sesión')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={onSubmit}>
        <h1>Homologador CUPS</h1>
        <p className="sub">SOAT vigente · Manual ISS 2001 · Vigencia de códigos</p>
        {error && <div className="error">{error}</div>}
        <label>Usuario</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus required />
        <label>Contraseña</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button className="btn" disabled={busy}>{busy ? 'Ingresando…' : 'Ingresar'}</button>
      </form>
    </div>
  )
}
