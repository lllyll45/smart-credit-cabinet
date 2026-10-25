import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

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
        {user?.email && (
          <span className="user-email">{user.email}</span>
        )}

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