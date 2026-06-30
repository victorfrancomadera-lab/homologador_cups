import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../auth'

export default function Layout() {
  const { user, logout } = useAuth()
  return (
    <>
      <header className="topbar">
        <div className="brand">🩺 Homologador CUPS</div>
        <nav style={{ display: 'flex', alignItems: 'center' }}>
          <NavLink to="/" end>Buscador</NavLink>
          {user?.is_admin && <NavLink to="/admin">Usuarios</NavLink>}
          <span className="user">{user?.full_name || user?.username}</span>
          <button className="btn-link" onClick={logout}>Salir</button>
        </nav>
      </header>
      <Outlet />
    </>
  )
}
