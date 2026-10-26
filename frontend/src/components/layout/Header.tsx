import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const ROLE_LABEL: Record<string, string> = {
  client: 'Клиент',
  staff: 'Сотрудник',
  admin: 'Администратор',
}

export default function Header() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="topbar">
      <div>
        <span className="topbar-label">ЛИЧНЫЙ КАБИНЕТ</span>
        <h2>Управление финансами</h2>
      </div>

      <div className="account-actions">
        {user?.role && (
          <span className="role-badge">
            {ROLE_LABEL[user.role] ?? user.role}
          </span>
        )}

        {user?.email && <span className="user-email">{user.email}</span>}

        {user ? (
          <button
            type="button"
            className="secondary-button"
            onClick={handleLogout}
          >
            Выйти
          </button>
        ) : (
          <Link to="/login" className="login-link">
            Войти в аккаунт
          </Link>
        )}
      </div>
    </header>
  )
}