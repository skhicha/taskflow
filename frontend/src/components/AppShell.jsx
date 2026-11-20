import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Avatar } from './ui'

export default function AppShell() {
  const { user, logout } = useAuth()

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <span className="brand-name">TaskFlow</span>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" end className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
            <span className="label">Projects</span>
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          {user && (
            <div className="user-chip">
              <Avatar name={user.full_name} title={user.email} />
              <div>
                <div className="user-chip-name">{user.full_name}</div>
                <div className="user-chip-email">{user.email}</div>
              </div>
            </div>
          )}
          <button type="button" className="btn btn-secondary btn-sm" onClick={logout}>
            <span className="label">Log out</span>
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
