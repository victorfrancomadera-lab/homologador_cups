import { useEffect, useState } from 'react'
import api from '../api'
import { useAuth } from '../auth'

const VACIO = {
  username: '', email: '', full_name: '', password: '',
  is_active: true, is_admin: false, can_view_soat: true, can_view_iss: true,
}

export default function Admin() {
  const { user: yo } = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null) // null | {mode:'create'|'edit', data}
  const [error, setError] = useState('')

  async function cargar() {
    setLoading(true)
    try {
      const { data } = await api.get('/api/admin/users')
      setUsers(data)
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => { cargar() }, [])

  async function eliminar(u) {
    if (!confirm(`¿Eliminar al usuario "${u.username}"?`)) return
    try {
      await api.delete(`/api/admin/users/${u.id}`)
      cargar()
    } catch (err) {
      alert(err.response?.data?.detail || 'No se pudo eliminar')
    }
  }

  return (
    <div className="container">
      <div className="admin-head">
        <h2>Administración de usuarios</h2>
        <button className="btn btn-sm" onClick={() => { setError(''); setModal({ mode: 'create', data: { ...VACIO } }) }}>
          + Nuevo usuario
        </button>
      </div>
      <p className="muted" style={{ marginTop: 0 }}>
        Crea cuentas y define qué equivalencias puede consultar cada usuario.
      </p>

      {loading ? (
        <div className="spinner">Cargando…</div>
      ) : (
        <div className="card" style={{ marginTop: 12, padding: 0, overflow: 'hidden' }}>
          <table>
            <thead>
              <tr>
                <th>Usuario</th><th>Nombre / Correo</th><th>Rol</th>
                <th>Permisos</th><th>Estado</th><th></th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td><strong>{u.username}</strong></td>
                  <td>{u.full_name || '—'}<br /><span className="muted">{u.email}</span></td>
                  <td>{u.is_admin ? <span className="chip admin">Admin</span> : <span className="chip">Usuario</span>}</td>
                  <td>
                    <div className="chips">
                      <span className={`chip ${u.can_view_soat ? 'on' : 'off'}`}>SOAT</span>
                      <span className={`chip ${u.can_view_iss ? 'on' : 'off'}`}>ISS</span>
                    </div>
                  </td>
                  <td>{u.is_active ? <span className="chip on">Activo</span> : <span className="chip off">Inactivo</span>}</td>
                  <td className="row-actions">
                    <button className="btn btn-sm btn-gris" onClick={() => { setError(''); setModal({ mode: 'edit', data: { ...u, password: '' } }) }}>Editar</button>
                    {u.id !== yo.id && (
                      <button className="btn btn-sm btn-rojo" onClick={() => eliminar(u)}>Eliminar</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modal && (
        <UserModal
          modal={modal}
          yo={yo}
          error={error}
          setError={setError}
          onClose={() => setModal(null)}
          onSaved={() => { setModal(null); cargar() }}
        />
      )}
    </div>
  )
}

function UserModal({ modal, yo, error, setError, onClose, onSaved }) {
  const [form, setForm] = useState(modal.data)
  const [busy, setBusy] = useState(false)
  const esEdicion = modal.mode === 'edit'
  const esYoMismo = esEdicion && form.id === yo.id

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  async function guardar(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      if (esEdicion) {
        const payload = {
          email: form.email, full_name: form.full_name,
          is_active: form.is_active, is_admin: form.is_admin,
          can_view_soat: form.can_view_soat, can_view_iss: form.can_view_iss,
        }
        if (form.password) payload.password = form.password
        await api.put(`/api/admin/users/${form.id}`, payload)
      } else {
        await api.post('/api/admin/users', form)
      }
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'No se pudo guardar')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-bg" onMouseDown={onClose}>
      <form className="modal" onMouseDown={(e) => e.stopPropagation()} onSubmit={guardar}>
        <h3>{esEdicion ? `Editar: ${form.username}` : 'Nuevo usuario'}</h3>
        {error && <div className="error">{error}</div>}

        {!esEdicion && (
          <>
            <label>Usuario *</label>
            <input value={form.username} onChange={(e) => set('username', e.target.value)} required />
          </>
        )}
        <label>Nombre completo</label>
        <input value={form.full_name} onChange={(e) => set('full_name', e.target.value)} />
        <label>Correo *</label>
        <input type="email" value={form.email} onChange={(e) => set('email', e.target.value)} required />
        <label>{esEdicion ? 'Nueva contraseña (dejar vacío para no cambiar)' : 'Contraseña *'}</label>
        <input type="password" value={form.password} onChange={(e) => set('password', e.target.value)}
          required={!esEdicion} minLength={6} />

        <div className="check-row">
          <input type="checkbox" id="soat" checked={form.can_view_soat} onChange={(e) => set('can_view_soat', e.target.checked)} />
          <label htmlFor="soat">Puede ver equivalencias SOAT</label>
        </div>
        <div className="check-row">
          <input type="checkbox" id="iss" checked={form.can_view_iss} onChange={(e) => set('can_view_iss', e.target.checked)} />
          <label htmlFor="iss">Puede ver equivalencias ISS 2001</label>
        </div>
        <div className="check-row">
          <input type="checkbox" id="admin" checked={form.is_admin} disabled={esYoMismo}
            onChange={(e) => set('is_admin', e.target.checked)} />
          <label htmlFor="admin">Administrador {esYoMismo && <span className="muted">(no editable en tu cuenta)</span>}</label>
        </div>
        <div className="check-row">
          <input type="checkbox" id="activo" checked={form.is_active} disabled={esYoMismo}
            onChange={(e) => set('is_active', e.target.checked)} />
          <label htmlFor="activo">Cuenta activa</label>
        </div>

        <div className="modal-actions">
          <button className="btn" disabled={busy}>{busy ? 'Guardando…' : 'Guardar'}</button>
          <button type="button" className="btn btn-gris" onClick={onClose}>Cancelar</button>
        </div>
      </form>
    </div>
  )
}
