import { useState, type FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import Loader from '../components/ui/Loader'
import { useAuth } from '../hooks/useAuth'

export default function LoginPage() {
  const { login, user, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) return <Loader />
  if (user) return <Navigate to="/dashboard" replace />

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      await login(email, password)
      const from = (location.state as { from?: string } | null)?.from
      navigate(from || '/dashboard', { replace: true })
    } catch {
      setError('Не удалось войти. Проверьте email и пароль, а также доступность сервера.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="page-content">
      <section className="auth-card">
        <Link to="/" className="brand">
          <span className="brand-icon">₽</span>
          <span>Smart Credit</span>
        </Link>

        <div className="page-heading">
          <span className="eyebrow">Личный кабинет</span>
          <h1>Вход в аккаунт</h1>
          <p>Войдите, чтобы управлять кредитными заявками.</p>
        </div>

        <form onSubmit={handleSubmit}>
          <Input
            label="Email"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
          <Input
            label="Пароль"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />

          {error && <p className="form-error">{error}</p>}

          <Button type="submit" disabled={submitting}>
            {submitting ? 'Входим...' : 'Войти'}
          </Button>
        </form>

        <p className="auth-switch">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </section>
    </main>
  )
}