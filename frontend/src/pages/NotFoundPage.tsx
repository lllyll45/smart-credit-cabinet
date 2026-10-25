import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <main className="page-content">
      <section className="content-card">
        <span className="eyebrow">Ошибка 404</span>
        <h1>Страница не найдена</h1>
        <p>Возможно, адрес изменился или страница была удалена.</p>
        <Link className="primary-button" to="/dashboard">
          На главную
        </Link>
      </section>
    </main>
  )
}