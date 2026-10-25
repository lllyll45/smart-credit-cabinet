
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/dashboard', label: 'Главная', icon: '⌂', end: true },
  { to: '/products', label: 'Кредитные продукты', icon: '▤', end: true },
  { to: '/compare', label: 'Сравнение кредитов', icon: '⇄', end: true },
  { to: '/applications', label: 'Мои заявки', icon: '▣', end: true },
  { to: '/applications/new', label: 'Новая заявка', icon: '+', end: true },
]

export default function Sidebar() {
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
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              `nav-link${isActive ? ' active' : ''}`
            }
          >
            <span className="nav-icon">{link.icon}</span>
            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="help-card">
          <span className="help-icon">?</span>
          <strong>Нужна помощь?</strong>
          <p>
            Управляйте заявками и сравнивайте условия кредитов
            в одном месте.
          </p>
        </div>

        <div className="version">SMART CREDIT · V1.0</div>
      </div>
    </aside>
  )
}
