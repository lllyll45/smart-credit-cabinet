import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

type Item = { to: string; label: string; icon: string }

const clientLinks: Item[] = [
  { to: '/dashboard', label: 'Главная', icon: '⌂' },
  { to: '/products', label: 'Кредитные продукты', icon: '▤' },
  { to: '/compare', label: 'Сравнение кредитов', icon: '⇄' },
  { to: '/recommendations', label: 'Подбор предложений', icon: '★' },
  { to: '/applications', label: 'Мои заявки', icon: '▣' },
  { to: '/applications/new', label: 'Новая заявка', icon: '+' },
  { to: '/business-profile', label: 'Профиль бизнеса', icon: '◈' },
]

const staffLinks: Item[] = [
  { to: '/staff/applications', label: 'Заявки клиентов', icon: '⚑' },
]

export default function Sidebar() {
  const { isStaff } = useAuth()

  return (
    <aside className="sidebar">
      <NavLink to="/dashboard" className="brand">
        <span className="brand-icon">₽</span>
        <span>
          <strong>Smart Credit</strong>
          <small>Финансы под контролем</small>
        </span>
      </NavLink>

      <p className="nav-caption">МЕНЮ</p>
      <nav className="navigation">
        {clientLinks.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end
            className={({ isActive }) =>
              `nav-link${isActive ? ' active' : ''}`
            }
          >
            <span className="nav-icon">{link.icon}</span>
            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>

      {isStaff && (
        <>
          <p className="nav-caption" style={{ marginTop: 18 }}>
            STAFF
          </p>
          <nav className="navigation">
            {staffLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end
                className={({ isActive }) =>
                  `nav-link${isActive ? ' active' : ''}`
                }
              >
                <span className="nav-icon">{link.icon}</span>
                <span>{link.label}</span>
              </NavLink>
            ))}
          </nav>
        </>
      )}

      <div className="sidebar-bottom">
        <div className="help-card">
          <span className="help-icon">?</span>
          <strong>Нужна помощь?</strong>
          <p>
            Управляйте заявками и сравнивайте условия кредитов в
            одном месте.
          </p>
        </div>
        <div className="version">SMART CREDIT · V1.0</div>
      </div>
    </aside>
  )
}