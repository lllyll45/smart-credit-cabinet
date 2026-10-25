import { Link } from 'react-router-dom'
import PageLayout from '../components/layout/PageLayout'
import CreditCalculator from '../features/calculator/CreditCalculator'
import { useAuth } from '../hooks/useAuth'

export default function DashboardPage() {
  const { isStaff } = useAuth()

  return (
    <PageLayout>
      <section className="welcome-banner">
        <div className="welcome-copy">
          <span className="banner-tag">SMART CREDIT</span>
          <h1>Ваши финансы — под контролем</h1>
          <p>
            Сравнивайте кредитные продукты, рассчитывайте платежи и
            следите за своими заявками в одном месте.
          </p>
          <Link to="/products" className="primary-button">
            Смотреть продукты
          </Link>
        </div>
        <div className="banner-decoration" aria-hidden="true">
          <div className="decoration-circle" />
          <div className="decoration-card">₽</div>
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <h2>Быстрые действия</h2>
        </div>
        <div className="action-grid">
          <Link to="/products" className="action-card">
            <span className="action-icon purple">▤</span>
            <h3>Кредитные продукты</h3>
            <p>Изучите доступные предложения.</p>
          </Link>
          <Link to="/recommendations" className="action-card">
            <span className="action-icon purple">★</span>
            <h3>Подбор предложений</h3>
            <p>Подберём продукты по параметрам бизнеса.</p>
          </Link>
          <Link to="/business-profile" className="action-card">
            <span className="action-icon green">◈</span>
            <h3>Профиль бизнеса</h3>
            <p>Заполните данные для точного подбора.</p>
          </Link>
          <Link to="/applications/new" className="action-card">
            <span className="action-icon purple">＋</span>
            <h3>Новая заявка</h3>
            <p>Подайте заявку на кредит.</p>
          </Link>
          <Link to="/applications" className="action-card">
            <span className="action-icon purple">▣</span>
            <h3>Мои заявки</h3>
            <p>Проверьте статус обращений.</p>
          </Link>
          {isStaff && (
            <Link to="/staff/applications" className="action-card">
              <span className="action-icon orange">⚑</span>
              <h3>Заявки клиентов</h3>
              <p>Проверка и решения по заявкам.</p>
            </Link>
          )}
        </div>
      </section>

      <section className="section-block">
        <CreditCalculator />
      </section>
    </PageLayout>
  )
}